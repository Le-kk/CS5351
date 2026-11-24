# Evaluation Logbook (Member B)

Status: architecture draft. Process/evidence record for architecture choices. It records the actual session decisions and their rationale; it does **not** invent test/implementation/course approvals, measurements or transcripts. **Process approvals that did occur** (Brian's Stage 1 plan approval, Stage 2 candidate-comparison approval, C2 selection, and Stage 3 write-set approval) are recorded below as real human process events. **Absent and not claimed:** C's test approvals/evidence, D's implementation approvals, E's governance installation, and course/instructor acceptance. The authentic exported session is preserved separately by Brian/E and is not reconstructed here.

## Timeline (session 2026-11-12)

1. **Stage 1 — evidence & plan.** Inventory of supplied inputs (`Prompt.md`, `docs/req/selected-requirements.md`, `docs/project-deliverables-and-ownership.md`); baseline facts cited (portfolio loader, CLI, reporting, prompts). Confirmed `tradingagents` 0.7.1. Reported governance absent (`AGENTS.md`, `.opencode/`). Proposed candidates, criteria, write set. **Stopped for review.**
2. **Brian corrections (Stage 1 review):** CI inventory corrected (upstream `.github/workflows/ci.yml` exists; team gates missing). Fixed working decisions treated as session inputs. Mapping corrected to include prompt/context semantics (both managers' legends contain current-position wording). Candidates neutralized; C3 scoped to single-run. Output sinks enumerated; fingerprint = full 64-char SHA-256; blueprint convention recorded. Approved Stage 2 only.
3. **Stage 2 — candidates & evaluation (corrected).** DQ1–DQ10 matrix for C1/C2/C3 with rationale; six-criterion weighted scores with rationale/uncertainty; corrected sensitivity scenarios normalized to 100% (scenario (b) = 3.156/4.800/4.000); sink handling table; disclosure sequencing (notice before consent; transmit after); refined C2 lifecycle coordinator. **Stopped.**
4. **Brian selection:** approved C2; rationale = explicit input/snapshot boundary, test seams, shared provenance, without C3's broader orchestration change; human choice on estimated tradeoffs, not verified superiority. Approved Stage 3 document writes with corrections (this draft set).
5. **Stage 3 — authoring (this draft).** Authored the approved B write set. Document-consistency review performed; no application verification.

## Score summary (design estimates)
Baseline: C1 3.300 · C2 4.650 · C3 3.750. Scenario (a): 3.425 / 4.525 / 3.500. Scenario (b): 3.156 / 4.800 / 4.000.

## Honesty notes
- No implementation, tests, measurements or transcripts were produced.
- Process approvals recorded (Brian): Stage 1 plan/write-set scope; Stage 2 candidate comparison; C2 selection; Stage 3 document-write authorization. **Not** produced or claimed: C test approvals/evidence, D implementation approvals, E governance installation, course/instructor acceptance.
- Estimates are labelled; pending C test IDs and D/E links remain pending in `traceability-inputs-member-b.md`.
- Governance was not installed at drafting; see `risk-list.md` R-GOV.
- Post-review revision logged in `docs/reviews/member-b-stage3-review-2026-11-12.md`; this file does not edit that review.

## 2026-11-24 implementation-alignment revision (documentation only)

A later documentation pass, authorized by the 24 November handoff, aligned B's architecture documents with the actual `a62b801` checkout and the [24 November integration review](../reviews/project-integration-review-2026-11-24.md). It **preserves** the Stage 1–3 history, the C1/C2/C3 comparison, the C2 selection and Brian's estimated rationale; it performs **no new candidate generation, approval or measurement**.

- Recorded: component names/paths are now implemented (verified against source); stop-reason vocabulary is five values (no `BUDGET`); findings are blocking-only; Q1–Q4 only; optional-portfolio scope disagreement with the uploaded `REQ-TA-*` candidate remains unresolved; `REQ-TA-INV-014`/`REQ-TA-GOV-004` are pending publication.
- Broader `REQ-TA-*` extensions (R1–R8, evidence/coverage registries, `BUDGET`, aggregate budgets, resume) are documented as **PROPOSED / NOT IMPLEMENTED**, not as adopted or verified work.
- C's verification tests now exist under `tests/member_c_verification/offline/` and are cited by path; independent acceptance remains C's verdict and is **not** claimed here.
- Note: the previously cited Stage-3 review path `docs/reviews/member-b-stage3-review-2026-11-12.md` is **not present** in the checkout; the recorded process above is unchanged by its absence.

## 2026-11-24 engineering-contributions addendum (documentation only)

Added an engineering-contributions section to the canonical blueprint (§8A) covering the three project-specific design threads named in the readiness review §7 and the work plan §3.1/§6: (1) protected portfolio facts across Research Manager/Trader/Portfolio Manager; (2) separation of model advice from authoritative provenance/check results with truthful publication and failure handling; (3) evaluation-evidence integrity (case/config/artifact correspondence, counterfeit rejection, unsuccessful-attempt accounting). Traceability inputs gained a matching §4.

- **No new design iteration, candidate evaluation, experiment, approval or measurement** is recorded. This addendum indexes **existing** R2/R3/R4/R5 repairs and retained tests/evidence; it does not add an ADD cycle.
- **Overstrong-claim correction:** ADR 001's R4 wording was revised from "cannot assert a nonexistent position" to **prompt grounding** — the trusted facts are deterministically delivered, but narrative compliance is semantic and pending C's GOV-004 acceptance.
- **Distinctions preserved:** video product demonstration ≠ original-SE explanation ≠ traceability/governance evidence; standard techniques are not claimed as inventions; no experiment/approval/ADD cycle is fabricated.
- The earlier Stage 1–3 history, C1/C2/C3 comparison, C2 selection and estimated rationale remain unchanged. Unused calendar and ownership assignments from the work plan are **not** reactivated.

### 2026-11-24 (later pass): attribution, privacy crosswalk, and extended-design records

- **Evaluator attribution (roles + verified commits):** the live evaluator originated as Member C's supplied tooling (`f66fc14`,`57b164c`,`b8c4a25`), hardened (`bb777d5`), with R2/R3 repairs and `member_b_remediation` regressions in the supervised OpenCode repair session under a Brian-approved plan (`56bbe29`); `replay_store.py` was introduced in `56bbe29`. A commit records submitted changes, not manual authorship. C's independent acceptance pending.
- **Privacy crosswalk corrected:** `SEL-TA-NFR-003` is broader than uploaded `REQ-TA-SEC-002` (credentials only); relationship is **partial**, the holdings-minimisation half maps to no registered entry (candidate-only `INV-010`, not in the registry), per the open scope/profile contradiction (OQ-13).
- **Extended design recorded separately:** ADR 002 and interface-contracts §13–§16 add implementation-ready (proposed) designs for evidence/coverage, output-check v2 (R1–R8 incl. corrected-finding R5), and the run budget controller. These are a **genuine new design cycle for the new requirements**, not a reopening of C2 and not an invented historical ADD cycle.
- **No experiment/approval/measurement added.** Feasibility estimates are labelled; adoption decisions remain open.
