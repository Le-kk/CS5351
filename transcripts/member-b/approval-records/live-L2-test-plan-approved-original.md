# Live-found fundamentals period contradiction: bounded repair/test plan L2

Status: awaiting Brian's approval before implementation. Additional to approved R1–R5/L1; no canonical requirements adoption or new runtime checker.

## Actual finding

The first fresh deepseek-profile C1 report (`20261121T095453Z-2a60842e`, as of 2026-01-09) opens its Fundamentals section by saying the company “just printed a record fiscal Q1 (December 2025 quarter)”, but later in that same section explicitly says “no December-2025 (FQ1 FY2026) income statement is present” and warns not to assume that print exists. Downstream managers largely recognize the missing print. Retaining the contradictory analyst summary weakens source/date traceability even when the deterministic Q1–Q4 checker is PASSED.

Bounded repair: strengthen `fundamentals_analyst.py`'s source/period instructions. Use explicit calendar period ends, fiscal labels and filing dates from tools; do not derive a calendar year by copying a fiscal-year label. Keep the opening summary, tables and caveats consistent about which periods are actually available. Do not claim a missing/unfiled quarter has reported, and do not invent an earnings-release date from prior knowledge. This is a prompt mitigation with live regression evidence, not a universal fact verifier or new rating/checker.

## Test/fit criteria

| ID | Input / path | Expected |
|---|---|---|
| L2-01 | Capture actual Fundamentals Analyst prompt using analysis date 2026-01-09 | It carries explicit tool-source/calendar-period/filing-cutoff/summary-consistency instructions; preserves tools, instrument/date context and delegation to decision agents. No hardcoded Apple figures/year-specific patch. |
| L2-02 | Three uniquely tagged real-school-model generations through the actual analyst prompt; synthetic facts include FY2025 Q1 ending 2024-12-31, latest income quarter 2025-06-28, balance sheet 2025-09-27, no income statement ending 2025-12-31 | All three summaries distinguish the old December-2024 report from unavailable December-2025 data. No claim that the missing quarter just reported. Cite the correct period or state unknown. Retain all attempts. |
| L2-03 | Missing-period / post-cutoff filing fixtures (filing dated 2026-01-29 versus analysis 2026-01-09), including real-model missing-data case | No manufactured latest-quarter figures, no use of the future filing as already available and no guessed earnings-release date. Clearly mark missing/stale/unavailable facts. Captured-path/offline checks preserve the supplied dates; contextual live inspection decides compliance. |
| L2-04 | Existing analyst/agent tests and fixed-case live replay after final prompt change | Tools, output/report structure, portfolio behavior, ratings/actions and Q1–Q4 unchanged. Capture current source/prompt hashes and two attempts per fixed case; all earlier attempts retained. No Member C approval or historical F8 recovery is claimed. |

Files: `tradingagents/agents/analysts/fundamentals_analyst.py`, narrowly scoped new tests under `tests/member_b_remediation/`, report/evidence notes. Implementation through OpenCode; no new dependencies, deterministic classifier, provider policy, credential edits, commits/pushes, governance or canonical requirement edits.

Sequence: approval → captured-path regressions → bounded prompt correction → immediate real-model fixture checks → final frozen ten-case replay plus appropriate offline/static checks → report update. If the targeted contradiction persists, retain it and ask about a wider data-validation design rather than claiming prompt instructions guarantee factual accuracy.

Approval before implementation is requested under the course requirement sheet page-10 test-approval gate. This analyst change was outside the previously approved Trader-only numerical repair.
