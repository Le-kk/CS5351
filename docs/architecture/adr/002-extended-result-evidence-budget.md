# ADR 002 — Extended result contract, output-check v2, evidence/coverage and run budget

- Status: **Proposed (architecture draft 2026-11-24)**. A **genuine new design cycle** for the broader proposed requirements. It is **separate** from, and does not modify, the preserved C2 evaluation (C1/C2/C3) in [ADR 001](001-portfolio-aware-cli.md). Not implementation; not team adoption of A's registry; D implementation and C acceptance are pending.
- Deciders: Member B (author), pending A (requirements meaning/scope), C (verification), D (implementation feasibility), E (governance/CI).
- Scope: `REQ-TA-ARCH-002`, `REQ-TA-FR-001/005/006/007/008`, `REQ-TA-SEC-003`, `REQ-TA-NFR-COST-002`, `REQ-TA-RUN-001` (`BUDGET`), and associated `REQ-TA-INV-*`. Detailed contracts are in [interface-contracts.md](../interface-contracts.md) §13–§16.
- Does not supersede ADR 001. The two coexist: C2's input-service/immutable-`RunContext`/shared-execution boundary is the base these extensions build on.

> Estimates are labelled **ESTIMATE**. No measurement, approval or historical alternative is invented. The old C2 candidate evaluation is preserved unchanged.

## Context

The 24 November requirements snapshot (`docs/req/requirements.yaml`, `status: proposed_for_adoption`) proposes obligations beyond the implemented `SEL-TA-*` baseline: an R1–R8 deterministic output check with a **corrected** finding class, an evidence-ID registry and per-run coverage record, a run-wide single-use request-budget controller and a `BUDGET` stop reason. The as-built system implements only Q1–Q4, five stop reasons, and input provenance (see interface-contracts §12). This ADR records the **bounded design decisions** needed to make those obligations implementable and testable, without claiming they are adopted or built.

## Decisions (bounded alternatives)

### D1 — Corrected findings may coexist with `PASSED` (approved *published target*)
- **Chosen (target):** `Finding.status ∈ {BLOCKING, CORRECTED}`; **any BLOCKING ⇒ `NEEDS_REVIEW`; CORRECTED-only ⇒ `PASSED`**; corrections applied before the single evaluation on the re-rendered, redacted delivered body (interface-contracts §14.2). The verdict covers the exact delivered body; only safe correction fields are persisted.
- **Wording note:** "approved published target" means **approval to draft this architecture target**, **not** final team adoption of the requirements and **not** a completed, tested ADD iteration.
- **Alternative (unapproved requirements-change only):** keep blocking-only (as-built). Recorded as a deferral alternative that would require a requirements change; **not** the target. Tradeoff: loses the ability to auto-downgrade (e.g., R5 confidence) while still passing.
- **Impact:** `Finding`/`CheckResult` types, report rendering, manifest `check_rules_version`, scorer readers — shipped together.

### D2 — R3 ownership check is a deterministic blocking phrase check (target)
- **Chosen (target):** R3 is a **blocking phrase/pattern check** over the delivered body against A's banned-ownership list; a match ⇒ BLOCKING.
- **Alternative (requires A/C/team agreement):** contextual handling — flagged only when not grounded in supplied facts, permitting quoted/conditional uses. Not reliably deterministic; would be a semantic-rubric matter. Recorded as an alternative, **not** an advisory replacement.
- **Impact:** checker rule + fixture list; no model call.

### D3 — Run budget: shared single-use reservation controller
- **Chosen:** one run-scoped controller; atomic `reserve()` issuing **single-use** reservations whose **successful-admission counter is monotonic** (an unused grant may be invalidated/audited but never refunds capacity); `dispatch_attempts <= granted <= CALL_CAP`; metering attached to the run's tier chat-model objects so **plain, tool-bound (`bind_tools`) and structured (`with_structured_output`) dispatches each consume exactly one reservation** (verified by probes, not assumed); SDK `max_retries=0` (reject clients that can't); exhaustion survives broad handlers; persistence failure stays primary.
- **Alternatives considered:** (a) reusable semaphore — rejects (bounds concurrency, not cumulative calls); (b) counter at high-level invocations with SDK retries on — rejects (cannot guarantee the bound); (c) branch-overshoot allowance — rejects (unnecessary under single-use reservations); (d) **slot recycling** (returning an unused grant to capacity) — **rejects** (violates the cumulative bound: at cap 1, grant/invalidate/re-grant would yield two successful reservations); an explicit **different counting contract + requirements decision** would be needed to adopt it.
- **Tradeoff:** strict cap can starve a parallel branch that loses the last slot (stops rather than degrades) — the price of a checkable guarantee.

### D4 — Evidence/coverage as separate registries feeding R2/R7
- **Chosen:** dedicated `EvidenceRegistry` (stable IDs, resolution) and `CoverageTracker` (12-channel record, `NOT_REQUESTED`), built from tool results, deterministic render; R2/R7 integrate **after** these contracts are agreed.
- **Alternative:** embed coverage in the checker — rejects (server-side determinism and R7 equality need a record, not a derived glance).
- **Dependency:** channel↔method map and the two router-bypass call sites to be confirmed by D/C.

### D5 — Resume identity (decision presented separately; not decided here)
- **Alternatives:** (a) fresh `run_id` per invocation (current INV-12, chosen baseline); (b) logical-run identity + attempt identities with isolated artifacts (D's call; requires revising INV-11/12 wording). **Not chosen here; not promised.** Interruption semantics (`INTERRUPTED`) stay; resume is a separate contract change.

## Consequences
- Positive: a concrete, testable target for the broader requirements; corrected findings enable auto-downgrade checks without failing; the budget bound is enforceable; evidence/coverage become deterministic.
- Negative/limits: larger result/report/manifest/scorer surface (version gates required); R3 deterministic phrase check cannot judge context; R5 corrected-only `PASSED` requires every reader to understand `CORRECTED`; evidence registry is the largest implementation risk before the deadline.
- Preserved: ADR 001 / C2 selection and rationale; Q2 trusted-provenance guard (kept separately from R2); as-built Q1–Q4 behaviour remains the current description until implementation.

## Implementation-status addendum (2026-11-25, `6b57aad`; decision unchanged)
Bounded dated status, **not** a new decision and **not** an acceptance:
- **D3 (call cap) — implemented for the bounded profile:** opt-in `RunBudgetController` (`runapi/budget.py`) with the synchronous SDK transport seam (`llm_clients/budget_transport.py`); supported tiers `deepseek`/`openai_compatible`, SDK/transport retries disabled, async rejected; monotonic single-use run-bound tickets; `seal()` waits active responses; `finalize` emits `BUDGET` on refusal with `PERSISTENCE_ERROR` primary; enabled budget-only manifest `schema_version` int `2`, `check_rules_version` int `1`, `run_budget` five safe counters, reusing `validate_budget_manifest`/scorer. **Not** a token/time cap, arbitrary-code protection or gateway-internal-retry count.
- **D1/D2/D4 (corrected findings, R1–R8, evidence/coverage) — still unimplemented:** the checker emits only Q1–Q4; types admit `CORRECTED` but no rule produces it.
- **Cumulative token admission (`REQ-TA-NFR-COST-001`, §15A, ADR-004) — still proposed:** not implemented.

## Related
- Canonical blueprint: [../../../architecture-blueprint.md](../../../architecture-blueprint.md)
- [../interface-contracts.md](../interface-contracts.md) §13–§16; [001-portfolio-aware-cli.md](001-portfolio-aware-cli.md); [../runtime-policy-catalog.md](../runtime-policy-catalog.md); [../invariants.md](../invariants.md); [../traceability-inputs-member-b.md](../traceability-inputs-member-b.md)
