---
name: source_rank
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [items, max_items]
outputs: [items, item_count]
side_effect: false
---
# source_rank

Ranks already-collected research items by simple citation quality signals. It
does not fetch new data.
