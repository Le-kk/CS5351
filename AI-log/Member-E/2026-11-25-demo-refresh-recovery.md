# Demo refresh and active-run recovery — 2026-11-25

## Selected original-language user request

> 请检查后端，我因为没完成一次run中断后刷新就不能run了

## Diagnosis and changes

Recovered the local backend while preserving prior reports and records. The unfinished registry record is shown as INTERRUPTED with NOT_RUN and partial usage, not a success. The single-active-run guard prevents a second concurrent start. Added an optional validated llm_request_timeout in tradingagents/llm_clients/factory.py; the demo freezes 120 seconds and exposes it in the confirmation snapshot. This is a model request timeout, not a total-run deadline, and refresh is not cancellation. Interface implementation details are outside this delivered backend record. The selected original user question remains above.

## Verification

Backend recovery and timeout negative tests: 17 passed. An initial restart test failed because its synthetic RUNNING job omitted the monotonic start time; corrected the fixture and retained the failure log locally. Existing run records remain available; backend reports no active run after recovery. Full regression results recorded after the final run below. No extra paid analysis was started as a browser test. Screenshot: demo-refresh-recovered.jpg (local temporary artifact). No GitHub commit or push made.

Final full regression: 2022 passed, 2 skipped, 1 deselected, 24 warnings, 100 subtests passed in 25.87s
Ruff passed. Actual HTTP prepare after recovery succeeded with a 120-second model request timeout; no additional model analysis started.
