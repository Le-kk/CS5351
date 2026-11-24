# Architecture Blueprint — Portfolio-Aware CLI and Auditable Reporting

Status: **architecture draft, implementation-aligned (revised 2026-11-24)** for Member B's session. It describes the C2 design and now also states, separately, what the `main` checkout implements at `a62b801a51e6310f3b46860f6d2790583a95e0e0` versus what remains proposed. Not implementation approval, not verification, not an approved course deliverable until E/team assembly and instructor reconciliation. Complements the D2 artifacts under `docs/architecture/`.

- Selection: **C2 — input-service + immutable `RunContext` boundary with a small lifecycle coordinator**, chosen by Brian (human) on 2026-11-12 based on **estimated** tradeoffs, not verified superiority. Preserved unchanged; no new candidate generation.
- Target baseline: TradingAgents **v0.7.1** (`tradingagents/__init__.py:3`, `pyproject.toml`).
- Working scope: `docs/req/selected-requirements.md` (`SEL-TA-FR-001..007`, `SEL-TA-NFR-001..006`, `SEL-TA-GOV-001..006`) remains the historical working selection that underlies the implemented C2 design and C's tests. The **current** registry is `docs/req/requirements.yaml`: **36 active entries, 3 withdrawn, `schema_version: 1.2.0`, `status: proposed_for_adoption`** — it includes `REQ-TA-INV-014` (immutable input) and `REQ-TA-GOV-004` (schema validation). It is still **proposed** (not adopted); see §1.4 and `docs/architecture/traceability-inputs-member-b.md`.
- Location convention (interim, pending course/instructor decision): this root file is canonical; `docs/architecture/architecture-blueprint.md` is a pointer only. One canonical blueprint is maintained here.

> Honesty statement: This document specifies architecture and testability, and records which parts the current checkout implements. Implementation links point at real source paths; independent acceptance (C) and enforcement (E) remain their owners'. Proposed obligations (broader `REQ-TA-*` extensions) are labelled **PROPOSED / NOT IMPLEMENTED** and are not claimed satisfied. Estimates are labelled **ESTIMATE**. Retained evidence is cited by path but not re-run here.

---

## 1. Scope and drivers

### 1.1 Scope
Extend the existing terminal UI (`cli/`), the Python/LangGraph workflow (`tradingagents/`), the portfolio loader (`tradingagents/portfolio.py`) and the Markdown/HTML reports (`tradingagents/reporting.py`, `tradingagents/report_html.py`) so a run can be performed in one of two input modes:

- `NO_PORTFOLIO` — the caller's holdings/cash are unknown; nothing is assumed.
- `PORTFOLIO_PROVIDED` — an explicitly selected, validated, frozen snapshot supplied by the user.

Both modes yield an auditable result with deterministic input provenance and a deterministic output check.

### 1.2 Drivers
| Driver | Source |
|---|---|
| Optional, explicitly confirmed holdings input | selected-requirements §1; Brian decision |
| No silent portfolio fallback; no invented zero holdings/cash | FR-003/004, NFR-001 |
| Deterministic check authority (model cannot override) | FR-007 |
| Frozen input provenance in every report | FR-006 |
| Secret/holdings privacy across sinks | NFR-003 |
| Reusable boundary without terminal prompts in engine/agents | NFR-005 |
| Reliable external-failure handling | NFR-001 |
| Structured observability | NFR-002 |
| Cohesive integration preserving upstream | NFR-005 |

### 1.3 Explicit non-goals (deferred; do not claim satisfied)
Web GUI; broker connection/order execution; exposure certification; automatic broker discovery; full twelve-channel evidence registry; new historical filtering/freshness rules; global source-confidence grades; R4–R6 sentiment correction; resume/checkpoint redesign; aggregate time/token/call budgets; debate convergence; analyst plugin redesign. (selected-requirements §5.)

### 1.4 Authority of current selection vs open decisions

Three requirement states are kept distinct and are **never** merged by numeric suffix:

1. **Working/historical baseline — `SEL-TA-*`** (`docs/req/selected-requirements.md`, 19 IDs). It authorized this architecture exploration and underlies C's existing tests. It is **not** the complete adopted D1 registry; it does **not** by itself cover the course-required performance/cost/governance/security types.
2. **Current registry — `REQ-TA-*`** (`docs/req/requirements.yaml`, relocated under `docs/req/`; `schema_version: 1.2.0`, `status: proposed_for_adoption`; **36 active entries, 3 withdrawn**). It **contains** `REQ-TA-INV-014` (immutable input) and `REQ-TA-GOV-004` (schema validation), both `status: proposed` (present and resolvable, not adopted). It remains **proposed**, not the adopted D1; the meaning crosswalk is in `docs/architecture/traceability-inputs-member-b.md`.
3. **As-built** — what `a62b801` implements. Verified against source in this revision; links below.

- **Approved working input (implemented, use directly):** CLI-only UI; `PORTFOLIO_DIR=<project-root>/portfolios`; `--without-portfolio`; `--portfolio-as-of`; consent behaviour; full normalized-content SHA-256 (64-char) fingerprint.
- **Implemented optional portfolio (keep):** the system supports `NO_PORTFOLIO` and an explicitly confirmed `PORTFOLIO_PROVIDED` snapshot, including an explicitly empty (flat) book. The current registry's scope statement now **includes optional portfolio input** (profiles A-A/A-B/A-C), consistent with the implemented flow; the confirmation-flow ownership remains open (OQ-16). Missing data is not an empty account; explicit empty input is valid and need not force Hold; user holdings are unverified context, not a broker account or executable instruction.
- **Open (not B's to close; do not invent):** final D1 **adoption** of the 36-entry registry (which already contains `REQ-TA-INV-014` and `REQ-TA-GOV-004`, both `status: proposed`) (A); confirmation-flow ownership (OQ-16); semantic rubric/threshold (`SEL-TA-GOV-004`, C/A/D/E); instructor-accepted source/test layout and transcript wording (E); **OpenCode per-role permission enforcement and merge-protection administrative confirmation (E)**; blueprint location final convention (E).
- **Schema CI gate — implemented and verified (not open):** `REQ-TA-GOV-004` / `SEL-TA-GOV-002` (schema validation) now has a real CI job `requirements schema` (`.github/workflows/ci.yml`) running `scripts/ci/check_requirement_schema.py` (wrapping A's `docs/req/validate.py`) plus `tests/member_d_verification/test_requirement_schema_gate.py`. Local/hosted verification and E-reported merge-protection activation are recorded in `docs/architecture/traceability-inputs-member-b.md`; this is **not** a claim of adoption or that other governance gaps are closed. (`SEL-TA-GOV-004` = semantic evaluation, `REQ-TA-GOV-001` — a different gate.)

### 1.5 Implemented now versus proposed (broader `REQ-TA-*`)

The broader uploaded promotion proposes obligations the current checkout does **not** implement. They are documented here as **PROPOSED / NOT IMPLEMENTED** so planned impact is visible without overclaiming. Authoritative as-built detail is `docs/architecture/interface-contracts.md` §12 and `docs/architecture/runtime-policy-catalog.md`.

| Subject | As-built at `a62b801` (verified) | Proposed (`REQ-TA-*`) — **not implemented** |
|---|---|---|
| Output check rules | **Q1–Q4** only (`runapi/checks.py`): Q1 rating readable, Q2 provenance matches trusted metadata, Q3 disclaimer present, Q4 no prohibited guarantee phrase. Findings are **`BLOCKING` only**; `PASSED` requires **empty** findings (`result.py`). | **R1–R8** (`REQ-TA-ARCH-002`): adds evidence-ID resolution (R2), ownership-phrase block (R3), sentiment band/confidence/coverage (R4–R6), coverage-section equality (R7). R1≈Q1, R8≈Q3/Q4; R2 has no enforcing component; R4–R7 inspect fields the checker ignores. |
| Stop-reason vocabulary | Five: `MODEL_FAILURE`, `DATA_FAILURE`, `INTERNAL_ERROR`, `PERSISTENCE_ERROR`, `INTERRUPTED` (`runapi/result.py:12-14`). | **Adds `BUDGET`** (six) plus a run-wide single-use call-reservation controller (`REQ-TA-RUN-001`, `REQ-TA-NFR-COST-002`). Adding an enum value breaks every existing reader unless updated. |
| Corrected findings | `Finding.status` is only `BLOCKING`; `CheckResult(PASSED)` rejects findings. | **R5** would permit **corrected-only** findings with `PASSED` — a coordinated result-contract extension (`Finding`/`CheckResult`/report/scorer) if retained. |
| Evidence/coverage registries | Input provenance only (`INV-04/05/05b`); no per-citation evidence registry, no per-run `data_coverage` record. | `REQ-TA-FR-001` evidence IDs; `REQ-TA-FR-005` twelve-channel coverage + `NOT_REQUESTED`; `REQ-TA-INV-002/007`. |
| Aggregate budgets, resume identity | Per-call `max_tokens`; each fresh invocation gets a fresh `run_id` (`INV-12`); no resume. | `REQ-TA-NFR-PERF-002`/`COST-001`/`COST-002` budgets; D-5 resume keeps `run_id` and appends attempts — **conflicts** with `INV-11/INV-12` and is an open contract change (OQ-8). |

**Concise intermediate context is a separate axis (integrated at `adb4dfc`, PR #18 — not a `REQ-TA-*` obligation; dangling-reference boundary and quality/approval remain open).** It is advisory output guidance + an exact-substring reference + a compaction safeguard (blueprint §5 step 6; runtime catalog R22). It introduces **no new forced truncation** and is **distinct from** both (i) the existing per-prompt character/4 guard (`bound_agent_prompt`) and (ii) the proposed run-wide `CALL_CAP`/`BUDGET` controller (ADR-002 D3, unimplemented). **Observed token savings do not satisfy `REQ-TA-NFR-COST-002` and do not implement Slice C**; no aggregate budget guarantee is introduced. A **separate proposed** cumulative-*token* admission design (`REQ-TA-NFR-COST-001`, interface-contracts §15A, ADR-004 Alt-B, catalog R23/R24) sits beside the call cap and is likewise **not implemented**.

Implementing any row above is a design + D implementation change requiring C's approved tests and E's gates; it is **not** satisfied by the working `SEL-TA-*` tests or this documentation revision.

---

## 2. System and deployment boundaries

- **Runtime:** a single local Python process. The user interacts through the terminal (the existing CLI). No network is required for input selection/validation; network/provider calls occur only inside the graph after confirmation.
- **Requested interface:** current CLI (`cli/main.py`), extended with input-mode flags. This is the only new user-facing surface; no new web application.
- **Baseline preserved:** `tradingagents/`, `cli/`, `pyproject.toml` and existing tests are preserved. The extension is discovery, explicit consent, frozen provenance and coherent reporting (Prompt.md "Session objective and input precedence" / "Access and output boundaries").
- **Trust boundary for data:** user-supplied portfolio files are *context*, never verified account facts. The trusted state used to build provenance is the frozen snapshot produced by the input service, not model text and not re-read file bytes.

### 2.1 Data-flow (C2)
```
terminal user
   │  (interactive, or flags)
   ▼
CLI adapter (cli/main.py)  ──►  PortfolioInputService (discover → validate/precheck → freeze)
   │                                         │
   │                                         ▼
   │                              RunContext (deeply immutable)
   │             frozen snapshot + mode + full-64 fingerprint + as-of + disclosure flags
   │                                         │
   │   [notice shown; consent gate]
   │                                         │
   ▼                                         ▼
runapi/execution.run_analysis_api  ── consent confirmed ──►  engine.stream_run
   │  (CLI single-run orchestration, no LLM)         (portfolio=None | frozen snapshot)
   │                                         │
   │                                         ▼
   │                     runapi/checks.py OutputChecker (non-LLM, authoritative)
   │                                         │
   │                                         ▼
   │                  runapi/finalize.py OutcomeFinalizer (COMPLETED|INCOMPLETE)
   │                                         │
   ▼                                         ▼
Artifact boundary (redaction + run-ID isolation)  →  report(MD/HTML), manifest, JSONL events, logs, state JSON
```

---

## 3. Components

Concrete module paths are in `docs/architecture/interface-contracts.md` §1 (B3-10). The `tradingagents/runapi/` modules and `cli/input_ui.py` **exist in the current checkout** (verified); the "Status" column records that. Reusable noninteractive services live under `tradingagents/runapi/` and must not import `cli`.

| Component | Responsibility | Where (verified path) | Status vs baseline |
|---|---|---|---|
| **Shared execution service** | **Common application entry** `run_analysis_api(RunContext, …)`: consent check → run → render → check → finalize → stage/publish → terminal event. Prompt-free; used by CLI and supported API. | `tradingagents/runapi/execution.py` | present (additive) |
| `PortfolioInputService` | Noninteractive discovery/precheck/freeze; **sole** discoverer/validator; prompt-free. | `tradingagents/runapi/input_service.py` | present (additive) |
| `RunContext` / `FrozenSnapshot` (deeply immutable) | Frozen value tuples + mode + full-64 fingerprint + as-of/basis + consent_state; read-only provenance source. | `tradingagents/runapi/context.py` | present (additive) |
| `OutputChecker` | Deterministic **Q1–Q4** on the checked **body**; assigns `output_check` + findings. Authoritative, non-LLM. | `tradingagents/runapi/checks.py` | present (additive) |
| `OutcomeFinalizer` | Maps graph return/exceptions/attempted critical-persistence failure to `run_outcome` + `stop_reason`. | `tradingagents/runapi/finalize.py` | present (additive) |
| `Redactor` | Central masking (keys/tokens/bearer, unsafe diagnostics) at every sink, including `agents/structured.py` warnings (R1 repair). | `tradingagents/runapi/redact.py` | present (additive) |
| `EventSink` (JSONL) | Fixed-field structured events; stage-private tentative terminal. | `tradingagents/runapi/events.py` | present (additive) |
| Persistence/Manifest | Staging (report+manifest **critical**; terminal event **best-effort**) → single atomic directory commit; manifest via `SafeRunMetadata`; `terminal_event.durable` decided pre-commit without blocking publication. | `tradingagents/runapi/persist.py` | present (additive) |
| Result schemas | `RunResult`, `CheckResult`, `Finding`, `InputError`, `RunRecord`, `summarize_records`. | `tradingagents/runapi/result.py` | present (additive) |
| CLI input UI | Interactive discovery/consent **only** here. | `cli/input_ui.py` | present (additive) |
| CLI adapter | Thin wiring; adds `--without-portfolio`, `--portfolio-as-of`; suppresses prompts under flags. | `cli/main.py` | adapted |
| Prompt/context semantics | Mode-aware rating-scale legend; no-portfolio Hold meaning; user-supplied/unverified wording. | `tradingagents/agents/context.py`, manager/trader prompts | adapted |
| Concise intermediate context *(integrated at `adb4dfc`)* | Advisory evidence-first brevity guidance (`concise_analysis_instruction`); exact-substring opponent reference (`opponent_argument_or_opening(...,history)`); compaction safeguard restoring explicit copies before `bound_agent_prompt` (`bound_debate_prompt`); `concise_intermediate_reports` switch. No new forced truncation, summarizer, tool-payload limiter, role/round change. | `tradingagents/agents/context.py`, `agents/analysts/turn.py`, `agents/researchers/*_researcher.py`, `agents/risk_mgmt/*_debator.py`; config in `default_config.py`, `graph/trading_graph.py`, `runapi/execution.py` — integrated via PR #18 (merge `adb4dfc`, ancestor of current HEAD) | present on main (integrated); dangling-reference boundary/quality/approval open |
| Reporting boundary | Renders checked **body** + trusted **envelope header** from `SafeRunMetadata`; stage labels `build_envelope`/`verify_envelope_header_matches`. | `tradingagents/runapi/reporting.py`, `tradingagents/reporting.py`, `tradingagents/report_html.py` | adapted |
| Existing loader/model | `PortfolioContext`/`Position` validation and rendering; alias matching. | `tradingagents/portfolio.py` (preserved) | unchanged semantics |
| Raw engine primitive | `TradingAgentsGraph.propagate/stream_run/create_run_state` signature preserved; **does not** traverse the boundary (reduced scope, A approval for product use). | `tradingagents/graph/trading_graph.py` | signature preserved |

---

## 4. Advisory versus authoritative data

| Data | Nature | Authority |
|---|---|---|
| Model narrative, ratings text, recommendations | **Advisory** | Cannot set `output_check`/`run_outcome`/provenance |
| Final rating (Buy/Overweight/Hold/Underweight/Sell/REVIEW) | Derived deterministically from the PM output | Reported, but check Q1 only *reads* readability |
| Frozen snapshot metadata (mode, basename, fingerprint, as-of) | **Authoritative** (trusted state) | Built by input service; used by header/result/check |
| `output_check` (PASSED/NEEDS_REVIEW/NOT_RUN) + findings | **Authoritative** (deterministic) | `OutputChecker` only |
| `run_outcome` (COMPLETED/INCOMPLETE) + `stop_reason` | **Authoritative** (deterministic) | `OutcomeFinalizer` only |

The disclaimer and no-portfolio notice are **frozen strings** (selected-requirements §1) and are treated as trusted content, excluded from Q4 phrase scanning.

---

## 5. Workflow (selected C2)

1. **Discover** eligible `.json` files (non-recursive, sorted, symlinks excluded) from `PORTFOLIO_DIR` — or accept explicit `--portfolio PATH` (outside dir allowed; parent not scanned).
2. **Select** one file, or choose no-portfolio, or cancel.
3. **Validate/precheck** the frozen bytes; reuse upstream model validation after explicit shape/type/as-of prechecks. Empty positions is valid (flat); no silent fallback.
4. **Freeze** → `RunContext` (deeply immutable value tuples; full-64 canonical fingerprint; as-of/basis recorded). Consent state `FROZEN`.
5. **Notice** (portfolio mode; §6) then **confirm** → `CONFIRMED` (default No). Non-interactive: valid flags are the consent expression.
6. **Run / analysis execution** via the **shared execution service** (`runapi/execution.py`): rejects any `RunContext` not `CONFIRMED`; holdings reach the provider **only after** confirmation. Within this analysis-execution stage (not rendering/publication):
   - **Intermediate context generation.** When `concise_intermediate_reports` is enabled, analysts and Bull/Bear/risk debaters receive **advisory** evidence-first brevity guidance (`concise_analysis_instruction`; ~450 words analysts, ~220 debates). **Placement:** in `analysts/turn.py` the guidance is appended to the **assembled system message** (tool-bound and wrap-up paths, preserving tool schemas/call IDs/messages); in the Bull/Bear researchers and three risk debaters it is appended to their **assembled prompt strings**. The guidance is **advisory** (subordinate to evidence/disclosures), not a hard output cap. This feature introduces **no new forced output/tool-payload truncation**; the existing per-prompt guard (`bound_agent_prompt`, character/4 estimate) can still trim narrative when a large assembled prompt exceeds its limit.
   - **Reference substitution (deterministic).** When an opponent's exact stripped latest argument already occurs in debate history, a reference replaces the duplicate copy (`opponent_argument_or_opening(...,history)`); an empty opponent keeps an explicit opening notice. This is **exact Python string-substring matching**, not semantic deduplication.
   - **Compaction safeguard (deterministic branch).** `bound_debate_prompt` reconstructs the explicit copies and, if the reconstructed-original length would exceed `min(context_cap_tokens, compaction_threshold_tokens) * 4`, passes the restored form to the existing `bound_agent_prompt` guard (else the reference form). This reduces but does **not** eliminate dangling-reference risk: a short argument can be replaced by a longer reference notice, so a reference form longer than the restored original can still be compacted (probe `docs/reviews/evidence/token-context-reference-probe-2026-11-24.json`). Restoring copies before the guard is **not** a guarantee that every evidence item survives compaction.
   - **Trusted portfolio facts** and all final provenance/check/publication authority below are unchanged; prompt instructions are not deterministic semantic enforcement.
   - **Separate from budgets:** this is neither the existing per-prompt character/4 guard nor the proposed run-wide `CALL_CAP`/`BUDGET` controller (ADR-002 D3, unimplemented).
   - **Status:** **integrated at `adb4dfc` (PR #18, ancestor of current HEAD `5672a79`)**; the dangling-reference boundary, quality acceptance and prior approval remain **open**. Switch `concise_intermediate_reports` (default True; `TRADINGAGENTS_CONCISE_INTERMEDIATE_REPORTS=false` or programmatic False restores legacy).
7. **Render body → scrub → single check (Q1–Q4; Q2 inspects the pre-check provenance fragment against explicit trusted metadata) → finalize → build trusted envelope → stage report+manifest (critical) → one atomic directory commit; terminal JSONL append is best-effort.** Incomplete runs bypass the checker and get `NOT_RUN`. The checked body is delivered unchanged; the envelope adds only trusted metadata. Terminal-event durability is decided before the manifest is staged but does not block publication; a terminal-append failure preserves the logical outcome and records `durable=false`. (§ interface-contracts §6–§7).
8. Pre-run cancellation/rejection starts **no graph, zero LLM calls, no completed run**; a critical persistence failure yields a typed INCOMPLETE result that never contradicts a returned success.

Detailed state machine, schemas, canonicalization, ordering and failure simulations: `docs/architecture/interface-contracts.md`.

### 5.1 Synthetic input-mode walkthrough (document example, not a passing test)
- **Interactive, portfolio:** user sees `a.json`, `b.json`; selects `b.json`; precheck passes; freezes `b` (fingerprint Fb); notice shows basename `b.json`, date D, as-of basis, provider-transmission statement; user answers Yes → `CONFIRMED`; run transmits frozen `b` after consent; report header carries Fb and mode `PORTFOLIO_PROVIDED`.
- **Interactive, no portfolio:** empty directory → no-portfolio confirmation with frozen notice; Yes → `CONFIRMED` with `portfolio=None`; header shows `NO_PORTFOLIO`, null file/fingerprint/as-of.
- **Noninteractive:** `--portfolio b.json --portfolio-as-of D` → freezes b, consent via flags, no prompt. `--without-portfolio` → `NO_PORTFOLIO`. Neither/both → `InputError`, zero calls.
- **Cancelled:** user answers No at consent → zero graph/LLM, no completed run, counted as a pre-run attempt (NFR-006).

---

## 6. Permissions and consent

- Interactive discovery/selection/consent lives **only** in the CLI (`cli/`). Agents and the engine never prompt.
- **Consent gate** is an explicit coordinator transition between freeze and run. A frozen snapshot is a *candidate input*, **not** a confirmed selection; immutability alone does **not** prevent bypass. Only a coordinator transition to `CONFIRMED` permits run entry (see interface-contracts §4, ADR §Consent).
- Mandatory execution, exception mapping, checks and artifact finalization sit behind a **shared application boundary** (`tradingagents/runapi/execution.py: run_analysis_api`) usable without terminal prompts. The upstream Python API signature is **preserved**; the supported project API routes through `run_analysis_api` (full requirement coverage). A raw low-level engine primitive (`TradingAgentsGraph.propagate/stream_run`) remains available but **does not** traverse the boundary and **does not** satisfy FR-006/FR-007/NFR-002/003/004; its scope is declared and product reliance requires **A's approval** (residual risk R-API, pending A). See `docs/architecture/interface-contracts.md` §5.
- Coding-agent file permissions (separate concern) are in `docs/architecture/permission-model.md`; E implements enforcement.

---

## 7. Observability

- New lifecycle event sink: UTF-8 JSONL; fixed fields `run_id, ticker, node, ts(UTC), elapsed_ms, event, event_outcome`. Console stays human-readable. Raw provider payload logging disabled by default. Progress vocabulary is separate from terminal `run_outcome`.
- Existing sinks are adapted, not silently trusted: see memory-design §Sinks and runtime-policy-catalog.

---

## 8. Verification strategy and current evidence (design-level only)

- **Testability seams** (for C): `PortfolioInputService` (discover/validate/freeze), `RunContext` identity, `OutputChecker` (Q1–Q4 with injected model claims), `OutcomeFinalizer` (typed exceptions), redaction at each sink, manifest atomicity, same-date isolation.
- **Real test definitions now exist** under `tests/member_c_verification/offline/` (C-owned), mapping to the working selection: `test_fr001_discovery.py`, `test_fr002_consent.py`, `test_fr003_validation_freeze.py`, `test_fr004_propagation.py`, `test_fr005_ratings.py`, `test_fr006_provenance.py`, `test_fr007_output_check.py`, `test_nfr001_failures.py`, `test_nfr002_events.py`, `test_nfr003_privacy.py`, `test_nfr004_persistence.py`, `test_nfr005_layering.py`, `test_nfr006_population.py`. B **links** these; B does not own, run or certify them.
- **Developer/remediation tests** under `tests/member_b_remediation/` (R1–R5 probes) and `tests/member_d_verification/` are diagnostic regression material; they are not independent acceptance.
- **Retained evidence** is cited by path and **not re-run here** (see `docs/architecture/traceability-inputs-member-b.md`): `docs/reviews/evidence/live-verification-2026-11-21/` (fresh five-case/two-trial live cohort; all 15 deduplicated attempts `COMPLETED`), `docs/reviews/evidence/live-diagnostic-2026-11-18.json`, and the 24 November integration review. Historical formal **PASS remains unverified**; independent current semantic acceptance remains **pending (C)**.
- **Distinction preserved:** a test *definition* existing ≠ passing; a developer diagnostic ≠ acceptance; a fresh live run ≠ formal acceptance under open `N_EVAL`/threshold parameters.
- **Document consistency checks** (this revision) are **not** application verification.

Verification links per requirement are in `docs/architecture/traceability-inputs-member-b.md`; C owns the verdict.

---

## 8A. Engineering contributions (project-specific design)

This section states the team's concrete engineering contributions honestly. The individual mechanisms are **standard software-engineering techniques** (immutability, content hashing, atomic directory replacement, append-before-dispatch ledgers, fail-closed checks). We do **not** claim to have invented them, and a standard technique's use does not by itself establish originality. The contribution is the **problem-specific design, its adaptation across the existing TradingAgents pipeline, and the demonstrated effect** in this application; the professor assesses originality. Each item separates what is **deterministically enforced** from what depends on **model compliance** (pending semantic acceptance).

### 8A.1 Protected portfolio facts across Research Manager, Trader and Portfolio Manager

- **Concrete problem.** In the baseline the portfolio block reached some decision stages unevenly. A real observed failure (2026-11-18, F9) showed an explicit-empty `PortfolioContext(positions=[])` run completing with deterministic check `PASSED` while the Trader/Portfolio-Manager narrative still spoke of "reducing/retaining existing exposure" — an unsupported account claim. Downstream stages could also inherit an ownership premise asserted upstream (the Research Manager's investment plan) without access to the same supplied facts.
- **Design decision.** Route the same protected portfolio block through a single helper, `get_portfolio_context_from_state` (`tradingagents/agents/context.py:214`), into **all three** decision stages — Research Manager, Trader, Portfolio Manager — and wrap it in `<protected_context>…</protected_context>` (`protect_context`, `context.py:271`) so context compaction cannot drop it. Absent input yields an explicit "no account ownership is assumed / unknown, not flat" notice; explicit-empty carries a no-nonzero-target instruction; a held book carries the supplied quantity. The stage instruction tells the model to correct conflicting upstream ownership premises (R4). The five research ratings and three Trader actions are unchanged; no rating is forced.
- **Baseline/team change.** Bounded R4 repair (2026-11-21): equalized the block across all three stages and added the corrective instruction. It is a prompt-grounding change, **not** a new authoritative check.
- **Tradeoff.** Prompt text grows slightly and each stage must be kept consistent; grounding reduces but cannot eliminate unsupported narrative. A deterministic ownership check would be a larger change the current Q1–Q4 checker deliberately does not make.
- **Implementation status.** **Implemented** (R4). **Deterministically enforced:** the trusted facts are delivered to all three stages and survive compaction (prompt-capture tests). **Not enforced deterministically:** that the model's prose never asserts an unsupported position — that is assessed semantically (pending C, GOV-004).
- **Links.** Tests: `tests/member_b_remediation/test_r4_research_manager_context.py` (RM/Trader/PM prompt distinction, shared facts, user-supplied/unverified label surviving compaction, absent≠flat); C seams `tests/member_c_verification/offline/test_fr004_propagation.py`, `test_fr005_ratings.py`. Source: `tradingagents/agents/managers/research_manager.py:27-52`, `portfolio_manager.py:30-51`, `trader/trader.py:34,82-93`, `context.py:214-273`. Evidence: `docs/reviews/evidence/live-diagnostic-2026-11-18.json`; `docs/reviews/remediation-r1-r5-2026-11-21.md`.
- **Residual limitation.** Prompts cannot guarantee every future narrative; Q1–Q4 does not inspect ownership wording. The concrete demonstration is the **explicit-empty → upstream RM trim error the downstream stages corrected → protected-context repair → fresh RM/Trader/PM prompt evidence** thread recorded in the remediation review (retained diagnostics, not a new experiment run here).

### 8A.2 Separation of model advice from authoritative provenance/check results (truthful publication and failure handling)

- **Concrete problem.** Model narrative, ratings text and any self-claimed "OUTPUT CHECK: PASSED" are advisory but can be mistaken for authoritative state; and a run can claim success while its artifacts failed to publish, or leave a caller-visible COMPLETED terminal for an unpublished run.
- **Design decision.** Advisory model output is separated from authoritative, deterministic state:
  - **Provenance** is built only from the frozen `RunContext` and a full 64-char SHA-256 over canonical JSON bytes (`runapi/context.py`), never re-read from the file or `final_state`.
  - **Check authority** lives in one non-LLM `OutputChecker` (Q1–Q4); model text cannot set or override `output_check` (`runapi/checks.py`, `test_fr007_output_check.py::test_tc_fr007_c_model_claim_cannot_override`).
  - **Outcome** is decided by `OutcomeFinalizer` from typed exceptions (`runapi/finalize.py`).
  - **Truthful publication:** report+manifest are **critical** and published by a **single atomic directory rename**; the JSONL terminal event is **best-effort** and its real durability is recorded as `terminal_event.durable` before the immutable manifest is staged (`runapi/persist.py:130-157`). A critical staging/commit failure returns `INCOMPLETE/PERSISTENCE_ERROR` with no artifact promise. A tentative terminal is staged privately and revealed only after the commit; a post-commit callback failure cannot revise a published COMPLETED result (R5).
- **Baseline/team change.** Bounded R5 repair plus the C2 boundary (`runapi/` modules). These separate advisory from authoritative status and make publication truthfully conditional.
- **Tradeoff.** More modules and a staging directory; best-effort events mean a run can publish with `durable=false` (stated, not hidden). Not a power-loss durability guarantee.
- **Implementation status.** **Implemented** (Q1–Q4 + R5). **Deterministically enforced:** check authority, provenance identity, conditional result fields, single-commit publication, truthful `durable`. **Residual:** the checker only covers Q1–Q4, not factual accuracy; terminal append remains best-effort.
- **Links.** Tests: `tests/member_b_remediation/test_r5_terminal_visibility.py` (rename-failure exposes INCOMPLETE only, manifest-write consistency, terminal-append keeps logical outcome, tentative not exposed pre-commit, single terminal); C seams `tests/member_c_verification/offline/test_fr006_provenance.py`, `test_fr007_output_check.py`, `test_nfr004_persistence.py`, `test_nfr002_events.py`. Source: `runapi/checks.py`, `runapi/finalize.py`, `runapi/persist.py`, `runapi/events.py`, `runapi/reporting.py`. Evidence: `docs/reviews/remediation-r1-r5-2026-11-21.md`.
- **Residual limitation.** Q1–Q4 certifies only its named rules, not truth or account suitability; publication durability is cooperative, not power-loss-proof. Demonstration: the **publication-failure / counterfeit-terminal negatives** in `test_r5_terminal_visibility.py` (offline regression material, not a new live run).

### 8A.3 Evaluation-evidence integrity (case/config/artifact correspondence, counterfeit rejection, unsuccessful-attempt accounting)
- **Concrete problem.** A semantic score is only meaningful if each result is bound to the case, configuration and artifact it claims to have come from; a forged or mismatched artifact could otherwise pass, and silently dropping failed or incomplete attempts could inflate completion/quality.
- **Design decision.** The live scorer/harness (`tests/member_c_verification/live/`) enforces the points below. **Provenance, by verified commit (roles only):** the evaluator originated as Member C's supplied tooling (`f66fc14`, `57b164c`, `b8c4a25`); it was subsequently hardened (`bb777d5`); the R2/R3 correspondence/counterfeit-replay repairs and the `tests/member_b_remediation/` regression tests were made in the supervised OpenCode repair session under a Brian-approved plan (`56bbe29`). `replay_store.py` was introduced in `56bbe29`, **not** with the original evaluator. A commit records submitted changes; it does **not** by itself prove who manually authored the code. C's **independent acceptance remains pending**. The points it enforces:
  - **Correspondence:** per case, the trusted `(input_mode, basename, fingerprint, as-of, kind)` is derived from the authoritative case definitions (`score_gov004.py::expected_case_identity`) and compared to the manifest; tier-provider settings must match the fixed configuration (`_tier_providers_match_fixed`); case/config/provenance/result and hash checks bind each report to its record.
  - **Counterfeit rejection:** conflicting mirror copies and bare authoritative metadata lines outside the header block are rejected (`_reject_counterfeit_metadata_outside_header`; canonical-record equality for durability mirrors).
  - **Unsuccessful-attempt accounting:** `replay_store.claim_start` records an exclusive, durable STARTED before dispatch under a cross-process lock; an unresolved start stays a non-completed denominator entry and blocks ID reuse; the scorer reports all started/completed attempts and separates retries.
- **Baseline/team change.** Verification-tooling changes (R2/R3) in the supervised OpenCode repair session on C's evaluator (origin/hardening/repair by commit per above). The application product code is not the evaluator; the ledger and scorer are verification governance.
- **Tradeoff.** Binding and duplicate-detection add complexity and refuse convenience shortcuts (e.g., reusing a run ID, or substituting a held-target artifact for an empty case); a stricter scorer can fail an otherwise "good-looking" package.
- **Implementation status.** **Implemented** as verification tooling: original evaluator (C), hardening (`bb777d5`), R2/R3 repairs/regressions (`56bbe29`). **Deterministically enforced:** case/config/artifact binding, counterfeit rejection, exclusive durable starts, all-start accounting. **Residual:** the scorer cannot authenticate a human reviewer or decide general financial truth; the human score sheet is intentionally unfilled and **C's independent acceptance is pending**.
- **Links.** Tests: `tests/member_b_remediation/test_r2_scorer_correspondence.py`, `test_r2_r3_differential_pins.py`, `test_r3_replay_durability.py` (durable-before-dispatch, later-failure retention, unresolved start stays non-completed, exclusive same-ID claim); C harness `tests/member_c_verification/live/test_score_gov004_exitcodes.py` (PASS/FAIL/PENDING exit codes), `test_harness_selfcheck.py`. Source: `tests/member_c_verification/live/score_gov004.py`, `replay_store.py`. Evidence: `docs/reviews/evidence/live-verification-2026-11-21/` (`gov004_starts.json`, `cohort.json`, `ai-review-proposed-scores.json`, `rescore-results.json`, `integrity.json`).
- **Residual limitation.** The retained cohort used a narrow rubric that does **not** test general financial arithmetic; the AI-proposed 28/28 is a proposal, not C acceptance. Demonstration: the **retained live package** is re-scored from the repository; the scorer reports `PENDING` until a real reviewer supplies the score sheet, while a counterfeit/substituted artifact fails (`test_r2_02_held_target_substituted_for_empty_case_fails`, `test_r2_03_*`, `test_r3_04_unresolved_start_stays_noncompleted_and_blocks_reuse`).

### 8A.3a Concise intermediate context: a reversible cost/evidence tradeoff *(integrated at `adb4dfc`)*

- **Concrete problem.** Verbose intermediate analyst reports are re-read by downstream agents, and debate prompts carried both the full history and a separate copy of the opponent's latest argument — the same evidence sent twice. The existing character/4 prompt guard bounded very large prompts but did not address this sub-threshold repetition.
- **Design decision (feature `9102759`).** Advisory evidence-first brevity guidance (~450-word analysts, ~220-word Bull/Bear/risk): in `analysts/turn.py` appended to the **assembled system message**, in Bull/Bear/risk appended to their **assembled prompt strings**. Deterministic replacement of a duplicated opponent argument by a reference **only when the exact stripped text occurs in history** (**exact Python string-substring matching**); and a compaction safeguard that reconstructs the explicit copies and, if the reconstructed-original length exceeds `min(context_cap_tokens, compaction_threshold_tokens)*4`, passes the restored form to the existing guard. **No unconditional no-dangling guarantee:** a short argument can be replaced by a longer reference notice, so the reference form can exceed the guard target even when the restored original fits, and checking only the restored-original length can miss compaction of the reference form (probe `docs/reviews/evidence/token-context-reference-probe-2026-11-24.json`). Reversible via `concise_intermediate_reports` (default True; env/programmatic False restores legacy).
- **Deterministic vs advisory.** Flag/metadata plumbing, the exact-string reference, and the reconstruct-then-guard branch are deterministic; the word targets and evidence-preservation wording are **advisory** prompt guidance. **No new forced output/tool-payload truncation** is introduced (the existing guard may still trim narrative); it is not a guarantee that every evidence item survives compaction.
- **Kept separate.** Not the existing per-prompt guard; not the proposed Slice C `CALL_CAP`/`BUDGET` controller (ADR-002 D3, unimplemented). Observed savings do not satisfy `REQ-TA-NFR-COST-002`.
- **Tradeoff.** Shorter intermediate context can omit nuance the model would otherwise restate; the reference depends on exact text presence (no semantic dedup). Reversible configuration bounds the risk.
- **Implementation status.** **Integrated at `adb4dfc` (PR #18 merge; ancestor of current HEAD `5672a79`).** The dangling-reference boundary (probe `docs/reviews/evidence/token-context-reference-probe-2026-11-24.json`), independent quality acceptance and prior approval remain **open**. Source changes touch files included in `prompt_hash`, so new-run `prompt_hash` differs; mode is recorded separately in `EffectiveConfig`.
- **Measurements (E-reported; not rerun here).** Optimized 99,532 / 103,120 / 110,725 tokens (mean 104,459) vs historical mean 138,896.5 (24.7936%) and a same-day one-sample control 160,826 (35.0484%); single NVDA/2026-01-09 case, four analysts, English, 1+1 rounds, school `openai_compatible` + DeepSeek V4 Flash, empty memory, no portfolio, caching; exclusions and a failed attempt disclosed; **no ablation**, **no universal/runtime/quality claim**. Benchmark uses raw `graph.run_transient`, not `run_analysis_api`; `COMPLETED` is not product/check/semantic acceptance. Supervising review reproduced **49 offline tests** (not E's 1,797 full suite).
- **Links.** Feature source (immutable): [`context.py`@9102759](https://github.com/kelepawuqiusi/CS5351/blob/9102759caaa59d778ba49cd57a1306f5f2ee5d88/tradingagents/agents/context.py), [`turn.py`@9102759](https://github.com/kelepawuqiusi/CS5351/blob/9102759caaa59d778ba49cd57a1306f5f2ee5d88/tradingagents/agents/analysts/turn.py), [test_token_input_reduction.py@9102759](https://github.com/kelepawuqiusi/CS5351/blob/9102759caaa59d778ba49cd57a1306f5f2ee5d88/tests/member_d_verification/test_token_input_reduction.py), [PR #18](https://github.com/kelepawuqiusi/CS5351/pull/18). Local review: `docs/reviews/token-context-architecture-review-2026-11-24.md`, `docs/reviews/evidence/token-context-review-2026-11-24.json`, `docs/reviews/evidence/token-context-pr-checks-2026-11-24.json`. Decision: `docs/architecture/adr/003-concise-intermediate-context.md`.
- **Residual limitation.** One case, no ablation, artifacts (report/measurement JSON) not uploaded; semantic quality and independent C acceptance remain pending.

### 8A.4 Demonstration types and originality claim

Three distinct deliverables use this material; they are not interchangeable:

- **Video — product demonstration.** Shows before/after behaviour (e.g., optional/empty portfolio, protected facts across stages, advisory-vs-authoritative status, a publication-failure or counterfeit negative) using recorded live **or clearly labelled scripted offline** material. It illustrates the mechanism; it does not itself prove originality or acceptance.
- **Original-SE explanation.** Explains the project-specific design decisions above: why these facts must be protected across stages, why advisory text is separated from deterministic authority, and why evaluation evidence must bind case/config/artifact. The novelty claim rests on this adaptation and demonstrated effect, **not** on the use of standard techniques.
- **Traceability/governance evidence.** The retained tests, evidence packages, and (when assembled by E) `docs/architecture/trace-matrix.md` link requirement → component → test/evidence → monitor. Presence of files or green CI does not by itself prove a gate is enforced or a rubric passed.

**Honesty boundary.** Standard techniques (immutability, hashing, atomic publication, ledgers, fail-closed checks) and compliance with course instructions alone do **not** establish originality. No experiment, approval, or ADD cycle is invented here; the demonstration thread reuses existing tests and retained artifacts. The honest limits (prompt grounding ≠ deterministic ownership enforcement; Q1–Q4 ≠ truth; scorer ≠ human acceptance) are stated above and must stay visible.

---

## 8B. Implementation-ready design for the extended requirements (PROPOSED)

The broader proposed `REQ-TA-*` obligations are not a wish-list: implementation-ready (proposed) contracts, sequences, failure/concurrency policies and proposed test scenarios are in [interface-contracts.md](docs/architecture/interface-contracts.md) §13–§16 and the new design decisions in [ADR 002](docs/architecture/adr/002-extended-result-evidence-budget.md). Summary map:

| Area | Requirements | Design location | Component (proposed) |
|---|---|---|---|
| Evidence & coverage | `REQ-TA-FR-001/004/005/006` | interface-contracts §13 | `runapi/evidence.py`, `runapi/coverage.py` |
| Output-check v2 | `REQ-TA-ARCH-002`, `FR-007/008`, `SEC-003`, `INV-001..008` | interface-contracts §14; ADR-002 D1/D2 | `runapi/checks.py` (R1–R8, corrected findings) |
| Run budget | `REQ-TA-NFR-COST-002`, RUN-001 `BUDGET` | interface-contracts §15; ADR-002 D3 | `runapi/budget.py` |
| Integration/handoff | all above | interface-contracts §16 | module boundaries, order, feasibility |

**Approved design targets (this pass):** corrected findings may coexist with `PASSED` while blocking findings produce `NEEDS_REVIEW` (R5, §14.2); the R3 ownership check is a **deterministic blocking phrase check** with contextual handling recorded only as an A/C/team alternative (§14.4); the Q2 trusted-provenance guard is **preserved separately** from evidence-ID R2 (§14.1); evidence/coverage data contracts are agreed **before** R2/R7 integration (§13, §16.1).

**This is a genuine new design cycle for the new requirements** (ADR 002), separate from and not altering the preserved C2 selection/evaluation (C1/C2/C3). Nothing here is implemented; D implementation and C acceptance remain pending; final requirements adoption is not implied. Feasibility and open adoption/config decisions are labelled in §16.4–§16.5.

---

## 9. Change policy

- ADRs required for safety-affecting changes (`GOV-006`); changes to provenance identity, check authority, redaction boundary or consent transitions require a new/updated ADR.
- Preserve upstream `tradingagents/`, `cli/`, `pyproject.toml` and tests unless an approved layout decision changes this.
- Intentional CLI/type-validation changes are documented in the ADR; they are not treated as accidental compatibility failures.
- Later architecture revisions based on real test evidence must cite that evidence (not manufactured now).

---

## 10. Requirement allocation summary

Full per-ID allocation (enforced-by component, fallback, other-owner/deferred) is in `docs/architecture/invariants.md` and `docs/architecture/traceability-inputs-member-b.md`. Summary:

- FR-001/002/003/004 → `PortfolioInputService` + `RunContext` + prompt semantics + coordinator consent.
- FR-005 → reporting stage labels; reuse `tradingagents/agents/rating.py` (REVIEW ≠ Hold).
- FR-006/FR-007 → provenance projection + `OutputChecker` (authoritative).
- NFR-001 → `runapi/finalize.py`; NFR-002 → `runapi/events.py`; NFR-003 → `runapi/redact.py`; NFR-004 → `runapi/persist.py` + fresh run ID; NFR-005 → `runapi/execution.py` shared service + preserved signature; NFR-006 → `RunRecord` accounting (interface-contracts §10).
- GOV-001..006 → allocated to C/E/A/human; B contributes permission model for `GOV-006`.

---

## 11. Provenance and limitations of this draft

- Alternatives and the human selection rationale: `docs/architecture/adr/001-portfolio-aware-cli.md`; scores and weights in `docs/architecture/evaluation-table.md`; process evidence in `docs/architecture/evaluation-logbook.md`.
- Unresolved decisions and pending evidence are recorded in `docs/architecture/risk-list.md` and the traceability handoff. No approvals, measurements or transcripts are invented here.
- This file is one of the approved B write set; `docs/architecture/architecture-blueprint.md` is a pointer to it.
- **2026-11-24 revision:** aligned component names/paths, result/check/publication contracts, stop-reason vocabulary, optional-portfolio scope disagreement, requirements ID namespaces and verification/evidence links with the `a62b801` checkout and the 24 November integration review. Broader `REQ-TA-*` extensions are documented as **PROPOSED / NOT IMPLEMENTED** (§1.5). C2 selection, C1/C3 alternatives and Brian's estimated rationale are preserved unchanged.
