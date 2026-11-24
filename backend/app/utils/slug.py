"""Tiny URL slug helper (no extra dependency)."""
from __future__ import annotations

import re
import unicodedata

_SAFE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return _SAFE.sub("-", ascii_text.lower()).strip("-")
