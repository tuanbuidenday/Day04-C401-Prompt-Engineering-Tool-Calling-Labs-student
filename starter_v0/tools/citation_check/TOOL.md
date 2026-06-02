---
name: citation_check
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [items]
outputs: [passed, issues, item_count]
side_effect: false
---
# citation_check

Checks whether research items include citation basics such as title, URL or
source, and summary. Use before formatting or publishing a digest.
