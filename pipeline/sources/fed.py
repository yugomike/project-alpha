"""Fetch new press releases from the Federal Reserve's monetary policy RSS feed."""

import feedparser

FEED_URL = "https://www.federalreserve.gov/feeds/press_monetary.xml"


def fetch_latest(limit=5):
    """Return the most recent Fed monetary policy press releases.

    Each item is a dict with: id, title, url, published.
    `id` is stable across runs and is what Phase 6 state tracking will use
    to detect items already processed.
    """
    feed = feedparser.parse(FEED_URL)
    items = []
    for entry in feed.entries[:limit]:
        items.append({
            "id": entry.get("id", entry.link),
            "title": entry.title,
            "url": entry.link,
            "published": entry.get("published", ""),
        })
    return items
