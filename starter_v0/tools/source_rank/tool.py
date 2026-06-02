from __future__ import annotations

from typing import Any

from tools._shared import domain


HIGH_SIGNAL_DOMAINS = {
    "arxiv.org",
    "openai.com",
    "anthropic.com",
    "deepmind.google",
    "nature.com",
    "science.org",
    "acm.org",
    "ieee.org",
}


def _score(item: dict[str, Any]) -> int:
    score = 0
    url = item.get("url") or ""
    source = (item.get("source") or domain(url)).lower()
    if item.get("title"):
        score += 2
    if url:
        score += 2
    if item.get("summary"):
        score += 2
    if any(host in source for host in HIGH_SIGNAL_DOMAINS):
        score += 3
    if item.get("published") or item.get("date"):
        score += 1
    return score


def source_rank(items: list[dict[str, Any]] | None = None, max_items: int = 5) -> dict[str, Any]:
    items = items or []
    try:
        max_items = int(max_items or 5)
    except (TypeError, ValueError):
        max_items = 5
    max_items = max(1, min(max_items, 20))
    ranked = []

    for item in items:
        ranked_item = dict(item)
        ranked_item["rank_score"] = _score(item)
        ranked.append(ranked_item)

    ranked.sort(key=lambda item: item["rank_score"], reverse=True)
    return {
        "tool": "source_rank",
        "items": ranked[:max_items],
        "item_count": len(ranked[:max_items]),
        "total_items": len(items),
    }
