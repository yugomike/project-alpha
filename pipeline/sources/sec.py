"""Fetch new 8-K filings from SEC EDGAR for a watchlist of tickers."""

import requests

HEADERS = {"User-Agent": "project-alpha-podcast-pipeline (personal use; contact: mikehy135@gmail.com)"}
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"


def _build_ticker_to_cik():
    """SEC identifies companies by a numeric CIK, not by ticker. Download
    their full ticker -> CIK mapping once per run and return it as a dict,
    since we need to look up every ticker in the watchlist."""
    response = requests.get(TICKERS_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return {
        entry["ticker"].upper(): f"{entry['cik_str']:010d}"
        for entry in response.json().values()
    }


def fetch_latest(tickers, limit=5):
    """Return the most recent 8-K filings for each ticker in the watchlist.

    Each item is a dict with: id, title, url, published, ticker.
    `limit` applies per ticker, not to the combined list.
    """
    ticker_to_cik = _build_ticker_to_cik()
    items = []
    for ticker in tickers:
        cik = ticker_to_cik.get(ticker.upper())
        if cik is None:
            continue
        response = requests.get(SUBMISSIONS_URL.format(cik=cik), headers=HEADERS, timeout=10)
        response.raise_for_status()
        recent = response.json()["filings"]["recent"]

        count = 0
        for i, form in enumerate(recent["form"]):
            if form != "8-K":
                continue
            accession = recent["accessionNumber"][i].replace("-", "")
            primary_doc = recent["primaryDocument"][i]
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary_doc}"
            items.append({
                "id": url,
                "title": f"{ticker} 8-K filed {recent['filingDate'][i]}",
                "url": url,
                "published": recent["filingDate"][i],
                "ticker": ticker,
            })
            count += 1
            if count >= limit:
                break
    return items