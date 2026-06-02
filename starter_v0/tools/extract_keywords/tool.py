from __future__ import annotations

from collections import Counter
import re
from typing import Any

from tools._shared import fold_text, terms


EXTRA_STOPWORDS = {
    "chu",
    "de",
    "hom",
    "kiem",
    "moi",
    "nhat",
    "search",
    "tim",
    "tin",
    "topic",
    "tuc",
}


def _bounded_int(value: int | str | None, default: int, lower: int, upper: int) -> int:
    try:
        parsed = int(value or default)
    except (TypeError, ValueError):
        parsed = default
    return max(lower, min(parsed, upper))


def extract_keywords(text: str, max_keywords: int = 5) -> dict[str, Any]:
    max_keywords = _bounded_int(max_keywords, 5, 1, 20)
    folded = fold_text(text or "")
    allowed = terms(folded) - EXTRA_STOPWORDS
    counts = Counter(term for term in re.findall(r"[a-z0-9]+", folded) if term in allowed)

    keywords = [term for term, _count in counts.most_common(max_keywords)]
    return {
        "tool": "extract_keywords",
        "query": text,
        "keywords": keywords,
        "count": len(keywords),
    }
