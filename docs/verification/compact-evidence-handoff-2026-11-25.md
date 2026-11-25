# Compact intermediate evidence: implementation and live verification

Date: 2026-11-25. Base revision `6b46854`, uncommitted working tree. Scope explicitly authorized by the user, including implementation and verification across normal D/C areas. Developer tests are not independent Member C acceptance.

## Small change, existing architecture

An opt-in `compact_evidence_handoff` flag changes writing instructions inside the existing model calls. Analysts organize existing required content as verdict/confidence, evidence bullets, conflicts and data limitations. Research/risk debaters add distinct arguments instead of repeating all inputs; Research Manager and Trader receive concise intermediate-format guidance. Final Portfolio Manager instructions, graph nodes/edges, tool responses, output schemas, trusted portfolio context and publication remain unchanged. Entire generated reports remain in state and downloadable files. There is no second summary, lossy extractor, role-specific report omission or extra summarizer call.

The separate structured Sentiment Analyst path previously bypassed the existing concise instruction. The opt-in format now reaches that path as well. Sources and structured/free-text renderer are unchanged. Advisory targets: analysts 300 words, debaters 140, Research Manager 220, Trader 250. Mandatory evidence, tables, risk disclosures and schemas outrank word targets. Models can exceed them; no hard truncation is performed.

Seven tracked application files changed: context.py, sentiment_analyst.py, research_manager.py, trader.py, default_config.py, graph/trading_graph.py and runapi/execution.py. Approximately 51 added lines and one replaced line. The new flag is recorded in graph settings/API manifests. No new dependency, agent or model client.

## Fixed comparison profile

All roles, NVDA / 2026-11-24, English, research 1/risk 1, both model tiers CS5351/DeepSeek-V4-Flash through school openai_compatible. Entry point run_analysis_api with the existing console's CLI-equivalent stream runner. NO_PORTFOLIO; isolated empty per-run memory; checkpoints off; zero SDK retries; call cap 40; concise_intermediate_reports=True for both groups. Ordinary shared vendor cache; vendors were not stubbed. Runs were sequential. Only compact_evidence_handoff differs in prompt behavior. A conditional master-switch compatibility fix does not alter either measured profile; the sentiment change is inactive for control.

## Actual live results

- Current-format control: 130,787 total = 114,255 input + 16,532 output; 20 requests.
- Final candidate 1: 96,160 total = 83,732 input + 12,428 output; 18 requests.
- Final candidate 2: 95,023 total = 83,212 input + 11,811 output; 18 requests.
- Candidate mean: 95,591.5; 26.91% below this control.

All three completed with known provider usage and output check PASSED. Sentiment word counts: control 1,412; final 552/485. Research Manager: control 755; final 267/362. Final ratings and wording may differ. Source/date, limitations and unknown-holdings language were spot-checked, but no claim of exhaustive semantic equivalence is made. Existing financial reasoning/chronology errors can still survive Q1–Q4; independent C acceptance remains pending.

Preliminary candidates before the sentiment-path fix used 123,111/110,213 tokens. They remain in evidence but are excluded from the final mean. Compared with the user's earlier 120,301-token demo, these final observations are lower, but that earlier run is not the controlled baseline. The November 24 run_transient experiment and its 104,459 mean also remain a separate profile.

This is one case with one control/two final runs, not a universal saving or 20-run budget acceptance. Tool selection/call count and stochastic/vendor/cache behavior varied. Provider token counts include provider cache accounting and do not imply a monetary saving of the same percentage. The candidate 120,000 TOKEN_BUDGET is unchanged/unimplemented.

## Use and rollback

General application default remains False. Enable explicitly with TRADINGAGENTS_COMPACT_EVIDENCE_HANDOFF=true or programmatic compact_evidence_handoff=True before creating the graph. False restores the prior format; TRADINGAGENTS_CONCISE_INTERMEDIATE_REPORTS=false also disables this new formatting. Restart long-running processes to load source/config changes.

Demo launcher now passes `--compact-evidence-handoff`. Remove that argument to restore the previous presentation format. The confirmation snapshot includes compactEvidenceHandoff; frozen jobs retain the value they confirmed. Revalidate after backend restart. No GitHub publication/protection changes are made.

Reproduce sequentially from repository root:

    python -m demo.measure_handoff --live --date 2026-11-24 --runs 2 --output .local-review/handoff-new-comparison

The tool defaults to one control followed by the requested candidate count; --live is required for paid calls. --candidate-only with --cache-dir can reuse a separately recorded control cache; disclose this when used, as in the recorded final phase.

## Evidence and checks

Compact records: tests/member_d_verification/evidence/compact-evidence-handoff-2026-11-25.json. Full local sanitized stage/report records are under .local-review/compact-handoff-live-20261125 and .local-review/compact-handoff-final-20261125; raw records are not published automatically.

Focused negative tests verify disabled/master switches, full oversized report retention, exact tool-source preservation, no extra model call, separate sentiment path, and frozen/visible demo configuration. Ruff, mypy (15 source files), requirements schema (36/3), workflow permissions (5) and application security scan (107 Python files, zero medium/high findings) passed. The demo Bandit scan also found no medium/high findings. Final complete suite results are appended below after completion.
