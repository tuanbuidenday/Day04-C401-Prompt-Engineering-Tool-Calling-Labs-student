# Day 04 Lab v2 Report — Research Agent

## Team

- Team: C401 Research Agent
- Members: Tuan, Dao Tat Thang, Nhan DH
- Provider/model: OpenRouter / default model from provider config

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent hỗ trợ tìm tin web, tìm bài đăng mạng xã hội, đọc URL, tìm paper arXiv, tra cứu policy nội bộ, kiểm tra/chấm nguồn và tổng hợp kết quả thành digest. Agent có guardrail: hỏi lại khi thiếu thông tin và yêu cầu xác nhận trước khi gửi/publish.

**Link dùng thử (deploy):**

- Public URL: https://frog-figured-block-etc.trycloudflare.com
- Local URL: http://localhost:8502
- Ghi chú: link `trycloudflare.com` chỉ sống khi lệnh `cloudflared tunnel` còn chạy.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
| --- | --- | --- |
| clarify | Hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận yes/no. | không |
| timeline | Lấy bài đăng gần đây của một tài khoản cụ thể theo `screenname`. | không |
| social_search | Tìm bài đăng mạng xã hội theo keyword, Latest hoặc Top. | không |
| lookup | Tìm thông tin/tin tức trên web với `topic` và `timeframe`. | không |
| fetch | Đọc nội dung từ một URL cụ thể. | không |
| format | Format các item đã có thành markdown digest. | không |
| send | Gửi text lên Telegram khi đã có xác nhận. | không |
| policy | Tìm trong tài liệu policy nội bộ. | không |
| papers | Tìm paper trên arXiv. | không |
| paper_text | Tải/trích text paper arXiv từ ID hoặc URL. | không |
| notion | Tìm page/database hoặc đọc page trong workspace Notion đã kết nối. | có |
| extract_keywords | Trích keyword chính từ query hoặc đoạn text. | có |
| date_normalize | Chuẩn hóa cụm thời gian thành day/week/month/year và khoảng ngày. | có |
| citation_check | Kiểm tra item research có đủ title, URL/source và summary. | có |
| source_rank | Xếp hạng item research theo chất lượng nguồn và độ đầy đủ citation. | có |

## A3. Câu hỏi mẫu để thử

1. Tin tức AI hôm nay có gì nổi bật?
2. Mọi người đang bàn gì về GPT-5 trên Twitter?
3. Tóm tắt bài này giúp mình: https://openai.com/research/
4. Tóm tắt 5 tweet mới nhất giúp mình.
5. Tìm paper mới về AI agent evaluation trên arXiv.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Final Metrics

- Final version: v3
- Final artifact_version: `v3+pe6b27afa6232+t47d46118524b`
- Best base run file: `runs/v3_B_base_openrouter_20260602T162856054332.json`
- Base case accuracy: 100% (20/20)
- Base tool routing accuracy: 100%
- Base argument accuracy: 100%
- Base multiturn accuracy: 100%
- Extension run file: `runs/v3_B_extension_openrouter_20260602T162945479792.json`
- Extension accuracy: 100% (10/10)
- Group eval run file: `runs/v3_B_group_openrouter_20260602T162727914615.json`
- Group accuracy: 100% (10/10)
- Group tool routing accuracy: 100%
- Group argument accuracy: 100%
- Group multiturn accuracy: 100%
- Chat transcript file: `transcripts/v3_openrouter_20260602T144702226831.transcript.json`
- UI transcript file: `transcripts/ui_v3_openrouter_20260602T152114666902.transcript.json`

## B2. Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
| --- | --- | --- | ---: | ---: | --- |
| v0 | baseline | Initial default prompt baseline | 0.00 | 0.70 | `runs/v0_B_base_openrouter_20260602T143011294601.json` |
| v1 | `artifacts/system_prompt.md` | Add routing rules, handle mappings, safety boundaries, and out-of-scope behavior. | 0.70 | 0.95 | `runs/v1_B_base_openrouter_20260602T143823820867.json` |
| v2 | `artifacts/system_prompt.md` | Require explicit `response_type` for `clarify` calls. | 0.95 | 1.00 | `runs/v2_B_base_openrouter_20260602T144037743463.json` |
| v3 | `artifacts/system_prompt.md` + `artifacts/tools.yaml` | Integrate expert feedback, multilingual consistency, parallel routing fixes, and Notion tool routing. | 1.00 | 1.00 | `runs/v3_B_base_openrouter_20260602T162856054332.json` |

## B3. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
| --- | --- | --- | --- | --- |
| R08_out_of_scope | out_of_scope | `send` | Model attempted tool use for a math/coding-style request. | Added rule to refuse out-of-scope requests without tools. |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Model guessed Sam Altman when account was missing. | Added rule to call `clarify(response_type="text")` when handle/account is missing. |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Model guessed a URL for "this article". | Added rule to call `clarify(response_type="text")` when URL is missing. |
| R12_confirm_before_send | wrong_boundary | `send` | Model tried to post before confirmation. | Added confirmation boundary: call `clarify(response_type="yes_no")` before `send`. |
| R13_parallel_web_and_tweets | wrong_tool / wrong_arg_value | `lookup(query="AI news")` | Model mixed news words into query instead of using `topic="news"`. | Added query extraction rule: core query only, map news intent to `topic="news"`. |

## B4. Team Eval Cases

Status: completed. `data/eval_group.json` contains 10 group cases with 5 single-turn and 5 multi-turn cases. The current group eval passed all cases:

```bash
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
```

Evidence:

| Requirement | Current Status |
| --- | --- |
| 10 total group cases | 10/10 |
| 5 single-turn cases | 5/5 |
| 5 multi-turn cases | 5/5 |
| `runs/v3_B_group_*.json` | `runs/v3_B_group_openrouter_20260602T162727914615.json` |
| Group case accuracy | 100% (10/10) |
| Group tool routing accuracy | 100% |
| Group argument accuracy | 100% |
| Group multiturn accuracy | 100% |

Group case coverage:

| Case ID | Type | What it tests |
| --- | --- | --- |
| G01_notion_read_page | single-turn | Read a specific Notion page by page ID. |
| G02_notion_search_database | single-turn | Search a connected Notion workspace for a database. |
| G03_keyword_extraction_vi | single-turn | Team helper `extract_keywords` with `max_keywords=4`. |
| G04_date_normalize_month | single-turn | Team helper `date_normalize` for "tháng này". |
| G05_parallel_news_policy | single-turn | Parallel `lookup` news + `policy(source_citation)`. |
| GM01_multiturn_notion_page | multi-turn | Carry Notion page ID from previous turns. |
| GM02_multiturn_send_confirmation | multi-turn | Confirm Telegram publishing with `clarify(response_type="yes_no")`. |
| GM03_multiturn_switch_to_arxiv | multi-turn | Switch from web lookup to arXiv `papers`. |
| GM04_multiturn_missing_url_then_policy | multi-turn | Carry supplied URL and call `fetch` + `policy(ai_research)`. |
| GM05_multiturn_timeframe_correction | multi-turn | Correct query and timeframe across turns. |

## B5. Live Chat Evidence

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
| --- | --- | --- | --- | --- |
| 1 | "Viết giúp mình một hàm Python tính Fibonacci bằng recursion" | none | v3 | Correctly refused out-of-scope coding request without tools. |
| 2 | "tin tức AI hôm nay có gì nổi bật" | `lookup(query="AI", topic="news", timeframe="day")` | v3 | Fetched AI news and produced a digest. |
| 3-4 | "Tóm tắt giúp mình 5 tweet mới nhất" then "elon musk" | `clarify`, then `timeline(screenname="elonmusk", limit=5)` | v3 | Asked for missing account, then used the provided account. |
| 5 | "Đăng bản tin này lên Telegram giúp mình" | `clarify(response_type="yes_no")` | v3 | Asked for confirmation before send. |

## B6. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
| --- | --- | --- | --- |
| send confirmation | `transcripts/v3_openrouter_20260602T144702226831.transcript.json` | Agent called `clarify(response_type="yes_no")` before sending; direct `send` tool live retest returned `status="sent"` after confirmed Telegram config. | Prevents unintended Telegram publishing. |
| arXiv/company policy | `runs/v3_B_extension_openrouter_20260602T162945479792.json` | `policy`, `papers`, and `paper_text` extension eval passed 10/10. | Prompt maps policy topics to correct `policy_area` and handles parallel calls. |
| Notion tool | `runs/v3_B_group_openrouter_20260602T162727914615.json` | `notion` search/page cases passed; live retest found workspace items and read page `Color`. | Requires `NOTION_API_KEY` and shared content access for the integration. |
| UI | `app.py` and Cloudflare URL above | Streamlit UI runs locally and is exposed through Cloudflare Tunnel. | Public tunnel is temporary and must stay running during demo. |
| >3 new tools | `tools/extract_keywords`, `tools/date_normalize`, `tools/citation_check`, `tools/source_rank`, `tools/notion` | Five team tools are implemented, documented, registered, and declared. | Descriptions mark helper tools as local helpers; `notion` requires explicit Notion intent and `NOTION_API_KEY`. |

## B7. Reflection

- Fixes in `system_prompt.md`: routing rules, handle mapping, missing-info clarification, send confirmation, out-of-scope refusal, multi-turn carryover/correction, expert feedback, and parallel routing.
- Fixes in `tools.yaml`: added five team tools, including the Notion workspace tool, with descriptions that keep helper tools from stealing core eval routing.
- Failure needing manual review: action/send boundary, because automatic scoring checks tool call shape but reviewers should also verify no side effect happens before confirmation.
- Next improvement: add a Notion-specific live transcript in the UI if the final demo wants to showcase workspace retrieval.
