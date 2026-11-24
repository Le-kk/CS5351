# Token-context optimization: integration and architecture review

**Date:** 24 November 2026, Asia/Hong_Kong.<br>
**Local main after synchronization:** `8bf739565d42c7d8ea972779ffd754c0d065b830`.<br>
**Reviewed feature:** `9102759caaa59d778ba49cd57a1306f5f2ee5d88`, E's `perf/token-context-code-only-20261124`.<br>
**Status at inspection:** [PR #18](https://github.com/kelepawuqiusi/CS5351/pull/18) open and unmerged. This is a time-specific snapshot, not a permanent branch-status claim.

## Conclusion

The implementation is a bounded change to intermediate context production and repeated-argument assembly. It can be documented without restarting C2 or discarding the proposed budget design. Architecture must distinguish implementation on E's feature branch from integration into main, and observed token savings from a hard budget or independently accepted report quality.

Local main was fast-forwarded from `71bd501` to `8bf7395`, matching both origin and E's main at inspection. This merge includes Member B's architecture PR #17 and changes no tracked file contents relative to `71bd501`. All ten existing modified/untracked draft files were checked by SHA-256 and preserved. E's feature objects were fetched for inspection; its application changes were not merged into main.

## 1. What is and is not uploaded

The feature has 10 changed application files, one new regression file, one new opt-in benchmark, and two Member E conversation/index files. Its code change is `aa3b02d`; two later commits add/format the conversation record.

The supplied `token-optimization-architecture-and-measurement-report-2026-11-24.md` is absent from both inspected main and feature trees. The report's referenced `tests/member_d_verification/evidence/token-input-reduction-2026-11-24.json` is also absent. The PR description explicitly excludes reports and raw measurement data. Thus the report's initial "not committed, pushed or merged" sentence is a historical status: the code is now pushed in PR #18, but is still unmerged at this inspection.

The report was copied unchanged to a private handoff source directory so OpenCode can read it in WSL. SHA-256: `cbed455094d5836cf59f9e9d110d7e5441eb8fd132cbfb75f4ffc63aeadb21b1`. The repository source and regression tests can be inspected independently; the three measured live reports/tool payloads cannot currently be audited from this PR alone.

## 2. Behavior verified in source

| Concern | Feature behavior | Qualification for architecture |
|---|---|---|
| Intermediate analyst reports | `concise_analysis_instruction()` requests approximately 450 words, evidence first. `analysts/turn.py` appends it to the assembled system message on ordinary tool-bound and wrap-up paths. | Advisory output guidance, not truncation, a tokenizer guarantee or a hard output limit. Existing context compaction still applies when needed. |
| Research/risk debates | Bull/Bear and three risk debaters receive approximately 220-word guidance. | Final managers/Trader are not given these new brevity targets by this patch; graph topology and round counts are unchanged. |
| Duplicate opponent text | `opponent_argument_or_opening(text, opponent, history)` substitutes a reference only when the stripped full argument occurs in history and the feature is enabled. Empty opponents retain an explicit opening notice. | This is exact text matching, not semantic deduplication or a new model summarizer. |
| Compaction safeguard | `bound_debate_prompt` reconstructs the original explicit argument copies for its length check. If that original would exceed `min(context_cap_tokens, compaction_threshold_tokens) * 4`, it passes the restored form to `bound_agent_prompt`; otherwise it passes the reference form. | Restoring a copy before the existing guard is not a promise that all narrative survives compaction. Protect the existing trusted portfolio blocks and document the guard's actual behavior. |
| Switch | `concise_intermediate_reports=True`; environment override `TRADINGAGENTS_CONCISE_INTERMEDIATE_REPORTS=false`, or programmatic `False`. | Reversible behavior on the feature branch. Existing environment-boolean parsing applies. |
| Configuration evidence | New flag in graph `run_settings()` and shared API `_effective_config()`. | Extend the architecture's safe configuration inventory and trace reader/fingerprint effects. Do not interpret an old artifact's missing field as proof it ran with the new default. |

Changed application paths are `tradingagents/agents/context.py`, `agents/analysts/turn.py`, both `agents/researchers/*_researcher.py`, the three `agents/risk_mgmt/*_debator.py`, `default_config.py`, `graph/trading_graph.py` and `runapi/execution.py` (all under `tradingagents/`).

No new provider calls, summarizer agent, hard call cap, aggregate token/time budget, evidence registry or checker rule is introduced. In particular, the proposed Slice C budget/BUDGET contract in ADR-002 remains separate work. The benchmark's one SDK retry must not silently replace Slice C's proposed no-hidden-retry metering policy.

## 3. Measurement interpretation

The supplied numbers reproduce exactly:

- `(99,532 + 103,120 + 110,725) / 3 = 104,459` tokens.
- Against `138,896.5`: saving `34,437.5`, or **24.7936%**.
- Against `160,826`: saving `56,367`, or **35.0484%**.
- Mean observed time: **69.2667 s** across the three optimized runs.

These are E's reported live measurements for NVDA, 2026-01-09, four analysts, English, one round of each debate, the school `openai_compatible` gateway and DeepSeek V4 Flash. They were not rerun in this review. The historical baseline differs in provider-wrapper labeling/data availability; the closer same-day legacy control has one sample. Different price lookback windows, ordinary caching and model sampling remain possible influences. There is no separate ablation isolating the two optimization mechanisms.

The uploaded benchmark uses `TradingAgentsGraph.run_transient`, not the supported `run_analysis_api` completion/check/publication envelope. Its `COMPLETED` field means that this benchmark call returned. It is not independent product acceptance, an authoritative Q1–Q4/R1–R8 verdict, or proof that all mandatory data were available. No portfolio is supplied by this benchmark; these runs do not cover confirmed-empty or held-portfolio acceptance.

The excluded missing-price comparison, cached-price profile and HTTP-429 partial attempt must remain distinct from the three successful online samples. Retain failures in an attempt inventory when assessing completion or overall operational cost. Missing news/social/macro inputs, varied ratings and free-text factual/arithmetic limitations mean that semantic quality still needs C's evaluation. The live measurements must not be presented as a universal 24.8% saving, guaranteed runtime, satisfied hard call limit or completed COST/semantic acceptance.

## 4. Verification performed here

An isolated source export of feature `9102759` was tested using the existing project virtual environment. Main's application files and tests were not changed. The exact command and output are retained in [review facts](evidence/token-context-review-2026-11-24.json).

| Local offline check | Result |
|---|---|
| New `tests/member_d_verification/test_token_input_reduction.py` plus existing `tests/test_portfolio_context.py` and `tests/member_b_remediation/test_r4_research_manager_context.py` | **49 passed in 1.94 s** |
| Live calls | None made |
| Full 1,797-test suite | E reports passing; not rerun locally in this review |

The new compaction-reference test replaces `bound_agent_prompt` with an identity function. It demonstrates the selection/restoration branch, not an end-to-end proof that every latest argument or every piece of evidence survives real compaction. Existing portfolio/context tests provide separate regression evidence for their tested cases. Advisory instructions cannot prove that model prose always preserves every disclosure.

At the public API inspection, the feature's required-tests summary, Python jobs, install smoke, AI-log, dependency and Ruff checks succeeded. The separate `test approval` and producer checks failed; the reported summary says the approval workflow did not finish successfully. This review does not infer the exact cause or invent an earlier approval. See the [check snapshot](evidence/token-context-pr-checks-2026-11-24.json). A green ordinary regression run does not repair approval chronology.

The newly added E record explicitly preserves public user/assistant turns and omits tool calls/results and code payloads. Keep that declared scope: it must not be relabelled as a full raw OpenCode implementation transcript. D5 assembly and original implementation-tool provenance remain separate.

## 5. Focused architecture handoff

Update the root blueprint, safe configuration contract, memory/context assembly, runtime policy, traceability and risk/logbook entries. A new narrow ADR can record this source-inspected decision without rewriting historical C1/C2/C3 evaluation or inventing an earlier approval/experiment. Update ADR-001 only to distinguish its historical planned compaction details from the actual guard and this feature; preserve its decision history.

Keep these boundaries explicit:

1. Concise generation/repeated-context reduction is distinct from per-prompt estimated context bounds and proposed run-wide budgets.
2. Trusted portfolio facts and final provenance/check/publication authority retain their existing contracts.
3. The concise mode is part of effective configuration; trace its actual metadata/reader/fingerprint handling and legacy absence.
4. Evidence-preservation wording is prompt guidance except where a tested deterministic mechanism actually applies.
5. Quantitative statements cite the report/PR and disclose missing measurement artifacts; no link may pretend the absent JSON is already uploaded.
6. Rebase architecture status on the actual main/PR state before writing. If PR #18 has merged, inspect the merge revision before calling the feature integrated.

Member B's new OpenCode documentation interaction should retain the planning decision, human review and corrections. It must not retroactively manufacture E's implementation planning/test-approval evidence. Canonical requirements, code, tests, CI and other members' evidence are outside this documentation update.
