# Traceability Inputs — Member B (for E)

Status: **revised 2026-11-24** (implementation-aligned). This is B's contribution of component/invariant/runtime-monitor rows for E's shared `trace-matrix.md`. B does **not** publish a competing final matrix (E owns assembly). Implementation links now point at **real source/CI paths** (verified); test links point at real owning test files — FR/NFR rows cite **C-owned** independent-verification tests (C reports their status), and the GOV-002 row cites a **CI gate probe** (E/D-owned) that is **not** C's independent acceptance. B does not certify results. E has assembled the final [trace-matrix.md](trace-matrix.md) (E-owned; B does not edit it).

Legend: **Enforced-by** = design component present in the checkout; **Fallback** = concrete behaviour; **Monitor** = runtime observation; **Test** = owning test file (existence only; not a pass claim) — the FR/NFR rows cite **C-owned** independent-verification tests, while the GOV-002 row cites a **CI gate probe** (`test_requirement_schema_gate.py`, E/D-owned) that is **not** C's independent acceptance; **Impl** = source/CI path (verified).

## 1. Working selection `SEL-TA-*` (implemented baseline)

| Req ID | Enforced-by (present) | Distilled invariant | Runtime monitor / event | Fallback | Test (owned; existence only) | Impl (verified) |
|---|---|---|---|---|---|---|
| SEL-TA-FR-001 | `PortfolioInputService.discover` | INV-01 | `input.selection` | reselect/cancel; zero LLM | `tests/member_c_verification/offline/test_fr001_discovery.py` | `tradingagents/runapi/input_service.py` |
| SEL-TA-FR-002 | Coordinator consent | INV-09 | `input.consent` | decline → no run | `tests/member_c_verification/offline/test_fr002_consent.py` | `tradingagents/runapi/execution.py` |
| SEL-TA-FR-003 | `PortfolioInputService` precheck+freeze | INV-01/INV-02 | `input.mode_resolved` | stop pre-dispatch | `tests/member_c_verification/offline/test_fr003_validation_freeze.py` | `tradingagents/runapi/input_service.py` |
| SEL-TA-FR-004 | RunContext + prompt/context semantics | INV-02/INV-13 | `input.mode_resolved` | render frozen notice; keep unknowns | `tests/member_c_verification/offline/test_fr004_propagation.py` | `tradingagents/agents/context.py`, `tradingagents/runapi/context.py` |
| SEL-TA-FR-005 | Reporting labels + `rating.py` | INV-13 | `output.check` | REVIEW stays REVIEW | `tests/member_c_verification/offline/test_fr005_ratings.py` | `tradingagents/runapi/reporting.py` |
| SEL-TA-FR-006 | `runapi/context.py` + reporting projection | INV-04/INV-05/INV-05b | `output.provenance` | refuse fallback to file/mtime; deep-immutable tuples | `tests/member_c_verification/offline/test_fr006_provenance.py` | `tradingagents/runapi/context.py`, `tradingagents/runapi/reporting.py` |
| SEL-TA-FR-007 | `runapi/checks.py` | INV-03/INV-08 | `output.check` | NEEDS_REVIEW; suppress badge | `tests/member_c_verification/offline/test_fr007_output_check.py` | `tradingagents/runapi/checks.py`, `tradingagents/runapi/finalize.py` |
| SEL-TA-NFR-001 | `OutcomeFinalizer` | INV-07 | `run.terminal` | typed incomplete | `tests/member_c_verification/offline/test_nfr001_failures.py` | `tradingagents/runapi/finalize.py` |
| SEL-TA-NFR-002 | `runapi/events.py` | INV-11 | `run.terminal` (count=1) | terminal-append failure best-effort: logical outcome preserved, `durable=false` | `tests/member_c_verification/offline/test_nfr002_events.py` | `tradingagents/runapi/events.py` |
| SEL-TA-NFR-003 | `Redactor` | INV-06 | `security.redaction` | redact before delivery | `tests/member_c_verification/offline/test_nfr003_privacy.py` | `tradingagents/runapi/redact.py`, `tradingagents/agents/structured.py` |
| SEL-TA-NFR-004 | `runapi/persist.py` + coordinator | INV-12/INV-14 | `output.persist` | run-ID isolation; refuse overwrite | `tests/member_c_verification/offline/test_nfr004_persistence.py` | `tradingagents/runapi/persist.py` |
| SEL-TA-NFR-005 | `runapi/execution.py` shared service + `cli/input_ui.py` | INV-10/INV-09 | `api.entry` | supported API traverses boundary; raw primitive reduced-coverage (A approval) | `tests/member_c_verification/offline/test_nfr005_layering.py` | `tradingagents/runapi/execution.py`, `cli/input_ui.py` |
| SEL-TA-NFR-006 | `RunRecord` aggregation (`runapi/result.py`; interface-contracts §10) | INV-21 (as-built) | `run.started`/`run.terminal` | zero-completed ⇒ `INSUFFICIENT_EVIDENCE`; unresolved counted | C: `test_nfr006_population.py`, `test_registry_result_repairs.py` (repair probes; **not** independent semantic acceptance) | `tradingagents/runapi/result.py` `summarize_records`/`RunRecord` |
| SEL-TA-GOV-001 | C/E/human (test-plan approval) | — | — | — | owned C/E | n/a |
| SEL-TA-GOV-002 | A (`docs/req/validate.py` cross-record) → E (`requirements schema` job) | `REQ-TA-GOV-004` schema validation | `requirements schema` CI job | gate non-zero on invalid; E-reported required | `tests/member_d_verification/test_requirement_schema_gate.py` (CI probe; **not** C independent acceptance) | `scripts/ci/check_requirement_schema.py`, `docs/req/validate.py`, `.github/workflows/ci.yml` |
| SEL-TA-GOV-003 | C/E (CI gates) | `type check`/`security checks`/`required tests`/`ruff`/`dependency`/`ai-log` jobs | CI job outcomes | blocking on failure | `test_type_gate.py`, `test_security_gate_boundaries.py` (E/D CI probes; **not** C independent acceptance) | `.github/workflows/ci.yml`, `scripts/ci/{check_security_scan,check_workflow_permissions}.py` |
| SEL-TA-GOV-004 | C/D/E (semantic threshold) | — | — | — | owned C/D/E | n/a |
| SEL-TA-GOV-005 | E/all (AI-use log) | — | — | — | owned E | n/a |
| SEL-TA-GOV-006 | B (permission design, `permission-model.md` §4a) → E (configure/enforce) | configured native profiles (last-match-wins) + launcher gate | launcher refusal / native probe denial | block denied write; hand to human/session | `scripts/verify_role_permissions.py` (E-native probes; **not** C acceptance) | `.opencode/permissions.jsonc`, `scripts/run_role_agent.py`, `.opencode/rules.md`, `.agent/rules.md` — E7 69 cases @1.19.5; local 1.18.34 **refused** |

All FR/NFR rows have an architecture allocation; the C test *files* above exist under `tests/member_c_verification/offline/`. **Passing status and independent acceptance are C's** and are not asserted here.

## 2. Provisional semantic crosswalk: `SEL-TA-*` → candidate `REQ-TA-*` (by meaning, not suffix)

The uploaded `REQ-TA-*` candidate uses different meanings for shared numeric suffixes. **Never map by suffix.** For example `SEL-TA-FR-003` is *input validation/freezing*, whereas `REQ-TA-FR-003` is *checkpoint/resume*. Relationship values: **same**, **partial**, **none/clash**, **proposed-only**. Status: `impl` = at least the `SEL-TA-*` baseline is implemented; the `REQ-TA-*` column is A's proposed obligation and is **not** claimed implemented.

| Working ID (`SEL-TA-`) | Implemented meaning | Candidate `REQ-TA-*` (meaning) | Relationship | Candidate status |
|---|---|---|---|---|
| FR-001 discover/select | portfolio file discovery + selection | — (candidate has no portfolio discovery; its FR-001 is *evidence IDs*) | none/clash | proposed-only |
| FR-002 explicit confirmation | consent gate | — (candidate FR-002 is *withdrawn*; its RUN-001 owns outcome fields) | none/clash | withdrawn |
| FR-003 validate/freeze snapshot | input precheck + freeze | `REQ-TA-INV-014` (frozen selection/fingerprint). *Not* `REQ-TA-FR-003` (=resume) | **partial** (A2) | proposed |
| FR-004 propagate explicit context | portfolio→prompt, no invented holdings | `REQ-TA-FR-004` = *point-in-time no look-ahead*; `REQ-TA-FR-007` ownership wording | partial | partial/proposed |
| FR-005 ratings vs actions | stage labels, REVIEW≠Hold | `REQ-TA-FR-007` rating meaning/labels/no ownership | partial | proposed |
| FR-006 deterministic provenance | frozen fingerprint identity | `REQ-TA-NFR-REPRO-001` run record; `REQ-TA-FR-006` freshness | partial | partial |
| FR-007 output-check authority | Q1–Q4 authoritative | `REQ-TA-ARCH-002` (R1–R8); `REQ-TA-INV-001` | partial | proposed |
| NFR-001 external failure | typed incomplete | `REQ-TA-NFR-001` **+ `REQ-TA-RUN-001`** (typed stop reasons) | **partial** (A2) | partial |
| NFR-002 observability | JSONL events | `REQ-TA-NFR-OBS-001` | same | partial |
| NFR-003 privacy | redaction/sinks; credentials **and** holdings minimisation | `REQ-TA-SEC-002` (**credentials only**) | **partial** | partial |
| NFR-004 immutable artifacts | per-run ID, atomic publish | `REQ-TA-NFR-REPRO-001` | same | partial |
| NFR-005 cohesive integration | shared boundary, no prompts in agents | `REQ-TA-ARCH-001` (vendors behind router) | partial | partial |
| NFR-006 evaluation population | started-run accounting; distinct case/aggregate counts; **duplicate-attempt rejection + declared population/control binding** (as-built) | `REQ-TA-NFR-EVAL-001` | same | **partial** — arithmetic + population/control binding implemented; expected-case completeness, general comparison and full `N_EVAL` acceptance remain gaps |
| GOV-001 test-plan approval | prior approval gate | `REQ-TA-GOV-002` | same | proposed |
| GOV-002 registry schema | schema validation: A's validator + `scripts/ci/check_requirement_schema.py` + `requirements schema` CI job + `test_requirement_schema_gate.py` | `REQ-TA-GOV-004` (schema validation — **not** semantic) | **same** (A2) | proposed (registry not adopted; gate implemented) |
| GOV-003 CI gates | lint/test/dependency CI gates | **none** — no registered coverage (**OQ-10**, A2); *not* `REQ-TA-GOV-003` (that is the AI-log gate) | **none** (A2) | open (OQ-10) |
| GOV-004 semantic threshold | semantic eval gate | `REQ-TA-GOV-001` (semantic; **not** `REQ-TA-GOV-004` = schema) | same | proposed (see §17) |
| GOV-005 AI-use log | AI-log-gated merge | `REQ-TA-GOV-003` | **same** (A2) | proposed |
| GOV-006 permissions/branch protection | default-intended-deny + native last-match rules + ADR review; OS ACL/identity outside current guarantee | — (no registered `REQ-TA-*` counterpart) | **none** | no candidate entry; configured+E-verified implementation recorded separately (E7 69 cases @1.19.5; conditional activation) |

**Candidate-only obligations with no `SEL-TA-*` counterpart** (proposed, not implemented): `REQ-TA-RUN-001` (six-value result incl. `BUDGET`), `REQ-TA-FR-001` (evidence IDs), `REQ-TA-FR-003` (resume), `REQ-TA-FR-004` (point-in-time), `REQ-TA-FR-005` (coverage/`NOT_REQUESTED`), `REQ-TA-FR-006` (freshness), `REQ-TA-FR-008`/`REQ-TA-INV-004..006` (sentiment), `REQ-TA-NFR-001..002`, `REQ-TA-NFR-PERF-001..002`, `REQ-TA-NFR-COST-001..003`, `REQ-TA-SEC-001`, `REQ-TA-ARCH-001..002`, `REQ-TA-INV-001..008`, `REQ-TA-GOV-001..003`.

> **NFR-003 is broader than its candidate row (correction 2026-11-24).** `SEL-TA-NFR-003` covers **credentials *and* holdings minimisation** (no raw portfolio bytes / other-position dump in sinks; source files read-only; unrelated-holding marker absent). Uploaded `REQ-TA-SEC-002` covers **credentials only**. So the relationship is **`partial`**, not `same`, and the **holdings half maps to no registered `REQ-TA-*` entry** — only to candidate-only `INV-010` clause 2 (profile A-C), which the YAML itself records as **not in the registry**. This was a **scope/profile contradiction** in the earlier snapshot (scope excluded portfolio files while profiles A-B/A-C required one, OQ-13). The current registry now **includes** optional portfolio input, so that particular contradiction is resolved; the **holdings-minimisation half** of NFR-003 still maps to no registered `REQ-TA-*` entry (candidate-only `INV-010` clause 2), and the confirmation-flow gap is OQ-16. Cross-references: `invariants.md` INV-06 (full privacy scope, correct) and `risk-list.md` R-PRIV.

## 3. Pending items (explicitly not invented)
- **`REQ-TA-INV-014` (immutable input) — present in the 36-entry registry** (`status: proposed`). Input freezing is covered by INV-04/05/05b; the ID is resolvable; adoption is still open.
- **`REQ-TA-GOV-004` (schema validation) — present in the registry** (`status: proposed`). **Implemented and locally/hosted verified** at baseline `2efbf0f` (PR #26): `.github/workflows/ci.yml` `requirements schema` runs `scripts/ci/check_requirement_schema.py` (wrapping A's `docs/req/validate.py`) and `tests/member_d_verification/test_requirement_schema_gate.py`; observed 36 requirements / 3 withdrawn / 0 errors / 0 warnings, 16 targeted probes passing, main schema job success, and a negative probe (PR #27) failing the schema job (closed unmerged). **E reports** the check is required on main with strict protection; the administrative endpoint could not be independently read (HTTP 401), so that setting is **E-reported**, not inspected here. This is `SEL-TA-GOV-002` → `REQ-TA-GOV-004`; **`SEL-TA-GOV-004` is semantic evaluation (`REQ-TA-GOV-001`), a different gate.** See `docs/reviews/requirements-schema-gate-review-2026-11-24.md`.
- **Optional-portfolio scope** — implemented here, and the current registry's scope statement **includes** optional portfolio input (profiles A-A/A-B/A-C); adoption is still open and confirmation-flow ownership is OQ-16.
- [trace-matrix.md](trace-matrix.md) (E-owned) **now exists**; these rows are B's input to verify against it (B does not edit it).

## 4. Engineering-contribution traces (for the D2 section and E's matrix)

Maps the four contributions in the canonical blueprint §8A to enforcing code, tests and retained evidence. These are **B's own remediation/design traces**, not C's independent acceptance. "Deterministic?" distinguishes deterministic enforcement from prompt-only grounding.

| Contribution | Design anchor | Deterministic? | Tests (exist; pass is owner's) | Evidence | Residual |
|---|---|---|---|---|---|
| 1. Protected portfolio facts (RM/Trader/PM) | `agents/context.py:214-273` (`get_portfolio_context_from_state`, `protect_context`); RM/PM/Trader templates | Facts **delivered deterministically** to all three stages and survive compaction; narrative **not** deterministically constrained | `tests/member_b_remediation/test_r4_research_manager_context.py`; C: `tests/member_c_verification/offline/test_fr004_propagation.py`, `test_fr005_ratings.py` | `docs/reviews/evidence/live-diagnostic-2026-11-18.json`; `docs/reviews/remediation-r1-r5-2026-11-21.md` | Prompt grounding ≠ "cannot assert"; Q1–Q4 ignores ownership wording; semantic acceptance pending C |
| 2. Advisory vs authoritative / truthful publication | `runapi/{checks,finalize,persist,events,reporting,context}.py` | **Yes** for Q1–Q4 authority, frozen provenance, conditional fields, single-commit publish, truthful `terminal_event.durable` | `tests/member_b_remediation/test_r5_terminal_visibility.py`; C: `test_fr006_provenance.py`, `test_fr007_output_check.py`, `test_nfr004_persistence.py`, `test_nfr002_events.py` | `docs/reviews/remediation-r1-r5-2026-11-21.md` | Q1–Q4 ≠ truth; terminal append best-effort; no power-loss guarantee |
| 3. Evaluation-evidence integrity | `tests/member_c_verification/live/score_gov004.py`, `replay_store.py` | **Yes** for case/config/artifact binding, counterfeit rejection, exclusive durable starts, all-start accounting | `tests/member_b_remediation/test_r2_scorer_correspondence.py`, `test_r2_r3_differential_pins.py`, `test_r3_replay_durability.py`; C: `tests/member_c_verification/live/test_score_gov004_exitcodes.py`, `test_harness_selfcheck.py` | `docs/reviews/evidence/live-verification-2026-11-21/` (`gov004_starts.json`, `cohort.json`, `ai-review-proposed-scores.json`, `rescore-results.json`, `integrity.json`) | Scorer ≠ human acceptance; narrow rubric; human score sheet unfilled (PENDING) |
| 4. Concise intermediate context *(integrated at `adb4dfc`)* | `agents/context.py` (`concise_analysis_instruction`, `opponent_argument_or_opening(...,history)`, `bound_debate_prompt`), `agents/analysts/turn.py`, `researchers/*`, `risk_mgmt/*`; config `default_config.py`, `graph/trading_graph.py`, `runapi/execution.py` | **Deterministic:** flag plumbing/metadata, exact Python string-substring reference, reconstruct-before-guard branch. **Advisory:** 450/220-word targets, evidence-preservation wording. No new forced truncation | Feature: [`test_token_input_reduction.py`@9102759](https://github.com/kelepawuqiusi/CS5351/blob/9102759caaa59d778ba49cd57a1306f5f2ee5d88/tests/member_d_verification/test_token_input_reduction.py); supervising local: **49 passed** (new test + `test_portfolio_context.py` + `test_r4_research_manager_context.py`), not E's 1,797 | `docs/reviews/token-context-architecture-review-2026-11-24.md`; `docs/reviews/evidence/token-context-review-2026-11-24.json`; `docs/reviews/evidence/token-context-pr-checks-2026-11-24.json` | E-reported measurements; token report + compact JSON **published/tracked** ([report](../verification/token-input-reduction-2026-11-24.md), [compact evidence](../../tests/member_d_verification/evidence/token-input-reduction-2026-11-24.json)); raw full-log/no-ablation limits remain; raw `run_transient` benchmark ≠ product acceptance; semantic acceptance pending C; approval checks failed, prior approval not established by inspected evidence |

**Video demonstration vs SE explanation vs traceability evidence** are distinct (blueprint §8A.4): the video shows product before/after; the SE explanation argues the project-specific design; the trace rows above + E's `trace-matrix.md` are governance evidence. None alone proves originality, and using standard techniques is not claimed as invention.

**Attribution for row 3 (roles + verified commits; 2026-11-24 correction).** The evaluator originated as Member C's supplied tooling (`f66fc14`, `57b164c`, `b8c4a25`), was hardened (`bb777d5`), and its R2/R3 repairs plus the `tests/member_b_remediation/` regressions were made in the supervised OpenCode repair session under a Brian-approved plan (`56bbe29`). `replay_store.py` was introduced in `56bbe29`, **not** with the original evaluator. A commit records submitted changes; it does not prove manual authorship. **C's independent acceptance remains pending.** These rows are B's design/trace documentation, not authorship of the evaluator and not a verdict.

## Notes
- Deferred requirements (selected-requirements §5) are **not** claimed satisfied and are omitted from §1.
- The candidate column is interpretive; A owns candidate meaning and the final crosswalk/adoption. An `impl` status on the working side does not imply the candidate obligation is met.
- §4 contribution rows are B's engineering traces for D2; they cite real paths/evidence but do not assert a passing verdict or replace C's independent acceptance.

## 5. Extended-design traces and implementation order (2026-11-24; PROPOSED, not implemented)

Requirement → proposed component/interface → proposed C scenario → implementation order for the new design (interface-contracts §13–§16, ADR 002). "Order" reflects the approved dependency sequence: budget first; evidence/coverage data contracts before R2/R7 checker integration.

| Req | Component (proposed) | B design | C scenario (proposed) | Order |
|---|---|---|---|---|
| `REQ-TA-NFR-COST-002`, RUN-001 `BUDGET` | `runapi/budget.py`; `result.py`; `finalize.py` | ic §15; ADR-002 D3 | B1–B11, P1–P4 | **1 (first handoff)** |
| `REQ-TA-FR-001` evidence IDs | `runapi/evidence.py` | ic §13.2; ADR-002 D4 | E1, E8 | 2 |
| `REQ-TA-FR-005` coverage | `runapi/coverage.py` | ic §13.2–13.3 (proposed catalog); ADR-002 D4 | E2–E6, E9–E12 | 2 |
| `REQ-TA-FR-006` freshness | dataflows (+coverage) | ic §13.4 | E5, E7 | 2 |
| `REQ-TA-FR-004` point-in-time | dataflows/agents (+coverage) | ic §13 | (§13 scenario set) | 2 |
| `REQ-TA-ARCH-002` R1–R8 | `runapi/checks.py` | ic §14 (single-verdict pipeline); ADR-002 D1/D2 | K1–K16 | 3 (after §13 for R2/R7) |
| `REQ-TA-FR-007` ownership (R3) | checker + prompts | ic §14.4; ADR-002 D2 | K2, K9 | 3 |
| `REQ-TA-FR-008` sentiment (R4–R6) | checker + schema | ic §14.1, §14.3; ADR-002 D1 | K11–K15 | 3 |
| `REQ-TA-NFR-REPRO-001` widen | `runapi/execution.py` | ic §16.1 step 4; §16.7 versions | config-diff/immutability; budget-only vs full-v2 examples | 4 |
| `REQ-TA-INV-014` / `REQ-TA-GOV-004` (present, `proposed`) | INV-014 → INV-04/05/05b; GOV-004 → `requirements schema` gate (implemented) | ic §11; oq8 reply; schema-gate review | reuse FR-003/FR-006; schema gate probes | proposed |
| `REQ-TA-FR-003` resume | CLI + checkpointer | ADR-002 D5 (separate) | — | optional/separate |
| `REQ-TA-NFR-COST-003` convergence | graph | — | — | optional/separate |

**Q2 preserved separately:** the trusted-provenance guard (ic §6.4) is independent of evidence-ID R2 in **all** rollout modes (§16.7); a run may fail one and pass the other (scenario K7/K8). No component here subsumes Q2.

**Version axes (AR24 06):** `schema_version` (manifest/result) and `check_rules_version` are separate; a schema-1 artifact with **no** `check_rules_version` takes the **explicit legacy path**; budget-only is `schema_version=2, check_rules_version=1` (Q1–Q4 kept); full v2 is `check_rules_version=2`; unknown/invalid combos are **rejected (fail closed)** — see ic §16.7.

**Correction notes (AR24):** coverage units ≠ vendor calls; the 12-row catalog in ic §13.3 is **visibly proposed** (11 router methods + 4 direct sources; “two bypass” undercounts) pending A's table; `NOT_REQUESTED` (never asked) ≠ `NO_DATA` (asked, empty) ≠ `UNAVAILABLE` (asked, failed); requested-core rule preserved with any unrequested-core **exemption surfaced as a requirements decision**; sentiment **both-paths-fail ⇒ INCOMPLETE/MODEL_FAILURE/NOT_RUN (no rating)**, usable-free-text-without-structured = **open policy case** (no invented rule); only **safe** correction fields persisted; final body **redacted before** evaluation/delivery.

**Proposed invariants:** INV-15 (evidence resolution/`REQ-TA-INV-002`), INV-16 (coverage equality/`REQ-TA-INV-007`), INV-17 (sentiment), INV-18 (budget, monotonic admission + exactly-once metering), INV-19 (single-verdict corrected-finding result contract) — all **proposed**, enforcers not yet built.

**Metering (budget):** controller attached to run tier chat-models (`trading_graph.py:79-80`); plain / `bind_tools(...).invoke` / `with_structured_output(...).invoke` each consume exactly one reservation; **no runtime guarantee claimed before probes P1–P4 pass**.

**Feasibility (ESTIMATE, not a promise):** budget+BUDGET is the most feasible offline slice; evidence/coverage is the largest deadline risk; full implementation of all new Must obligations before 25 Nov 2026 23:59 HKT is **not promised**.

### 5.3 Evaluation-population arithmetic — as-built H3 (merged) and residuals

| Req | As-built mechanism (present) | Tests (exist; owner reports status) | Truthful limit |
|---|---|---|---|
| `REQ-TA-NFR-EVAL-001` / `SEL-TA-NFR-006` | `runapi/result.py` `summarize_records` + `RunRecord.case_id` (interface-contracts §10; invariants INV-21) | C: `tests/member_c_verification/offline/test_nfr006_population.py`, `tests/member_c_verification/test_registry_result_repairs.py`; related `tests/member_c_verification/offline/test_registry_gaps.py` | Result-summary **arithmetic** (denominator incl. unresolved, completed numerator, null/0 fraction, distinct-case/aggregate counts with known explicit IDs, null/1/0 `population_result_count`, 20/40/1) **and** population validation (duplicate/blank attempt IDs, unknown categories, invalid present case IDs, bound-case/control membership; truthy `controlled_change` rejected **only in bound mode**) are implemented. **Remaining gaps:** no requirement that all declared cases be observed, no general before/after comparison reporter (unscoped path does not validate comparisons), no `N_EVAL`/full-population acceptance. Passing tests ≠ independent semantic acceptance. Whole requirement remains **partial**. |

### 5.1 Concise intermediate context — source revision, measurement limits, pending status (feature `9102759`)

- **Revision / integration:** code commit `aa3b02d`, feature tip `9102759caaa59d778ba49cd57a1306f5f2ee5d88` (PR #18), merge-base `8bf7395`. **Integrated into main via PR #18 merge `adb4dfc` (ancestor of current HEAD `5672a79`);** the dangling-reference boundary, quality acceptance and prior approval remain **open**. See `docs/architecture/adr/003-concise-intermediate-context.md`.
- **Feature files:** `tradingagents/agents/context.py`, `agents/analysts/turn.py`, `agents/researchers/{bull,bear}_researcher.py`, `agents/risk_mgmt/{aggressive,conservative,neutral}_debator.py`, `default_config.py`, `graph/trading_graph.py`, `runapi/execution.py`.
- **Config/fingerprint:** `concise_intermediate_reports` (default True) recorded in `run_settings()`/`EffectiveConfig`; the touched prompt sources are in `_prompt_hash`, so new-run `prompt_hash` differs even when concise mode is disabled. Legacy artifacts lacking the field are `unknown/legacy`, not today's default.
- **Confirmed vs pending (must not overclaim):**
  - **Confirmed (source-inspected + supervising local 49 tests):** mechanism present; tool schemas/call IDs/messages preserved; legacy switch restores; config recorded; 49 offline tests passed in an isolated feature snapshot. Not E's 1,797 (reported, not rerun here).
  - **E-reported, not reproduced:** optimized 99,532/103,120/110,725 (mean 104,459) vs historical 138,896.5 (24.7936%) and same-day control 160,826 (35.0484%); NVDA/2026-01-09, four analysts, English, 1+1 rounds, school `openai_compatible` + DeepSeek V4 Flash, isolated **empty memory** (distinct from an empty config or a confirmed-empty portfolio), no portfolio input, caching; exclusions (missing-price run; HTTP-429 8,299 partial = INCOMPLETE) and cached-price diagnostic disclosed. **No ablation.**
  - **Pending:** independent semantic/C acceptance; end-to-end compaction preservation (test mocks the guard); feature integration to main; the approval checks failed at `9102759` and prior approval is **not established** by the inspected evidence.
- **Not product acceptance:** the opt-in benchmark uses `TradingAgentsGraph.run_transient` (not `run_analysis_api`); its `COMPLETED` is not a Q1–Q4/R1–R8 verdict, semantic acceptance, or evidence that mandatory data were available.

### 5.2 Cumulative token admission — `REQ-TA-NFR-COST-001` (proposed; Alt-B)

Requirement → proposed component/interface → proposed C scenario. **Not implemented** (ADR-004; interface-contracts §15A).

| Req | Component (proposed) | B design | C scenario (proposed) | Order |
|---|---|---|---|---|
| `REQ-TA-NFR-COST-001` | `runapi/token_admission.py` + §15 `AdmissionCoordinator`; metering seam `ChatOpenAI._create_chat_result` (`llm_clients/openai_client.py`) | ic §15A (incl. §15A.6 seam); ADR-004 (Alt-B) | T1–T15 (§15A.8) | after §15 call cap; beside it |
| `REQ-TA-NFR-COST-002` (call cap) | §15 `RunBudgetController` | ic §15 (unchanged counting) | B1–B11, P1–P4 | existing |

**Accounting invariant:** `K+R+U+(input_bound+output_allowance) <= TOKEN_BUDGET`, **conditional on the asserted request bounds**; a detected bound/protocol violation is recorded (no clamp) and visible. **No new serialized stop reason:** violation → `INTERNAL_ERROR`; ordinary required-refusal → `BUDGET`; `PERSISTENCE_ERROR` primary. UNKNOWN stays in U to finalization (no late U→K).

**Parameters left unset (no adoption):** `TOKEN_BUDGET`, `CALL_CAP`, input bound/multiplier, output allowance, 120000 candidate, quality/profile. **Input accounting method and UNSUPPORTED-profile behaviour are required design, not parameters.**

**Source revision (updated):** main **`6b57aad`** (this pass). Concise optimization integrated at `adb4dfc`. Requirements at `docs/req/` (36 entries, schema 1.2.0, `proposed_for_adoption`). CALL-CAP (`RunBudgetController`/`budget_transport.py`) and H3/H5 repairs are **merged**; cumulative-token (§15A/ADR-004) and R1–R8 remain **proposed/unimplemented**.

### 5.4 Delivery evidence, trace-matrix link and A-requirement conflicts (implementation `6b57aad`; A requirements update `6b46854`, 2026-11-25)

- **E-owned final matrix:** [trace-matrix.md](trace-matrix.md) now exists (E1, baseline `761918e`). It is **E-owned; B does not edit it**. B's §1/§2 rows above are the inputs to verify against it; discrepancies are reported to **E**, not silently reconciled here.
- **Token-optimization evidence (now published/tracked):** [optimization report](../verification/token-optimization-architecture-and-measurement-report-2026-11-24.md), [token-input reduction](../verification/token-input-reduction-2026-11-24.md), and [compact evidence](../../tests/member_d_verification/evidence/token-input-reduction-2026-11-24.json). **Retain** the historical/no-ablation/quality limits — compact evidence ≠ raw full logs, and measured savings ≠ a hard budget.
- **A2 crosswalk applied by meaning** (A-owned corrections to B's provisional table): FR-003→`REQ-TA-INV-014` partial; NFR-001 also `RUN-001`; `GOV-003` CI gates have **no** registered counterpart (OQ-10) — distinct from `GOV-005` AI-log → `REQ-TA-GOV-003`; `GOV-002` schema → `REQ-TA-GOV-004` (**not** semantic `GOV-004`).
- **A-requirement clarifications now recorded (OQ-19/OQ-20):** OQ-19's entry point is **acknowledged** — `summarize_records(records, *, population=None)` with `score_gov004.py` printing the fields; the repeated "where do the counts come from" question is **closed** in current status, while **general comparison acceptance remains unestablished** (the helper refuses bound comparisons). OQ-20 records **PILOT nonblocking while `QUALITY_THRESHOLD` is open** (deferred *gate*, not a behavior waiver); the four minimum behaviors (`FR-005` disclosure, `FR-007` ownership, `SEC-001` injection, `SEC-003`/`INV-008` guarantee/disclaimer) remain **required in both phases and not claimed to pass**; the **five cases / two trials are a project trial**, still **five cases** vs provisional `N_EVAL=20` (no lowering; `QUALITY_THRESHOLD` D/E-owned). See interface-contracts §17.
- **Still-unresolved A wording (flag, do not edit A):** (1) `REQ-TA-NFR-EVAL-001` fit's "both counts null without a population" conflicts with its own note/code (distinct_case_count remains countable from explicit IDs; empty ⇒ aggregate 0) — observed in §5.3/§10; **A to reconcile**. (2) **H5 — new conflict:** A now **acknowledges** the leading envelope, but the note still calls `envelope + body` noncompliant **because** `render_body` appends a footer, even though the same note/OQ-18 **explicitly permits a retained compatibility footer**; the normative first-visible rule has **no one-copy-only restriction**. B **retains the leading notice + compatibility footer** (Q3 checks the rendered body; the envelope supplies the leading notice) — **flagged to A** to reconcile the prose (B does not edit requirements or remove the footer).
- **Status boundary:** call-cap/BUDGET emission exists; H3/H5 repaired; R1–R8/evidence/coverage and cumulative-token/time caps are **unimplemented**. Tests passing ≠ independent semantic acceptance or full requirement satisfaction. The H5 synthetic renderer/check probe (first line `DISCLAIMER`, current `PASSED`, footer-removal ⇒ Q3 `NEEDS_REVIEW`) is **developer evidence**, not semantic acceptance.
