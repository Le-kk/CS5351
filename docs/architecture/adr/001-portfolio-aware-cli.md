# ADR 001 — Portfolio-aware CLI: input/service boundary and consent

- Status: **Proposed (architecture draft; implementation-aligned 2026-11-24)**. Selection made by Brian (human) 2026-11-12; awaiting team/instructor reconciliation. The C2 boundary is **implemented** at `a62b801` (verified); this ADR records the decision and its as-built status, not an approval.
- Deciders: Brian (selection), Member B (author), pending A (requirements coherence), E (governance/assembly).
- Scope: `SEL-TA-FR-001..007`, `SEL-TA-NFR-001..006`, `SEL-TA-GOV-006` (permission design contribution). Broader `REQ-TA-*` extensions are recorded as proposed impacts in §"Proposed broader requirements", not adopted here.
- Supersedes: none. Does not modify v2 requirements or the D1 registry (A owns).

> Estimates in this ADR are labelled **ESTIMATE** and are design judgements. No measurement or verification is claimed.

## Context

TradingAgents v0.7.1 already has an optional `--portfolio PATH` that loads a `PortfolioContext` and renders it into decision-agent prompts (`cli/main.py:50-55`, `tradingagents/portfolio.py`, `tradingagents/graph/trading_graph.py:293-307`). The selected requirements extend this into a discovery + explicit-consent + frozen-provenance + deterministic-check workflow, with distinct `NO_PORTFOLIO`/`PORTFOLIO_PROVIDED` semantics. The course additionally requires a **layered agent context** design, context assembly and compaction constraints, which this ADR records.

Constraints from the current selection (treated as fixed working decisions): CLI-only UI; `PORTFOLIO_DIR=<root>/portfolios`; `--without-portfolio`; `--portfolio-as-of`; consent behaviour; full normalized-content SHA-256 fingerprint; no silent fallback; no invented zero holdings/cash; model cannot assign checks.

## Course-required layered context (design)

| Layer | Content (bounded application context) | Source |
|---|---|---|
| Identity | Instrument/ticker + resolved identity context | `agents/context.py:build_instrument_context` |
| Standing constraints | Advisory-only role; no execution; rating vocabulary; disclaimer requirement; "no account ownership assumed" | prompts + frozen strings |
| Knowledge | Analyst reports, research/trader plans, risk debate | graph state |
| History | Memory-log lessons from prior decisions | `tradingagents/memory/` |
| State | Input mode, selected basename, as-of/basis, fingerprint (safe projection) | `RunContext` |
| Current task | The run's instruction to produce a rating + decision | node prompt |

### Context assembly pipeline (application-bound)
`deduplicate → prioritize (identity/constraints first) → budget (per-agent token cap) → compact (summarize low-priority narrative; never drop mode/snapshot identity/output authority/critical constraints) → assemble (final prompt)`.

#### Operational budget and compaction design (B3-07, F6; proposed, unmeasured)
All numbers are **proposed design values (ESTIMATE)**, not measured. C/D later verify/measure.

> **Historical-vs-current clarification (2026-11-24).** This subsection is the *originally proposed* per-agent compaction design (target `T_compact`, optional summarizing call, `context.compact` event). The **actual implemented guard** (`bound_agent_prompt` in `agents/context.py`) is narrower: it estimates `ceil(len/4)`, trims low-priority narrative against `context_cap_tokens`/`compaction_threshold_tokens`, and protects `<protected_context>` regions — it does **not** implement the full target/threshold/re-injection pipeline below as such, and it adds no summarizing model call. E's concise intermediate-context feature (ADR-003, feature `9102759`, unmerged) is a **separate** change that restores explicit debate copies before this guard. The proposed design here is retained as design intent; the implemented behaviour is authoritative where they differ. C2 selection and rationale below are unchanged.

- **Estimator:** token counts approximated by `ceil(len(prompt_chars)/4)` (cheap, provider-agnostic; **explicitly estimated**, no guarantee against provider tokenizer; no tokenizer dependency added).
- **Per-agent context cap** `C_cap = 24,000` estimated tokens (proposed): bounds the **assembled prompt context** for one agent, not an aggregate run budget.
- **Critical reserve** `R_reserve = 4,000` estimated tokens (proposed) planned for identity + standing constraints + state/authority + frozen notice/disclaimer; never compacted.
- **Compaction threshold** `T_compact = floor(0.8 · C_cap) = floor(19,200) = 19,200`; compact when estimated context exceeds `T_compact`; hard stop at `C_cap`. (Arithmetic corrected: 0.8 × 24,000 = **19,200**, not 20,000.)
- **Protected-context overflow (actual estimate, not the constant):** let `P` be the **measured estimate of the protected layers** (identity + constraints + state/authority + notice/disclaimer) at assembly time. If `P + (minimum irreducible task/history context) > C_cap`, or more simply if `P > C_cap − C_min_task` (where `C_min_task` is the minimum needed for the current task), **fail closed** (typed `INTERNAL_ERROR`, redacted). The guard compares the **actual protected estimate `P`**, never merely `R_reserve` (which by construction is ≤ `C_cap` and could never overflow).
- **Compaction termination:** compaction reduces only low-priority narrative (debate prose, redundant analyst text) until total ≤ `T_compact` or until the only remaining reducible content is protected; if compacting all reducible narrative still leaves total > `C_cap`, **fail closed**. Available narrative budget = `C_cap − P`; stop when narrative reaches that bound.
- **Compaction method:** summarize/trim **low-priority narrative layers only**; deterministic truncation with an explicit "(compacted)" marker is the baseline. If a summarizing **model call** is used it is an **explicitly disclosed extra provider call** logged as `event=context.compact` — not silent network behaviour. Default design = deterministic truncation (no extra model; consistent with the note that these corrections imply **no new summarizing provider call**).
- **Re-injection:** after compaction re-inject identity, mode, snapshot identity (fingerprint/basename/as-of), output authority and frozen disclaimer/notice.
- **Where:** node-prompt assembly in the agent context layer (`tradingagents/agents/context.py` + prompt builders); **not** OpenCode's internal context.
- **Temporal guards:** memory/context retrieval keeps upstream as-of/time guards; compaction must not reintroduce out-of-window history.
- **Illustrative over-cap (document example; arithmetic verified):** assembled estimate = 26,000 tokens; protected `P ≈ 3,200` (identity/constraints/state/notice). Reducible narrative ≈ 22,800. Compaction truncates older bull/bear debate prose (~6,500 → ~500, saving ~6,000) giving 26,000 − 6,000 = **20,000**, still > `T_compact`=19,200, so further low-priority narrative is trimmed (e.g., another ~800) to reach ≈ **19,200** ≤ `T_compact`; protected `P` and current task survive. If instead `P` were 23,000, then `C_cap − P = 1,000` narrative budget, and it fails closed when the minimum task context cannot fit.
- **Distinction:** bounded **application-context** design; not OpenCode internal management; **not** an aggregate run-token/time/call budget (deferred).

## Decision

Adopt **C2: an input-service + deeply immutable `RunContext` boundary with a small explicit CLI lifecycle coordinator and a shared execution service.**

- `PortfolioInputService` (`tradingagents/runapi/input_service.py`): the sole discoverer/validator/freezer; produces a `RunContext`.
- `RunContext`/`FrozenSnapshot` (`runapi/context.py`): deeply immutable value tuples + mode + full-64 canonical SHA-256 + as-of/basis + consent_state; read-only provenance source.
- **Shared execution service** (`runapi/execution.py: run_analysis_api`): the **common application entry** for CLI and supported project API; rejects non-`CONFIRMED` contexts; owns execution, exception mapping, checks, finalize, staging/publish and terminal event; prompt-free.
- `RunLifecycleCoordinator` (CLI layer): interactive selection/consent transitions; no LLM; no broad orchestration rewrite; no backtest/resume.
- `OutputChecker` and `OutcomeFinalizer` are the sole assigners of `output_check`/`run_outcome`.
- Upstream engine signature preserved; the raw primitive is a declared reduced-coverage path whose product reliance requires A's approval (R-API).

## Alternatives considered (actual, preserved)

- **C1 — Minimal baseline extension.** Inline discovery/validation (sole shared module, thin inline adapter); header lines appended in reporting; small checker; inline manifest. Pros: smallest footprint. Cons: lifecycle sequencing inline; higher risk of provenance drift if reporting re-derives from `final_state` (latent FR-006/007 risk); weakest typed failure behaviour. Score 3.30.
- **C2 — Input-service + `RunContext` + small coordinator + shared execution service (selected).** Pros: explicit input/snapshot boundary; clean test seams; shared provenance; typed outcomes; full-coverage API path. Cons: more modules than C1. Score 4.65.
- **C3 — Phased single-run orchestrator façade.** Same service/context, plus a façade over the whole single-run lifecycle. Pros: strong phase testing. Cons: broader `cli/run.py` change; highest coupling/surface; scope-creep risk. Score 3.75.

## Human selection rationale (recorded verbatim in substance)

Brian selected **C2** because of its **explicit input/snapshot boundary, test seams and shared provenance, without C3's broader orchestration change.** This is a **human design choice based on estimated tradeoffs**, explicitly **not** a claim of verified superiority.

## Consequences

Positive: single provenance source; deterministic check authority; consent is an explicit transition; shared execution service gives full-coverage API path; preserved engine signature.
Negative/risks: the raw low-level engine primitive can bypass the boundary and its product use requires A's approval (R-API); full-64 fingerprint canonicalization must be exactly implemented (`interface-contracts.md` §2.2); prompt/context wording changes are required (not optional).
Scope note: the implemented optional-portfolio flow is retained here. The broader `REQ-TA-*` candidate's scope statement excludes portfolio files while its fixture profiles include them; that replacement-scope disagreement is **unresolved (A/C/team)** and does not change this ADR's decision.

## Repairs (2026-11-21, R1–R5)

These bounded repairs keep the selected architecture; see [remediation record](../../reviews/remediation-r1-r5-2026-11-21.md).

- **R4:** the Research Manager now receives the same protected `get_portfolio_context_from_state` block as the Trader and Portfolio Manager, together with a stage-appropriate instruction to correct conflicting upstream ownership premises. The five-tier research vocabulary and three-action Trader vocabulary are unchanged and no rating is forced. **Scope of the guarantee:** this is *prompt grounding* — the trusted snapshot facts are deterministically delivered to all three decision stages (verified by prompt-capture tests), not a guarantee that the model *cannot* state a nonexistent position. Only a deterministic check could enforce that; the current Q1–Q4 checker does not inspect ownership narrative, so whether a given model response honours the grounding is a **semantic** matter pending C's GOV-004 acceptance. The R4 repair reduces the chance of an unsupported ownership claim; it does not deterministically forbid one.
- **R5:** publication stages a private tentative terminal on the `EventSink` and only commits the caller-visible terminal after the single directory rename succeeds; a critical publication failure exposes exactly one matching `INCOMPLETE` terminal. Terminal-append failure alone still preserves the logical outcome with `terminal_event.durable=false`; report/manifest remain critical and the single-terminal rule is preserved.

## Implementation status at `a62b801` (verified 2026-11-24)

The C2 boundary is present in the checkout, not merely designed:

- `runapi/input_service.py` (`PortfolioInputService`, `freeze_explicit`, `freeze_no_portfolio`), `runapi/context.py` (`RunContext`, `FrozenSnapshot`, `ConsentState`), `runapi/execution.py` (`run_analysis_api`, rejects non-`CONFIRMED` at `:149`), `runapi/checks.py` (`OutputChecker`, Q1–Q4), `runapi/finalize.py` (`classify_exception`, `OutcomeFinalizer`), `runapi/persist.py` (single `os.rename` publication at `:154`), `runapi/events.py` (stage-private tentative terminal), `runapi/result.py` (`RunResult`/`CheckResult`/`Finding`), `runapi/reporting.py` (`build_envelope`, `verify_envelope_header_matches`), `runapi/redact.py`.
- R1–R5 repairs are implemented (`agents/structured.py` applies the shared `Redactor` to its fallback warnings). Independent acceptance of these repairs remains **pending (C)**; the implementation's own remediation record is `docs/reviews/remediation-r1-r5-2026-11-21.md`.
- The C-owned tests under `tests/member_c_verification/offline/` define the seams; passing status is C's to report, not this ADR's.

## Proposed broader requirements — impact, **not** implemented

The uploaded `docs/req/requirements.yaml` (`status: proposed_for_adoption`) and A's later correspondence would extend the as-built system. If adopted, the following are architecture impacts, documented but **not** designed as accepted decisions here:

- **`BUDGET` stop reason** and a run-wide **single-use call-reservation** controller (`REQ-TA-RUN-001`, `REQ-TA-NFR-COST-002`): would add a sixth serialized `StopReason`, a shared budget component consulted before every model dispatch, and updates to every reader. The current five-value literal (`runapi/result.py:12-14`) has no `BUDGET`.
- **R1–R8 output check** (`REQ-TA-ARCH-002`) and **corrected-only `PASSED`** (R5): R2 (evidence-ID resolution) and R4–R7 (sentiment/coverage) require new data fields and registry components the checker does not inspect; R5 would change `Finding.status`/`CheckResult` so `PASSED` can carry corrected findings — a coordinated type change across checks/report/scorer if retained.
- **Evidence and coverage registries** (`REQ-TA-FR-001`, `REQ-TA-FR-005`, `REQ-TA-INV-002/007`), **aggregate budgets/resume** (`REQ-TA-NFR-PERF-002`, `COST-001/002`, D-5): new components and a resume contract that currently conflicts with `INV-11`/`INV-12`.
- **`REQ-TA-INV-014` / `REQ-TA-GOV-004`** are pending publication; the existing design already covers input freezing (`INV-04/05/05b`) and treats schema validation as a governance/CI boundary, so their absence does not change C2's data flow.

## Reopening conditions

- Instructor mandates a single orchestration façade → revisit C3.
- File-count/scope constraints favour C1 → revisit.
- Real test evidence (C) shows C1's inline path is cleanly testable with no provenance drift → re-score.
- Any change to consent semantics, provenance identity or check authority requires a new ADR.

## Related

- Canonical blueprint: [../../../architecture-blueprint.md](../../../architecture-blueprint.md)
- [../interface-contracts.md](../interface-contracts.md), [../evaluation-table.md](../evaluation-table.md), [../evaluation-logbook.md](../evaluation-logbook.md), [../risk-list.md](../risk-list.md), [../option-ledger.md](../option-ledger.md), [../invariants.md](../invariants.md), [../memory-design.md](../memory-design.md), [../runtime-policy-catalog.md](../runtime-policy-catalog.md), [../permission-model.md](../permission-model.md), [../traceability-inputs-member-b.md](../traceability-inputs-member-b.md).
