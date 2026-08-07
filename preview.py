"""Manual check: fetch the latest item from each source, print its
extracted text, and synthesize it to an MP3 so both the text quality and
voice quality can be checked in one run.

Run with: .venv\\Scripts\\python.exe preview.py
""" 

import functools
import yaml

from pipeline.extract import extract_boc, extract_fed, extract_sec_filing
from pipeline.sources import boc, fed
from pipeline.sources import sec


def preview(source_name, fetch_latest, extract):
    """Print the latest item from one source: metadata plus extracted text."""
    items = fetch_latest(limit=1)
    if not items:
        print(f"{source_name}: no items found")
        return
    item = items[0]
    print(f"=== {source_name}: {item['title']} ===")
    print(f"Published: {item['published']}")
    print(f"URL: {item['url']}")
    print()
    print(extract(item["url"]))
    print()


if __name__ == "__main__":
    preview("Federal Reserve", fed.fetch_latest, extract_fed)
    preview("Bank of Canada", boc.fetch_latest, extract_boc)

    with open("config/watchlist.yml") as f:
        tickers = yaml.safe_load(f)["tickers"]
    preview("SEC EDGAR", functools.partial(sec.fetch_latest, tickers), extract_sec_filing)