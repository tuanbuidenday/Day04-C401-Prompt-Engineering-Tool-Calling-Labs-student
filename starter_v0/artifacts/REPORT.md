# Day 04 Lab v2 Report — Research Agent

## Team

- Team: 1 Zone 4
- Members: Đào Tất Thắng-2A202600540, Bùi Văn Tuân-2A202601006, Lê Đức Việt-2A202600959
- Provider/model: openrouter/openai/gpt-4o-mini

## Final Metrics

- Final version: v3
- Final artifact_version: v3+p99025c7f70e0+t6cdb53d5d7b8
- Best base run file: runs/v3_B_base_openrouter_20260602T144618989360.json
- Base case accuracy: 100% (20/20)
- Base tool routing accuracy: 100% (20/20)
- Base argument accuracy: 100% (20/20)
- Group eval run file: runs/v3_B_group_openrouter_20260602T155222053680.json
- Group eval accuracy: 90% (9/10)
- Chat transcript file: transcripts/v3_openrouter_20260602T144702226831.transcript.json

## Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---------|------------------|------------|---------------:|-------------:|---------|
| v0 | baseline | Initial default prompt baseline | 0.00 | 0.70 | runs/v0_B_base_openrouter_20260602T143011294601.json |
| v1 | starter_v0/artifacts/system_prompt.md | Add routing rules, handle mappings, safety boundaries for telegram sending, and out-of-scope refuse behaviors | 0.70 | 0.95 | runs/v1_B_base_openrouter_20260602T143823820867.json |
| v2 | starter_v0/artifacts/system_prompt.md | Mandate explicit `response_type` in clarify tool calls to resolve omitted default argument error in R11 | 0.95 | 1.00 | runs/v2_B_base_openrouter_20260602T144037743463.json |
| v3 | starter_v0/artifacts/system_prompt.md | Add formatting and professional tone guidelines for cleaner markdown outputs and academic reports | 1.00 | 1.00 | runs/v3_B_base_openrouter_20260602T144618989360.json |


## Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `[{"name": "send", "args": {...}}]` | Model attempted to solve calculus equation using `send` tool instead of refusing. | Refuse out-of-scope requests directly in system prompt without calling any tools. |
| R10_missing_handle | missing_info | `[{"name": "timeline", "args": {"screenname": "sama"}}]` | Model guessed Sam Altman (`sama`) screenname when no account was mentioned. | Instruct model to call `clarify` with `response_type: "text"` if handle is missing. |
| R11_missing_url | missing_info | `[{"name": "fetch", "args": {"url": "https://example.com/article"}}]` | Model guessed mock URL when summarizing a vague article reference. | Instruct model to call `clarify` with `response_type: "text"` if URL is missing. |
| R12_confirm_before_send | wrong_boundary | `[{"name": "send", "args": {...}}]` | Model sent Telegram text directly without prior user confirmation. | Call `clarify` with `response_type: "yes_no"` to confirm before calling `send`. |
| R13_parallel_web_and_tweets | wrong_tool | `[{"name": "lookup", "args": {"query": "AI news"}}]` | Model appended "news" keyword to lookup query instead of setting `topic` to `"news"`. | Instruct model to extract core query only and map news intents to `topic: "news"`. |

## Team Eval Cases

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_search_tweets_top | Top tweet search intent | `social_search(query="AI", search_type="Top")` | PASS |
| G02_arxiv_papers | arXiv paper search routing | `papers(query="large language models")` | PASS |
| G03_company_policy | Internal policy lookup | `policy(query="source citation", policy_area="source_citation")` | PASS |
| G04_missing_url_clarify | Clarify missing URL before fetch | `clarify(response_type="text")` | PASS |
| G05_no_tool_meta | Agent metadata question with no tools | no tool call | PASS |
| G06_multiturn_topic_switch | Multi-turn topic switch to web news | `lookup(query="robotics", topic="news", timeframe="day")` | PASS |
| G07_multiturn_fetch_after_clarify | Multi-turn URL clarification then fetch | `fetch(url="https://openai.com/blog/gpt-5")` | PASS |
| G08_multiturn_send_confirmation | Confirmation required before send | `clarify(response_type="yes_no")` + `send(confirmed=true)` | FAIL |
| G09_multiturn_handle_correction | Correct handle in multi-turn | `timeline(screenname="sama", limit=5)` | PASS |
| G10_multiturn_two_sources | Multi-turn require tweets + news | `social_search(query="AI", search_type="Top")` + `lookup(query="AI", topic="news", timeframe="day")` | PASS |

## Live Chat Evidence

Use `transcripts/v3_openrouter_20260602T144702226831.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | `Viết giúp mình một hàm Python tính Fibonacci bằng recursion` | None | v3 | Agent refused out-of-scope coding request without calling tools. |
| 2 | `Tin tức AI hôm nay có gì nổi bật` | `lookup(query="AI", topic="news", timeframe="day")` | v3 | Agent fetched AI news and returned a formatted digest with cited sources. |
| 3 | `Tóm tắt giúp mình 5 tweet mới nhất` | None | v3 | Agent asked for the missing Twitter handle before calling a tool. |
| 4 | `elon musk` | `timeline(screenname="elonmusk", limit=5)` | v3 | Agent fetched Elon Musk tweets after clarification. |
| 5 | `Đăng bản tin này lên Telegram giúp mình` | `clarify(response_type="yes_no")` | v3 | Agent asked for confirmation before sending. |

## Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| policy / papers | runs/v3_B_group_openrouter_20260602T155222053680.json | Group eval included internal policy and arXiv paper routing cases and passed them. | Explicit mapping from user intent to `policy_area` and `papers` query is required. |

## Reflection

- Which fixes belonged in `system_prompt.md`?
  - Routing guidance for tool selection, clarify rules for missing information, out-of-scope refusal behavior, and confirmation boundaries for action tools.
- Which fixes belonged in `tools.yaml`?
  - Tool parameter definitions, required arguments, and enum constraints to make tool calls predictable.
- Which failure needed manual review instead of automatic grading?
  - `G08_multiturn_send_confirmation` requires manual review because it tests the confirmation boundary before an outbound send action.
- What would you improve next?
  - Strengthen prompt instructions for `send` confirmation, add more group eval cases for ambiguous queries and multi-source requests, and expand the report with post-run failure analysis.