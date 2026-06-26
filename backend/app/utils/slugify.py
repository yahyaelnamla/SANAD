"""URL-safe slug generation."""

from __future__ import annotations

import re
import unicodedata


def slugify(value: str) -> str:
    """Convert a display name to a URL slug."""
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^\w\s-]", "", ascii_text)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug[:80] or "scholar"
