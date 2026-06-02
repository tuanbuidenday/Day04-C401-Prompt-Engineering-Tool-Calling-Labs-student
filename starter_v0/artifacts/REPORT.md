# Day 04 Lab v2 Report — Research Agent

## Team

- Team: [Tên Nhóm của bạn]
- Members: [Tên thành viên 1], [Tên thành viên 2], [Tên thành viên 3]
- Provider/model: openrouter/openai/gpt-4o-mini

## Final Metrics

- Final version: v3
- Final artifact_version: v3+pb847723bab22+t6cdb53d5d7b8
- Best base run file: runs/v3_B_base_openrouter_20260602T153144748278.json
- Base case accuracy: 100% (20/20)
- Base tool routing accuracy: 100% (20/20)
- Base argument accuracy: 100% (20/20)
- Group eval run file: runs/[Group Run File Path] (được điền bởi Người 3)
- Group eval accuracy: [Nhóm tự chạy và điền] (được điền bởi Người 3)
- Chat transcript file: transcripts/v3_openrouter_20260602T144702226831.transcript.json

## Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Initial default prompt baseline | 0.00 | 0.70 | runs/v0_B_base_openrouter_20260602T143011294601.json |
| v1 | starter_v0/artifacts/system_prompt.md | Add routing rules, handle mappings, safety boundaries for telegram sending, and out-of-scope refuse behaviors | 0.70 | 0.95 | runs/v1_B_base_openrouter_20260602T143823820867.json |
| v2 | starter_v0/artifacts/system_prompt.md | Mandate explicit `response_type` in clarify tool calls to resolve omitted default argument error in R11 | 0.95 | 1.00 | runs/v2_B_base_openrouter_20260602T144037743463.json |
| v3 | starter_v0/artifacts/system_prompt.md | Integrate expert feedback (handle discovery, multilingual consistency) and fix parallel routing regression (E06) | 1.00 | 1.00 | runs/v3_B_base_openrouter_20260602T153144748278.json |



## Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `[{"name": "send", "args": {...}}]` | Model attempted to solve calculus equation using `send` tool instead of refusing. | Refuse out-of-scope requests directly in system prompt without calling any tools. |
| R10_missing_handle | missing_info | `[{"name": "timeline", "args": {"screenname": "sama"}}]` | Model guessed Sam Altman (`sama`) screenname when no account was mentioned. | Instruct model to call `clarify` with `response_type: "text"` if handle is missing. |
| R11_missing_url | missing_info | `[{"name": "fetch", "args": {"url": "https://example.com/article"}}]` | Model guessed mock URL when summarizing a vague article reference. | Instruct model to call `clarify` with `response_type: "text"` if URL is missing. |
| R12_confirm_before_send | wrong_boundary | `[{"name": "send", "args": {...}}]` | Model sent Telegram text directly without prior user confirmation. | Call `clarify` with `response_type: "yes_no"` to confirm before calling `send`. |
| R13_parallel_web_and_tweets | wrong_tool | `[{"name": "lookup", "args": {"query": "AI news"}}]` | Model appended "news" keyword to lookup query instead of setting `topic` to `"news"`. | Instruct model to extract core query only and map news intents to `topic: "news"`. |

## Team Eval Cases

List at least 5 cases added to `data/eval_group.json`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| [Case 1 ID] | [Điền bởi Người 3] | [Điền bởi Người 3] | [Điền bởi Người 3] |
| [Case 2 ID] | [Điền bởi Người 3] | [Điền bởi Người 3] | [Điền bởi Người 3] |
| [Case 3 ID] | [Điền bởi Người 3] | [Điền bởi Người 3] | [Điền bởi Người 3] |
| [Case 4 ID] | [Điền bởi Người 3] | [Điền bởi Người 3] | [Điền bởi Người 3] |
| [Case 5 ID] | [Điền bởi Người 3] | [Điền bởi Người 3] | [Điền bởi Người 3] |

## Live Chat Evidence

Use `transcripts/v3_openrouter_20260602T144702226831.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| Lượt 1 | "Viết giúp mình một hàm Python tính Fibonacci bằng recursion" | None | v3 | Agent correctly refused out-of-scope coding request directly. |
| Lượt 2 | "tin tức AI hôm nay có gì nổi bật" | `lookup(query="AI", topic="news", timeframe="day")` | v3 | Agent fetched AI news and formatted the digest beautifully. |
| Lượt 3-4 | "Tóm tắt giúp mình 5 tweet mới nhất" -> "elon musk" | `clarify` then `timeline(screenname="elonmusk", limit=5)` | v3 | Agent clarified the missing username handle and then fetched Elon Musk's tweets. |
| Lượt 5 | "Đăng bản tin này lên Telegram giúp mình" | `clarify(question="...", response_type="yes_no")` | v3 | Agent safely asked for yes/no confirmation before calling send tool. |


## Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | [Điền nếu nhóm làm] | [Điền nếu nhóm làm] | [Điền nếu nhóm làm] |
| arXiv/company policy | runs/v3_B_extension_openrouter_20260602T153245035985.json | arXiv search (`papers`), pdf extraction (`paper_text`), and company policy search (`policy`) worked perfectly at 100% (10/10) accuracy. | Incorrect `policy_area` extraction or missing parallel calls. Mitigated by explicit topic-to-enum mapping and parallel tool rules in prompt. |
| UI | [Điền nếu nhóm làm] | [Điền nếu nhóm làm] | [Điền nếu nhóm làm] |

## Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

