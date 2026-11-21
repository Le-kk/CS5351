# Numeric-validation extension plan (PROPOSAL, unapproved)

Status: **PROPOSAL only.** Prepared 2026-11-21, Asia/Hong_Kong, by the OpenCode repair session at Brian's request (“Prepare a numeric-validation extension plan”, Codex call `call_2908c9d302df46eebfbf787d3853dcf3`). This authorizes **drafting a plan**, not implementing a validator, checker, schema, test, code change, canonical-requirement adoption or approval. Nothing here is an accepted requirement, a measured result, an independent score, or a Member C acceptance. Requirement IDs below use a separate **`NVR-`** prefix and are explicitly **UNAPPROVED**; they do not modify or renumber any `SEL-TA-*` ID.

Related existing documents (unchanged): [interface contracts](../interface-contracts.md), [invariants](../invariants.md), [runtime policy catalog](../runtime-policy-catalog.md), [ADR 001](../adr/001-portfolio-aware-cli.md), [memory design](../memory-design.md), [permission model](../permission-model.md), and the approved bounded prompt plans [`live-trader-numeric-test-plan-2026-11-21.md`](../../verification/proposals/live-trader-numeric-test-plan-2026-11-21.md) (L1) and [`live-fundamentals-vintage-test-plan-2026-11-21.md`](../../verification/proposals/live-fundamentals-vintage-test-plan-2026-11-21.md) (L2).

---

## 0. Deadline context and an optional small first slice

The course deadline is **26 Nov 2026, 23:59 Hong Kong**. The full programme in §7 is **not** proposed as an immediate, necessary fix and cannot be promised before the deadline. The frozen current-source live cohort and its source inventory must not be disturbed by this work; it is a separate, post-run audit proposal.

An **optional, small, bounded first slice** (see §6.0) is offered only if the team wants *something* reviewable quickly: a **standalone, post-run audit** run over already-saved artifacts, using an **explicitly supplied, run-bound typed input fixture**, covering only **price distance** and **price direction** and **ATR band**. It excludes LLM extraction, automatic typed extraction from the graph/snapshot, any staging integration, any report/UI change and any gating. It does **not** claim that any frozen report is already validated. Everything broader (§7 roadmap) is clearly **beyond** this immediately approved drafting work.

---

## 1. Problem statement

Prompt instructions alone (L1/L2) reduce but cannot certify free-text financial arithmetic. The coordinator observed on the current frozen source (not re-run by this drafting session):

- **L1 historical arithmetic (bounded fixtures now corrected):** before the L1 prompt fix, the Trader described stop `255.33` as “roughly 1.5×ATR (6.6 points) below” a `258.47` close with ATR `4.39`; the real difference is `258.47 − 255.33 = 3.14` ≈ `0.7153×ATR`. The L1 bounded fixtures now yield the correct `3.14`/about `0.72×ATR` and “below” **for those observed fixture cases only**. L1 did not repair all price prose.
- **C4 trial 2 Trader (residual after L1):** on the current final source, C4 trial 2 Trader run `20261121T101520Z-3680051f` says “a `$254` stop is only `$4.47` (≈1.02 ATR at 4.39) below today's low of `$255.33`.” The actual low-to-stop gap is `255.33 − 254 = 1.33` ≈ `0.303×ATR`; the `4.47` is actually `258.47 − 254` (measured from the **close**, not the stated low). A **wrong anchor** can therefore recur after the L1 fixture successes — the full narrative still has this error, so it is **not** “all price math fixed”.
- **PM band wording (a unit/definition, not pure price arithmetic):** full C1 `20261121T101520Z-52544e6d` (deepseek profile) PM prose says a `1.5–2×ATR` stop is “~6.6–8.8 points (ATR 4.39)” and later writes **“anchor the stop 1.5–8.8 points below the fill.”** Both ends of the later phrase read as “points”; text alone cannot prove the leading `1.5` was meant as a multiplier. This is a **range mismatch against the explicitly anchored preceding `1.5–2×ATR` claim** *only if* trusted context establishes that association; otherwise it is `NOT_VERIFIABLE`.
- **C2 ATR multiple (observed multiple error):** the final C2 PM described downside from `258.47` to `250.94` as “roughly 1×ATR” with ATR `4.39`. The actual move is `258.47 − 250.94 = 7.53`, and `7.53 / 4.39 ≈ 1.7153×ATR` — the “roughly 1×” wording does not match.

These are coordinator-observed examples used as **design coverage**, not an assertion that every claim in any report was independently audited, and not a re-run by this drafting session.

Broader financial definitions also matter and are **not** trivially certifiable: EPS is not generally safely additive across quarters; an effective tax rate cannot be certified from net income / operating income when pretax income and tax expense are absent. A calculator can check a **relation relative to specified operands**; it cannot certify the truth, semantics or exhaustive extraction of financial prose.

### 1.1 Proposed (UNAPPROVED) requirement IDs

Separate `NVR-` prefix; not canonical requirements.

- **NVR-001 — Typed supplied facts first.** Numeric inputs are supplied to the auditor as a typed, run-bound fact bundle (ticker, analysis date, source identifier and availability date, period, units, declared precision) rather than parsed from prose. Automatic typed extraction from the graph/snapshot is a **later** change (§7), not part of the first slice.
- **NVR-002 — Registered relations only.** A deterministic calculator evaluates only **registered** relations (see §4.2 roles) over `Decimal` (precision 28), with fixed units and defined rounding. No `eval`, no model-authored expected values. It verifies a relation against the **specified operands**; it does not certify the operands' truth or that the operand set is complete.
- **NVR-003 — Bounded relation-class coverage.** The first slice covers only price distance, price direction and ATR band; the broader roadmap adds percentages with an explicit denominator, position notional from supplied quantities, and risk/reward with explicit anchors. Out-of-scope financial definitions (tax-rate from net/operating income, weighted-EPS derivation) are **`UNSUPPORTED`**, never “verified” merely because a formula runs.
- **NVR-004 — Coverage-honest status.** Each **detected, registered** claim gets a status from `{VERIFIED, MISMATCH, NOT_VERIFIABLE, UNSUPPORTED}` (§4.3); there is **no** fifth per-claim `UNVERIFIED` status. Prose spans that are not detected/registered are counted separately, not scored. The denominator is only the **detected registered claims**, not every statement in the report. Partial coverage never yields a whole-narrative “verified” claim.
- **NVR-005 — Standalone audit first.** The first slice runs **outside** the live run: a standalone post-run tool reads saved artifacts and a separately supplied typed fixture, and writes its own audit file (not into the finalized run directory). It changes **no** `output_check`, `run_outcome`, Q1–Q4, public enum, manifest or rendered report. Any staging integration, render/gating or public status change is separately unapproved.
- **NVR-006 — Provenance and immutability.** Facts and claims bind to run id, ticker, analysis date, source identifier, source availability date, period, input fingerprint, unit and stage text hash+offset; unknown is never `0`; saved run artifacts are read-only. The audit's own retention/integrity is distinct from the authoritative report/manifest (which it never alters).

### 1.2 Preserved decisions (not reopened)

Two input modes; five research ratings and three Trader actions; Q1–Q4 unchanged; user-supplied/unverified holdings/cash; no orders; source-date constraints; report+manifest critical, terminal-append best-effort; the frozen `RunContext`/fingerprint; no reliance on the raw low-level primitive. This plan does **not** restart the ADR 001 C1/C2/C3 architecture decision.

---

## 2. Candidate approaches (design comparison; ESTIMATE, no measurements)

Estimates are design judgements labelled **ESTIMATE**. No measured latency/cost/accuracy is claimed.

### 2.1 A — Expanded prompts only (status quo + more instructions)

- **Rationale:** cheapest; no new modules. L1/L2 already show prompt wording changes behaviour.
- **Coverage:** cannot certify arithmetic; unit/definition wording (e.g. the PM band, C2 multiple) can recur; no machine-readable coverage.
- **Cost:** ESTIMATE ~0.2–0.5 day; low value as a correctness claim.
- **Verdict:** necessary but insufficient; keep L1/L2, do not extend as the solution.

### 2.2 B — Typed supplied-fact bundle + deterministic relation calculator + claim ledger (recommended)

- **Rationale:** separates *facts* (typed, run-bound, supplied or later projected), *claims* (detected relations) and *computed results* (deterministic). A claim is checked **against the specified operands**; unregistered relations are `UNSUPPORTED`; missing/unknown/ambiguous inputs are `NOT_VERIFIABLE`.
- **Coverage gaps:** undetected prose stays uncounted; semantic financial definitions remain `UNSUPPORTED`; coverage is bounded to the registered relations.
- **Integration cost:** first slice (standalone, supplied fixture, three relations) small; automatic extraction, more classes and any staging/gating are later.
- **Verdict:** recommended bounded design; do **not** restart C1/C2/C3.

### 2.3 C — Prose parsing / second-LLM critique

- **Rationale:** flexible; can “explain” arithmetic in arbitrary prose.
- **Coverage:** a regex cannot universally verify financial prose; a second LLM is non-deterministic, adds cost/latency, can hallucinate agreement, and is itself unverifiable. It can at most **triage or extract candidate claims**, never certify.
- **Cost:** ESTIMATE ~2–4 days plus per-call cost/latency; weak auditability.
- **Verdict:** acceptable only as a *detection aid*; its output is always an `UNSUPPORTED`/`NOT_VERIFIABLE`-until-confirmed suggestion and never yields `VERIFIED` by itself (wrong operands/formula that happen to compute must not certify the prose).

**Recommendation:** **B**. Do not restart C1/C2/C3.

---

## 3. Actual code seams inspected (read-only)

- **Graph state holds prose, not structured numbers.** `tradingagents/agents/state.py` (`AgentState`) carries prose reports and a rendered `portfolio_context` string; there is **no** typed numeric-facts field.
- **The verified market snapshot is rendered text, computed transiently.** `tradingagents/dataflows/vendors/yahoo/snapshot.py::build_verified_market_snapshot` computes latest OHLCV + indicators deterministically but **returns a markdown string**; the structured values are not exposed to state. Tool: `tradingagents/agents/tools.py::get_verified_market_snapshot`.
- **Some structured numeric fields exist for the Trader only.** `tradingagents/agents/schemas.py::TraderProposal` has `entry_price`, `stop_loss` and free-text `position_sizing`; the PM `PortfolioDecision.price_target` is similar. **These are the model's proposed levels, not verified external market truth.**
- **Portfolio facts are caller input, not market data.** `tradingagents/portfolio.py::PortfolioContext` (user-supplied, **unverified**) and the frozen `RunContext`/`FrozenSnapshot` in `tradingagents/runapi/context.py` (fingerprint, as-of) are the only canonical account snapshot.
- **Checks and result enums.** `tradingagents/runapi/checks.py::OutputChecker` implements Q1–Q4 only; `tradingagents/runapi/result.py` defines `Finding` rules `Q1|Q2|Q3|Q4|CHECK_ERROR` and `OutputCheck = PASSED|NEEDS_REVIEW|NOT_RUN`.
- **Envelope/report assembly.** `tradingagents/runapi/reporting.py` builds the trusted envelope; `tradingagents/runapi/execution.py` builds the final markdown/HTML; `tradingagents/reporting.py::_report_parts` selects prose sections.

**Consequence:** the code does **not** already expose a trusted structured numeric projection for price/ATR/position facts. A **new** projection (or, for the first slice, an explicitly supplied typed fixture) is **required**; this plan does not invent an existing canonical snapshot. A separate post-run audit can read the **saved** prose artifacts without touching the live path.

---

## 4. Proposed schema/interface (NEW; UNAPPROVED)

First slice modules (out-of-tree standalone acceptable; paths proposed):

- `tradingagents/runapi/numeric/__init__.py` — package (NEW; D implements, B contract, C tests, E wiring).
- `tradingagents/runapi/numeric/facts.py` — `TrustedFact`/`FactBundle` + precision/unit policy (NEW).
- `tradingagents/runapi/numeric/calculator.py` — registered relations over `Decimal` (NEW).
- `tradingagents/runapi/numeric/claims.py` — claim model + (fixture-supplied) claim set (NEW).
- `tradingagents/runapi/numeric/audit.py` — standalone audit over saved artifacts + supplied fixture (NEW).

No existing production module is modified by the first slice.

### 4.1 `TrustedFact` / `FactBundle`

```
FactSource = Literal[
  "supplied_run_fixture",        # explicitly supplied, run-bound typed inputs (first slice)
  "verified_market_snapshot",    # later: typed values derived from snapshot.py
  "fundamentals_statement",      # later: statement facts with period/availability date
  "trader_proposed_level",       # later: the Trader's *proposed* level (NOT verified market truth)
  "portfolio_user_supplied",     # user-supplied holdings/cash (unverified)
]

TrustedFact {
  fact_id: str                   # UNIQUE within the bundle; the operand `fact` references this
  value: Decimal | None          # None = unknown (never coerced to 0)
  unit: Literal["price","points","shares","currency","multiple","percent","ratio"]
  source: FactSource
  source_id: str                 # snapshot row id / statement ref / "user_input"
  availability_date: str         # ISO date the fact became knowable (<= run analysis date)
  period: str | None             # explicit statement period end/label; for actuals <= cutoff
  run_analysis_date: str         # the run's analysis date
  declared_precision: int        # digits after decimal this sourced fact carries
  verified: bool                 # True only for externally evidence-backed sources
}

FactBundle {
  run_id: str; ticker: str; analysis_date: str
  fingerprint_sha256: str | None # frozen portfolio fingerprint when portfolio-derived (else None)
  source_revision: str; prompt_hash: str
  facts: list[TrustedFact]       # fact_id/name must be unique
}
```

Rules: `fact_id`/name must be **unique** in the bundle (a duplicate is a bundle error, not silently merged); unknown `value` is `None` (never `0`); both `availability_date` and, for actuals, `period` must be `<=` the run analysis date (post-cutoff facts are excluded); `period` and `availability_date` are distinct from the run date. **`verified=True` means only that the fact is externally evidence-backed.** First-slice facts come from `supplied_run_fixture` and are **manually supplied**; unless they are themselves tied to external evidence, they are **not** assertions of source truth. `trader_proposed_level` and `portfolio_user_supplied` are always `verified=False`. A claim's `stage_text_sha256`+`text_span` must correspond to the actual stage prose (a mismatch is `NOT_VERIFIABLE`), and a band/anchor link must be an explicit trusted supplied binding (`anchor_evidence`), never inferred. **`VERIFIED` on a claim means "relation verified against the specified operands", not "the prose is true" or "extraction is exhaustive".** The bundle binds to the frozen `RunContext` (provenance per [INV-04/05](../invariants.md)).

### 4.2 `NumericClaim` (a detected relation) and calculator operations

```
ClaimClass = str   # a nonempty class name; membership is decided by the REGISTERED_CLASSES registry

REGISTERED_CLASSES = frozenset({          # first slice
  "price_distance","price_direction","atr_band",
})  # roadmap adds: "atr_distance","percent_with_denominator",
    # "position_notional","risk_reward"

OperandRef {
  fact: str                      # fact name in the bundle
  role: Literal["anchor","level","atr","minuend","subtrahend","numerator",
                "denominator","factor_min","factor_max","quantity","price"]
}

NumericClaim {
  claim_id: str
  claim_class: ClaimClass        # arbitrary nonempty string; not one of a fixed literal set
  operands: list[OperandRef]     # roles make the relation explicit
  asserted_unit: "price|points|currency|percent|ratio|multiple"
  asserted_value: Decimal | None # single stated number, or...
  asserted_range: tuple[Decimal, Decimal] | None
  asserted_direction: "above|below|none"   # for distance/direction claims
  claim_precision: int | None    # digits after decimal the *claim* states; None = not stated
  anchor_evidence: str | None    # trusted reference linking a claim to its anchor claim, if any
  stage: str                     # "trader" | "portfolio_manager" | "research_manager" | ...
  stage_text_sha256: str         # hash of the stage prose the span indexes into
  text_span: tuple[int,int]      # offsets into that stage prose (evidence; never rewritten)
  extraction_provenance: "supplied" | "deterministic" | "llm_assisted"
}
```

A named class (e.g. `tax_rate`, `weighted_eps`) that is **not** in `REGISTERED_CLASSES` yields `UNSUPPORTED`; the class is carried as an arbitrary string, so any class name is representable. `extraction_provenance`/`notes` describe **how** a claim was obtained, not **which** class it is. A claim whose operands cannot be bound, whose extraction is ambiguous, whose `claim_precision` is `None`, or which needs a missing `anchor_evidence` for an associated band is `NOT_VERIFIABLE`.

**Operations (fixed registry) with named unit algebra:**
- `subtract(minuend: price, subtrahend: price) -> points` (prices in one quote currency).
- `abs_distance(anchor: price, level: price) -> points`.
- `direction(anchor: price, level: price) -> above|below|equal`.
- `divide_positive(numerator: points, denominator: atr(>0, points)) -> multiple` (dimensionless).
- `scaled_band(factor_min: multiple, factor_max: multiple, atr: points) -> points` — this **multiplies** dimensionless factors by ATR-in-points to yield points; it is valid and must not be rejected as a unit incompatibility.

The calculator verifies the relation **relative to the specified operands**; it does not assert that those operands are the true or complete facts. A band whose factors are *claimed as points* (rather than dimensionless multipliers) without the registered `scaled_band` multiplication is `NOT_VERIFIABLE`; an ambiguous operand/anchor unit is `NOT_VERIFIABLE`.

### 4.3 `ComputedResult` (proposal; NOT Q1–Q4)

```
CoverageStatus = Literal["VERIFIED","MISMATCH","NOT_VERIFIABLE","UNSUPPORTED"]

ComputedResult {
  claim_id: str
  computed_value: Decimal | None
  computed_range: tuple[Decimal, Decimal] | None
  computed_unit: ...
  expected_at_claim_precision: Decimal | tuple[Decimal, Decimal] | None  # round-half-up of computed at claim_precision
  status: CoverageStatus
  source_facts: list[str]
  notes: str     # e.g. "missing atr" / "ambiguous 1.5 role" / "unregistered relation"
}
```

**Do not reuse `CHECK_ERROR`** for a numerical semantic mismatch and **do not create a Q5 silently.** A later, A/C-approved change may add a proposal-only finding type (`NumericFinding { rule: "NUMERIC", ... }`); until then results live only in the standalone audit file.

### 4.4 Precision / rounding / tolerance policy (exact)

- **Arithmetic:** Python `Decimal` at **context precision 28**; no binary float in the calculator.
- **Comparison rule: NO tolerance.** Compute exactly, **round half-up to the claim's declared `claim_precision`**, and require **equality** with the asserted value/range endpoints. A different rounded value is `MISMATCH`.
- **Precision bounds per registered class (a claim outside its bound, or with `claim_precision=None`, is `NOT_VERIFIABLE`):**
  - `price_distance` → `claim_precision ∈ {0,1,2}`.
  - `atr_band` → `claim_precision ∈ {0,1,2}`.
  - `price_direction` → no numeric precision (boolean); `claim_precision` is `null`.
  - `atr_distance` (roadmap registry) → `claim_precision ∈ {0,1,2,3,4}` (0 permits “roughly 1×ATR”).
- **Unknown/ambiguous precision** (the prose does not state enough digits to pin `claim_precision`; or a claim declares a precision inconsistent with its written form) → `NOT_VERIFIABLE`.
- **Comparison is per the claim's own stated precision**, not a re-interpretation: a literal `1` is compared at precision 0, not assumed to be `1.0`; `6.6–8.8` is compared at precision 1, and `6.60–8.80` at precision 2. The **same source text cannot declare an arbitrary precision**; the stated form fixes it (a `6.6` written claim cannot be re-declared as precision 2).
- **Units:** each operation declares its unit algebra (§4.2). Ambiguous operand/anchor units → `NOT_VERIFIABLE`.
- No caller-chosen wide tolerances are permitted.

### 4.5 Worked examples under this policy (document examples, exact)

- **Distance/direction (positive):** `anchor=258.47`, `level=255.33`. `abs(258.47 − 255.33) = 3.14`; `255.33 < 258.47` ⇒ **below**. Prose “≈3.14 points below” at `claim_precision=2` → expected `3.14` → `VERIFIED`.
- **Direction (negative, reverse level/anchor):** `anchor=258.47`, `level=261.61` (above). `abs = 3.14`; `261.61 > 258.47` ⇒ **above**. A prose claiming **“below”** ⇒ `asserted_direction` mismatch ⇒ `MISMATCH`; prose correctly saying “above” ⇒ `VERIFIED`.
- **ATR band (positive):** `factor_min=1.5`, `factor_max=2`, `atr=4.39` → `1.5 × 4.39 = 6.585`, `2 × 4.39 = 8.78`. At `claim_precision=1`, round-half-up → expected band `(6.6, 8.8)`. Prose “6.6–8.8 points” → `VERIFIED`. At `claim_precision=2`, expected `(6.59, 8.78)`; prose “6.59–8.78 points” → `VERIFIED`.
- **ATR band (boundary negative, same precision):** expected `(6.6, 8.8)` at precision 1; prose “6.6–8.7 points” (a wrong upper value at the **same** declared precision) ⇒ `MISMATCH`. Likewise prose written as `6.60–8.80` is compared at precision 2 against `(6.59, 8.78)` ⇒ `MISMATCH`.
- **PM band “1.5–8.8 points below the fill” (observed):** parsed literally, both endpoints are `points`; the written form `1.5` and `8.8` gives `claim_precision=1`, so the asserted range is `(1.5, 8.8)` at precision 1. If trusted `anchor_evidence` links it to the preceding `1.5–2×ATR` claim, compare against expected `(6.6, 8.8)` at precision 1 → `MISMATCH` (lower `1.5` ≠ `6.6`). If no trusted `anchor_evidence` exists, the first endpoint's role is ambiguous (`1.5` could be a factor) ⇒ `NOT_VERIFIABLE`. Not auto-rewritten; never a run failure.
- **C2 ATR multiple (observed):** `anchor=258.47`, `level=250.94`, `atr=4.39` → `7.53`; `7.53 / 4.39 = 1.71526195…`. The literal “roughly 1×ATR” is a precision-0 claim: round-half-up `1.7152…` → `2`. `2 ≠ 1` ⇒ `MISMATCH`. (`1` is **not** assumed to mean `1.0`.)
- **ATR multiple (roadmap, boundaries):** `3.14 / 4.39 = 0.71526195…`. At `claim_precision=2` → `0.72`: prose “0.72×ATR” `VERIFIED`. At `claim_precision=4` → `0.7153`: prose “0.7153×ATR” `VERIFIED`; prose “0.7152×ATR” at precision 4 ⇒ `MISMATCH`.
- **Unsupported:** a named class such as `tax_rate` (net income / operating income) or `weighted_eps` when it is not in `REGISTERED_CLASSES` ⇒ `UNSUPPORTED`, never `VERIFIED`.
- **Not verifiable:** ATR missing or `≤ 0` ⇒ ATR multiple/band `NOT_VERIFIABLE`; unknown cash ⇒ any affordability/notional claim needing cash `NOT_VERIFIABLE` (no `0`).

---

## 5. Integration stages

**Stage 0 — standalone post-run audit (first slice; no live-path change).** A separate tool reads **saved** stage artifacts plus an **explicitly supplied, run-bound typed fact fixture**, evaluates only the first-slice relations, and writes its **own** audit file at a caller-chosen location **outside** the finalized run directory. It does **not** modify saved artifacts, the manifest or its hashes, and its retention/integrity (`audit.json` + its own checksum) is **distinct** from the authoritative report/manifest. It changes no `Finding`/`output_check`/`run_outcome`/rendering. Coverage is reported **inside the audit file only**, never in the published report/UI.

**Stage 1 — later: automatic typed fact projection + staging integration (needs named seams and approval).** Extracting typed facts directly from `snapshot.py`/graph, writing the audit into the staging area, or surfacing coverage in the report requires touching these existing modules, with separate review:
`tradingagents/dataflows/vendors/yahoo/snapshot.py`, `tradingagents/agents/state.py`, `tradingagents/runapi/execution.py`, `tradingagents/runapi/persist.py`, `tradingagents/runapi/reporting.py`, `tradingagents/reporting.py`, `tradingagents/runapi/execution.py::_prompt_hash` (source inventory).

**Stage 2 — optional render/gating (separately unapproved).** Only if A/C approve a schema/interface/quality-rule change: map a `MISMATCH` on a registered relation to `NEEDS_REVIEW` via a **new, named** finding type (never a reused `CHECK_ERROR`, never a silent Q5) and/or communicate coverage in the report without implying whole-narrative certification. Would also require edits to `docs/architecture/interface-contracts.md` §3.1–3.6/§6, `docs/architecture/invariants.md` INV-03/04/08/11, `docs/architecture/runtime-policy-catalog.md`, `docs/architecture/memory-design.md`, `permission-model.md`, and the `docs/verification/*` registry.

**Q1–Q4 remains unchanged until such approval.** Undetected/unregistered numerical prose remains uncounted; the audit states coverage as “N of M **detected registered** claims checked”, never a whole-narrative certification.

---

## 6. Acceptance plan

### 6.0 Optional small first slice (price distance / direction / ATR band only)

Fixture: a supplied typed fact packet for one saved run (e.g. `close=258.47`, `stop=255.33`, `atr=4.39`, `as_of=2026-01-09`; facts `supplied_run_fixture`, manually supplied — not source-truth claims) and a small set of supplied claims with roles/precision. Scenarios (first slice also proves the trust/immutability rules, not just arithmetic):

| ID | Fixture | Expected | Seam |
|---|---|---|---|
| NVA-01 | prose “≈3.14 points below” | `VERIFIED` (distance + direction) | `abs_distance` / `direction` |
| NVA-02 | same anchors; prose says “above” | `MISMATCH` (direction) | `direction` |
| NVA-03 | **reverse** level/anchor: `level=261.61`, `anchor=258.47` ⇒ above; prose says “below” | `MISMATCH` (direction reversed) | `direction` |
| NVA-04 | `1.5–2×4.39`; prose “6.6–8.8 points” at precision 1 | `VERIFIED` (ATR band) | `scaled_band` |
| NVA-05 | PM-style “1.5–8.8 points” **with** trusted `anchor_evidence` to the `1.5–2×ATR` claim (path A) vs **without** it (path B) | A: `MISMATCH`; B: `NOT_VERIFIABLE` | `scaled_band` + `anchor_evidence` |
| NVA-06 | ATR missing / `0` / nonfinite | `NOT_VERIFIABLE`; no `0`, no divide-by-zero | `scaled_band` |
| NVA-07 | saved report/manifest read by the audit; audit writes only outside the run dir | saved report/manifest **bytes and hashes unchanged**; audit retention distinct from manifest | Stage 0 standalone |
| NVA-08 | wrong ticker / analysis date / source / fingerprint binding (bundle vs saved run) | claims `NOT_VERIFIABLE`/excluded, never `VERIFIED`; bundle error if binding inconsistent | fact run-binding |
| NVA-09 | duplicate `fact_id`, duplicate claim_id, non-`Decimal` value, `claim_precision=None`, invalid `text_span`/hash | bundle/claim is rejected or `NOT_VERIFIABLE`; never `VERIFIED`; no crash | facts/claims validation |
| NVA-10 | partial coverage (some detected claims `NOT_VERIFIABLE`) | audit summary reports counts only; **no** published report/UI change and **no** whole-narrative verified claim | audit summary |

The slice stops there; it does **not** validate any frozen report. ESTIMATE for this slice: **~1–2 working days** for a standalone tool + fixture + these scenarios, **if** the team wants it before the deadline; otherwise it should be deferred. This estimate is not a promise.

### 6.1 Full roadmap scenarios (beyond the first slice, needing later approval)

| ID | Fixture | Expected | Seam |
|---|---|---|---|
| NVA-11 | ATR multiple `3.14/4.39`: “0.72×ATR” @2dp, “0.7153×ATR” @4dp, and literal “roughly 1×ATR” @0dp → `2` | @2/@4 `VERIFIED`; “0.72” declared at 4dp `NOT_VERIFIABLE`; “1×ATR” `MISMATCH` (2≠1) | `divide_positive` + precision |
| NVA-12 | notional: supplied quantity `40` × price `258.47` → `10338.80`; separately an affordability claim needing **cash** (unknown) | notional `VERIFIED`; affordability `NOT_VERIFIABLE` (cash unknown, not `0`) | `position_notional` vs affordability inputs |
| NVA-13 | explicit-empty vs NO_PORTFOLIO portfolios | distinct; flat not asserted where unknown | fact bundle |
| NVA-14 | unregistered named class (`tax_rate` from net/operating income; `weighted_eps`) | `UNSUPPORTED`, never `VERIFIED` | registry |
| NVA-15 | precision boundaries (0.7153 vs “0.72”; 6.6 vs 6.59; declared vs written precision) | exact per §4.4; wrong precision `NOT_VERIFIABLE`, wrong rounded value `MISMATCH` | calculator precision |
| NVA-16 | band whose factors are *claimed as points* without `scaled_band` multiplication | `NOT_VERIFIABLE` (unit algebra), not a dimension rejection of valid factors×ATR | `scaled_band` units |
| NVA-L | after any Stage-1/2 change: live fixed replay | registered relations evaluated against real facts; coverage internal; independent human/C review | integration |

If a claim names a class that is not in `REGISTERED_CLASSES`, its result is `UNSUPPORTED`; the class is carried as an arbitrary `claim_class` string.

**Independent human review / C scoring is still required** for: whether a `VERIFIED` relation is the *right* claim to make, narrative quality, ownership/challenge semantics, and any promotion from audit-only to gating. No numeric threshold constitutes C acceptance or F8 recovery.

---

## 7. Work split, prerequisites, estimates, migration, risks

### 7.1 Handoff (recorded team allocation; not universal course roles)

- **B (architecture):** propose `NVR-` scope, the fact/claim/status contract, units/precision policy and Stage-1/2 deltas.
- **A (requirements):** adopt (or not) any `NVR-` item and any Stage-2 gating; A owns requirement adoption.
- **C (independent tests/evaluation):** own NVA acceptance, a real cohort and semantic judgement. C owns acceptance; D does not define it.
- **D (implementation):** build the standalone first slice; later, the typed projection, calculator and claim extraction.
- **E (integration/governance):** prompt-hash/source-inventory, staging/sink/privacy, report and registry edits — only after approval.

No approvals are asserted or invented here.

### 7.2 Prerequisites and genuinely pending choices

Pending: whether to do the optional first slice before the deadline or defer; adopt B (vs B+detection aid); exact precision bounds if more classes are added; where trusted facts come from (supplied fixture now; `snapshot.py`-derived projection later); whether/when any render/gating is wanted; who owns semantic acceptance.

### 7.3 Estimates (ESTIMATE; no measurements, no promise)

- Optional first slice (standalone, supplied fixture, 3 relations, §6.0): **~1–2 working days**.
- Full Stage-0/1 typed projection + more classes + tests: **~4–7 working days** (beyond the immediate deadline; not proposed as a necessary immediate fix).
- Stage-2 render/gating + contract review + live replay: **~3–6 working days**, plus A/C review.

### 7.4 Migration / rollback

- **Migration:** the first slice is fully standalone and additive; no live-path, enum, manifest or rendering change; it reads saved artifacts and writes its own file.
- **Rollback:** delete/ignore the standalone tool and its audit file; saved run artifacts and manifest hashes are untouched, so rollback is simply not running the tool.

### 7.5 Risks

- **False assurance:** `VERIFIED` must not read as “whole report correct”. Mitigation: coverage counts of detected registered claims only; no whole-narrative badge; explicit `UNSUPPORTED`/`NOT_VERIFIABLE`.
- **Bounded coverage / detection:** only registered detected relations are scored; undetected prose is uncounted and stated.
- **Fact provenance:** facts must be from a supplied or externally-verifiable source; model-proposed levels and user-supplied holdings are unverified inputs, never “truth”.
- **Detection aid errors:** LLM/regex extraction is unverified; it cannot yield `VERIFIED` and must not include clearly different relations that happen to compute.
- **Scope creep:** Stage-1/2 touches check authority and contracts; keep separately approved and beyond the immediate deadline.

---

## 8. Status and next step

This is a **plan for review**, not implementation, not approval, and not a claim that any current report is validated. Brian authorized only drafting it. Implementation, tests, canonical-requirement adoption and any render/gating wait for A/B/C/D/E scope, design and test approval. The coordinator-observed examples (L1 historical arithmetic, the PM band wording, the C2 ATR multiple) are retained as design evidence; they are not reclassified as passed, and the optional first slice does not rescue them before review. The broader roadmap is **beyond** this immediately approved drafting work.

PLAN_READY_FOR_HUMAN_REVIEW — /home/brian/projects/CS5351/docs/architecture/proposals/numeric-validation-extension-plan-2026-11-21.md
