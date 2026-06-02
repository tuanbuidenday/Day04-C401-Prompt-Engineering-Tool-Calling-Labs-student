---
name: date_normalize
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [text, reference_date]
outputs: [timeframe, start_date, end_date]
side_effect: false
---
# date_normalize

Normalizes common time phrases into the timeframe values used by research tools:
`day`, `week`, `month`, or `year`.
