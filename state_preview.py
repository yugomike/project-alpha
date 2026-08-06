"""Manual check for Phase 6: fetch the latest Fed item, show it's new,
mark it seen, then fetch again to show it no longer counts as new.

Run with: .venv\\Scripts\\python.exe state_preview.py
"""

from pipeline.sources import fed
from pipeline.state import filter_new, load_seen, save_seen

if __name__ == "__main__":
    seen = load_seen()
    print(f"Currently tracking {len(seen)} seen item(s)")

    items = fed.fetch_latest(limit=1)
    new_items = filter_new(items, seen)
    print(f"Fetched {len(items)} item(s), {len(new_items)} new")

    seen.update(item["id"] for item in new_items)
    save_seen(seen)

    items_again = fed.fetch_latest(limit=1)
    new_again = filter_new(items_again, seen)
    print(f"Second fetch: {len(new_again)} new (should be 0)")