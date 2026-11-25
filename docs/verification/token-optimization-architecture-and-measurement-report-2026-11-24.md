# Token Optimization: Architecture Differences and Measurement Report

> Delivery note (2026-11-25, main 761918e): this is a historical measurement report. The implementation was later integrated (commit aa3b02d); the original local-status and measurement statements below describe their original snapshot. No new model run, quality acceptance or token ceiling is claimed. The same-day control is the stronger controlled comparison; the earliest-baseline comparison is descriptive. Primary compact evidence: [measurement JSON](../../tests/member_d_verification/evidence/token-input-reduction-2026-11-24.json).

**Date:** 24 November 2026, Asia/Hong_Kong
**Repository:** `kelepawuqiusi/CS5351`
**Base revision:** `a62b801`
**Local branch:** `perf/token-input-reduction-20261124`
**Status:** Locally implemented and tested; not committed, pushed or merged at the time of this report.

## 1. Result and scope

The optimization changes how intermediate analysis is written and how repeated debate context is passed between agents. It is a limited change to context handling, not a redesign of the multi-agent graph.

Three completed online runs used **99,532, 103,120 and 110,725 total tokens**, averaging **104,459**. This is **24.79% below the earliest reported baseline mean of 138,896.5**, and **35.05% below the same-day legacy-mode control of 160,826**. Each optimized run was below both earliest baseline runs. Real price data and a matching verification snapshot were present in all three optimized runs.

The target was met for the measured NVDA case. This does not establish the same reduction for other instruments, dates, portfolio modes or models, or certify semantic quality.

## 2. Architecture before and after

### Before: verbose intermediate reports propagated downstream

The four analysts produce market, news, sentiment and fundamentals reports. The research and risk agents receive upstream reports and debate history; later decisions build on those outputs. Long intermediate reports therefore cost tokens when generated and again each time a downstream agent reads them.

Debate prompts also included both the full debate history and a separate copy of an opponent's latest argument. When that argument was already in the history, the same evidence was sent twice. The existing context guard bounded very large prompts, but did not systematically prevent this repetition below its compaction threshold.

### After: concise evidence reports and conditional references

1. **Analyst output guidance:** The shared analyst-turn layer adds an evidence-first target of about 450 words. It is advisory: source references, dates, fiscal periods, units, contradictions, uncertainty and missing-data disclosures take priority. Tool results and generated reports are not forcibly truncated.
2. **Research/risk output guidance:** Bull/Bear researchers and the three risk debaters receive an advisory target of about 220 words, focusing on their distinct argument and specific rebuttals rather than retelling all upstream reports. These shorter outputs also reduce later input.
3. **Repeated-argument handling:** When the exact latest opponent argument is already present in debate history, the separate copy becomes a reference. The original argument remains in history. If the original assembled prompt would need context compaction, the explicit copy is restored before the existing guard runs, avoiding a reference to history that might be trimmed.
4. **Configuration and provenance:** `concise_intermediate_reports` controls the behavior and is recorded in graph run settings and shared API configuration evidence. The environment setting is `TRADINGAGENTS_CONCISE_INTERMEDIATE_REPORTS`.

The same analyst roles, research manager, trader, risk trio and portfolio manager remain connected in the same graph. Model selection, tool interfaces, debate rounds, context caps, structured-output schemas and final-manager output formats were retained. No new summarizer agent, summary-model call, tool-output limiter or hard output-token cap was introduced.

### Implementation boundaries

- `tradingagents/agents/context.py`: common brevity guidance, exact-argument references and the compaction safeguard.
- `tradingagents/agents/analysts/turn.py`: applies analyst guidance while preserving tool-call structure and source messages.
- `tradingagents/agents/researchers/` and `tradingagents/agents/risk_mgmt/`: apply debate guidance and safe references.
- `tradingagents/default_config.py`: default and environment switch.
- `tradingagents/graph/trading_graph.py` and `tradingagents/runapi/execution.py`: record the effective mode.

## 3. Measurement method

The case was NVDA, analysis date **2026-01-09**, English output, all four analysts, one research-debate round and one risk-debate round. Both model tiers used **CS5351/DeepSeek-V4-Flash** through the configured school `openai_compatible` gateway. Checkpoints were disabled and the control and optimized profiles used isolated empty memory. Existing context settings remained 24,000 estimated tokens maximum and 19,200 estimated tokens for compaction. The measurement guard used a 60-second model timeout and one SDK retry in both profiles.

Token totals came from provider-reported usage collected by `StatsCallbackHandler` after completion, not the CLI live panel. Online legacy mode was selected with `--legacy`; optimized mode used the default enabled switch. Final comparison runs were performed sequentially to avoid simultaneous benchmark workloads triggering the school gateway's rate limit. The production price tool was not replaced in the online comparison; ordinary vendor caching remained available.

The original report labelled its provider `deepseek`; current local credentials use the school `openai_compatible` wrapper. The model name is the same, but wrapper differences and historical data availability mean the earliest baseline is a historical comparison, not a perfectly matched experiment. The same-day legacy-mode control provides a closer comparison, although it contains only one sample.

## 4. Results

### Earliest baseline, recorded on 13 November

- B1: input **114,911**; output **24,100**; total **139,011**; 16 model calls; 117.6 seconds.
- B2: input **116,314**; output **22,468**; total **138,782**; 17 model calls; 110.6 seconds.
- Mean total: **138,896.5 tokens**.

### Same-day online legacy-mode control

- Input **135,790**; output **25,036**; total **160,826**.
- 19 model calls; 132.71 seconds; rating `Hold`.

### Online optimized runs

- O1: input **86,331**; output **13,201**; total **99,532**; 18 calls; 69.51 seconds; `Hold`.
- O2: input **89,062**; output **14,058**; total **103,120**; 19 calls; 69.84 seconds; `Overweight`.
- O3: input **96,963**; output **13,762**; total **110,725**; 18 calls; 68.45 seconds; `Hold`.
- Means: input **90,785.3**; output **13,673.7**; total **104,459**; 18.33 calls; 69.27 seconds.

The mean saves **34,437.5 tokens per run** relative to the historical baseline and **56,367** relative to the same-day control. Input and output both decreased; the model-call count remained similar. This supports shorter intermediate context, rather than removing workflow stages, as the main explanation. No ablation experiment separately measures the contribution of brevity versus duplicate references. Timing differences are observations, not a guaranteed speedup: network conditions, caches and sampling can affect them.

### Separate diagnostic and excluded attempts

A separate real historical-price-cache profile produced a legacy control of **151,796** and optimized totals of **91,213, 91,118 and 88,369**. These are not mixed into the online averages.

The earlier **121,207 / 82,971** comparison was excluded because core price data was unavailable. A later concurrent attempt stopped with school-model HTTP 429 after **8,299 partial tokens**; it is `INCOMPLETE` and excluded. Neither is treated as evidence of successful reduction.

## 5. Data and regression verification

Yahoo access recovered during the retry: a direct query2 request returned HTTP 200, and the project's own price and verification tools returned data. In the three optimized online runs, the price tool returned 196, 154 and 256 rows respectively, reflecting model-selected lookback windows; every set ended on 2026-01-09 with no later dates. Each latest close matched the verified snapshot at **184.428 on an adjusted-price basis**. The Yahoo webpage's **184.86** is the unadjusted close; these values must not be mixed.

Full offline regression: **1,797 passed, 2 skipped, 1 deselected, and 100 subtests passed**. Repository Ruff passed. Added coverage checks tool payload and call-ID preservation, message immutability, debate openings, safe references under compaction, legacy-mode behavior and recorded configuration. The skipped live semantic suite and optional Bedrock dependency are not counted as passing checks.

News, social feeds, macro data and historical valuation still have availability limitations. Ratings varied across optimized runs. There is no independent semantic approval or proof that all generated arithmetic and financial conclusions are correct. Broader quality acceptance remains separate from the token target.

## 6. Reproduction, rollback and evidence

Run from the repository root with the configured school-model credentials:

```bash
python tests/member_d_verification/token_input_benchmark.py \
  --repo . --output .local-review/token-control --live --legacy --runs 1

python tests/member_d_verification/token_input_benchmark.py \
  --repo . --output .local-review/token-optimized --live --runs 3
```

Run these sequentially, using fresh output directories. `--live` explicitly enables billable model calls. The optional `--cached-prices` profile is a distinct diagnostic and must be labelled accordingly.

Set `TRADINGAGENTS_CONCISE_INTERMEDIATE_REPORTS=false` before starting a new process, or supply `concise_intermediate_reports=False` programmatically, to restore legacy verbosity and repeated-argument behavior. The changes are isolated on the local optimization branch; no GitHub workflow or branch-protection rule was changed.

Evidence in the repository:

- `tests/member_d_verification/evidence/token-input-reduction-2026-11-24.json`: measured totals, controls, exclusions and price audits.
- `tests/member_d_verification/token_input_benchmark.py`: opt-in live measurement tool.
- `tests/member_d_verification/test_token_input_reduction.py`: regression coverage.
- `AI-log/Member-E/2026-11-24_token-input-reduction.md`: AI-use record.

Sanitized full state and tool payloads are retained locally under `.local-review/token-input-reduction-2026-11-24/`; they are not automatically included in a GitHub submission.
