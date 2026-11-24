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

### 2026-11-24 (later still): token-context feature documentation (source-inspected)

A further **documentation-only** pass aligned architecture with E's concise intermediate-context feature and with the current main/PR state. It records source inspection, not implementation.

- **State at inspection:** local `main` `8bf739565d42c7d8ea972779ffd754c0d065b830` (merge of PR #17). Feature `9102759caaa59d778ba49cd57a1306f5f2ee5d88` (PR #18, `aa3b02d` code) is a **fast-forward descendant of main, open and unmerged**; code inspected via `git diff`, not merged. Main does **not** contain the optimization.
- **Documented as feature-branch implementation, pending integration**, distinct from main integration. Measured savings are **E-reported** (optimized mean 104,459 vs historical 138,896.5 = 24.7936%, and same-day control 160,826 = 35.0484%; single NVDA case, no ablation) and distinct from (i) the existing per-prompt guard and (ii) ADR-002's unimplemented run-wide `CALL_CAP`/`BUDGET` controller.
- **Verification:** supervising review reproduced **49 offline tests** in an isolated feature snapshot; E reports 1,797 full-suite passes (not rerun here). Compaction-reference test mocks the guard (selection/restoration branch only). No live calls made in this pass.
- **PR #18 approval checks failed**; prior approval is **not established** by the inspected evidence. No approval was created, relocated or backdated; the cause is not asserted.
- **New decision record:** `docs/architecture/adr/003-concise-intermediate-context.md` (retrospective source analysis + current rationale; explicitly not a past ADD experiment/comparison/approval/ablation). C2 selection, C1/C2/C3 history and ADR-002's proposed slices are unchanged.

**Reference-boundary correction (focused follow-up, documentation only).** An independent synthetic reviewer probe (`docs/reviews/evidence/token-context-reference-probe-2026-11-24.json`, no paid calls) demonstrated that a **short** argument replaced by a **longer** reference notice can make the reference form exceed the guard target even though the restored-original length fits; checking only the restored-original length can therefore miss compaction of the reference form and its cited history. The unconditional "reference can never outlive..." claim was removed from ADR-003 and interface-contracts §3.11; the demonstrated boundary is recorded and a fix/regression is handed to **E** (reference notice no longer than the replaced argument, or evaluate the reference form) and **C** (reproduce the synthetic boundary and assert the delivered prompt never cites trimmed history). Recorded as `risk-list.md` R-CONCISE. No implementation was changed; the feature remains unmerged. Prompt-placement wording was also corrected (analyst path = assembled system message; researcher/risk path = assembled prompt strings), and `prompt_hash` §3.8 restored to its exact byte construction with a new `R-HASH` entry for the unreadable-file skip.

### 2026-11-24 (architecture update at `5672a79`): integration status, registry alignment, token admission

Documentation-only drafting pass; source inspected, nothing implemented.

- **Baseline:** main `5672a79` (previous pin `ddfcaf3`→`47c8a28`→`5672a79`). Concise intermediate-context optimization now **integrated at `adb4dfc`** (PR #18 merge, ancestor of HEAD); dangling-reference boundary, quality acceptance and prior approval remain **open**. Requirements relocated to `docs/req/` (36 entries, schema 1.2.0, `proposed_for_adoption`; `REQ-TA-INV-014`, `REQ-TA-GOV-004` present). **COST-001 comparison-wording cleanup resolved at `5672a79`** (old blanket "different configuration" ban removed; named-experimental-factor wording retained) — no A follow-up.
- **New design (proposed):** cumulative token admission (`REQ-TA-NFR-COST-001`) — ADR-004 selects **Alt-B** (known-usage settlement with UNKNOWN retention); interface-contracts §15A; INV-20; catalog R23/R24; memory §10. **No new serialized stop reason** (violation → `INTERNAL_ERROR`; ordinary required-refusal → `BUDGET`; `PERSISTENCE_ERROR` primary). Beside §15's call cap, which keeps its counting semantics.
- **Preserved:** C2 selection/history; ADR-002 call-cap design; **ADR-003 stays Proposed** (integration recorded separately); evaluation tables/option ledger unchanged.
- **Not added:** no experiment, approval, measurement, or adoption of `TOKEN_BUDGET`/`CALL_CAP`/120000; parameters remain unset.

### 2026-11-24 (baseline `2efbf0f`): requirements schema-gate governance integration

Documentation-only factual governance-status correction based on the source/evidence review `docs/reviews/requirements-schema-gate-review-2026-11-24.md` and its evidence JSON. No architecture experiment, candidate comparison, approval, original-engineering claim or runtime-behavior change is added.

- **What changed (PR #26, merged at `2efbf0f`):** a `requirements schema` job in `.github/workflows/ci.yml` runs `scripts/ci/check_requirement_schema.py` (wrapping A's `docs/req/validate.py`) and `tests/member_d_verification/test_requirement_schema_gate.py`; governance instructions in `docs/code-governance/requirements-schema-gate.md`. It touches no `tradingagents/`, `cli/`, requirements YAML, JSON schema or A's validator.
- **Observed verification (supervising review):** registry 36 entries / 3 withdrawn / 0 errors / 0 warnings; 16 targeted probes pass; dependency/style checks pass; main schema job success; negative probe PR #27 fails the schema job and was closed unmerged. Local virtual environment initially lacked `jsonschema`; declared dev deps installed (no tracked dependency files edited). **No live model calls.**
- **Merge-protection activation is E-reported:** E reports `requirements schema` is required alongside the original four with strict protection retained and the probe observed blocked. The administrative required-check endpoint returned **HTTP 401**, so this session did **not** independently inspect the protected setting; an empty rulesets response does not prove classic protection absent. Recorded as **E-reported**, not inspected here.
- **Distinctions preserved:** `SEL-TA-GOV-002` → `REQ-TA-GOV-004` (schema validation) is this gate; **`SEL-TA-GOV-004` = semantic evaluation (`REQ-TA-GOV-001`)** is separate and still pending. OpenCode per-role permission enforcement, paused `test approval` enforcement, independent semantic acceptance, registry **adoption** (`proposed_for_adoption`/`proposed` unchanged), OQ-16 consent and OQ-17 population remain **separate** open items. Green schema CI is structural only — not adoption, not semantic adequacy, not an original-engineering claim.
- **Preserved:** C1/C2/C3 history, C2 selection, ADR-002/003/004 reasoning, and earlier dated logbook entries (including the `a62b801`/`5672a79` baseline notes and the explicitly historical registry pre-gate note) are unchanged.
