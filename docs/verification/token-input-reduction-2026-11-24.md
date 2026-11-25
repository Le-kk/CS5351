# Token input reduction — implementation and verification

Date: 24 November 2026 (Asia/Hong_Kong). Baseline source: `a62b801`.

## Result

The three online optimized NVDA runs used 99,532, 103,120 and 110,725 total tokens. Their mean is 104,459.0: 24.79% below the original report's mean of 138,896.5 (139,011 and 138,782). Every optimized run is below both original rows. The same-day legacy-mode control used 160,826; the optimized mean is 35.05% lower. All three online runs returned real price rows and a matching verified snapshot on 2026-01-09. This meets the token target for this measured case; it is not a claim of general model-quality acceptance.

The separately labelled cached-price experiment used a frozen, real Yahoo price cache, not synthetic prices: its legacy control used 151,796 and the optimized runs used 91,213, 91,118 and 88,369. It is kept separate from the online comparison.

## Changes and rationale

- Intermediate analysts receive an advisory evidence-first target of about 450 words; research/risk debaters about 220. Dates, fiscal periods, units, source references, conflicting evidence, uncertainty and data gaps take priority over brevity. There is no hard truncation of generated reports or raw tool payloads.
- An opponent argument already present verbatim in debate history is referenced rather than copied twice. The history itself stays intact. When the original assembled debate prompt would need context compaction, the explicit recent-argument copy is restored so references cannot point to a trimmed passage.
- The four analyst roles, original tool interfaces, model, debate rounds, context caps, portfolio constraints, structured outputs and final manager formats remain. No new model call or summary-model stage was introduced.
- `concise_intermediate_reports` is recorded in graph settings and shared API evidence. The environment override is `TRADINGAGENTS_CONCISE_INTERMEDIATE_REPORTS`.

## Reproduce and disable

From the repository root, run `python tests/member_d_verification/token_input_benchmark.py --repo . --output .local-review/token-online --live --runs 3`. The configured `.env` must select the same school model. `--live` explicitly enables billable calls. Run a separate, sequential control with `--legacy` and a different output directory. Do not run both profiles concurrently: a concurrent attempt received school-gateway HTTP 429 and is recorded as INCOMPLETE, not averaged.

`--cached-prices` is a distinct diagnostic profile using the existing NVDA Yahoo cache, clipped to the analysis date. It must never be described as a direct live-vendor reproduction of the historical baseline. Full sanitized state/tool payloads are retained locally under `.local-review/token-input-reduction-2026-11-24/`; the compact shareable record is `tests/member_d_verification/evidence/token-input-reduction-2026-11-24.json`.

To disable the feature, set `TRADINGAGENTS_CONCISE_INTERMEDIATE_REPORTS=false` before starting a new process, or pass `concise_intermediate_reports=False` in a programmatic config. This restores legacy verbosity and duplicate-argument behavior. To undo the source changes, revert this isolated branch's optimization changes; do not reset unrelated work. No GitHub workflow or protection rule was changed.

## Data recovery and verification

Yahoo query1 initially returned 429; query2 with a normal browser request header returned HTTP 200. The project's own unmodified tools then returned five daily price rows for 5–9 January and a verified snapshot with RSI, MACD, moving averages and ATR. Yahoo's unadjusted close of 184.86 differs from the project's adjusted close of 184.428; the project price tool and snapshot agree on the adjusted basis. No TLS verification was disabled and no Yahoo network fix was added to application code.

Full offline regression: 1,797 passed, 2 skipped, 1 deselected, 100 subtests passed. The skips are the opt-in live semantic replay and unavailable optional Bedrock SDK. Repository Ruff passed. Added tests cover preserved tool payloads/call IDs, source message immutability, opening arguments, safe history references, disabled mode and recorded configuration. These checks do not certify that every model-generated numeric or semantic claim is correct.

News/social/macro availability limitations and rating variability remain and must be disclosed. The original baseline is historical; source availability and provider-wrapper labels differ. The same-day control is therefore the stronger controlled comparison. The initial 121,207/82,971 missing-price measurements and the 8,299-token rate-limited attempt are excluded from success evidence.
