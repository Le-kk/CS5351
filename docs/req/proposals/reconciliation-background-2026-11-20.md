# Historical reconciliation background — 2026-11-20

**Background only. Read the [improved selected requirements](reconciliation-2026-11-20.md) first.**

This preserves the earlier OpenCode reconciliation for its source references, all 25 active v2 dispositions and withdrawn entries. Its implementation recommendations, scope options, unresolved immediate choices and “no fresh measurements” statement describe that earlier document, not the current implementation candidate. The candidate now makes explicit next-increment choices; neither document records A's approval. Broader v2 coverage decisions still belong to A/the team.

Original proposal SHA-256 before this archival heading adjustment: `e7aa154992ccf7ddedbf27545a72f8446d69127e281a470b035b3ae5d8f21dce`. Only heading levels have been demoted below; earlier wording is retained as historical context. Section references inside the retained text refer to its own numbered sections. The original bytes are retained privately outside tracked deliverables.

---

## Requirements Reconciliation Proposal — 2026-11-20

**Status: Member B proposal only. Pending Member A / team decision. Not an approved
requirements baseline, not a registry, not a substitute for the D1 deliverables.**

- Author: Member B (architecture). This is a *proposal document*, not an authoritative
  requirements file. `docs/req/selected-requirements.md` remains a *working selection*;
  A's broader draft (`requirements-draft-v2.md`) is a *draft*; neither is the final
  approved registry. Final requirements and acceptance criteria are owned by Member A.
- Scope of this document: reconcile (a) A's broader v2 draft, (b) the working selected
  requirements (`SEL-TA-*`), (c) the current architecture and implementation at the
  reviewed revision, (d) verification/review evidence, and (e) the original course
  obligations — into a coherent proposal A can decide on.
- This document records **no approvals, no fresh test results, and no measurements**.
  Historical test counts and live-diagnostic outcomes are cited as *attributed records*,
  not re-verified here and not proof that requirements are satisfied.
- Nothing in this proposal is approved by virtue of appearing here. Every "adopt",
  "defer", "restore" or "replacement" is a **proposal** subject to A's decision.
- Verified read-only against local checkout at HEAD `e7aed7a9d735c7524eca583be1c2ed569f8c5ac2`
  (`main`). No files altered by this proposal except this proposal file. Remote branch
  protection state is **UNKNOWN** (not inspected). No live tests were run.

---

### 0. Corrections incorporated (read first)

These corrections constrain how every later section must be read:

1. **Course compliance is not inferred from the blocking-gate list.** A green gate list
   does not prove D1–D9 compliance. Performance/cost deferral eligibility remains a
   **justified decision for A, or an instructor clarification** — not a settled fact.
2. **Inexpensive offline tests ≠ inexpensive call-cap implementation.** Test cost and
   implementation cost are separate; a cheap test does not imply a cheap feature.
3. **R1–R8 → Q1–Q4 mapping is partial** (see §5): R1→Q1; R8 partially→Q3/Q4;
   R2/R3/R4–R6/R7 have **no complete deterministic equivalent**; Q2 (input provenance
   match) is **new** and is not an upstream/draft rule.
4. **SEL-TA-FR-005 is NOT part of the data-gap mapping.** FR-005 concerns ratings/actions;
   it does not own data-gap behaviour.
5. **Usable free-text fallback is preserved** (upstream `agents/structured.py`), not
   removed.
6. **Logging sinks differ in scope** between the draft and the selection (described in §5).
7. **Configuration inventory gap** exists (described in §6): the selection does not define
   the full effective-config key inventory that the draft's REPRO-001 did.
8. **Evaluation-comparison rule change is intentional**: the selection separates
   repeatability comparisons from controlled change experiments; the draft's blanket
   "must match config+prompt_hash to compare" is deliberately changed.
9. **Satisfying an original ≠ proposing its replacement.** Where an original is "covered"
   by meaning, that is coverage, not endorsement of dropping the original text; where a
   replacement is proposed it is labelled a replacement and is unapproved.
10. **"Semantic-only" claims are removed where deterministic authority already exists.**
    Q1–Q4 and outcome typing are deterministic authorities; injection *persuasion*
    testing is semantic, but the deterministic check is real (see SEC-001 in §4).

Also preserved and non-negotiable in this proposal:
- **Optional portfolio use** remains supported in both modes (`NO_PORTFOLIO` / `PORTFOLIO_PROVIDED`).
- **F9's correct interpretation**: an Underweight research rating on an explicit flat
  snapshot is valid; the concern is *wording* that issues unconditional instructions about
  a nonexistent/existing exposure. F9 is **not** a Q1–Q4 failure and **not** a defect of
  the optional-portfolio feature; PASSED is intentionally narrower than ownership semantics.

---

### 1. Sources and verified references

| Source | Reference / hash | Use |
|---|---|---|
| A's draft | `requirements-draft-v2.md` SHA-256 `5742540b…a62519f` | Original active + withdrawn requirements |
| Historical review | `requirements-v2-review-2026-11-12.md` SHA-256 `5bd41de3…107689629` | Suggestions only; not approved |
| Course spec | `CS5351-2026-2027-project.pdf` SHA-256 `6af742d3…` | D1–D9, gates |
| Course intro | `CS5351-introduction-group-project-extract.pdf` SHA-256 `b9efef89…` | Scope/examples aspirations |
| Ownership | `Deliverables-and-Ownership.pdf` SHA-256 `b3d820af…` | A/B/C/D/E boundaries |
| Working selection | `docs/req/selected-requirements.md` | SEL-TA-* working scope |
| Architecture | root `architecture-blueprint.md`, `docs/architecture/*` | C2 design (drafts) |
| Review | `docs/reviews/project-review-2026-11-18.md` | F1–F9 |
| Diagnostic | `docs/reviews/evidence/live-diagnostic-2026-11-18.json` | Attributed live diagnostic (attributed evidence, not formal gate) |
| Verification | `docs/verification/semantic-evaluation.md`, `requirement-test-mapping.md`, CI `.github/workflows/ci.yml` | Rubric R1–R7; C mappings; CI scope |

All source-pack hashes were verified read-only during Stage 1 and are not re-verified here.

---

### 2. Dispositions of all 25 active originals (+ withdrawn)

Classification key: **C**overed · **P**artial · **X** clarification/conflict ·
**I** additional implementation proposed · **D** defer (proposed, unapproved) ·
**H** human/team decision. Every "D" and every "replacement" below is **proposed and
unapproved**.

**ID legend (unambiguous shorthand):** a bare ID such as `FR-007` or `RUN-001` or
`NFR-EVAL-001` denotes an **original requirement** from A's draft (`REQ-TA-…`), unless the
row header says otherwise. `SEL-TA-…` always denotes a **selected** requirement. Per-row
mappings are written with full `SEL-TA-…` IDs (e.g., `FR-007 → SEL-TA-FR-004, SEL-TA-FR-005`).

> Coverage distinction used throughout: coverage **in the selected registry** (a SEL
> requirement states the intent) is separate from **implementation already present
> upstream/baseline**. Baseline safeguards that are preserved are **not** counted as new
> project contributions, and preserving them is not "satisfying" the original requirement.

#### Active functional

**RUN-001** (Must/proposed) → SEL-TA-FR-004, SEL-TA-FR-006, SEL-TA-NFR-001, SEL-TA-NFR-004 — **P**.
- Impl: `runapi/finalize.py`, `result.py` (outcome/stop/rating/check/findings).
- Evidence: inspected — no per-channel `data_coverage`; inspected — outcome typing exists; reported — C `test_nfr001/006`, `test_fr006` pass.
- Uncovered: per-channel `data_coverage`; `DATA`/`BUDGET` stop semantics; stop-vocabulary divergence.
- Disposition (proposed): adopt selection's outcome/rating/check fields; **propose deferral** of coverage grid + budgets. Rationale: selected scope excludes twelve-channel grading/budgets; stop vocabulary needs A's single ruling. Owner: A.

**FR-001** (Must/proposed) → none — **D** (proposed).
- Impl: none (no evidence-ID registry); upstream dated vendor text is baseline only.
- Evidence: inspected — no registry module.
- Uncovered: evidence IDs, records, visible source+date, 12-channel capture, evidence retention, finding R2.
- Disposition (proposed): defer as "full stable-evidence registry". Preserve dated vendor text as baseline. Owner: A.

**FR-003** (Should/partial) → none — **D** (proposed); preserve baseline resume.
- Impl: upstream checkpointer/resume; no list/rerun command.
- Evidence: inspected — checkpointer modules exist; reported — upstream checkpoint tests pass.
- Uncovered: list command, rerun command, three-fit acceptance.
- Disposition (proposed): defer UX redesign; preserve upstream resume (safeguard, not contribution). Owner: A.

**FR-004** (Must/partial) → none (per-channel guards only) — **D** (proposed); preserve guards.
- Impl: upstream per-channel look-ahead guards.
- Evidence: inspected — guards present; reported — upstream look-ahead tests pass.
- Uncovered: whole-run 12-channel planted-marker CI check; project-level no-look-ahead claim.
- Disposition (proposed): defer the whole-run test and project-level claim; preserve guards. Do **not** claim project-wide no-look-ahead from baseline guards. Owner: A.

**FR-005** (Must/partial) → SEL-TA-NFR-001 (failure typing only) — **P**.
- Impl: `finalize.py` `DATA_FAILURE`; recoverable non-core sentinel preserved.
- Evidence: inspected — `classify_exception` maps dataflows/vendor to `DATA_FAILURE`; reported — `test_no_data_handling`, `test_vendor_errors`, C `test_nfr001` pass.
- Uncovered: core-data-stop invariant; "Data coverage" section; `STALE`/`WITHHELD` codes.
- Disposition (proposed): adopt failure typing; defer coverage section/core-stop. Note: **original FR-005 is not in the data-gap mapping of SEL-TA-FR-004 / SEL-TA-FR-005**; SEL-TA-FR-005 is the ratings/actions requirement, not a data-gap rule. Owner: A (coverage) / B (design).

**FR-006** (Should/partial) → none — **D** (proposed); preserve price-staleness guard.
- Impl: upstream `MAX_OHLCV_STALE_DAYS = 10`.
- Evidence: inspected — constant present; reported — `test_yfinance_stale_ohlcv_guard` passes.
- Uncovered: statement-age rule, `STALE` code, boundary fixtures.
- Disposition (proposed): defer; preserve guard. Owner: A.

**FR-007** (Must/proposed) → SEL-TA-FR-004, SEL-TA-FR-005 — **C** (preserved intent + proposed replacement).
- Impl: `portfolio_manager.py:31` no-portfolio Hold meaning; `rating.py` REVIEW≠Hold; stage separation.
- Evidence: inspected — conditional `hold_meaning`; reported — C `test_fr004/005` pass; semantic R1/R4 recorded 1.
- **Preserved intent:** "ratings describe the instrument, not the user's account; Hold ≠ maintaining an assumed position" — this intent is retained (upstream Hold-meaning edit + REVIEW≠Hold).
- **Proposed replacement (unapproved):** the draft's **universal** "no ownership wording" ban is replaced by **conditional-on-supplied-positions** wording. This is a scope change, not a satisfaction of the original text; it requires A's confirmation.
- Disposition (proposed): retain preserved intent; label the conditional-ownership reword a **proposed replacement** pending A. Owner: A.

**FR-008** (Should/proposed) → none — **D** (proposed).
- Impl: `SentimentReport` bounds/labels only.
- Evidence: inspected — bounds only; reported — none for R4–R6.
- Uncovered: band–score match, confidence cap, no-direction-without-data.
- Disposition (proposed): defer ("sentiment correction"). Owner: A.

#### Active non-functional

**NFR-001** (Must/partial) → SEL-TA-NFR-001 — **X**.
- Impl: `finalize.py` five typed reasons; `classify_exception`.
- Evidence: inspected — five reasons present; usable free-text fallback preserved in `agents/structured.py`; reported — C `test_nfr001` passes.
- Uncovered: draft `DATA/MODEL/BUDGET` vocabulary; `BUDGET` reason.
- Disposition (proposed): adopt selection typing; **A ruling** on authoritative vocabulary. Rationale: preserve free-text fallback (already preserved). Owner: A.

**NFR-002** (Could/partial) → none — **D** (proposed).
- Impl: upstream analyst plan; factories hard-coded in `setup.py`.
- Evidence: inspected — `analyst_execution.py`; reported — `test_analyst_execution` passes.
- Uncovered: add-analyst without orchestration edit.
- Disposition (proposed): defer ("analyst plugin redesign"). Owner: A.

**NFR-OBS-001** (Should/partial) → SEL-TA-NFR-002 — **P**. **Logging sink scope differs.**
- Impl: `runapi/events.py` JSONL sink; `execution.py` events.
- Evidence: inspected — JSONL event module; reported — C `test_nfr002` passes.
- Uncovered: budget-limit naming; **field-set difference** — the draft specified "every line of both sinks" parse with six fields and named a JSON state file + plain-text CLI log; the selection specifies a *new* JSONL lifecycle sink with a distinct field set (run_id, ticker, node input/engine/output, UTC ts, elapsed_ms, event, event_outcome) and explicitly does **not** falsely describe upstream state snapshots as JSONL. These are **different scopes**, not one satisfying the other.
- Disposition (proposed): adopt JSONL lifecycle sink; record the sink-scope difference as a replacement/reframing for A, not a silent satisfaction of OBS-001. Owner: A/B.

**NFR-REPRO-001** (Should/partial) → SEL-TA-NFR-004, SEL-TA-FR-006 — **P**.
- Impl: `persist.py` staging+atomic rename+manifest; `context.py` fingerprint; fresh run IDs.
- Evidence: inspected — staging/commit present **and F1 cleanup-ownership defect present**; reported — C `test_nfr004`, `test_fr006` pass.
- Uncovered: strict one-record-per-run under resume (moot: resume deferred); F1 correctness; **configuration-inventory gap** (§6): the draft enumerated a specific `DEFAULT_CONFIG`-derived recorded-key set and 10 omitted keys with a one-key-diff test, whereas the selection's NFR-004 names a "safe effective config" without that full enumerated inventory.
- Disposition (proposed): adopt selection wording (config-only diff; conditional fields); F1 is a D fix; configuration inventory is an **open gap** for A/B to close if retained. Owner: A/B.

**PERF-001** (Should/proposed) → none — **D** (proposed). *Meaning: successful completion within a measured wall-clock cap.*
- Impl: no run timer; parallel analysts.
- Evidence: inspected — none.
- Uncovered: `RUN_TIME_CAP` fixed from measurement; 20/20 `COMPLETED` within cap.
- Disposition (proposed): defer; if restored, measure first. Note: cheap to *test* does not mean already implemented; the cap is measurement-dependent. Owner: A/D.

**PERF-002** (Should/proposed) → none — **D** (proposed). *Meaning: timeout/cancellation handling.*
- Impl: no deadline/cancellation.
- Evidence: inspected — none.
- Uncovered: crossing budget → `INCOMPLETE(BUDGET)`; return within cap + `CANCEL_ALLOWANCE`; bounded in-flight calls.
- Disposition (proposed): defer; distinct from PERF-001. Owner: A/D.

**COST-001** (Should/proposed) → none — **D** (proposed).
- Impl: per-call `max_tokens` only.
- Evidence: inspected — `max_tokens`; reported — none.
- Uncovered: run token budget from usage; UNKNOWN handling.
- Disposition (proposed): defer. Owner: A/D.

**COST-002** (**Must**/proposed) → none — **D** (proposed, **flagged**).
- Impl: per-scope limits only.
- Evidence: inspected — per-scope limits; reported — none.
- Uncovered: shared run-scoped call cap enforced pre-dispatch; counting rule.
- Disposition (proposed): defer **but A must confirm** the Must→defer downgrade. Note: offline *testing* is cheap, but a run-wide, concurrency-safe, pre-dispatch call cap is a **non-trivial implementation**; test cheapness does not imply implementation cheapness. Owner: A.

**COST-003** (Could/proposed) → none — **D** (proposed).
- Impl: round-count only.
- Evidence: inspected — round control; reported — none.
- Uncovered: convergence signal/fixtures.
- Disposition (proposed): defer. Owner: A.

**NFR-EVAL-001** (Should/proposed) → SEL-TA-NFR-006 — **C** (preserved intent + intentional replacement of comparison rule).
- Impl: `result.py` `RunRecord`; pre-run categories.
- Evidence: inspected — categories present; reported — C `test_nfr006` passes.
- **Preserved intent:** completion = completed ÷ all started (no dropped starts); quality over completed only; `NEEDS_REVIEW`/incomplete counts reported alongside; zero completed ⇒ insufficient evidence.
- **Proposed replacement (unapproved):** the draft's blanket "compare only if config+prompt_hash match" is **deliberately changed** to separate repeatability comparisons from controlled change experiments. This is a recorded *intentional change*, and it is a **replacement of the original comparison rule**, not a satisfaction of it.
- Uncovered/carried: at rule level the counting intent is covered; the changed comparison policy is the open item needing A's confirmation.
- Disposition (proposed): retain preserved counting intent; label the comparison-rule change a **proposed replacement** pending A. Owner: A/B.

#### Active security

**SEC-001** (Must/proposed) → SEL-TA-FR-007 (deterministic check authority) + SEL-TA-GOV-004 (semantic evaluation, separately) — **P** (corrected).
- Three distinct pieces:
  - **Existing deterministic check authority** — present and mapped to **SEL-TA-FR-007**: `checks.py` Q1–Q4 fail-closed; `finalize.py` outcome authority. Real, deterministic.
  - **Missing coverage/result protections** — absent: no `data_coverage` object exists, so "injected content cannot change coverage" has no target; result fields are deterministic but there is no coverage record to protect.
  - **Semantic persuasion evaluation** — mapped **separately** to **SEL-TA-GOV-004**: challenge cases C4/C5 test whether the *narrative* resists injection. Semantic, not a deterministic runtime guarantee.
- Evidence: inspected — Q1–Q4 fail-closed, no coverage field; reported — challenge exposures reached (true).
- Uncovered: deterministic protection over a coverage record (feature deferred); universal persuasion guarantee (out of deterministic scope).
- Disposition (proposed): keep deterministic check authority (SEL-TA-FR-007); defer coverage protections with the coverage feature; keep persuasion testing under SEL-TA-GOV-004 semantic evaluation. **Not** "semantic-only" — deterministic authority exists for Q1–Q4/outcome. Owner: A.

**SEC-002** (Must/partial) → SEL-TA-NFR-003 — **C/P** (bounded).
- Impl: `redact.py` at sink boundary.
- Evidence: inspected — **F2 bypass present**; reported — C `test_nfr003` pass; diagnostic credential scan 0.
- Uncovered: universal/paraphrase absence (bounded claim only); F2 correctness.
- Disposition (proposed): adopt bounded claim; F2 is a D fix. Owner: C/D.

**SEC-003** (Should/proposed) → SEL-TA-FR-007 Q3/Q4, SEL-TA-GOV-004 — **C/P**.
- Impl: `checks.py` Q3/Q4 (disclaimer excluded).
- Evidence: inspected — three-phrase list; reported — C `test_fr007` pass; C4/C5 NEEDS_REVIEW.
- Uncovered: R8 broader list; never-display vs flag; quotation/refusal (semantic).
- Disposition (proposed): adopt Q3/Q4 + semantic complement. Owner: A/C.

#### Active architectural / governance

**ARCH-001** (Should/partial) → none — **D** (proposed); preserve layering.
- Impl: `test_layering.py` bans `yfinance` only; 4 direct vendor imports remain.
- Evidence: inspected — layering scoped to `yfinance`; reported — `test_layering` passes.
- Uncovered: router routing of all vendor access; import-boundary extension.
- Disposition (proposed): defer routing extension; preserve existing layering test. Owner: A.

**ARCH-002** (Must/proposed) → SEL-TA-FR-007 Q1–Q4 — **C** (preserved intent + proposed narrowing, unapproved).
- Impl: `checks.py` single `OutputChecker`, fail-closed, `CHECK_ERROR`.
- Evidence: inspected — one call site, Q1–Q4 only; reported — C `test_fr007` passes.
- **Preserved intent:** one deterministic, non-LLM component owns the check result; model text cannot set/bypass it; `PASSED` means only rule compliance, not truth.
- **Proposed narrowing (unapproved), per §5 corrected mapping:** R1→Q1; R8 only partially→Q3/Q4; R2/R3/R4–R6/R7 have **no complete deterministic equivalent**; Q2 (input-provenance match) is **new** and not a draft rule. Hence Q1–Q4 is a **narrowing replacement** of R1–R8, not a satisfaction of the full rule set.
- Uncovered: R2, R3, R4–R6, R7 (and the non-covered portion of R8).
- Disposition (proposed): retain preserved intent; label Q1–Q4 a **proposed narrowing** pending A; **do not redefine PASSED** (it certifies Q1–Q4 only). F9 is not a Q1–Q4 failure. Owner: A/B.

**GOV-001** (Must/proposed) → SEL-TA-GOV-004 — **C/P**.
- Impl: `tests/member_c_verification/live/*`; R1–R7 rubric (`semantic-evaluation.md`).
- Evidence: inspected — rubric/thresholds present; scorer F3/F4 defects present; reported — 10/10, 28/28, 4/4 at `git:e975528`; original artifacts absent here (F8).
- Uncovered: threshold/rubric approval status; scorer correctness; durable evidence.
- Disposition (proposed): adopt; keep existence vs approval vs evidence vs defects separate (§5). Owner: C/A.

**GOV-002** (Must/to be confirmed) → SEL-TA-GOV-001 — **C** (process).
- Impl: none; reference in `test-plan.md` §2.
- Evidence: inspected — approval described as a recorded human message in the transcript (attributable, not separately signed); text, approver identity, and chronology **not independently verified**.
- **Pending work (not a demand for a separate document):** verify the referenced approval — its **text**, **approver**, **chronology** (approval precedes first implementation commit), and **CI enforcement** — against the existing record. A separate signed artifact is **not** automatically required merely because the record is a transcript.
- Uncovered: verified approval + CI enforcement evidence.
- Disposition (proposed): adopt course gate; pending work is verification of the existing record and CI enforcement. Owner: E/human.

#### Withdrawn (kept; IDs preserved; no priority asserted)

- **REQ-TA-FR-002** GUI — withdrawn (out of scope). *No priority asserted.*
- **REQ-TA-NFR-SAFETY-001** exposure cap — withdrawn. *No priority asserted.*
- **REQ-TA-NFR-SAFETY-002 + Appendix B (NH-1…NH-5)** — withdrawn; *intent* reframed into conditional wording (FR-004/005). This is a **proposed replacement of intent**, unapproved.

---

### 3. Coverage vs. implementation, and "satisfy" vs "replace"

- **Selection-registry coverage** ≠ **upstream implementation**. E.g., FR-007's *meaning* is
  in the selection (FR-004/005); the *implementation* of the Hold meaning is a small project
  edit, while resume/look-ahead/staleness are **baseline safeguards** that the project does
  not re-implement or claim as contribution.
- **Satisfying vs replacing:** where a draft requirement's intent is expressed differently
  (stop vocabulary, logging sink, coverage of ratings, evaluation comparison rule), this
  document labels it a **proposed replacement/reframing**, not "satisfied". Replacements
  are unapproved and require A's decision.
- **Preserved baseline safeguards (not replaced):** upstream free-text fallback, resume,
  per-channel look-ahead guards, price-staleness guard, layering test.

---

### 4. SEC-001 in context (deterministic vs semantic)

Deterministic authority **exists** for the check and outcome (Q1–Q4, outcome typing,
fail-closed, `CHECK_ERROR`). What is **missing** is deterministic protection over a
coverage record (that feature is deferred), and **semantic** persuasion resistance is the
only test posture for narrative-level injection. Therefore SEC-001 is *partially* covered
by real deterministic authority plus semantic testing — **not** "semantic-only", and **not**
a blanket injection-proof guarantee.

---

### 5. Verification-evidence state (separated)

**R1–R7 rubric / thresholds — four separate facts:**
1. **Exists:** `semantic-evaluation.md` defines R1–R7 (1/0/N/A), applicability C1→R1,R4 … C5→R4,R5,R6,R7, thresholds (≥9/10 completed, ≥1 valid report/case, ≥90% semantic, 0 critical, challenge exposure all).
2. **Reported result (attributed):** 10/10, 28/28=100%, 4/4 exposure at `git:e975528` — **not re-verified here**.
3. **Approval status:** approval is a **recorded human message in the transcript**, not a separate signed artifact. I inspected that this is how approval is *described/referenced*; I did not open the raw transcript to verify text or chronology. That is an **attributable, non-signed** mechanism — not deficient because it is a transcript.
4. **Scorer defects (separate):** F3 (sparse/unrelated sheet → PASS), F4 (failed starts hidden from denominator). Rubric existence ≠ approval ≠ evidence ≠ scorer correctness.

**R1–R8 → Q1–Q4 mapping (corrected):**
- **R1 → Q1** (rating readable).
- **R8 → partially Q3/Q4** (disclaimer + some prohibited phrases; not the full R8 list).
- **R2, R3, R4–R6, R7 → no complete deterministic equivalent** in Q1–Q4.
- **Q2 is new** (input-provenance fragment match) — not an upstream/draft rule.

**Original-vs-selected logging sink scope:** draft OBS-001 = "every line of both sinks" with
six fields (JSON state file + plain-text CLI log). Selection NFR-002 = a *new* JSONL
lifecycle sink with the input/engine/output node vocabulary and elapsed_ms/event_outcome;
it does **not** claim upstream state snapshots are JSONL. Different scope; a reframing.

**Configuration-inventory gap:** the draft REPRO-001 enumerated the recorded-key set
(`DEFAULT_CONFIG` minus a named excluded set) and a 10-key one-key-diff test; the selection
NFR-004 names "safe effective config" without that full enumerated inventory. This is an
**open gap** if the reproducibility claim is retained.

**Historical attributed results (not fresh, not proof):**
- Offline suite at `ee7a0a8`: 1,500 passed / 2 skipped / 1 deselected / 100 subtests (review record).
- C offline mapping: 80 passed; baseline 1,412 passed / 1 failed (BD-001 environmental).
- Live diagnostic: 6 started / 5 completed, `formal_gate_pass: false`; C4/C5 NEEDS_REVIEW (Q4).
These are as-recorded, source-revision-scoped, and do not establish compliance.

---

### 6. Configuration inventory gap (detail)

If a final baseline retains reproducibility, it must state the recorded config inventory
explicitly (which `DEFAULT_CONFIG` keys are recorded, which are excluded and why, and how
secret endpoints are represented). The selected text does not yet do this; the draft did.
**Proposed, unapproved:** A/B decide whether to restore an enumerated inventory or accept a
narrower declared set, with the one-key-diff comparison defined over **config objects only**
(identity/timing/results excluded).

---

### 7. Feasible final-scope alternatives (for A)

Neither option assumes every old requirement or only the selection. Course-compliance is
**not** inferred from green gates in either option.

#### Option 1 — Complete the selection (recommended baseline; A decides)
- Scope: SEL 7 FR + 6 NFR + 6 GOV as runtime scope; other originals deferred with rationale; three withdrawn stay withdrawn.
- **Mandatory course obligations** (D1–D9, six gates, branch protection, transcripts, report, demo) are **separate delivery obligations** and are **not** discharged by this runtime scope.
- **Category coverage:** functional ✓, invariants ✓, quality/observability ✓, reproducibility ✓ (with config-inventory caveat), governance ✓, security ✓ (bounded); **performance/cost ✗ (proposed deferral)**.
- **Eligibility question (not settled):** with performance/cost unaddressed, Option 1 may be
  eligible only as an **A-justified decision or instructor clarification**; the intro's
  performance/cost items are **examples/aspirations**, not named blocking gates, which
  supports (but does not itself settle) deferral.
- Enhancement beyond upstream: optional confirmed portfolio + frozen provenance + atomic
  run isolation + bounded deterministic check + structured events. Baseline safeguards are
  preserved, not counted as contribution.

#### Option 2 — Selection + justified additions (A decides)
- Independently selectable additions (do not bundle):
  - **Call cap (COST-002):** *testable offline*, but implementation is a concurrency-safe pre-dispatch cap — separate implementation cost. Production-default cap selection is a **separate measured decision**.
  - **Timeout/cancellation (PERF-002):** needs cancellation/isolation design; independently selectable.
  - **Success cap (PERF-001):** requires **live measured** wall-clock; independent.
- Performance/cost category can be restored only by A adopting specific additions.

**Recommendation:** Option 1 as the working proposal now, with performance/cost recorded as
an **unresolved eligibility decision** for A (or instructor clarification); COST-002 appears
as a flagged, separately selectable candidate — not silently dropped.

---

### 8. Preserved semantics (non-negotiable in this proposal)

- Both input modes supported; optional portfolio retained.
- Missing portfolio = unknown; explicit empty positions = supplied flat; nonempty portfolio may lack target position; missing cash = unknown, not zero.
- Empty positions are valid and **must not force Hold**; any research rating allowed.
- Research rating ≠ account instruction; portfolio guidance conditional on supplied facts.
- `COMPLETED` + `REVIEW` + `NEEDS_REVIEW` valid; `INCOMPLETE` + no rating + `NOT_RUN` valid.
- Q1–Q4 are deterministic and fail-closed; PASSED certifies **only** Q1–Q4.
- F9: wording defect on flat snapshot ≠ check failure ≠ feature defect; a new authoritative check is **not** proposed here.
- Remote branch protection: **UNKNOWN**.

---

### 9. Unresolved decisions (owner-tagged; none approved)

1. **A** — Confirm scope change research-only → optional holdings.
2. **A** — Authoritative stop-reason vocabulary (draft vs selection).
3. **A** — COST-002 Must→defer downgrade acceptable? (flagged)
4. **A** — SEC-001: is deterministic Q1–Q4 authority + semantic persuasion testing sufficient, or is a new deterministic coverage protection required?
5. **A** — Option 1 vs Option 2; and performance/cost deferral eligibility (justified decision or instructor clarification).
6. **A/B** — F9 resolution direction (prompt/context fix only vs new authoritative check).
7. **A** — Approve or reject reliance on the reduced-coverage raw primitive (R-API).
8. **A/B** — Configuration-inventory gap (§6): restore enumerated inventory or accept narrower declared set.
9. **A/B** — Logging-sink scope: adopt lifecycle JSONL reframing vs restore draft two-sink scope.
10. **C** — Fix F3/F4/F5; supply/verify F8 evidence; record approval mechanism as found.
11. **C/A** — Freeze semantic rubric (R1–R7), population, and ≥90% as explicitly approved (as a recorded approval, not inferred).
12. **D** — Fix F1/F2/F6/F7, then F9; regression without weakening assertions.
13. **E** — Install D3/D7 blocking gates per course list; report branch-protection state (UNKNOWN until inspected); assemble trace matrix.
14. **Instructor** — Source/test layout (`src/`/`test/` vs current), transcript interpretation, demo grading; and performance/cost expectation.

---

### 10. Proposed Stage 2 outputs

#### 10.1 Proposal-directory outputs (all under `docs/req/proposals/`; candidate, `owner_of_authority: A`)

These are **proposal files only**; they are never written to A's canonical paths unless A
expressly authorizes it.

1. `reconciliation-2026-11-20.md` (this file).
2. **A-ready candidate registry** `SEL-TA-registry.candidate.yaml` — reflects the
   **human-approved scope as decided by A**, not a preselection of SEL only; each entry
   carries original ID, SEL map, chosen disposition, and A-decision reference.
3. **Candidate schema** `req-schema.candidate.json` — candidate only.
4. **Candidate change-log** `change-log.candidate.md` — entries for A to copy after confirmation.

#### 10.2 Separately authorized conditional architecture updates (B-owned; NOT written in Stage 2)

Only after A adopts an actual decision, and only with the owning member's authorization:

5. **ADR** — created only if A adopts an actual decision (e.g., stop-vocabulary change, a
   new authoritative check, or the logging-sink reframing); otherwise **no ADR** is created.
6. **Traceability input** — appended to `docs/architecture/traceability-inputs-member-b.md`
   (B-owned) for E's matrix assembly, conditional on the reconciliation being accepted.

**Guardrail:** one authoritative baseline stays with A. This proposal and any Stage 2
candidate are never silently promoted to A's canonical files; §10.2 items do not occur until
authorized.

---

### 11. Assumptions behind effort estimates (if any are later given)

Effort figures (when used) are **ESTIMATES** that assume: existing seams (input service,
checker, finalizer, persist) are reused; fixes are localized; no new measurement rig is
built; and no Option-2 or new authoritative check is adopted. They are not commitments and
shift with scope. Offline test cost and implementation cost are treated as **separate**
quantities throughout.

*End of proposal. No canonical requirements, schema, architecture, code, tests, or
governance were edited. Nothing was committed or pushed. Remote branch protection remains
UNKNOWN.*
