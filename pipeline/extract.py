"""Turn a source's raw HTML page into clean, readable text.

Each source gets its own extraction function because every site structures
its HTML differently. The shared rule across all of them: subtract noise
(navigation, boilerplate), never add or rewrite anything.
"""

import re
import warnings
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# A descriptive User-Agent is good practice for any automated fetching, and
# a hard requirement for the SEC EDGAR API used in Phase 3 — set the
# convention here so every source module uses the same one.
HEADERS = {"User-Agent": "project-alpha-podcast-pipeline (personal use; contact: mikehy135@gmail.com)"}


def _clean_text(text):
    """Fix spacing artifacts left by inline tags with no surrounding
    whitespace in the source HTML (e.g. a link glued directly to a
    neighboring word)."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,;:%)])", r"\1", text)
    text = re.sub(r"([(])\s+", r"\1", text)
    return text.strip()


def _paragraphs_to_text(paragraphs):
    """Join <p> elements into clean text."""
    lines = []
    for p in paragraphs:
        text = p.get_text(" ", strip=True)
        if text:
            lines.append(_clean_text(text))
    return "\n\n".join(lines)


def extract_fed(url):
    """Extract the body text of a Federal Reserve press release page.

    The content lives entirely in <p> tags inside div#article — restricting
    to that container and tag already excludes the page's "Share" button
    and heading, so no further boilerplate stripping is needed.
    """
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    # federalreserve.gov doesn't declare a charset in its Content-Type
    # header, so requests falls back to Latin-1 and mangles characters
    # like em-dashes. The page is actually UTF-8.
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "lxml")
    article = soup.select_one("div#article")
    return _paragraphs_to_text(article.find_all("p"))


def extract_boc(url):
    """Extract the body text of a Bank of Canada press release page.

    The content lives in <p> tags inside div.post-content.
    """
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    content = soup.select_one("div.post-content")
    return _paragraphs_to_text(content.find_all("p"))


ITEM_HEADING_RE = re.compile(r"^Item\s+\d+\.\d+")
SIGNATURE_RE = re.compile(r"^SIGNATURE", re.IGNORECASE)


def _fetch_soup(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"
    return BeautifulSoup(response.text, "lxml")


def _remove_noise(soup):
    """Strip elements that would otherwise leak into extracted text:
    hidden inline-XBRL metadata (marked display:none in CSS, invisible on
    screen but not to a text scraper) and genuine tabular data (financial
    statements, exhibit lists — unreadable as narration). Single-row
    tables are left alone: some filers use them purely to bold a heading
    next to its text, not to hold data, and real data tables always have
    more than one row."""
    for hidden in soup.find_all(style=lambda s: s and "display:none" in s.replace(" ", "")):
        hidden.decompose()
    for table in soup.find_all("table"):
        if len(table.find_all("tr")) > 1:
            table.decompose()


def _leaf_blocks_to_lines(soup, stop_at_hr=False):
    """SEC filings structure paragraphs as <div> elements, not <p> — and a
    surviving single-row heading table (see _remove_noise) holds its text
    in <td>. Return the text of each innermost div/td (one with no nested
    div/td) that has content — the paragraph-equivalent unit here.

    stop_at_hr: press releases use <hr> to mark the end of the actual news
    and the start of the standard "forward-looking statements / About the
    company / press contacts" footer. Primary 8-K forms also contain <hr>
    tags, but just as generic layout dividers throughout their cover page
    — so this cutoff is only correct for exhibits, not primary documents.
    """
    lines = []
    for block in soup.find_all(["div", "td", "hr"]):
        if block.name == "hr":
            if stop_at_hr:
                break
            continue
        if block.find(["div", "td"]) is not None:
            continue
        text = block.get_text(" ", strip=True)
        if text:
            lines.append(_clean_text(text))
    return lines


def _extract_document_text(url):
    """Fetch one SEC document (a primary filing or an attached exhibit)
    and return its cleaned text as a list of lines."""
    soup = _fetch_soup(url)
    _remove_noise(soup)
    return _leaf_blocks_to_lines(soup.body, stop_at_hr=True)


def extract_sec_filing(url):
    """Extract the body text of an SEC 8-K filing.

    Every 8-K opens with the same legal cover page (registrant info,
    exchange checkboxes) before the actual news — drop everything before
    the first "Item X.X" heading, and drop the signature block at the end.
    If the filing links to an attached exhibit (common for earnings
    announcements, where the real content is a separate press release),
    fetch and append that too.
    """
    soup = _fetch_soup(url)

    # Exhibit links must be found before tables are stripped — on EDGAR
    # filings, the exhibit list itself is a (multi-row) table, so removing
    # data tables would delete this link along with the real noise.
    exhibit_urls = [
        urljoin(url, a["href"])
        for a in soup.find_all("a", href=True)
        if not a["href"].startswith(("http", "#"))
    ]

    _remove_noise(soup)
    lines = _leaf_blocks_to_lines(soup.body)

    start = next((i for i, line in enumerate(lines) if ITEM_HEADING_RE.match(line)), 0)
    end = next((i for i, line in enumerate(lines) if SIGNATURE_RE.match(line)), len(lines))
    sections = ["\n\n".join(lines[start:end])]

    for exhibit_url in exhibit_urls:
        sections.append("\n\n".join(_extract_document_text(exhibit_url)))

    return "\n\n".join(sections) 