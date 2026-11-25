# Demo refresh and active-run recovery — 2026-11-25

## Selected original-language user request

> 请检查后端，我因为没完成一次run中断后刷新就不能run了

## Diagnosis and changes

Refreshing cleared the browser's selected run while a daemon worker continued in the backend. The single-active-run guard correctly rejected a second start, but the UI made the existing run difficult to find. One run remained active for more than seven minutes. Explicitly restored the local server; the prior unfinished registry record is shown as INTERRUPTED with NOT_RUN and partial usage, not a success. Preserved all prior reports and records.

Updated external nocode frontend: keep only the opaque run ID in sessionStorage (not portfolio data); reopen the same run after refresh; show the active backend run and a View running analysis button; consume the confirmation after a successful start; refresh the CSRF token once following a rejected 403 after backend restart, without retrying network-ambiguous starts. Added an optional validated llm_request_timeout in tradingagents/llm_clients/factory.py; demo freezes 120 seconds and exposes it in the confirmation snapshot. This is a model request timeout, not a guaranteed total-run deadline, and refresh is not cancellation.

## Verification

Backend recovery and timeout negative tests: 17 passed. An initial restart test failed because its synthetic RUNNING job omitted the monotonic start time; corrected the fixture and retained the failure log locally. Browser opened the interrupted run and retained the same ID/status after actual reload. Frontend build passed. Existing run records remain available; backend reports no active run after recovery. Full regression results recorded after the final run below. No extra paid analysis was started as a browser test. Screenshot: demo-refresh-recovered.jpg (local temporary artifact). No GitHub commit or push made.

Final full regression: 2022 passed, 2 skipped, 1 deselected, 24 warnings, 100 subtests passed in 25.87s
Ruff passed. Actual HTTP prepare after recovery succeeded with a 120-second model request timeout; no additional model analysis started.
