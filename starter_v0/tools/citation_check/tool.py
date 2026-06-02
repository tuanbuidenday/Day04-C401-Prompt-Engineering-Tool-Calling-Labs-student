from __future__ import annotations

from typing import Any


def citation_check(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    items = items or []
    issues: list[dict[str, Any]] = []

    for index, item in enumerate(items):
        missing = []
        if not item.get("title"):
            missing.append("title")
        if not item.get("url") and not item.get("source"):
            missing.append("url_or_source")
        if not item.get("summary"):
            missing.append("summary")
        if missing:
            issues.append({"index": index, "missing": missing})

    return {
        "tool": "citation_check",
        "passed": not issues,
        "item_count": len(items),
        "issues": issues,
    }
