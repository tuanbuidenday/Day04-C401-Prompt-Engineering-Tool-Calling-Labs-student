---
name: notion
track: bonus
kind: live_api
provider: Notion API
requires_env: [NOTION_API_KEY]
inputs: [query, mode, page_id, limit]
outputs: [items]
side_effect: false
---
# notion

Searches a connected Notion workspace or reads text blocks from a specific Notion page.

Use `mode="search"` with `query` to find pages/databases. Use `mode="page"` with
`page_id` to read page content. The Notion integration must be invited to the pages
or databases it should access.
