from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _headers() -> dict[str, str]:
    token = os.getenv("NOTION_API_KEY")
    if not token:
        raise RuntimeError("Missing NOTION_API_KEY env var")
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": os.getenv("NOTION_VERSION", NOTION_VERSION),
        "Content-Type": "application/json",
    }


def _plain_text(rich_text: list[dict[str, Any]] | None) -> str:
    return "".join(part.get("plain_text", "") for part in rich_text or []).strip()


def _title_from_properties(properties: dict[str, Any]) -> str:
    for prop in properties.values():
        if prop.get("type") == "title":
            title = _plain_text(prop.get("title"))
            if title:
                return title
    return "Untitled"


def _object_title(item: dict[str, Any]) -> str:
    if item.get("object") == "database":
        return _plain_text((item.get("title") or [])) or "Untitled database"
    if item.get("object") == "page":
        return _title_from_properties(item.get("properties") or {})
    return item.get("id", "Untitled")


def _block_text(block: dict[str, Any]) -> str:
    block_type = block.get("type")
    data = block.get(block_type or "", {}) if block_type else {}
    if block_type in {
        "paragraph",
        "heading_1",
        "heading_2",
        "heading_3",
        "bulleted_list_item",
        "numbered_list_item",
        "to_do",
        "toggle",
        "quote",
        "callout",
    }:
        return _plain_text(data.get("rich_text"))
    if block_type == "child_page":
        return data.get("title", "")
    if block_type == "child_database":
        return data.get("title", "")
    return ""


def _search_notion(query: str, limit: int) -> dict[str, Any]:
    response = requests.post(
        f"{NOTION_API_URL}/search",
        headers=_headers(),
        json={
            "query": query,
            "page_size": limit,
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
        },
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    items = []
    for item in data.get("results", []):
        object_type = item.get("object", "")
        item_id = item.get("id", "")
        items.append({
            "title": _object_title(item),
            "id": item_id,
            "object": object_type,
            "url": item.get("url", ""),
            "source": "notion",
            "last_edited_time": item.get("last_edited_time"),
            "summary": f"Notion {object_type}: {item_id}",
        })
    return {
        "tool": "notion",
        "mode": "search",
        "query": query,
        "items": items,
        "has_more": data.get("has_more", False),
    }


def _read_page(page_id: str, limit: int) -> dict[str, Any]:
    response = requests.get(
        f"{NOTION_API_URL}/blocks/{page_id}/children",
        headers=_headers(),
        params={"page_size": limit},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    lines = [text for block in data.get("results", []) if (text := _block_text(block))]
    summary = "\n".join(lines)[:4000]
    return {
        "tool": "notion",
        "mode": "page",
        "page_id": page_id,
        "items": [{
            "title": f"Notion page {page_id}",
            "id": page_id,
            "url": f"https://www.notion.so/{page_id.replace('-', '')}",
            "source": "notion",
            "summary": summary,
        }],
        "block_count": len(data.get("results", [])),
        "has_more": data.get("has_more", False),
    }


def notion(query: str = "", mode: str = "search", page_id: str = "", limit: int = 5) -> dict[str, Any]:
    try:
        mode = (mode or "search").strip().lower()
        limit = max(1, min(int(limit or 5), 20))
        if mode == "page":
            if not page_id:
                raise ValueError("page_id is required when mode='page'")
            return _read_page(page_id=page_id, limit=limit)
        if not query:
            raise ValueError("query is required when mode='search'")
        return _search_notion(query=query, limit=limit)
    except Exception as exc:
        return err("notion", exc)
