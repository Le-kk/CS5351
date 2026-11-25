# Historical record — requirement-test-mapping.md

Archived 25 November 2026. [Current document](../requirement-test-mapping.md) · [History index](README.md)

This archive preserves the earlier narrative and observations. Relative Markdown links are rebased; missing referenced files are identified inline. Current outcomes and acceptance status are in the current document.


> **Member C correction — 2026-11-25:** Historical sections below are preserved as batch records, not current acceptance. See the reconciled batch ledger (unavailable record: evidence-reconciliation-2026-11-25.md) and inspected evidence inventory (unavailable record: evidence-inventory-2026-11-25.json) for source/environment/command boundaries, requirement-to-node mappings and evidence limitations. The latest retained final dirty-snapshot developer regression reports 1918 passed, 1 skipped and 1 deselected; it was not run at current HEAD 6d2e3d98bb213270aa0a13beac515aee43980c77. Historical GOV-004 PASS/10-of-10/28-of-28 claims are **UNVERIFIED; independent acceptance PENDING** because original summaries/reports/scores cannot be audited. Eight passing semantic self-tests are not live acceptance. Earlier “latest”, “current”, missing-BUDGET, failing-CORRECTED, REVIEW/PASSED and disclaimer-failure statements apply only to their original batches. No requirement adoption or human sign-off is inferred.

> Latest results: Linux rerun below reports 1882 passed / 26 failed; earlier Windows counts remain historical.

> 2026-11-25 classified handoff: failure investigation and owner actions (unavailable record: registry-test-update-2026-11-25.md#failure-investigation-and-owner-handoff--2026-11-25). The 62 failing full-suite nodes group into ten causes, not 62 defects; 37 additional nodes are individually investigated. C fixture corrections preserve 25 visible focused failures. EVAL-001 output keys and disclaimer/header alignment are interface/requirements questions, not unqualified product-defect claims. No owner approval or publication implied.

# Requirement → test mapping

Updated 2026-11-25. Source: [requirements.yaml](../../req/requirements.yaml), schema 1.2.0, **proposed_for_adoption**, 36 active requirements and 3 withdrawn IDs. This is a static coverage review, not adoption, a fresh test result, or independent acceptance.

Baseline: clean `main` at `14b06a57e3e779435614d066dfd6ab94510b0d2b`; local origin `hedyliu-574/CS5351`, different from the instructed team remote `kelepawuqiusi/CS5351`. No remote-state equivalence or branch-protection activation is asserted.

**covered** = existing assertions address the obligation; **partial** = relevant assertions exist with stated gaps; **pending implementation** = the required mechanism and acceptance tests remain absent; **needing clarification** = a scope, parameter or policy decision prevents a stable acceptance oracle (existing partial evidence is retained). Coverage is not a PASS verdict. Test filenames/TC IDs remain historical identifiers; they are not requirement IDs.

## Current registry coverage

Paths are repository-relative. Application paths identify inspected missing enforcement, not tests. Each gap is the next acceptance work item; the registry's full fit criterion remains authoritative.

| Requirement | Coverage | Existing evidence/source | Gap or scope of coverage |
|---|---|---|---|
| REQ-TA-RUN-001 | partial | `tests/member_c_verification/offline/test_nfr001_failures.py`, `tests/member_c_verification/offline/test_nfr004_persistence.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | Added six serialized incomplete reasons and five completed ratings; all eleven pass. BUDGET is still absent from declared StopReason. REVIEW/PASSED validity negative fails; aggregate budget dispatch and failure precedence for budget remain pending. |
| REQ-TA-FR-001 | pending implementation | `tests/test_no_data_handling.py` | Vendor absence tests do not assign evidence IDs. Add citation resolution, visible dates and retained evidence after incomplete runs. |
| REQ-TA-FR-003 | partial | `tests/test_checkpoint_resume.py`, `tests/test_checkpoint_lifecycle.py`, `tests/test_graph_end_to_end.py` | Resume has regression tests; add checkpoint listing, explicit rerun and four-branch invocation assertions. Resolve resumed identity with A/B. |
| REQ-TA-FR-004 | partial | `tests/test_tool_date_enforcement.py`, `tests/test_news_lookahead.py`, `tests/test_fundamentals_lookahead.py`, `tests/test_social_lookahead.py`, `tests/test_undated_tools_as_of.py` | Date guards exist; reconcile channel catalog with A and capture all prompts for ten planted/control pairs plus two live-only channels. |
| REQ-TA-FR-005 | partial | `tests/test_no_data_handling.py` | Absence versus failure has tests; implement per-channel coverage and all twelve core/non-core fixtures. A must resolve channel/core catalog. |
| REQ-TA-FR-006 | partial | `tests/test_yfinance_stale_ohlcv_guard.py`, `tests/test_statement_knowledge_time.py` | Price/vintage guards are narrower than the six required freshness boundaries; add statement, news and portfolio cases with agreed thresholds. |
| REQ-TA-FR-007 | partial | `tests/member_c_verification/offline/test_fr005_ratings.py`, `tests/member_c_verification/offline/test_fr004_propagation.py`, `tests/member_b_remediation/test_r4_research_manager_context.py` | Labels and protected input facts covered at seams; add exhaustive ownership phrase fixtures and deterministic R3 enforcement. |
| REQ-TA-FR-008 | pending implementation | `tradingagents/runapi/checks.py` | Checker has Q1-Q4 only; implement six sentiment fixtures, caps, correction and both-path failure handling; clarify usable free-text policy. |
| REQ-TA-NFR-001 | partial | `tests/member_c_verification/offline/test_nfr001_failures.py`, `tests/test_vendor_errors.py`, `tests/test_structured_agents.py` | Typed failures and fallback seams exist; bind the six required failure fixtures to full product outcomes and prevent missing-output completion. |
| REQ-TA-NFR-002 | partial | `tests/test_analyst_execution.py` | Selection/order tests are not an add/remove analyst change-cost experiment; record required changed files/lines and removal behaviour. |
| REQ-TA-NFR-OBS-001 | partial | `tests/member_c_verification/offline/test_nfr002_events.py`, `tests/member_b_remediation/test_r1_logging_redaction.py` | JSONL terminal and redaction tests exist; verify both sinks on completed/incomplete runs against every required field, including new budget/coverage fields. |
| REQ-TA-NFR-REPRO-001 | needing clarification | `tests/member_c_verification/offline/test_nfr004_persistence.py`, `tests/member_c_verification/offline/test_fr006_provenance.py`, `tests/member_b_remediation/test_r5_terminal_visibility.py` | Isolation/publication covered in part; blanket non-null fit conflicts with conditional RUN-001 fields. A must reconcile wording; new fields and resume identity also remain open. |
| REQ-TA-NFR-PERF-001 | needing clarification | `tests/member_d_verification/token_input_benchmark.py` | No qualifying twenty-run maximum-time cohort; provisional cap/profile need agreement. Raw graph benchmark is not product acceptance. |
| REQ-TA-NFR-PERF-002 | pending implementation | `tradingagents/runapi/result.py` | No aggregate time-budget stop contract; add ten slow-model runs, 30-second test cap and two-second cancellation allowance. |
| REQ-TA-NFR-COST-001 | needing clarification | `tests/member_d_verification/test_token_input_reduction.py`, `tests/member_d_verification/token_input_benchmark.py` | Concise-context tests/measurements do not enforce total tokens. Budget and quality threshold remain open; require twenty known input+output totals and controlled quality comparison. |
| REQ-TA-NFR-COST-002 | pending implementation | `tradingagents/runapi/result.py` | Implement run-wide admission and BUDGET; test cap=8 across retries, tools, structured fallback and settlement, including refusal before generic exception handling. |
| REQ-TA-NFR-COST-003 | pending implementation | `tests/test_debate_opening.py` | Opening prompt tests do not establish convergence. Add four convergence and four disagreement fixtures across both debates. |
| REQ-TA-NFR-EVAL-001 | needing clarification | `tests/member_c_verification/offline/test_nfr006_population.py`, `tests/member_b_remediation/test_r3_replay_durability.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | Updated ten-record fixture passes with DATA_FAILURE=1, MODEL_FAILURE=2, BUDGET=1; pending start retained. Twenty cases/two attempts probe fails: no distinct_case_count. H3: proposed observable keys are not an adopted API. B/A must agree evaluator entry and reporting schema; missing keys alone do not establish an implementation defect. Comparison policy tests need the same agreement. |
| REQ-TA-SEC-001 | pending implementation | `tests/test_prompt_integrity.py` | Prompt shape tests do not exercise twenty hostile vendor-text fixtures. Add five per analyst channel and assert no instruction takeover or disclosure. |
| REQ-TA-SEC-002 | partial | `tests/member_c_verification/offline/test_nfr003_privacy.py`, `tests/member_b_remediation/test_r1_logging_redaction.py`, `tests/member_d_verification/test_f2_redaction.py` | Planted credentials and major sinks covered; complete registry all-vendor/all-output matrix across A-A/B/C. Holdings minimisation is additional historical scope, not an adopted invariant. |
| REQ-TA-SEC-003 | partial | `tests/member_c_verification/offline/test_fr007_output_check.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | H5: twenty synthetic reports fail the registry leading-disclaimer requirement. A/B must reconcile this with the architecture leading-envelope contract before D changes layout. Guarantee Q4 regression retained; exact five-item registry fixture corpus and R8 mapping remain pending. |
| REQ-TA-ARCH-001 | partial | `tests/test_layering.py`, `tests/test_vendor_routing.py` | Import boundaries/router tests exist; direct data helpers bypass router. Verify every agent/graph vendor route, not merely library imports. |
| REQ-TA-ARCH-002 | partial | `tests/member_c_verification/offline/test_fr007_output_check.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | Existing Q1-Q4 tests retained. Corrected-only PASSED fails in both CheckResult and RunResult; mixed finding retention passes. R2-R7 implementations remain absent. |
| REQ-TA-INV-001 | partial | `tests/member_c_verification/offline/test_fr005_ratings.py`, `tests/member_c_verification/offline/test_fr007_output_check.py`, `tests/member_c_verification/offline/test_nfr001_failures.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | Checker regression passes, but new public RunResult negative fails: REVIEW can be constructed with PASSED. Registry validity is not enforced at every public seam. |
| REQ-TA-INV-002 | pending implementation | `tradingagents/runapi/checks.py` | No evidence resolver; add unresolved/duplicate citation negatives and retained registry checks. |
| REQ-TA-INV-003 | partial | `tests/member_c_verification/offline/test_fr004_propagation.py`, `tests/member_b_remediation/test_r4_research_manager_context.py` | Prompt facts tested; banned-phrase scan across reports/prompts and blocking R3 are missing. |
| REQ-TA-INV-004 | pending implementation | `tradingagents/runapi/checks.py` | Add six band/score fixtures and R4 classification. |
| REQ-TA-INV-005 | pending implementation | `tradingagents/runapi/checks.py` | Add unavailable Reddit/high-confidence cap correction, recorded original/corrected values and verdict. |
| REQ-TA-INV-006 | pending implementation | `tradingagents/runapi/checks.py` | Add all-three-unavailable directional sentiment correction and R6 finding. |
| REQ-TA-INV-007 | pending implementation | `tradingagents/runapi/checks.py` | Add coverage record/report equality and market-only 4 OK/8 NOT_REQUESTED after A resolves channel catalog. |
| REQ-TA-INV-008 | partial | `tests/member_c_verification/offline/test_fr007_output_check.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | H5 (shared with SEC-003, one issue): twenty leading-disclaimer probes fail; A/B layout reconciliation pending. Q3/Q4 existing checks remain valid narrower regressions; exact five guarantee fixtures and R8 remain pending. |
| REQ-TA-GOV-001 | needing clarification | `tests/member_c_verification/live/test_harness_selfcheck.py`, `tests/member_c_verification/live/test_score_gov004_exitcodes.py` | Harness is not semantic acceptance. Threshold/population and required gate policy unresolved; historical PASS superseded, independent scoring PENDING. |
| REQ-TA-GOV-002 | needing clarification | `tests/member_d_verification/test_test_approval_completion.py` | Tooling exists but user has paused pre-approval as a required merge check. A/E must reconcile registry; do not reinstate it. |
| REQ-TA-GOV-003 | partial | `scripts/ci/check_ai_log_updated.py`, `tests/member_d_verification/test_security_gate_boundaries.py` | Checker and governed API probe exist; verify complete governed-path negative/positive PR matrix and live protection separately. |
| REQ-TA-INV-014 | covered | `tests/member_c_verification/offline/test_fr003_validation_freeze.py`, `tests/member_c_verification/offline/test_fr006_provenance.py`, `tests/member_c_verification/offline/test_fr002_consent.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | Confirmed source overwrite/replacement plus consumer mutation now tested through engine input and published report/manifest (six profile/change combinations); seven INV-014 probes pass, including no-portfolio versus empty and new selection identity. Covered means scoped offline assertions, not live acceptance. |
| REQ-TA-GOV-004 | partial | `tests/member_d_verification/test_requirement_schema_gate.py` | Positive, five named negatives and cross-record failures have probes and CI wiring. Required-check blocking in live protection not independently verified here. |

## Current execution update — 2026-11-25

Offline follow-up results and pending work (unavailable record: registry-test-update-2026-11-25.md#missing-test-follow-up): 40 new parameterized probes, 18 passed and 22 failed. Combined focused suite: **138 passed, 25 failed, 1 skipped**. Failure counts are not distinct defects. No new skips/xfails or deleted regressions. The status table records coverage separately from passing acceptance; the original static-review description refers to the first pass only.

### Pending implementation and offline acceptance

- RUN-001, ARCH-002, INV-001: BUDGET dispatch/classification/secondary-cause retention, corrected-only public envelopes, REVIEW validity. Preserve legacy Q2 separately.
- FR-001/004/005/006, INV-002/007: evidence IDs, retention on failure, all-channel point-in-time capture, coverage/core catalog and six freshness boundaries. A must settle channel units before inventing a 12-channel fixture catalog.
- FR-007/008, INV-003/004/005/006: ownership negatives, sentiment band/cap corrections and no-data cases, safe persisted correction fields. Implement proposed interfaces before claiming end-to-end acceptance.
- SEC-001/003, INV-008: twenty injection fixtures, authoritative five-phrase corpus, leading disclaimer and R8; deterministic scripted text is suitable, not dependent on live models.
- FR-003: explicit list/rerun CLI and four-branch no-repeat counts; settled resume run/attempt identity. Existing checkpoint resume/clear primitives are retained.
- NFR-OBS-001/REPRO-001, SEC-002: full sink/profile/field matrix for new outcomes and safe secondary diagnostics; conditional-null wording needs A resolution.
- NFR-PERF-002/COST-002/COST-003: aggregate time/call admission, last-slot concurrency, retries/fallback/settlement, convergence/disagreement fixtures.
- NFR-EVAL-001/NFR-002/ARCH-001: comparison-mode contract, analyst change-cost experiment, direct vendor-routing exceptions.
- GOV-002/003/004: paused pre-approval policy reconciliation, governed-path negative PR matrix and actual required-check activation verification. Schema conformance alone is not adoption.

### Live-model acceptance (not run)

- NFR-PERF-001/COST-001: twenty controlled live runs with fixed profile, complete input+output usage, agreed time/token limits, UNKNOWN accounting and matched quality comparison. Concise-context benchmarks do not establish enforcement.
- GOV-001/NFR-EVAL-001: agreed rubric, critical items, threshold and distinct semantic case population; retain all attempts and portable report/manifest evidence, then obtain independent human scores. Twenty synthetic reports are not twenty live semantic cases.
- FR-007/SEC-001: live narrative/ownership/injection challenge assessment supplements deterministic offline checks; it does not replace those checks or certify every future output.

## Withdrawn requirements

REQ-TA-FR-002 (GUI), REQ-TA-NFR-SAFETY-001 (validated sizing) and REQ-TA-NFR-SAFETY-002 (replaced by FR-007 ownership wording) are excluded from the active denominator. Consent must never be mapped to withdrawn FR-002.

## Historical record (superseded for current coverage)

The original roll-up below is retained as historical evidence. Its PASS statements, counts and missing-gate claims are not current conclusions. In particular, historical semantic PASS remains PENDING independent audit under [verification constraints](../../code-governance/verification-constraints.md) and [evidence requirements](../gov004-evidence-package.md). Current tests are under pytest testpaths; the historical claim that C tests are outside testpaths is obsolete.

# Requirement → Test Mapping (for Member E)

> Remediation update 2026-11-21: current developer regression results and remaining F8/F9 acceptance limitations are recorded in `docs/reviews/remediation-2026-11-21.md`. Historical counts and claims below must not be treated as acceptance of the modified revision without independent review.

Status: C's current verification roll-up for E's shared `docs/architecture/trace-matrix.md`.
Test IDs and evidence are C-owned and real; **implementation links are D's** and
left as the existing `runapi/*` module references. Governance rows are marked by
status, not faked.

Legend for **Status**:
- `PASS (offline)` — covered by a passing synthetic offline test now.
- `PASS` — a governance gate satisfied by recorded evidence (offline and/or live).
- `PARTIAL` — some aspects covered; noted gaps remain.
- `NOT VERIFIED` — no passing evidence; reason given.
- `OWNED ELSEWHERE` — not a C test artifact (A/E/human).

Evidence root: `tests/member_c_verification/offline/` (run: `.venv/bin/python -m pytest tests/member_c_verification/offline -p no:cacheprovider`).
Suite result at time of writing: **80 passed, 0 failed**.
Live semantic evidence: `tests/member_c_verification/live/` (opt-in; see `docs/verification/semantic-evaluation.md`).

## Functional requirements

| Req ID | Test IDs | Status | Evidence location | Notes / gap |
|---|---|---|---|---|
| SEL-TA-FR-001 | TC-FR001-a..e | PASS (offline) | `tests/member_c_verification/offline/test_fr001_discovery.py` | Interactive picker UI flow itself mocked at service layer |
| SEL-TA-FR-002 | TC-FR002-a..d | PASS (offline) | `tests/member_c_verification/offline/test_fr002_consent.py` | Consent gate + flag rules; EOF prompt path not driven via tty |
| SEL-TA-FR-003 | TC-FR003-a..g | PASS (offline) | `tests/member_c_verification/offline/test_fr003_validation_freeze.py` | 5 of 6 invalid classes param'd + unreadable as TC-e |
| SEL-TA-FR-004 | TC-FR004-a..e | PASS (offline) | `tests/member_c_verification/offline/test_fr004_propagation.py` | Asserted at render/context seam, not live LLM prompt |
| SEL-TA-FR-005 | TC-FR005-a..d | PASS (offline) | `tests/member_c_verification/offline/test_fr005_ratings.py` | TC-d end-to-end: 3 labelled stages (RM/Trader/PM) + exactly one PM-sourced final rating |
| SEL-TA-FR-006 | TC-FR006-a..e | PASS (offline) | `tests/member_c_verification/offline/test_fr006_provenance.py` | TC-e now end-to-end: two full runs, both texts published, provenance identical minus run ID/timestamp |
| SEL-TA-FR-007 | TC-FR007-a..e | PASS (offline) | `tests/member_c_verification/offline/test_fr007_output_check.py` | TC-d now drives `run_analysis_api`; checker raising ⇒ COMPLETED + NEEDS_REVIEW + one CHECK_ERROR |

## Non-functional requirements

| Req ID | Test IDs | Status | Evidence location | Notes / gap |
|---|---|---|---|---|
| SEL-TA-NFR-001 | TC-NFR001-a..e,d2 | PASS (offline) | `tests/member_c_verification/offline/test_nfr001_failures.py` | Typed outcomes; no escape; INTERRUPTED (R12) not yet tested |
| SEL-TA-NFR-002 | TC-NFR002-a..c | PASS (offline) | `tests/member_c_verification/offline/test_nfr002_events.py` | Sink-level; full-run JSONL parse via completed run |
| SEL-TA-NFR-003 | TC-NFR003-a..g | PASS (offline) | `tests/member_c_verification/offline/test_nfr003_privacy.py` | Offline redaction evidence: TC-a..c scrub four planted secret types and secret-keyed values; TC-d model-error, TC-e CLI input-error, TC-f mid-run vendor/data-error, TC-g successfully-published narrative each show no secret/unrelated-holding leak across result/report(.md/.html)/manifest/events/CLI, benign sentence retained, source bytes unchanged, vendor stub reached (DATA_FAILURE/NOT_RUN). Residual: universal absence of *arbitrary/paraphrased* secrets in free-text narrative is a Redactor-pattern property, not proven exhaustively; semantic *wording* quality is a separate gate (GOV-004, PASS) |
| SEL-TA-NFR-004 | TC-NFR004-a..i | PASS (offline) | `tests/member_c_verification/offline/test_nfr004_persistence.py` | Isolation (a), payload omission (b), completed conditional fields (c), config-only one-key diff (d), prompt-template hash change (e), published INCOMPLETE has no rating (f), R13a critical publish failure → INCOMPLETE/PERSISTENCE_ERROR/NOT_RUN + nothing published (g), R13b best-effort failure preserves outcome (h), R14 terminal-event failure → `terminal_event.durable=false` (i). Residual: total-disk/power-loss durability out of scope (cooperative PERSISTENCE_ERROR contract). |
| SEL-TA-NFR-005 | TC-NFR005-a,b | PASS (offline) | `tests/member_c_verification/offline/test_nfr005_layering.py` | Structural import scan (INV-10) |
| SEL-TA-NFR-006 | TC-NFR006-a,b | PASS (offline) | `tests/member_c_verification/offline/test_nfr006_population.py` | Aggregation interface; zero-completed ⇒ insufficient |

## Governance requirements

| Req ID | Status | Evidence / owner | Notes |
|---|---|---|---|
| SEL-TA-GOV-001 | OWNED ELSEWHERE | E/human; transcript approval ref in test-plan §2 | Formal attributable sign-off pending in trace-matrix/CI |
| SEL-TA-GOV-002 | OWNED ELSEWHERE | A (schema); E (validate) | A's `requirements.yaml`/schema not delivered here |
| SEL-TA-GOV-003 | NOT VERIFIED | E (CI); baseline in verification-report §2 | Zero-regression blocked by BD-001 env failure decision |
| SEL-TA-GOV-004 | PASS | `tests/member_c_verification/live/` (C); C/A rubric; D runner | Formal semantic evaluation **PASS** under the confirmed scoring plan: 5 fixed cases × 2 valid attempts = 10/10 completed; semantic 28/28 = 100% (≥90%); 0 critical violations; challenge exposure 4/4. System verdict for C4/C5 stays NEEDS_REVIEW (Q4), recorded separately from the human score. Record: `docs/verification/semantic-evaluation.md`. Rubric/threshold approval = reviewer instruction for this step (transcript), not a separate signed artifact |
| SEL-TA-GOV-005 | NOT VERIFIED | E/all | AI-use-log gate not installed |
| SEL-TA-GOV-006 | NOT VERIFIED | B design; E enforce | Denied-write demo not installed |

## Baseline regression evidence

- Upstream suite: **1412 passed, 1 failed (BD-001, environmental), 0 skipped, 1 deselected**.
- C suite: **80 passed**.
- No new regressions attributable to C's tests (they live outside `tests/`/`testpaths`).

## Live semantic evidence (GOV-004)

- Harness self-check: `pytest tests/member_c_verification/live/test_harness_selfcheck.py` → **4 passed** (offline).
- Live replay: `deepseek` / `CS5351/DeepSeek-V4-Flash` at `git:e975528`; **two valid
  attempts per case**, 5 cases.
  - Attempt 1 (trial 1) evidence: `tests/member_c_verification/live/evidence/gov004_20261117T070010Z.json`.
  - Attempt 2 (trial 2) evidence: `tests/member_c_verification/live/evidence/gov004_20261117T071056Z.json`.
  - Human scores: `tests/member_c_verification/live/evidence/gov004_scores.json`.
  - Aggregate verdict: `.venv/bin/python tests/member_c_verification/live/score_gov004.py tests/member_c_verification/live/evidence/gov004_scores.json`
    → `FINAL VERDICT: PASS`.
- Completed 10/10; semantic 28/28 = 100%; 0 critical violations; exposure 4/4.
- No incomplete/exposure-failure attempts in this pass. (This set replaced a
  deleted earlier evidence set; the live suite was re-run to regenerate genuine
  evidence, so run IDs differ from the deleted set.)

## Linux registry verification rerun — 2026-11-25

This dated addendum supersedes the earlier Windows-only missing-evidence statements for H6/H8/H10, without changing their historical results. Tested local main `14b06a57e3e779435614d066dfd6ab94510b0d2b` plus the pre-existing dirty C tests/documents (including untracked `test_registry_gaps.py`); origin is `hedyliu-574/CS5351`, not the instructed team remote. No current team-main equivalence is claimed. Ubuntu-24.04 WSL, Python 3.12.3, declared editable `.[dev]` install succeeded. Registry remains schema 1.2.0, proposed_for_adoption, 36 active/3 withdrawn.

Commands use `.venv/bin/python` from the repository root:

- `-m pytest -q -p no:cacheprovider --tb=short tests/member_c_verification/offline tests/test_checkpoint_lifecycle.py tests/test_checkpoint_resume.py tests/member_b_remediation/test_r3_replay_durability.py tests/member_b_remediation/test_r2_r3_differential_pins.py tests/member_d_verification/test_requirement_schema_gate.py`: **202 passed, 25 failed**, no skips, 4.40 s. Raw local evidence: `.local-review/registry-linux-20261125.txt`. Pytest reports failure; the surrounding shell wrapper returned zero, so that wrapper status is not a passing verdict.
- `-m pytest -q -p no:cacheprovider --tb=short`: **1882 passed, 26 failed, 1 skipped, 1 deselected, 24 warnings, 100 subtests passed**, 16.83 s, exit 1. Raw local evidence: `.local-review/registry-linux-full-20261125.txt`. Skip is the opt-in live semantic replay; integration deselection remains in force.
- `scripts/ci/check_requirement_schema.py`: PASS, 36 requirements/3 withdrawn, zero errors/warnings. Ruff full repository PASS; mypy PASS (14 configured files); workflow permissions PASS (5 workflows); security scan PASS (105 application files, zero medium/high).

### Mapping and bug disposition

H1–H5 remain open with exactly the same 25 failing nodes: BUDGET vocabulary (1), corrected-only findings rejected (2), distinct-case population interface ambiguity (1), REVIEW/PASSED accepted (1), leading-disclaimer contract mismatch (20). Existing requirement-row coverage classifications remain unchanged; passing schema validation does not establish implementation or adoption. Owners and next acceptance evidence remain as in the classified handoff.

H6 replay locking, H7 schema-gate fixtures, H8 symlink isolation and H10 loopback authentication now execute successfully on Linux in the full run. This supplies the missing Linux evidence, not Windows portability or a Windows fixture repair. The remaining additional full-suite failure is H9 / BD-001: Bedrock construction still attempts ambient credential discovery and fails against the stale localhost proxy. No waiver, implementation fix or new defect category is claimed. E/D test-isolation follow-up remains open.

Only verification documentation was changed in this rerun; prior test edits are preserved. No live model replay, human semantic scoring, remote CI/branch-protection inspection, commit or publication occurred. Full registry acceptance remains blocked; prior historical records are retained.

Documentation check: default Linux git diff --check flags CRLF in pre-existing dirty files; the CR-at-EOL-aware check is recorded separately. No test line endings were changed.



