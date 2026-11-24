# ADR 004 — Cumulative token admission beside the call cap (Alt-B settlement)

- Status: **Proposed (architecture record 2026-11-24)**. A genuinely new design cycle for `REQ-TA-NFR-COST-001` (cumulative token budget). It **does not modify** the C2 evaluation (C1/C2/C3) in [ADR 001](001-portfolio-aware-cli.md), the call-cap design (ADR-002 D3, §15), or the concise-context record (ADR-003, still **Proposed**). Not implementation; D implementation and C acceptance pending.
- Deciders: Member B (author), pending A (requirement meaning), C (verification), D (feasibility), E (evidence). Does not adopt requirements.
- Scope: cumulative input+output token admission across all model-request paths, alongside §15's call cap. Detailed contracts: [interface-contracts.md](../interface-contracts.md) §15A; state: [memory-design.md](../memory-design.md) §10.

> This is current design reasoning, not a measured experiment. No paid runs, no invented comparison.

## Context

§15 bounds the **number** of model-request attempts (`CALL_CAP`) with monotonic, single-use call reservations. That is orthogonal to **token** consumption: a within-cap run can still spend unbounded tokens (long prompts, large outputs, retries, concurrency). `REQ-TA-NFR-COST-001` requires a cumulative input+output budget with **reserve-before-dispatch**. `max_tokens=None` and the advisory 450/220-word targets are **not** finite output bounds. The provider-usage seam exists (`usage_metadata.input_tokens`/`output_tokens`) but `cli/stats_handler.py` zero-defaults missing fields, which must not be copied.

## Decision

Adopt, as a **proposed** design, a per-run `AdmissionCoordinator` that checks the §15 call cap **and** a token ledger **atomically** (no partial grant), with these elements:

1. **Defensible bounds, not estimates.** Admission requires a per-profile provider capability contract: a defensible **input upper bound** (exact tokenizer, or tokenizer-family + safety multiplier **justified for the complete supported request domain**; samples alone do not prove an upper bound), **tool/schema overhead** included, and a **finite enforced output allowance**. A profile lacking these is **UNSUPPORTED** (admission refuses; surfaced as a decision), never silently estimated. Character/4 is not admissible. The reservation is bound to the **final prepared request + config**, immutable after measurement.
2. **Mutually exclusive ledger** K (known actual) / R (reserved/in-flight) / U (UNKNOWN retained). Admission: `K+R+U+(input_bound+output_allowance) <= TOKEN_BUDGET` **conditional on the bounds holding**; a violation is made visible, never hidden. `H=K+R+U` is **not** monotonic; cumulative counters are.
3. **Alt-B settlement:** on **known** usage, move R→K with actual (unused allowance released; a decrease in H is intended); on **UNKNOWN**, move R→U (capacity retained, not reported as actual). **This version keeps U until finalization — no late U→K.**
4. **Invariant/refusal/overage semantics:** a **bound/protocol violation** (actual > allowance) records actual (no clamp), halts admissions, propagates a typed `TokenBoundViolation` → `INTERNAL_ERROR` with a safe diagnostic; an **ordinary required-refusal** (cannot fit) → `BUDGET`. **No new serialized stop reason.** `PERSISTENCE_ERROR` precedence preserved; in-flight accounted before immutable finalization; single terminal; truthful durability.
5. **Usage seam correctness (supported route only):** admission happens **before** the provider request. For the **supported non-streaming Chat Completions route** (chat-completions and the `response_format` parse branch), raw provider usage is captured at the **`_create_chat_result` seam** — the pattern already overridden in `DeepSeekChatOpenAI` — **below** the structured parser, before normalization/parse can discard it (including parse-failure followed by fallback). This hook does **not** cover every path: the **Responses API** branch returns via `_construct_lc_result_from_responses_api` without `_create_chat_result`, and **streaming** yields chunks without it; both are **excluded by pre-dispatch capability validation** until separately designed and tested (no universal-hook claim). `normalize_content` is post-response; `with_structured_output` builds a runnable and issues no request. The reservation binds the **final prepared request** (post-`_get_request_payload`, including provider-added fields) via an immutable `payload_fingerprint`. Raw usage is validated **before** normalization (the normalizer substitutes missing counts with 0, so normalized metadata cannot prove presence); missing/partial/invalid raw counts ⇒ UNKNOWN. Exception cleanup is state-aware (settle UNKNOWN only if still `DISPATCHED`, else preserve; always reset request-scoped context); exactly-once via ticket state; SDK retries `max_retries=0`.
6. **Call-cap coordination:** one atomic ticket; call grants are **never refunded** on invalidation (§15 monotonic), while **token** capacity **is** released on proven non-dispatch. Integration is a **targeted wrapper** of §15's entry point; §15 counting rules unchanged.

## Alternatives (genuinely distinct; current reasoning)

- **Alt-A — conservative full-allowance retention.** A dispatched attempt **permanently charges its full allowance** even if known usage is smaller; measured usage is recorded **separately** as information. Simplest accounting; strictest (persistently under-admits after cheap calls); UNKNOWN is a non-issue since the allowance was never released.
- **Alt-B — known-usage settlement with UNKNOWN retention (SELECTED).** On known settle, release unused allowance (R→K by actual); on UNKNOWN, retain capacity in U. Tighter capacity use; requires reliable usage capture + explicit UNKNOWN handling. **Selected** because it better matches `REQ-TA-NFR-COST-001`'s intent (count actual cumulative tokens, not permanently over-charge) while still reserving-before-dispatch and retaining UNKNOWN.
- **Usage-only post-accounting (NON-COMPLIANT).** Admit *after* observing usage. Cannot reserve before dispatch and cannot bound concurrency; explicitly **not compliant** with COST-001. Not offered as a choice.

**Tradeoff of the selection:** Alt-B's accuracy depends on the usage seam and bounds holding; a bound/protocol violation must be surfaced (it is). Alt-B is not "uniquely compliant" versus Alt-A — both reserve before dispatch and satisfy the reserve clause; Alt-A is more conservative and simpler, Alt-B uses capacity more efficiently. The choice reflects the requirement's "count actual tokens" intent, not a measured result.

## Consequences
- **Positive:** a checkable cumulative bound with a precise ledger; violations visible; no new stop reason; §15 call semantics preserved; reversible/parked behind a config gate.
- **Costs/limits:** requires the provider/profile bounds contract (UNSUPPORTED otherwise); bound violation may occur even under budget → `INTERNAL_ERROR`; empirical per-profile bound validity is separate evidence (E). Offline tests prove accounting logic, not deployed bounds. U retained to finalization (no late resolution) may overstate held capacity.
- **Preserved:** C2 history; ADR-002 call semantics; ADR-003 Proposed status; no adoption of `TOKEN_BUDGET`/`CALL_CAP`/120000.

## Related
- Canonical blueprint: [../../../architecture-blueprint.md](../../../architecture-blueprint.md)
- [../interface-contracts.md](../interface-contracts.md) §15 (call cap), §15A (token admission), §16.7 (version axes) · [../invariants.md](../invariants.md) INV-18/INV-20 · [../runtime-policy-catalog.md](../runtime-policy-catalog.md) R17/R23/R24 · [../memory-design.md](../memory-design.md) §10
- [001-portfolio-aware-cli.md](001-portfolio-aware-cli.md) (C2) · [002-extended-result-evidence-budget.md](002-extended-result-evidence-budget.md) (call cap) · [003-concise-intermediate-context.md](003-concise-intermediate-context.md)
