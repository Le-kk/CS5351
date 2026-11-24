# ADR 003 — Concise intermediate context and reversible repeated-argument references

- Status: **Proposed (architecture record 2026-11-24)**. Documents the design of E's concise intermediate-context feature as **inspected from source** (`aa3b02d` on feature `9102759caaa59d778ba49cd57a1306f5f2ee5d88`, PR #18). **Implemented on the feature branch; NOT integrated into main.** This is a *current rationale and retrospective source analysis*, **not** a historical ADD experiment, candidate comparison, human approval or ablation.
- Deciders: Member B (author); A/C/D/E coordination pending. Does not adopt requirements or approve implementation.
- Scope: intermediate context generation/assembly in the analysis-execution stage. It does **not** change checker/evidence/publication contracts or ADR-002's proposed slices.
- Relationship: does not supersede ADR 001 (C2) or ADR 002. Preserves C1/C2/C3 history and the C2 choice.

## Context

Analysts produce verbose intermediate reports that downstream research/risk agents re-read, and debate prompts carried both the full history and a separate copy of the opponent's latest argument (duplicate evidence below the existing character/4 prompt guard's threshold). The existing `bound_agent_prompt` guard (`agents/context.py`) bounds very large assembled prompts by estimation `ceil(len/4)` against `context_cap_tokens`/`compaction_threshold_tokens`, trimming low-priority narrative; it did not prevent this sub-threshold repetition.

## Decision

This proposed record describes three mechanisms already implemented on the feature branch; retention/integration remains subject to team review and C acceptance:

1. **Advisory brevity guidance.** `concise_analysis_instruction(stage)` appends evidence-first brevity text (~450 words analysts, ~220 debates). **Placement differs by path:** in the analyst tool loop (`analysts/turn.py`) it is appended to the **assembled system message** (preserving tool schemas, call IDs and original input messages); in the Bull/Bear researchers and the three risk debaters it is appended to their **assembled prompt strings**. Advisory only — evidence, disclosures and required fields take priority; no hard output cap and no new forced truncation.
2. **Exact-string opponent reference.** `opponent_argument_or_opening(text, opponent, history)` returns a reference when the exact stripped argument occurs in history; empty opponents keep an explicit opening notice. This is exact Python string-substring matching, not semantic deduplication.
3. **Restore-before-guard safeguard.** `bound_debate_prompt` reconstructs explicit copies and, if the reconstructed original exceeds `min(context_cap_tokens, compaction_threshold_tokens) * 4`, passes the restored form to the existing guard; else the reference form. **No unconditional no-dangling guarantee:** a demonstrated boundary shows a short argument can be replaced by a *longer* reference notice, so the reference form can exceed the guard target even when the restored-original length fits; checking only the restored-original length can therefore miss compaction of the reference form (and thus of the history it cites). The safeguard reduces but does not eliminate dangling-reference risk. See `docs/reviews/evidence/token-context-reference-probe-2026-11-24.json`; follow-up for E/C below.

**Configuration/rollback:** `concise_intermediate_reports` (default `True`); `TRADINGAGENTS_CONCISE_INTERMEDIATE_REPORTS=false` or programmatic `False` restores legacy. Recorded in `run_settings()`/`EffectiveConfig`; the flag is not hashed, but the touched prompt sources are in `_prompt_hash` (interface-contracts §3.8), so new-run `prompt_hash` differs. Legacy artifacts lacking the field are `unknown/legacy`, not today's default.

## Alternatives considered (bounded)
- **No change (verbose baseline):** rejected as the measured driver of repeated input cost.
- **New summarizer/summary-model call:** rejected — adds provider cost/calls and a new failure mode; out of the bounded goal.
- **Hard output-token cap / tool-payload truncation:** rejected — risks dropping required evidence/disclosures; the feature adds no new forced truncation (the existing guard may still trim narrative).
- **Semantic deduplication:** rejected — not deterministically enforceable cheaply; the exact-substring reference is deterministic and reversible, subject to the documented reference-boundary risk.

## Consequences
- **Positive:** shorter intermediate context and removed duplicate argument text, with a concrete reversible switch; trusted portfolio facts, provenance/check/publication authority unchanged; existing guard preserved.
- **Cost/tradeoff:** advisory brevity can omit nuance; reference depends on exact text presence; one measured case with no ablation (E-reported optimized mean 104,459 vs historical 138,896.5 ≈ 24.79%, same-day control 160,826 ≈ 35.05%) — **not** a universal, runtime, or quality guarantee, and **not** COST-002/Slice C.
- **Limits:** feature unmerged; benchmark uses raw `run_transient` (not product acceptance); compaction preservation not proven end-to-end; semantic acceptance pending C; PR #18 approval checks failed and prior approval is not established.
- **Known boundary and follow-up (E/C, not implemented here):** the reference notice can be longer than the argument it replaces, so the restore-before-guard length check (on the restored-original form) can pass while the reference form still exceeds the guard and has its cited history trimmed. Follow-up for **E**: use a reference notice no longer than the replaced argument, or evaluate compaction against the reference form; for **C**: add a regression fixture reproducing the synthetic boundary and asserting the delivered prompt never cites trimmed history. Recorded in `risk-list.md` R-CONCISE.
- **Separateness preserved:** distinct from the existing per-prompt guard and from ADR-002's proposed run-wide `CALL_CAP`/`BUDGET` controller.

## Related
- Canonical blueprint: [../../../architecture-blueprint.md](../../../architecture-blueprint.md) §5 step 6, §8A.3a
- [001-portfolio-aware-cli.md](001-portfolio-aware-cli.md) (C2; unchanged) · [002-extended-result-evidence-budget.md](002-extended-result-evidence-budget.md) (proposed slices; unchanged)
- [../interface-contracts.md](../interface-contracts.md) §3.7/§3.8/§3.11 · [../memory-design.md](../memory-design.md) §9 · [../runtime-policy-catalog.md](../runtime-policy-catalog.md) R22 · [../traceability-inputs-member-b.md](../traceability-inputs-member-b.md) §4/§5.1
- Review: `docs/reviews/token-context-architecture-review-2026-11-24.md`
