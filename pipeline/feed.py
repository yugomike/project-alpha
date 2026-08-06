"""Build the podcast RSS feed from whatever episodes exist in docs/episodes/."""

import os
from datetime import datetime, timezone
from pathlib import Path

from feedgen.feed import FeedGenerator

BASE_URL = "https://yugomike.github.io/project-alpha"
EPISODES_DIR = Path("docs/episodes")
FEED_PATH = Path("docs/feed.xml")


def build_feed():
    """Regenerate docs/feed.xml from every MP3 currently in docs/episodes/.

    Rebuilding from the actual files on disk (rather than tracking a
    separate list of published episodes) means the feed can never drift
    out of sync with what's actually there.
    """
    fg = FeedGenerator()
    fg.load_extension("podcast")
    fg.id(BASE_URL)
    fg.title("Project Alpha Briefing")
    fg.link(href=BASE_URL, rel="alternate")
    fg.description("Primary-source economic and investment briefing.")
    fg.language("en")
    fg.podcast.itunes_category("News")
    fg.podcast.itunes_author("Project Alpha")
    fg.podcast.itunes_explicit("no")

    episode_files = sorted(EPISODES_DIR.glob("*.mp3"))  # oldest first —
    # feedgen inserts each new entry at the front, so this ends up
    # newest-first in the actual feed, which is what podcast apps expect.
    for episode_path in episode_files:
        date_str = episode_path.stem  # filename is YYYY-MM-DD.mp3
        url = f"{BASE_URL}/episodes/{episode_path.name}"
        size = os.path.getsize(episode_path)

        fe = fg.add_entry()
        fe.id(url)
        fe.title(f"Briefing for {date_str}")
        fe.description(f"Primary-source briefing for {date_str}.")
        fe.enclosure(url, str(size), "audio/mpeg")
        fe.pubDate(datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc))

    fg.rss_file(str(FEED_PATH))