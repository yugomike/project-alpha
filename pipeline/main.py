"""Daily orchestration: fetch new items from every source, synthesize
them, assemble into one episode, and update the feed — skipping anything
already processed (see state.py)."""

import functools
import tempfile
from datetime import date
from pathlib import Path

import yaml

from pipeline.assemble import assemble_episode
from pipeline.extract import extract_boc, extract_fed, extract_sec_filing
from pipeline.feed import build_feed
from pipeline.sources import boc, fed, sec
from pipeline.state import filter_new, load_seen, save_seen
from pipeline.tts import synthesize


def _load_watchlist():
    with open("config/watchlist.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)["tickers"]


def main():
    seen = load_seen()

    # Central bank statements first, then SEC filings — matches the
    # listening order described back in the original project plan.
    sources = [
        ("Federal Reserve", fed.fetch_latest, extract_fed),
        ("Bank of Canada", boc.fetch_latest, extract_boc),
    ]
    tickers = _load_watchlist()
    if tickers:
        sources.append(("SEC EDGAR", functools.partial(sec.fetch_latest, tickers), extract_sec_filing))

    new_ids = []
    clip_paths = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        for source_name, fetch_latest, extract in sources:
            items = filter_new(fetch_latest(limit=5), seen)
            for item in items:
                print(f"New: {source_name} — {item['title']}")
                text = extract(item["url"])
                clip_path = f"{tmp_dir}/{len(clip_paths)}.mp3"
                synthesize(text, clip_path)
                clip_paths.append(clip_path)
                new_ids.append(item["id"])

        if not clip_paths:
            print("Nothing new today — no episode created.")
            return

        Path("docs/episodes").mkdir(parents=True, exist_ok=True)
        episode_path = f"docs/episodes/{date.today().isoformat()}.mp3"
        assemble_episode(clip_paths, episode_path)
        print(f"Episode saved to {episode_path}")

    seen.update(new_ids)
    save_seen(seen)

    build_feed()
    print("Feed updated.")


if __name__ == "__main__":
    main()