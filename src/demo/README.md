# Real-model research presentation console

Canonical frontend: `src/frontend`; backend: `src/demo`. From the repository root, build with `cd src/frontend && npm ci --ignore-scripts && npm run build`, then run `python -m demo.console --compact-evidence-handoff --open`. Default URL: http://127.0.0.1:8766. Keys stay in existing private backend configuration. The build is generated locally/CI and is not a second source of truth.

Select ticker/date, analysts, rounds, configured models and optional request-count cap. Portfolio modes distinguish unknown holdings, known empty input and supplied JSON. Validate, inspect the frozen snapshot/fingerprint, confirm and start. Actual reports, discussions, provider usage and files appear as stages finish. A request cap is not a token ceiling. A passed output check is not financial or semantic acceptance.

Refresh retains only the run ID in sessionStorage, never the supplied portfolio. It does not cancel backend work. One run is active at a time; a banner links back to it. Model requests use a 120-second timeout, not a total-run deadline. Backend restart labels unfinished history INTERRUPTED and preserves partial records. Revalidate after restart.

Full generated reports remain; compact_evidence_handoff is opt-in and reversible. General application default remains False. The browser launcher enables it explicitly. The November 25 NVDA case measured control 130,787 and candidates 96,160/95,023 total tokens, a 26.91% mean reduction. This is not a universal saving, semantic acceptance or TOKEN_BUDGET implementation. See [evidence](../../docs/verification/compact-evidence-handoff-2026-11-25.md).

For isolated paid comparison: `python -m demo.measure_handoff --live --runs 2 --output .local-review/new-comparison`. Prior scripted presenter assets remain supported for offline developer tests/legacy demonstrations, but are not the default real-model console and must not be presented as real execution. Their old instructions are under [history](../../history/demo-prototype/README.md).
