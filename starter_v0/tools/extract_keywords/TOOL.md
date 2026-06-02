---
name: extract_keywords
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [text, max_keywords]
outputs: [keywords, count]
side_effect: false
---
# extract_keywords

Extracts search keywords from a user query or short text. Use it when a request
needs a compact topic string before search or when the user explicitly asks for
keywords.
