# Live-found Trader arithmetic: bounded repair/test plan L1

Status: awaiting Brian's approval before implementation. This is additional to the approved R1–R5 plan, not an amendment adopted on Member A's behalf.

## Actual finding and scope

On 2026-11-21, the C3 diagnostic (`20261121T093733Z-8c832879`) returned COMPLETED/PASSED but its delivered Trader section described a stop at 255.33 as about 1.5×ATR (6.6 points) below a close of 258.47, with ATR 4.39. The actual difference is 3.14, or approximately 0.715×ATR. PM corrected the arithmetic later, but the erroneous Trader section remained in the delivered report. This is a fresh arithmetic-quality issue, distinct from the repaired holdings-context issue. The original synthetic input was 40 AAPL units at average 190, cash omitted.

Proposed bounded repair: strengthen the Trader's numerical-grounding instruction so that stated distances/multiples are recomputed from explicit source values, contradictory upstream arithmetic is corrected rather than repeated, and unsupported ratios are omitted or marked unknown. Preserve absolute-price fields, user-supplied ownership/cash semantics, free-text fallback, ratings/actions and Q1–Q4. Do not introduce a new runtime checker, claim universal mathematical verification, silently rewrite earlier reports, or adopt new account-execution features. A deterministic financial-math validator would need a separate design/approval.

## Concrete acceptance cases

| ID | Input / path | Expected |
|---|---|---|
| L1-01 | Capture the actual Trader prompt with close 258.47, stop 255.33, ATR 4.39, a contradictory upstream 1.5× claim, and supplied 40-unit/unknown-cash context | Numeric grounding and correction instructions reach the model alongside all source values and portfolio facts, on structured and fallback paths. No invented account facts or forced action. |
| L1-02 | Three fresh real-school-model Trader runs with the above reproducible fixture | Each uses the 3.14 difference / approximately 0.715×ATR if it makes that claim, or omits the multiple; none asserts 6.6 is the difference or that 255.33 is 1.5×ATR below 258.47. Record every attempt and exact citations; no retries to hide failures. |
| L1-03 | Live free-text fallback forced through a non-supporting structured-binding adapter using the same real model | The same numerical instruction applies, output remains usable and no false arithmetic claim recurs. Record fallback explicitly. |
| L1-04 | Missing or nonpositive ATR / missing necessary price input, captured prompt plus live missing-ATR fixture | Do not fabricate an ATR multiple or divide by zero; omit unsupported distance/multiple or state it cannot be calculated. Preserve legitimate absolute prices present in evidence. |
| L1-05 | Existing explicit-empty/no-portfolio and supplied-holding regressions | Optional portfolios, unknown cash, five ratings and three Trader actions remain valid. Q1–Q4 has unchanged meaning and is not presented as an arithmetic certificate. |
| L1-06 | Current-version five fixed GOV004 cases, two predeclared attempts each, after the prompt change | Retain all starts, reports/manifests, actual profile and source/prompt hashes. Inspect ownership, cash, rating/action separation and challenge resistance in context. New evidence does not recover historical F8 or impersonate Member C's independent scoring. |

Implementation files: `tradingagents/agents/trader/trader.py`, narrowly necessary related prompt/schema descriptions only if needed and explained, new regressions under `tests/member_b_remediation/`, and report/evidence notes. Application implementation must be through OpenCode. No commits/pushes, credential edits, new provider policy or changes to canonical requirements/governance.

Sequence: approval → captured-path negative/positive regressions → bounded prompt correction → immediate live Trader checks → full fixed live replay and appropriate offline suite/lint/dependency checks → contextual report update. If arithmetic still fails, retain the failure and ask about a separate deterministic-validator design; do not call it fixed.

Approval is requested because the course requirement sheet page 10 says: “no code change merges unless the tests for the change were approved before implementation began.” This new finding was not covered by the original five-repair test plan.
