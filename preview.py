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
from pipeline.tts import synthesize


def preview(source_name, fetch_latest, extract, audio_path):
    """Print the latest item from one source and synthesize it to audio.

    source_name:  label for the printed header, e.g. "Federal Reserve".
    fetch_latest: a source module's function for listing new items,
                  e.g. fed.fetch_latest or boc.fetch_latest. Takes a
                  `limit` argument, returns a list of item dicts
                  (each with id/title/url/published).
    extract:      the matching extraction function for that source,
                  e.g. extract_fed or extract_boc. Takes one item's
                  url, returns its cleaned body text as a string.
    audio_path:   where to save the synthesized MP3, e.g. "sample_fed.mp3".
    """
    items = fetch_latest(limit=1)
    if not items:
        print(f"{source_name}: no items found")
        return
    item = items[0]
    print(f"=== {source_name}: {item['title']} ===")
    print(f"Published: {item['published']}")
    print(f"URL: {item['url']}")
    print()
    text = extract(item["url"])
    print(text)
    print()
    synthesize(text, audio_path)
    print(f"Audio saved to {audio_path}")
    print()

if __name__ == "__main__":

    with open("config/watchlist.yml") as f:
            tickers = yaml.safe_load(f)["tickers"]


    preview("Federal Reserve", fed.fetch_latest, extract_fed, "sample_fed.mp3")
    preview("Bank of Canada", boc.fetch_latest, extract_boc, "sample_boc.mp3")
    preview("SEC EDGAR", functools.partial(sec.fetch_latest, tickers), extract_sec_filing, "sample_sec.mp3")