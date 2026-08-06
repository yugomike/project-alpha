"""Fetch new press releases from the Bank of Canada's press-release RSS feed."""

import feedparser

FEED_URL = "https://www.bankofcanada.ca/content_type/press-releases/feed/"


# Unlike the Fed, Bank of Canada has no feed scoped to just rate-decision
# statements — their "press releases" feed mixes rate decisions in with
# museum exhibit announcements, staff appointments, media interviews, etc.
# There's also no metadata tag distinguishing them (everything is tagged
# "Announcement"). The only reliable signal is the title itself: every rate
# decision follows the pattern "...maintains/raises/lowers the policy rate
# at X%". So we filter on that rather than taking every item in the feed.
RATE_DECISION_KEYWORD = "policy rate"


def fetch_latest(limit=5):
    """Return the most recent Bank of Canada rate-decision statements.

    Each item is a dict with: id, title, url, published.
    Bank of Canada's feed is RSS 1.0 (RDF), not RSS 2.0 like the Fed's —
    feedparser normalizes both into the same entry shape, but RDF feeds use
    `updated` for the date field where RSS 2.0 uses `published`.
    """
    feed = feedparser.parse(FEED_URL)
    items = []
    for entry in feed.entries:
        if RATE_DECISION_KEYWORD not in entry.title.lower():
            continue
        items.append({
            "id": entry.get("id", entry.link),
            "title": entry.title,
            "url": entry.link,
            "published": entry.get("published", entry.get("updated", "")),
        })
        if len(items) >= limit:
            break
    return items
