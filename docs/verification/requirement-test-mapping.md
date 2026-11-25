# Requirement-to-test mapping

Updated 25 November 2026.

[Verification package](README.md) · [Test results](verification-report.md) · [Evidence index](evidence-index.md)

## Scope

Registry 1.2.0 contains 36 active entries and 3 withdrawn IDs; its status is proposed_for_adoption. This mapping combines test coverage with the [verification report's closeout decisions](verification-report.md#open-decisions-and-next-owners).

Coverage describes the fit criterion: covered, partial, pending implementation or needing clarification. Closeout disposition describes the action for this submission. A partial row identifies remaining work; its submission treatment follows the linked decision. VC-DEC-02 remains a proposed deferral requiring the affected owners' scope decision.

## Closeout decision key

| Decision | Treatment in this mapping |
|---|---|
| VC-DEC-01 | A confirms requirement scope/adoption and unresolved acceptance wording |
| VC-DEC-02 | Existing verified behavior is retained; engineering follow-up is proposed for owner disposition |
| VC-DEC-04 | Formal semantic replay is deferred optional work |
| VC-DEC-05 | E integrates governance evidence; test-plan pre-approval remains paused |
| VC-DEC-06 | Recorded test evidence is indexed for handoff |

VC-DEC-03, final delivery-source verification, remains tracked separately in the report.

## Requirement coverage

| Requirement | Fit-criterion coverage | Closeout disposition | Existing evidence/source | Verified scope and remaining work |
|---|---|---|---|---|
| REQ-TA-RUN-001 | partial | Follow-up proposed — VC-DEC-02 | `tests/member_c_verification/offline/test_nfr001_failures.py`, `tests/member_c_verification/offline/test_nfr004_persistence.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | Post-repair focused batch passes BUDGET vocabulary; aggregate admission/cancellation and secondary-cause policy remain unverified. See the evidence index. |
| REQ-TA-FR-001 | pending implementation | Follow-up proposed — VC-DEC-02 | `tests/test_no_data_handling.py` | Vendor absence tests do not assign evidence IDs. Add citation resolution, visible dates and retained evidence after incomplete runs. |
| REQ-TA-FR-003 | partial | Follow-up proposed — VC-DEC-02 | `tests/test_checkpoint_resume.py`, `tests/test_checkpoint_lifecycle.py`, `tests/test_graph_end_to_end.py` | Resume has regression tests; add checkpoint listing, explicit rerun and four-branch invocation assertions. Resolve resumed identity with A/B. |
| REQ-TA-FR-004 | partial | Follow-up proposed — VC-DEC-02 | `tests/test_tool_date_enforcement.py`, `tests/test_news_lookahead.py`, `tests/test_fundamentals_lookahead.py`, `tests/test_social_lookahead.py`, `tests/test_undated_tools_as_of.py` | Date guards exist; reconcile channel catalog with A and capture all prompts for ten planted/control pairs plus two live-only channels. |
| REQ-TA-FR-005 | partial | Follow-up proposed — VC-DEC-02 | `tests/test_no_data_handling.py` | Absence versus failure has tests; implement per-channel coverage and all twelve core/non-core fixtures. A must resolve channel/core catalog. |
| REQ-TA-FR-006 | partial | Follow-up proposed — VC-DEC-02 | `tests/test_yfinance_stale_ohlcv_guard.py`, `tests/test_statement_knowledge_time.py` | Price/vintage guards are narrower than the six required freshness boundaries; add statement, news and portfolio cases with agreed thresholds. |
| REQ-TA-FR-007 | partial | Follow-up proposed — VC-DEC-02 | `tests/member_c_verification/offline/test_fr005_ratings.py`, `tests/member_c_verification/offline/test_fr004_propagation.py`, `tests/member_b_remediation/test_r4_research_manager_context.py` | Labels and protected input facts covered at seams; add exhaustive ownership phrase fixtures and deterministic R3 enforcement. |
| REQ-TA-FR-008 | pending implementation | Follow-up proposed — VC-DEC-02 | `tradingagents/runapi/checks.py` | Checker has Q1-Q4 only; implement six sentiment fixtures, caps, correction and both-path failure handling; clarify usable free-text policy. |
| REQ-TA-NFR-001 | partial | Follow-up proposed — VC-DEC-02 | `tests/member_c_verification/offline/test_nfr001_failures.py`, `tests/test_vendor_errors.py`, `tests/test_structured_agents.py` | Typed failures and fallback seams exist; bind the six required failure fixtures to full product outcomes and prevent missing-output completion. |
| REQ-TA-NFR-002 | partial | Follow-up proposed — VC-DEC-02 | `tests/test_analyst_execution.py` | Selection/order tests are not an add/remove analyst change-cost experiment; record required changed files/lines and removal behaviour. |
| REQ-TA-NFR-OBS-001 | partial | Follow-up proposed — VC-DEC-02 | `tests/member_c_verification/offline/test_nfr002_events.py`, `tests/member_b_remediation/test_r1_logging_redaction.py` | JSONL terminal and redaction tests exist; verify both sinks on completed/incomplete runs against every required field, including new budget/coverage fields. |
| REQ-TA-NFR-REPRO-001 | needing clarification | Owner decision — VC-DEC-01/02 | `tests/member_c_verification/offline/test_nfr004_persistence.py`, `tests/member_c_verification/offline/test_fr006_provenance.py`, `tests/member_b_remediation/test_r5_terminal_visibility.py` | Isolation/publication covered in part; blanket non-null fit conflicts with conditional RUN-001 fields. A must reconcile wording; new fields and resume identity also remain open. |
| REQ-TA-NFR-PERF-001 | needing clarification | Owner decision — VC-DEC-01/02 | `tests/member_d_verification/token_input_benchmark.py` | No qualifying twenty-run maximum-time cohort; provisional cap/profile need agreement. Raw graph benchmark is not product acceptance. |
| REQ-TA-NFR-PERF-002 | pending implementation | Follow-up proposed — VC-DEC-02 | `tradingagents/runapi/result.py` | No aggregate time-budget stop contract; add ten slow-model runs, 30-second test cap and two-second cancellation allowance. |
| REQ-TA-NFR-COST-001 | needing clarification | Owner decision — VC-DEC-01/02 | `tests/member_d_verification/test_token_input_reduction.py`, `tests/member_d_verification/token_input_benchmark.py` | Concise-context tests/measurements do not enforce total tokens. Budget and quality threshold remain open; require twenty known input+output totals and controlled quality comparison. |
| REQ-TA-NFR-COST-002 | pending implementation | Follow-up proposed — VC-DEC-02 | `tradingagents/runapi/result.py` | Run-wide admission/budget enforcement remains pending in the carried-forward review. Passing BUDGET vocabulary alone does not enforce budgets across retries, tools and fallback. |
| REQ-TA-NFR-COST-003 | pending implementation | Follow-up proposed — VC-DEC-02 | `tests/test_debate_opening.py` | Opening prompt tests do not establish convergence. Add four convergence and four disagreement fixtures across both debates. |
| REQ-TA-NFR-EVAL-001 | partial | Comparison follow-up proposed — VC-DEC-02 | `tests/member_c_verification/offline/test_nfr006_population.py`, `tests/member_b_remediation/test_r3_replay_durability.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | ER-01 covers the 6/10 counting fixture, stop-reason breakdown, distinct cases versus attempts and pending-start denominator. Repeatability and controlled-change comparison criteria remain follow-up work. |
| REQ-TA-SEC-001 | pending implementation | Follow-up proposed — VC-DEC-02 | `tests/test_prompt_integrity.py` | Prompt shape tests do not exercise twenty hostile vendor-text fixtures. Add five per analyst channel and assert no instruction takeover or disclosure. |
| REQ-TA-SEC-002 | partial | Follow-up proposed — VC-DEC-02 | `tests/member_c_verification/offline/test_nfr003_privacy.py`, `tests/member_b_remediation/test_r1_logging_redaction.py`, `tests/member_d_verification/test_f2_redaction.py` | Planted credentials and major sinks covered; complete registry all-vendor/all-output matrix across A-A/B/C. Holdings minimisation is additional historical scope, not an adopted invariant. |
| REQ-TA-SEC-003 | partial | Follow-up proposed — VC-DEC-02 | `tests/member_c_verification/offline/test_fr007_output_check.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | Post-repair batch passes twenty leading-disclaimer nodes. This covers layout, not the full guarantee/injection corpus or contextual resistance; A retains wording/adoption decisions. |
| REQ-TA-ARCH-001 | partial | Follow-up proposed — VC-DEC-02 | `tests/test_layering.py`, `tests/test_vendor_routing.py` | Import boundaries/router tests exist; direct data helpers bypass router. Verify every agent/graph vendor route, not merely library imports. |
| REQ-TA-ARCH-002 | partial | Follow-up proposed — VC-DEC-02 | `tests/member_c_verification/offline/test_fr007_output_check.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | Post-repair batch passes corrected-only envelopes and mixed-finding retention. This does not establish correction algorithms or complete Q-to-R checker migration. |
| REQ-TA-INV-001 | covered | Recorded coverage — VC-DEC-06 | `tests/member_c_verification/offline/test_fr005_ratings.py::test_tc_fr005_b_unreadable_final_is_review`, `tests/member_c_verification/offline/test_nfr001_failures.py::test_tc_nfr001_a_unreadable_final_text_is_review`, `tests/member_c_verification/offline/test_fr007_output_check.py::test_tc_fr007_b_single_rule_failures[Q1]`, `tests/member_c_verification/offline/test_registry_gaps.py::test_inv001_review_cannot_claim_passed_in_public_result` | ER-01 covers unreadable text becoming COMPLETED/REVIEW/NEEDS_REVIEW, Q1 rejection and public-result rejection of REVIEW/PASSED. Rating presentation and ownership wording belong to separate obligations. |
| REQ-TA-INV-002 | pending implementation | Follow-up proposed — VC-DEC-02 | `tradingagents/runapi/checks.py` | No evidence resolver; add unresolved/duplicate citation negatives and retained registry checks. |
| REQ-TA-INV-003 | partial | Follow-up proposed — VC-DEC-02 | `tests/member_c_verification/offline/test_fr004_propagation.py`, `tests/member_b_remediation/test_r4_research_manager_context.py` | Prompt facts tested; banned-phrase scan across reports/prompts and blocking R3 are missing. |
| REQ-TA-INV-004 | pending implementation | Follow-up proposed — VC-DEC-02 | `tradingagents/runapi/checks.py` | Add six band/score fixtures and R4 classification. |
| REQ-TA-INV-005 | pending implementation | Follow-up proposed — VC-DEC-02 | `tradingagents/runapi/checks.py` | Add unavailable Reddit/high-confidence cap correction, recorded original/corrected values and verdict. |
| REQ-TA-INV-006 | pending implementation | Follow-up proposed — VC-DEC-02 | `tradingagents/runapi/checks.py` | Add all-three-unavailable directional sentiment correction and R6 finding. |
| REQ-TA-INV-007 | pending implementation | Follow-up proposed — VC-DEC-02 | `tradingagents/runapi/checks.py` | Add coverage record/report equality and market-only 4 OK/8 NOT_REQUESTED after A resolves channel catalog. |
| REQ-TA-INV-008 | partial | Follow-up proposed — VC-DEC-02 | `tests/member_c_verification/offline/test_fr007_output_check.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | Leading-disclaimer nodes pass post-repair (shared with SEC-003). Q3/Q4 tests remain narrower than the full corpus and R8 obligation. |
| REQ-TA-GOV-001 | partial | Replay deferred — VC-DEC-04; integration — VC-DEC-05 | `tests/member_c_verification/live/test_harness_selfcheck.py`, `tests/member_c_verification/live/test_score_gov004_exitcodes.py` | ER-03 records eight harness/scorer self-tests; the fixed cases, thresholds and evidence contract are documented. Formal scoring is pending; prompt/model trigger and required-check integration remain with E. |
| REQ-TA-GOV-002 | needing clarification | Required gate paused — VC-DEC-05 | `tests/member_d_verification/test_test_approval_completion.py` | Approval tooling and its tests are present. Test-plan pre-approval remains paused as a required merge check; registry-policy reconciliation remains with A/E. |
| REQ-TA-GOV-003 | partial | Integration handoff — VC-DEC-05 | `scripts/ci/check_ai_log_updated.py`, `tests/member_d_verification/test_security_gate_boundaries.py` | Checker and governed API probe exist; verify complete governed-path negative/positive PR matrix and live protection separately. |
| REQ-TA-INV-014 | covered | Recorded coverage — VC-DEC-06 | `tests/member_c_verification/offline/test_fr003_validation_freeze.py`, `tests/member_c_verification/offline/test_fr006_provenance.py`, `tests/member_c_verification/offline/test_fr002_consent.py`, `tests/member_c_verification/offline/test_registry_gaps.py` | Confirmed source overwrite/replacement plus consumer mutation now tested through engine input and published report/manifest (six profile/change combinations); seven INV-014 probes pass, including no-portfolio versus empty and new selection identity. Covered means scoped offline assertions, not live acceptance. |
| REQ-TA-GOV-004 | partial | Integration handoff — VC-DEC-05 | `tests/member_d_verification/test_requirement_schema_gate.py` | Positive, five named negatives and cross-record failures have probes and CI wiring. Required-check blocking in live protection not independently verified here. |

## Reassessment

REQ-TA-INV-001 is covered by the recorded unreadable-rating, Q1 and public-result regressions. Its previous gap included broader rating/ownership behavior belonging to other requirements.

REQ-TA-NFR-EVAL-001 is partial: recorded population arithmetic is covered, with comparison-mode criteria remaining. REQ-TA-GOV-001 is partial: evaluator mechanisms and policy are documented, with formal replay deferred and integration assigned to E.

Other coverage ratings remain unchanged. Decisions assign work and delivery treatment; no new test run is included in this reassessment.

## Follow-up

A resolves requirement/oracle decisions; B/D own design and implementation; C supplies verification evidence; E assembles the final trace matrix. Remaining work is tracked in the [debt register](../debt-register.md).

Historical namespace mappings and earlier observations are in the [plan archive](history/test-plan-2026-11-25.md#semantic-migration-of-historical-references) and [mapping archive](history/requirement-test-mapping-2026-11-25.md).
