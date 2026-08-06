"""Manual check for Phase 5: combine the Phase 4 sample clips into one
dated episode and regenerate the podcast feed, so it can be pushed to
GitHub Pages and subscribed to in a real podcast app.

Run with: .venv\\Scripts\\python.exe assemble_preview.py
"""

from datetime import date
from pathlib import Path

from pipeline.assemble import assemble_episode
from pipeline.feed import build_feed

if __name__ == "__main__":
    Path("docs/episodes").mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    episode_path = f"docs/episodes/{today}.mp3"
    assemble_episode(["sample_fed.mp3", "sample_boc.mp3", "sample_sec.mp3"], episode_path)
    print(f"Episode saved to {episode_path}")

    build_feed()
    print("Feed saved to docs/feed.xml")