# Project Alpha — Primary-Source Briefing Archive

A personal pipeline that finds and extracts primary-source economic/investment text
— straight from the source, before any commentator has interpreted it — and archives
it as clean markdown articles.

## Why "primary source" and not just "another finance newsletter"

Popular finance commentary is secondary: someone already read the Fed statement or
the 8-K and is telling you what they think it means. That's a layer of interpretation
on top of the original text, and it's the same layer everyone else is hearing too —
there's no edge in it. This project extracts the original text itself, so the
interpretation is left to the reader.

Note that "primary source" doesn't mean "unbiased" — a Fed statement is a deliberately
crafted communication, and an 8-K's management commentary is curated PR. What this
project avoids isn't bias in the source, it's an *additional* layer of bias from a
commentator on top of the source.

## How it works

```
sources → extract → archive (markdown)
```

1. **Sources** (`pipeline/sources/`) fetch new items from each origin: Fed and Bank of
   Canada press releases (via their official RSS feeds), and SEC 8-K filings for a
   watchlist of tickers (via SEC EDGAR's public API).
2. **Extract** (`pipeline/extract.py`) turns each item's raw HTML into clean, readable
   text — stripping navigation, legal boilerplate, and other non-content — without
   summarizing or rewriting anything. The goal is subtraction only, never addition.
3. **Archive** (`pipeline/archive.py`) saves each extracted item as its own markdown
   file with metadata (title, source, published date, url) as YAML frontmatter, under
   `articles/<source>/`.

`state/seen.json` tracks which items have already been processed, so running the
pipeline again never re-extracts or duplicates an article.

Run it with:

```bash
python -m pipeline.main
```

There's no automation right now — it's run on demand while the project is still
actively taking shape (see Project status below).

## Project status

Pivoted away from an earlier text-to-speech/podcast version of this project (that
code briefly existed and was removed — see git history if curious) once it became
clear the actual value here is the extraction layer, not the audio delivery
mechanism. Currently focused on building out that extraction layer and adding more
sources before revisiting output format (written digest, audio, something else) or
scheduling.

## Currently being added

Earnings call transcripts — a high-value primary source deferred from the original
MVP, now the next priority given the source → extract → archive pattern is proven
across three very differently-structured sources.

## Explicitly out of scope (for now)

ECB statements, economic data releases (CPI/jobs), summarization of extracted
content, and any scheduling/automation. Deferred, not forgotten.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
