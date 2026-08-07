"""Run once: fetch new items from every source, extract their text, and
save each as a markdown article — skipping anything already processed
(see state.py)."""

import functools

import yaml

from pipeline.archive import save_article
from pipeline.extract import extract_boc, extract_fed, extract_sec_filing
from pipeline.sources import boc, fed, sec
from pipeline.state import filter_new, load_seen, save_seen


def _load_watchlist():
    with open("config/watchlist.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)["tickers"]


def main():
    seen = load_seen()

    sources = [
        ("fed", "Federal Reserve", fed.fetch_latest, extract_fed),
        ("boc", "Bank of Canada", boc.fetch_latest, extract_boc),
    ]
    tickers = _load_watchlist()
    if tickers:
        sources.append(("sec", "SEC EDGAR", functools.partial(sec.fetch_latest, tickers), extract_sec_filing))

    new_ids = []
    for slug, source_name, fetch_latest, extract in sources:
        items = filter_new(fetch_latest(limit=5), seen)
        for item in items:
            print(f"New: {source_name} — {item['title']}")
            text = extract(item["url"])
            path = save_article(slug, item, text)
            print(f"Saved to {path}")
            new_ids.append(item["id"])

    if not new_ids:
        print("Nothing new.")

    seen.update(new_ids)
    save_seen(seen)


if __name__ == "__main__":
    main()