# OpenCode prompt — align architecture with E's token-context change

Paste the following into the existing `CS5351 C2 architecture docs update` OpenCode session. This is a new bounded documentation task. It is not authorization to implement the proposed budget/checker/evidence slices.

```text
You are updating Member B's architecture for CS5351 using OpenCode and the available school DeepSeek V4 Flash model. Use precise source-backed reasoning, a bounded change plan and a human review checkpoint. Do not select a new model or claim a model-comparison result.

WORKSPACE AND BASELINE
- Work in /home/brian/projects/CS5351. Read applicable repository instructions first. Do not read credentials, .env, SSH/auth stores or unrelated private data.
- At the supervising review, main and both repositories' main were 8bf739565d42c7d8ea972779ffd754c0d065b830, containing B's architecture PR #17. E's PR #18 was OPEN, feature perf/token-context-code-only-20261124 at 9102759caaa59d778ba49cd57a1306f5f2ee5d88; code commit aa3b02d. Main did not contain the optimization. Recheck actual HEAD/PR status; do not assume this snapshot is still current.
- Existing local drafts must remain untouched. Record HEAD and the dirty-file set before work. No checkout, merge, reset, commit, push, PR comments or live/paid calls are authorized.
- Feature objects are fetched. Inspect them with git show/git diff; do not merge the feature just to read it. An isolated source snapshot is available at /home/brian/.local/state/cs5351-handoffs/2026-11-24-token-architecture-update/feature-source-9102759.

SOURCES TO READ
1. docs/reviews/token-context-architecture-review-2026-11-24.md and its two linked evidence snapshots.
2. /home/brian/.local/state/cs5351-handoffs/2026-11-24-token-architecture-update/sources/token-optimization-architecture-and-measurement-report-2026-11-24.md (unchanged supplied E report).
3. PR https://github.com/kelepawuqiusi/CS5351/pull/18 and actual feature/main diffs. The report and tests/member_d_verification/evidence/token-input-reduction-2026-11-24.json were NOT uploaded in the inspected PR; do not invent their availability.
4. Current root blueprint, ADR-001/002, interface-contracts, memory-design, runtime-policy-catalog, traceability inputs, risk-list, evaluation-logbook and implementation prompt pack. Read current requirements only as sources; do not adopt/amend them.
5. Feature source: agents/context.py, agents/analysts/turn.py, Bull/Bear researchers, three risk debaters, default_config.py, graph/trading_graph.py and runapi/execution.py (all under tradingagents/). Trace the config to actual stored metadata/fingerprint/reader seams. Read the added regression file and opt-in benchmark under tests/member_d_verification/.

PHASE 1 — READ-ONLY PLAN, THEN STOP
Return at most 900 words:
A. Current main/feature/PR status, dirty-file inventory and source applicability. Label feature-branch implementation separately from main integration. If code materially differs from 9102759, describe the difference before proposing edits.
B. A compact before/after context sequence, deterministic mechanisms versus advisory model behavior, and any real contradiction with existing architecture.
C. Exact proposed file/section write set and acceptance checklist. Explain why each change is needed. Identify source/evidence gaps without reopening unrelated requirements or C2 candidate selection.
D. Only decisions that block truthful documentation. Use pending-integration/pending-evidence labels for bounded uncertainties that can be documented. Do not block the whole update merely because A/C acceptance is unfinished.
Do not write files in Phase 1. Stop for my approval of this concrete plan.

PHASE 2 — AFTER I APPROVE THAT PLAN
Write only the approved B-owned documentation paths. Expected targets, to narrow in Phase 1:
- architecture-blueprint.md: affected component/data-flow and context sections, implementation-status table, and a concise engineering-contribution entry tied to actual source/evidence.
- docs/architecture/interface-contracts.md: EffectiveConfig field/inventory/example compatibility and concise-context assembly contracts where appropriate; no checker/evidence/budget semantics changed.
- docs/architecture/memory-design.md and runtime-policy-catalog.md: exact-reference assembly, fallback to explicit copies before compaction, trusted context, prompt targets, rollback. Use an unused policy ID; do not confuse it with checker R1-R8 or Q1-Q4.
- docs/architecture/traceability-inputs-member-b.md, risk-list.md, evaluation-logbook.md: real mappings, source revision, checks, measurement limits, pending acceptance and chronology.
- A narrow new docs/architecture/adr/003-concise-intermediate-context.md if justified. Label retrospective source analysis/current rationale honestly; never invent a past ADD experiment, candidate comparison, human approval or ablation. Update ADR-001 only where a clear historical-versus-current clarification is necessary. Preserve C1/C2/C3 history, C2 choice and ADR-002's proposed slices.
Do not edit evaluation-table/option-ledger or the pointer blueprint unless an actual cross-reference/status change requires it and the plan explicitly includes it. Do not edit the pre-existing numeric-extension proposal, requirements, application code, tests, CI, review/evidence files or other members' logs. No new D5 completion or implementation approval may be claimed.

REQUIRED CONTENT AND GUARDRAILS
1. Feature guidance is approximately 450 words for analysts and 220 for Bull/Bear/risk debates, advisory and subordinate to evidence/disclosures. No hard output-token cap, new summarizer/model call, tool-payload limiter, graph-role deletion or round reduction is introduced. The existing guard can still compact large inputs.
2. References require the complete stripped opponent text to occur in history. Explicit copies are restored when the reconstructed original prompt exceeds min(context_cap_tokens, compaction_threshold_tokens)*4, before bound_agent_prompt runs. Describe this actual algorithm, not semantic deduplication or guaranteed preservation of every narrative fact. Empty-opponent notices remain.
3. Preserve protected portfolio facts, ownership semantics, five research ratings versus three Trader actions, authoritative provenance, final rendering/checking and publication contracts. Prompt instructions are not deterministic semantic enforcement.
4. concise_intermediate_reports defaults True on the feature; environment switch TRADINGAGENTS_CONCISE_INTERMEDIATE_REPORTS=false or programmatic False restores legacy mode. It is recorded in run_settings/_effective_config. Address old artifacts missing the field and actual config/hash/reader effects; do not silently relabel historical runs as using today's default. Do not invent schema-version changes without finding a contract need.
5. Keep three mechanisms separate: (a) advisory brevity/exact reference optimization, (b) existing character/4 estimated per-prompt guard, (c) proposed run-wide call admission/BUDGET design. Cost savings do not satisfy COST-002 or implement Slice C. The benchmark's retry=1 does not replace the proposed metering policy against hidden retries.
6. Measurements are REPORTED by E: optimized 99,532/103,120/110,725, mean 104,459; historical mean138,896.5 =>24.7936%; same-day one-sample control160,826 =>35.0484%. Keep the NVDA/2026-01-09, model/provider, empty-memory, round and data/cache qualifiers, exclusions and failed attempt. No universal saving/runtime/quality claim, no causal attribution to each mechanism without an ablation.
7. The benchmark uses raw graph.run_transient without portfolio, not the supported run_analysis_api acceptance/publication path. Its COMPLETED label is not formal product or semantic acceptance. Confirmed-empty/held modes and independent C acceptance remain unverified by these measurements.
8. Supervising review reproduced49 offline tests in an isolated feature snapshot; E reports1,797 full-suite passes and ordinary hosted checks succeeded. Do not present those1,797 as rerun by you. The new reference test mocks the final guard; no end-to-end universal compaction proof follows. No live runs in this task.
9. PR's separate test-approval check failed at review. Do not weaken the policy, retrospectively create approval, relabel E's implementation tool as OpenCode or claim the public-turn extract includes omitted tool payloads. Preserve authentic current OpenCode interactions for later AI-log/D5 work. The school model is an access constraint, not an originality claim.
10. Relate the optimization to the project's engineering argument as a concrete cost/evidence tradeoff with reversible configuration and measured observations. Standard techniques are not world-first inventions. Originality and semantic acceptance remain separate assessments.

FINAL VERIFICATION AFTER APPROVED EDITS
- Exact approved write set; existing dirty files preserved; no protected paths changed.
- Every factual statement has source/evidence or is explicitly proposed/reported/pending.
- Local links work in the intended published set, not merely because an unrelated private/untracked file exists. Do not link an absent measurement JSON as if uploaded.
- No stale contradictory descriptions of concise generation, compaction, aggregate budgets or branch status. Preserve C2/ADR002 history and unknown requirements decisions.
- Markdown fence/link checks and git diff --check. No invented tests or measurements.
- Finish with changed file/section -> source/requirement/check mapping, real checks performed, residuals and exactly what C/D/E should do next. Stop; no commit/push or implementation.
```
