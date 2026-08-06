"""Track which items have already been processed, so re-running the
pipeline doesn't reprocess or duplicate them."""

import json
from pathlib import Path

STATE_PATH = Path("state/seen.json")


def load_seen():
    """Return the set of item IDs already processed, empty if none yet."""
    if not STATE_PATH.exists():
        return set()
    with open(STATE_PATH, encoding="utf-8") as f:
        return set(json.load(f))


def save_seen(seen_ids):
    """Persist the given set of item IDs to disk."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(seen_ids), f, indent=2)


def filter_new(items, seen_ids):
    """Return only the items whose id is not already in seen_ids."""
    return [item for item in items if item["id"] not in seen_ids]