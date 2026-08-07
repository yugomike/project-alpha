"""Save each extracted item as a markdown article, so an item is never
re-extracted once we already have it."""

import hashlib
from pathlib import Path

import yaml

ARTICLES_DIR = Path("articles")


def _article_path(source_slug, item):
    # Hash the item's id (its URL) rather than deriving a filename from
    # its title/date — those vary in format across sources (Fed's date
    # string, BoC's ISO timestamp, SEC's plain date), while the id is
    # always a clean, unique URL.
    digest = hashlib.sha256(item["id"].encode()).hexdigest()[:16]
    return ARTICLES_DIR / source_slug / f"{digest}.md"


def save_article(source_slug, item, text):
    """Save one extracted item as a markdown file: YAML frontmatter
    holding its metadata, followed by the extracted text. Returns the
    path it was saved to."""
    path = _article_path(source_slug, item)
    path.parent.mkdir(parents=True, exist_ok=True)

    frontmatter = yaml.safe_dump({
        "title": item["title"],
        "source": source_slug,
        "published": item["published"],
        "url": item["url"],
    }, sort_keys=False, allow_unicode=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"---\n{frontmatter}---\n\n{text}")
    return path