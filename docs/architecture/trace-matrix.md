> E integration update, 2026-11-25: canonical source/test paths now follow course D8. Compatibility aliases remain. Latest compact-format measurements are [separate developer evidence](../verification/compact-evidence-handoff-2026-11-25.md), not budget enforcement or independent semantic acceptance.

# Final requirement trace matrix — E1

Assembled by E on 2026-11-25 (Asia/Hong_Kong). Source baseline: team main
`761918e` (PR37 implementation and PR38 requirement updates merged), registry schema `1.2.0`, **36 active and 3 withdrawn IDs**.
This is the canonical repository matrix; “final” identifies the delivery artifact,
not a declaration that every requirement is implemented or accepted.

## Authority, interpretation and review

A's [registry](../req/requirements.yaml) supplies IDs, titles, text and registry
status; its document status remains `proposed_for_adoption`. This matrix does not
adopt or rewrite requirements. B's [trace inputs](traceability-inputs-member-b.md),
[contracts](interface-contracts.md), [invariants](invariants.md),
[runtime policies](runtime-policy-catalog.md) and [blueprint](../../architecture-blueprint.md)
supply allocations. C's [mapping](../verification/requirement-test-mapping.md) and
[retained verification index](../verification/evidence-index.md) supply verification
references. Current source supplies implementation links in place of an additional
D handoff. E owns assembly; A verifies IDs/adoption, B verifies allocations and
boundaries, C verifies tests/acceptance, and D verifies implementation/measurement
claims. These contributor confirmations are **requested, not recorded approvals**.

The row's implementation/verification assessment is separate from A's registry
status. “Scoped enforcement” or a passing offline probe is not full acceptance.
A target source file in a gap row identifies the intended owning component, not
an implemented capability. Test paths show relevant probes, not exhaustive coverage.
Where C lists only a source file, “no dedicated probe linked” is explicit below.
Runtime observations distinguish actual events/artifacts from missing monitors;
design-only event names in B's older inputs are not asserted emitted.

## Evidence baseline and precedence

- **C repair evidence:** PR34 commit `6d2e3d9` adds actual product changes; C's latest
  dated record reports 237 focused passes and a final 1918-pass Linux suite
  (one live skip, one integration deselection). Earlier 25-node H1–H5 failures in
  the same documents are historical. Repairs cover vocabulary, H2/H4 result
  validation, H3 arithmetic and H5 layout, not all obligations behind those tests.
- **H1 evidence:** [PR36](https://github.com/kelepawuqiusi/CS5351/pull/36) adds real
  opt-in call admission beyond C's BUDGET vocabulary. Publication-scope regression:
  1954 passed, 2 skipped, 1 deselected, 100 subtests; seven required checks passed.
  Local absent optional AWS dependency and opt-in live replay account for skips.
  The [H1 log](../../AI-log/Member-E/2026-11-25_h1-call-budget.md) distinguishes that
  run from the earlier [hashed snapshot](../verification/h1-call-budget-2026-11-25.json).
  Historical hashes must not be treated as hashes of later integrated files.
- **Current H3/H5 follow-up:** [PR37](https://github.com/kelepawuqiusi/CS5351/pull/37)
  supplies explicit population bindings, actual scorer counts and legacy export notices;
  [hashed evidence](../verification/h3-h5-follow-up-2026-11-25.json) records 1974
  offline passes, two skips, one deselection and 100 subtests. Seven required PR
  checks passed. This does not adopt a new semantic threshold or the provisional
  twenty-case formal profile. [PR38](https://github.com/kelepawuqiusi/CS5351/pull/38)
  adds A's H3/H5 wording, COUNTS_CASES and layout validation. A's
  [A2 handoff](../req/a2-handoff-to-member-e-2026-11-25.md) confirms the registry is
  still proposed, not adopted. OQ-18/OQ-19 remain open in A's notes: implemented
  mechanism and contributor confirmation must not be conflated.
- **Semantic acceptance:** [evidence requirements](../verification/gov004-evidence-package.md)
  supersede historical unconditional PASS claims. Current formal acceptance is
  PENDING; no new live replay or human scoring was performed for this matrix.
- **Hosted settings:** E directly inspected main's required-status API on
  2026-11-25: `required tests`, `ruff (strict, full repo)`, `dependency check`,
  `ai-log updated`, `requirements schema`, `type check`, `security checks`.
  Test pre-approval remains excluded; the semantic gate is not required.
  This is a dated observation, not a guarantee about future settings or full
  safety/ADR review enforcement. [CI](../../.github/workflows/ci.yml) and
  [coverage limits](../code-governance/types-and-security-coverage.md) define scope.

## Active registry — 36 requirements

Each row includes its requirement meaning, component/source allocation, test/evidence
references, actual observation or missing monitor, and remaining limitation.
Common evidence above applies to every row; per-row claims are deliberately narrower.

### REQ-TA-RUN-001 — Run result fields

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/result.py](../../src/tradingagents/runapi/result.py); [tradingagents/runapi/finalize.py](../../src/tradingagents/runapi/finalize.py); [tradingagents/runapi/execution.py](../../src/tradingagents/runapi/execution.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_nfr001_failures.py](../../test/offline/member_c_verification/offline/test_nfr001_failures.py); [tests/member_c_verification/offline/test_nfr004_persistence.py](../../test/offline/member_c_verification/offline/test_nfr004_persistence.py); [tests/member_c_verification/offline/test_registry_gaps.py](../../test/offline/member_c_verification/offline/test_registry_gaps.py); [tests/member_c_verification/test_registry_result_repairs.py](../../test/offline/member_c_verification/test_registry_result_repairs.py) |
| Runtime monitor / observation | run.terminal; manifest run_outcome/stop_reason/output_check |
| Implementation / verification assessment | Partial: six reasons and H2/H4 result guards present; full new coverage/correction payload is not implemented. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-FR-001 — Evidence IDs, records and visible source dates

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py) |
| Tests / evidence | [tests/test_no_data_handling.py](../../test/offline/test_no_data_handling.py) |
| Runtime monitor / observation | No evidence-ID resolver monitor implemented |
| Implementation / verification assessment | Gap: no complete evidence registry/resolver; checker is an allocation target only. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-FR-003 — Checkpoint list, resume and rerun

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | partial |
| Component / source | [tradingagents/graph/checkpointer.py](../../src/tradingagents/graph/checkpointer.py); [tradingagents/graph/trading_graph.py](../../src/tradingagents/graph/trading_graph.py) |
| Tests / evidence | [tests/test_checkpoint_resume.py](../../test/offline/test_checkpoint_resume.py); [tests/test_checkpoint_lifecycle.py](../../test/offline/test_checkpoint_lifecycle.py); [tests/test_graph_end_to_end.py](../../test/offline/test_graph_end_to_end.py) |
| Runtime monitor / observation | Checkpoint records; no complete CLI list/resume acceptance monitor |
| Implementation / verification assessment | Partial: checkpoint lifecycle exists; complete user list/resume/rerun and identity contract require acceptance. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-FR-004 — Point-in-time evidence (no look-ahead)

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | partial |
| Component / source | [tradingagents/dataflows/date_window.py](../../src/tradingagents/dataflows/date_window.py); [tradingagents/dataflows/router.py](../../src/tradingagents/dataflows/router.py) |
| Tests / evidence | [tests/test_tool_date_enforcement.py](../../test/offline/test_tool_date_enforcement.py); [tests/test_news_lookahead.py](../../test/offline/test_news_lookahead.py); [tests/test_fundamentals_lookahead.py](../../test/offline/test_fundamentals_lookahead.py); [tests/test_social_lookahead.py](../../test/offline/test_social_lookahead.py); [tests/test_undated_tools_as_of.py](../../test/offline/test_undated_tools_as_of.py) |
| Runtime monitor / observation | Date-window decisions/vendor diagnostics; no universal all-channel audit |
| Implementation / verification assessment | Partial: date filtering exists; historical snapshots and all-channel no-look-ahead are not established. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-FR-005 — Data gaps and the core-data rule

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | partial |
| Component / source | [tradingagents/dataflows/errors.py](../../src/tradingagents/dataflows/errors.py); [tradingagents/runapi/finalize.py](../../src/tradingagents/runapi/finalize.py) |
| Tests / evidence | [tests/test_no_data_handling.py](../../test/offline/test_no_data_handling.py) |
| Runtime monitor / observation | Typed errors; manifest stop_reason; run.terminal |
| Implementation / verification assessment | Partial: typed data failure exists; complete channel coverage/core catalog and record equality missing. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-FR-006 — Freshness thresholds

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | partial |
| Component / source | [tradingagents/dataflows/vendors/yahoo/snapshot.py](../../src/tradingagents/dataflows/vendors/yahoo/snapshot.py); [tradingagents/dataflows/vendors/yahoo/fundamentals.py](../../src/tradingagents/dataflows/vendors/yahoo/fundamentals.py) |
| Tests / evidence | [tests/test_yfinance_stale_ohlcv_guard.py](../../test/offline/test_yfinance_stale_ohlcv_guard.py); [tests/test_statement_knowledge_time.py](../../test/offline/test_statement_knowledge_time.py) |
| Runtime monitor / observation | Vendor snapshot/vintage diagnostics; no six-boundary monitor |
| Implementation / verification assessment | Partial: existing price/fiscal checks do not implement all six freshness boundaries or adopted thresholds. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-FR-007 — Rating meaning and no ownership wording

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/agents/rating.py](../../src/tradingagents/agents/rating.py); [tradingagents/agents/context.py](../../src/tradingagents/agents/context.py); [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_fr005_ratings.py](../../test/offline/member_c_verification/offline/test_fr005_ratings.py); [tests/member_c_verification/offline/test_fr004_propagation.py](../../test/offline/member_c_verification/offline/test_fr004_propagation.py); [tests/member_b_remediation/test_r4_research_manager_context.py](../../test/offline/member_b_remediation/test_r4_research_manager_context.py) |
| Runtime monitor / observation | output.check; final_rating; rendered stage labels |
| Implementation / verification assessment | Partial: labels/context exist; deterministic banned-ownership R3 not implemented. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-FR-008 — Sentiment score and confidence consistent with available data

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/agents/schemas.py](../../src/tradingagents/agents/schemas.py); [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py) |
| Tests / evidence | No dedicated acceptance probe linked in C’s current row; see the gap assessment and common evidence above. |
| Runtime monitor / observation | No R4-R6 sentiment correction monitor |
| Implementation / verification assessment | Gap: schemas do not implement band/cap rules or final safe correction and re-render pipeline. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-NFR-001 — Fail safely on external failures

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | partial |
| Component / source | [tradingagents/runapi/finalize.py](../../src/tradingagents/runapi/finalize.py); [tradingagents/agents/structured.py](../../src/tradingagents/agents/structured.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_nfr001_failures.py](../../test/offline/member_c_verification/offline/test_nfr001_failures.py); [tests/test_vendor_errors.py](../../test/offline/test_vendor_errors.py); [tests/test_structured_agents.py](../../test/offline/test_structured_agents.py) |
| Runtime monitor / observation | run.terminal; typed stop_reason |
| Implementation / verification assessment | Partial: typed outcomes/fallback present; all required model/data failure profiles need end-to-end acceptance. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-NFR-002 — Add or remove an analyst

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | partial |
| Component / source | [tradingagents/graph/analyst_execution.py](../../src/tradingagents/graph/analyst_execution.py); [tradingagents/graph/setup.py](../../src/tradingagents/graph/setup.py) |
| Tests / evidence | [tests/test_analyst_execution.py](../../test/offline/test_analyst_execution.py) |
| Runtime monitor / observation | No retained add/remove change-cost measurement |
| Implementation / verification assessment | Partial: registration/execution tests exist; required changed-file/line experiment absent. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-NFR-OBS-001 — Structured logging

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | partial |
| Component / source | [tradingagents/runapi/events.py](../../src/tradingagents/runapi/events.py); [tradingagents/runapi/execution.py](../../src/tradingagents/runapi/execution.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_nfr002_events.py](../../test/offline/member_c_verification/offline/test_nfr002_events.py); [tests/member_b_remediation/test_r1_logging_redaction.py](../../test/offline/member_b_remediation/test_r1_logging_redaction.py) |
| Runtime monitor / observation | JSONL ts/elapsed_ms/node/event_outcome; run.budget |
| Implementation / verification assessment | Partial: actual lifecycle events and call-budget diagnostics exist; all requested fields/sinks and time/token stop kinds not complete. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-NFR-REPRO-001 — Immutable run record and report

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | partial |
| Component / source | [tradingagents/runapi/context.py](../../src/tradingagents/runapi/context.py); [tradingagents/runapi/persist.py](../../src/tradingagents/runapi/persist.py); [tradingagents/runapi/reporting.py](../../src/tradingagents/runapi/reporting.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_nfr004_persistence.py](../../test/offline/member_c_verification/offline/test_nfr004_persistence.py); [tests/member_c_verification/offline/test_fr006_provenance.py](../../test/offline/member_c_verification/offline/test_fr006_provenance.py); [tests/member_b_remediation/test_r5_terminal_visibility.py](../../test/offline/member_b_remediation/test_r5_terminal_visibility.py) |
| Runtime monitor / observation | run_id; manifest/report paths; publication commit; run.terminal |
| Implementation / verification assessment | Partial: isolated artifacts/frozen provenance exist; extended evidence/correction fields and resume identity remain gaps. Critical publication failure can prevent durable artifacts. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-NFR-PERF-001 — Maximum run time

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/execution.py](../../src/tradingagents/runapi/execution.py) |
| Tests / evidence | [tests/member_d_verification/token_input_benchmark.py](../../test/offline/member_d_verification/token_input_benchmark.py) |
| Runtime monitor / observation | Elapsed events only; no qualifying 20-case timing cohort |
| Implementation / verification assessment | Gap: maximum wall-time acceptance and fixed profile not demonstrated. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-NFR-PERF-002 — Time-budget handling

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/execution.py](../../src/tradingagents/runapi/execution.py) |
| Tests / evidence | No dedicated acceptance probe linked in C’s current row; see the gap assessment and common evidence above. |
| Runtime monitor / observation | No run-wide deadline/cancellation monitor |
| Implementation / verification assessment | Gap: call cap is not a time deadline; CANCEL_ALLOWANCE not enforced as a run-wide limit. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-NFR-COST-001 — Run token budget

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/agents/structured.py](../../src/tradingagents/agents/structured.py); [tradingagents/default_config.py](../../src/tradingagents/default_config.py) |
| Tests / evidence | [tests/member_d_verification/test_token_input_reduction.py](../../test/offline/member_d_verification/test_token_input_reduction.py); [tests/member_d_verification/token_input_benchmark.py](../../test/offline/member_d_verification/token_input_benchmark.py) |
| Runtime monitor / observation | Provider usage/benchmark measurements where available; no total-token admission controller |
| Implementation / verification assessment | Gap: concise context reduces measured tokens but does not enforce TOKEN_BUDGET; candidate 120000 is not an adopted/enforced ceiling. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-NFR-COST-002 — Run-wide LLM call cap

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/budget.py](../../src/tradingagents/runapi/budget.py); [tradingagents/llm_clients/budget_transport.py](../../src/tradingagents/llm_clients/budget_transport.py); [tradingagents/llm_clients/factory.py](../../src/tradingagents/llm_clients/factory.py); [tradingagents/runapi/execution.py](../../src/tradingagents/runapi/execution.py) |
| Tests / evidence | [tests/member_d_verification/test_h1_call_budget.py](../../test/offline/member_d_verification/test_h1_call_budget.py) |
| Runtime monitor / observation | run.budget; schema-2 run_budget counters; BUDGET terminal result |
| Implementation / verification assessment | Scoped implementation: opt-in synchronous deepseek/openai_compatible, shared per-run reservations/dispatch, retries/fallback/settlement included; default cap None, async/other providers refused when enabled. Production cap and independent acceptance pending. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-NFR-COST-003 — Early debate convergence

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/graph/conditional_logic.py](../../src/tradingagents/graph/conditional_logic.py); [tradingagents/graph/trading_graph.py](../../src/tradingagents/graph/trading_graph.py) |
| Tests / evidence | [tests/test_debate_opening.py](../../test/offline/test_debate_opening.py) |
| Runtime monitor / observation | Configured debate counts; no semantic-convergence verdict |
| Implementation / verification assessment | Gap: bounded rounds/opening optimizations do not establish convergence or required disagreement fixtures. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-NFR-EVAL-001 — Evaluation counting rules

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/result.py](../../src/tradingagents/runapi/result.py); [tests/member_c_verification/live/score_gov004.py](../../test/live/member_c_verification/score_gov004.py); [tests/member_c_verification/live/replay_store.py](../../test/live/member_c_verification/replay_store.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_nfr006_population.py](../../test/offline/member_c_verification/offline/test_nfr006_population.py); [tests/member_b_remediation/test_r3_replay_durability.py](../../test/offline/member_b_remediation/test_r3_replay_durability.py); [tests/member_c_verification/offline/test_registry_gaps.py](../../test/offline/member_c_verification/offline/test_registry_gaps.py); [tests/member_c_verification/test_registry_result_repairs.py](../../test/offline/member_c_verification/test_registry_result_repairs.py); [H3/H5 integration probes](../../test/offline/member_d_verification/test_h3_h5_integration.py); [follow-up evidence](../verification/h3-h5-follow-up-2026-11-25.json) |
| Runtime monitor / observation | runapi EvaluationPopulation/RunRecord; scorer Evaluation counts JSON; completion/review accounting |
| Implementation / verification assessment | Scoped enforcement: duplicate/blank identities fail; explicit population/revision/prompt/configuration bindings validate one population, unbound legacy records report null. The real scorer outputs case/population counts and refuses PASS for unknown identity. Started failures/retries remain counted. Comparison mode is explicitly refused; formal evaluator remains 5 cases / 10 attempts, so provisional N_EVAL=20 and comparison acceptance are not claimed. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-SEC-001 — Prompt-injection resistance

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/agents/structured.py](../../src/tradingagents/agents/structured.py); [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py) |
| Tests / evidence | [tests/test_prompt_integrity.py](../../test/offline/test_prompt_integrity.py) |
| Runtime monitor / observation | Prompt boundaries; deterministic output.check; no full hostile-source matrix |
| Implementation / verification assessment | Partial defenses: twenty required vendor-injection scenarios are not established by prompt-shape tests. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-SEC-002 — No credential or token leakage

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | partial |
| Component / source | [tradingagents/runapi/redact.py](../../src/tradingagents/runapi/redact.py); [tradingagents/runapi/persist.py](../../src/tradingagents/runapi/persist.py); [tradingagents/agents/structured.py](../../src/tradingagents/agents/structured.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_nfr003_privacy.py](../../test/offline/member_c_verification/offline/test_nfr003_privacy.py); [tests/member_b_remediation/test_r1_logging_redaction.py](../../test/offline/member_b_remediation/test_r1_logging_redaction.py); [tests/member_d_verification/test_f2_redaction.py](../../test/offline/member_d_verification/test_f2_redaction.py) |
| Runtime monitor / observation | Redacted published artifacts/logs; no dedicated security.redaction event |
| Implementation / verification assessment | Partial: credential/sink probes exist; complete all-vendor/all-profile matrix pending. Holdings minimization is separate historical scope. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-SEC-003 — No promise of guaranteed returns

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/reporting.py](../../src/tradingagents/runapi/reporting.py); [tradingagents/report_html.py](../../src/tradingagents/report_html.py); [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py); [legacy complete-report writer](../../src/tradingagents/reporting.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_fr007_output_check.py](../../test/offline/member_c_verification/offline/test_fr007_output_check.py); [tests/member_c_verification/offline/test_registry_gaps.py](../../test/offline/member_c_verification/offline/test_registry_gaps.py); [tests/member_c_verification/test_registry_result_repairs.py](../../test/offline/member_c_verification/test_registry_result_repairs.py); [H3/H5 integration probes](../../test/offline/member_d_verification/test_h3_h5_integration.py); [follow-up evidence](../verification/h3-h5-follow-up-2026-11-25.json) |
| Runtime monitor / observation | Canonical leading disclaimer; Q3/Q4 output.check; direct-export regressions |
| Implementation / verification assessment | Scoped H5 layout enforcement: canonical disclaimer leads complete Markdown and visible HTML in both shared API and legacy complete exporters, including absent/empty metadata. Footer compatibility retained. Per-agent section files are source sections, not complete reports. Full R8 corpus and final B layout confirmation are separate outstanding items. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-ARCH-001 — Vendors behind one routing point

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | partial |
| Component / source | [tradingagents/dataflows/router.py](../../src/tradingagents/dataflows/router.py) |
| Tests / evidence | [tests/test_layering.py](../../test/offline/test_layering.py); [tests/test_vendor_routing.py](../../test/offline/test_vendor_routing.py) |
| Runtime monitor / observation | Router dispatch diagnostics; no universal bypass monitor |
| Implementation / verification assessment | Partial: router exists; direct helper routes mean universal routing restriction not proven. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-ARCH-002 — Deterministic output check

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py); [tradingagents/runapi/result.py](../../src/tradingagents/runapi/result.py); [tradingagents/runapi/execution.py](../../src/tradingagents/runapi/execution.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_fr007_output_check.py](../../test/offline/member_c_verification/offline/test_fr007_output_check.py); [tests/member_c_verification/offline/test_registry_gaps.py](../../test/offline/member_c_verification/offline/test_registry_gaps.py); [tests/member_c_verification/test_registry_result_repairs.py](../../test/offline/member_c_verification/test_registry_result_repairs.py) |
| Runtime monitor / observation | output.check; manifest findings and check_rules_version when enabled |
| Implementation / verification assessment | Partial: Q1-Q4 authoritative; corrected-only DTOs accepted by C repair, but full R1-R8 resolver/coverage/correction engine not implemented. Budget schema-2 check_rules_version=1 is not full checker v2. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-INV-001 — Unreadable rating never passes

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/agents/rating.py](../../src/tradingagents/agents/rating.py); [tradingagents/runapi/result.py](../../src/tradingagents/runapi/result.py); [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_fr005_ratings.py](../../test/offline/member_c_verification/offline/test_fr005_ratings.py); [tests/member_c_verification/offline/test_fr007_output_check.py](../../test/offline/member_c_verification/offline/test_fr007_output_check.py); [tests/member_c_verification/offline/test_nfr001_failures.py](../../test/offline/member_c_verification/offline/test_nfr001_failures.py); [tests/member_c_verification/offline/test_registry_gaps.py](../../test/offline/member_c_verification/offline/test_registry_gaps.py); [tests/member_c_verification/test_registry_result_repairs.py](../../test/offline/member_c_verification/test_registry_result_repairs.py) |
| Runtime monitor / observation | REVIEW plus NEEDS_REVIEW; output.check |
| Implementation / verification assessment | Scoped enforcement: C H4 rejects public REVIEW/PASSED; malformed-rating/checker probes exist. Not full semantic acceptance. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-INV-002 — Every cited evidence ID resolves

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py) |
| Tests / evidence | No dedicated acceptance probe linked in C’s current row; see the gap assessment and common evidence above. |
| Runtime monitor / observation | No evidence-ID resolution monitor |
| Implementation / verification assessment | Gap: target checker has no full citation registry/resolver; no completed invariant enforcement. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-INV-003 — No banned ownership phrase

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/agents/context.py](../../src/tradingagents/agents/context.py); [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_fr004_propagation.py](../../test/offline/member_c_verification/offline/test_fr004_propagation.py); [tests/member_b_remediation/test_r4_research_manager_context.py](../../test/offline/member_b_remediation/test_r4_research_manager_context.py) |
| Runtime monitor / observation | Frozen context; no exhaustive banned-phrase R3 monitor |
| Implementation / verification assessment | Partial: prompt facts preserve unknown holdings; deterministic delivered-text ban not implemented. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-INV-004 — Sentiment score matches band

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/agents/schemas.py](../../src/tradingagents/agents/schemas.py); [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py) |
| Tests / evidence | No dedicated acceptance probe linked in C’s current row; see the gap assessment and common evidence above. |
| Runtime monitor / observation | No R4 band/score finding |
| Implementation / verification assessment | Gap: sentiment schema alone does not enforce required band/score invariant. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-INV-005 — Sentiment confidence within the coverage cap

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py); [tradingagents/runapi/result.py](../../src/tradingagents/runapi/result.py) |
| Tests / evidence | No dedicated acceptance probe linked in C’s current row; see the gap assessment and common evidence above. |
| Runtime monitor / observation | CORRECTED supported structurally; no automatic R5 correction event |
| Implementation / verification assessment | Gap: H2 structure repaired, but coverage cap, safe original/corrected values, final re-render and versioned correction publication absent. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-INV-006 — No sentiment direction without any sentiment data

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py); [tradingagents/agents/schemas.py](../../src/tradingagents/agents/schemas.py) |
| Tests / evidence | No dedicated acceptance probe linked in C’s current row; see the gap assessment and common evidence above. |
| Runtime monitor / observation | No R6 coverage-linked neutral-band monitor |
| Implementation / verification assessment | Gap: all-sources-unavailable sentiment invariant not fully enforced. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-INV-007 — Data coverage section equals the record

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py) |
| Tests / evidence | No dedicated acceptance probe linked in C’s current row; see the gap assessment and common evidence above. |
| Runtime monitor / observation | No canonical data_coverage record/report equality monitor |
| Implementation / verification assessment | Gap: coverage registry/channel catalog and equality check not complete. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-INV-008 — Disclaimer present, no guarantee phrase

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/reporting.py](../../src/tradingagents/runapi/reporting.py); [tradingagents/report_html.py](../../src/tradingagents/report_html.py); [tradingagents/runapi/checks.py](../../src/tradingagents/runapi/checks.py); [legacy complete-report writer](../../src/tradingagents/reporting.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_fr007_output_check.py](../../test/offline/member_c_verification/offline/test_fr007_output_check.py); [tests/member_c_verification/offline/test_registry_gaps.py](../../test/offline/member_c_verification/offline/test_registry_gaps.py) (`TC-SEC003-c` negative position probe); [tests/member_c_verification/test_registry_result_repairs.py](../../test/offline/member_c_verification/test_registry_result_repairs.py); [H3/H5 integration probes](../../test/offline/member_d_verification/test_h3_h5_integration.py); [follow-up evidence](../verification/h3-h5-follow-up-2026-11-25.json) |
| Runtime monitor / observation | Leading disclaimer in every complete-report renderer; Q3/Q4 output.check |
| Implementation / verification assessment | Scoped H5 repair shared with SEC-003: complete Markdown/HTML leading notice now covers legacy paths and no-metadata renders. Positive nodes are complemented by `TC-SEC003-c`, which rejects a disclaimer that is present but only later (Markdown first non-blank line; HTML first visible body element). Guarantee Q4 remains; full R8 corpus and contributor design confirmation are not inferred. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-GOV-001 — Semantic evaluation gate

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tests/member_c_verification/live/score_gov004.py](../../test/live/member_c_verification/score_gov004.py); [tests/member_c_verification/live/replay_store.py](../../test/live/member_c_verification/replay_store.py); [.github/workflows/ci.yml](../../.github/workflows/ci.yml) |
| Tests / evidence | [tests/member_c_verification/live/test_harness_selfcheck.py](../../test/live/member_c_verification/test_harness_selfcheck.py); [tests/member_c_verification/live/test_score_gov004_exitcodes.py](../../test/live/member_c_verification/test_score_gov004_exitcodes.py) |
| Runtime monitor / observation | Opt-in replay/scorer exit codes; Evaluation counts JSON; frozen evidence ledger |
| Implementation / verification assessment | Framework remains opt-in: scorer now validates population identity and outputs distinct-case/population counts; historical formal PASS remains PENDING audit. Existing 5-case/10-attempt profile is not the provisional 20-case requirement, and QUALITY_THRESHOLD remains open in the registry; no required semantic CI check enabled. |
| Contributors | A: requirement; B: architecture; C: independent verification; E: governance integration; D: runnable support |

### REQ-TA-GOV-002 — Test plan approved before implementation

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [scripts/ci/check_test_approval.py](../../scripts/ci/check_test_approval.py); [.github/workflows/test-approval.yml](../../.github/workflows/test-approval.yml); [.github/workflows/test-approval-complete.yml](../../.github/workflows/test-approval-complete.yml) |
| Tests / evidence | [tests/member_d_verification/test_test_approval_completion.py](../../test/offline/member_d_verification/test_test_approval_completion.py) |
| Runtime monitor / observation | test approval checks; receipt attachments/approval records |
| Implementation / verification assessment | Implemented tooling, PAUSED as required merge check by user decision. Current development is not claimed compliant with prior-approval requirement; historical approvals not reconstructed. |
| Contributors | A: requirement; B: architecture; C: independent verification; E: governance integration; D: runnable support |

### REQ-TA-GOV-003 — AI-use log updated before merge

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [scripts/ci/check_ai_log_updated.py](../../scripts/ci/check_ai_log_updated.py); [.github/workflows/ci.yml](../../.github/workflows/ci.yml) |
| Tests / evidence | [tests/member_d_verification/test_security_gate_boundaries.py](../../test/offline/member_d_verification/test_security_gate_boundaries.py) |
| Runtime monitor / observation | ai-log updated required CI check |
| Implementation / verification assessment | Scoped enforcement: important-path changes require added/modified substantive AI-log file; format/content/complete course logs not certified. |
| Contributors | A: requirement; B: architecture; C: independent verification; E: governance integration; D: runnable support |

### REQ-TA-INV-014 — Immutable input snapshot

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [tradingagents/runapi/input_service.py](../../src/tradingagents/runapi/input_service.py); [tradingagents/runapi/context.py](../../src/tradingagents/runapi/context.py); [tradingagents/runapi/execution.py](../../src/tradingagents/runapi/execution.py) |
| Tests / evidence | [tests/member_c_verification/offline/test_fr003_validation_freeze.py](../../test/offline/member_c_verification/offline/test_fr003_validation_freeze.py); [tests/member_c_verification/offline/test_fr006_provenance.py](../../test/offline/member_c_verification/offline/test_fr006_provenance.py); [tests/member_c_verification/offline/test_fr002_consent.py](../../test/offline/member_c_verification/offline/test_fr002_consent.py); [tests/member_c_verification/offline/test_registry_gaps.py](../../test/offline/member_c_verification/offline/test_registry_gaps.py) |
| Runtime monitor / observation | input.mode_resolved; frozen fingerprint/input_mode; report/manifest provenance |
| Implementation / verification assessment | Scoped enforcement: freeze/overwrite/consumer mutation and no-portfolio-vs-empty covered by C; optional external input remains read-only, no post-freeze reread. |
| Contributors | A: requirement; B: architecture; C: independent verification; D: implementation; E: integration |

### REQ-TA-GOV-004 — Requirement registry validates against its schema

| Trace field | Allocation / evidence |
|---|---|
| Registry status (A) | proposed |
| Component / source | [docs/req/req-schema.json](../req/req-schema.json); [docs/req/validate.py](../req/validate.py); [scripts/ci/check_requirement_schema.py](../../scripts/ci/check_requirement_schema.py); [.github/workflows/ci.yml](../../.github/workflows/ci.yml) |
| Tests / evidence | [tests/member_d_verification/test_requirement_schema_gate.py](../../test/offline/member_d_verification/test_requirement_schema_gate.py) |
| Runtime monitor / observation | requirements schema required CI check; 36 active/3 withdrawn |
| Implementation / verification assessment | Implemented schema/cross-record gate with positive/negative evidence; validity is not adoption or implementation acceptance. |
| Contributors | A: requirement; B: architecture; C: independent verification; E: governance integration; D: runnable support |

## Historical SEL crosswalk — map by meaning

B's historical selection remains a separate namespace. The table below preserves
its semantic relationship; it is not an additional set of 36 requirements and its
historical status labels are not copied as current acceptance. The active rows
above govern current assessments. FR-001 discovery, explicit consent and holdings
minimization have historical coverage without a complete matching registry ID;
those gaps are not repaired by renumbering unrelated requirements.

| Historical SEL suffix / meaning | Historical implemented meaning | Registry relationship by meaning | Relationship |
|---|---|---|---|
| FR-001 discover/select | portfolio file discovery + selection | — (candidate has no portfolio discovery; its FR-001 is *evidence IDs*) | none/clash |
| FR-002 explicit confirmation | consent gate | — (candidate FR-002 is *withdrawn*; its RUN-001 owns outcome fields) | none/clash |
| FR-003 validate/freeze snapshot | input precheck + freeze | `REQ-TA-FR-003` = *checkpoint list/resume/rerun* | none/clash |
| FR-004 propagate explicit context | portfolio→prompt, no invented holdings | `REQ-TA-FR-004` = *point-in-time no look-ahead*; `REQ-TA-FR-007` ownership wording | partial |
| FR-005 ratings vs actions | stage labels, REVIEW≠Hold | `REQ-TA-FR-007` rating meaning/labels/no ownership | partial |
| FR-006 deterministic provenance | frozen fingerprint identity | `REQ-TA-NFR-REPRO-001` run record; `REQ-TA-FR-006` freshness | partial |
| FR-007 output-check authority | Q1–Q4 authoritative | `REQ-TA-ARCH-002` (R1–R8); `REQ-TA-INV-001` | partial |
| NFR-001 external failure | typed incomplete | `REQ-TA-NFR-001` | same |
| NFR-002 observability | JSONL events | `REQ-TA-NFR-OBS-001` | same |
| NFR-003 privacy | redaction/sinks; credentials **and** holdings minimisation | `REQ-TA-SEC-002` (**credentials only**) | **partial** |
| NFR-004 immutable artifacts | per-run ID, atomic publish | `REQ-TA-NFR-REPRO-001` | same |
| NFR-005 cohesive integration | shared boundary, no prompts in agents | `REQ-TA-ARCH-001` (vendors behind router) | partial |
| NFR-006 evaluation population | started-run accounting | `REQ-TA-NFR-EVAL-001` | same |
| GOV-001 test-plan approval | prior approval gate | `REQ-TA-GOV-002` | same |
| GOV-002 registry schema | schema validation: A's validator + `scripts/ci/check_requirement_schema.py` + `requirements schema` CI job + `test_requirement_schema_gate.py` | `REQ-TA-GOV-004` (present, `status: proposed`; gate **implemented+verified**) | same |
| GOV-003 CI gates | `REQ-TA-GOV-003` = **AI-log merge obligation** (registry status: `proposed`); observed CI also runs `type check`, `security checks`, `required tests`, `ruff`, `dependency` (implemented, hosted-verified) — these are *different* course duties, not `REQ-TA-GOV-003` | `REQ-TA-GOV-003` (AI-log) | **partial** |
| GOV-004 semantic threshold | semantic eval gate | `REQ-TA-GOV-001` semantic suite | same |
| GOV-005 AI-use log | AI-log-gated merge | `REQ-TA-GOV-003` | same |
| GOV-006 permissions/branch protection | default-intended-deny + native last-match rules + ADR review; OS ACL/identity outside current guarantee | — (no registered `REQ-TA-*` counterpart) | **none** |

## Supplementary architecture and course duties

These duties are not invented registry IDs. B's INV-01 etc. are architecture
invariants, not aliases for A's REQ-TA-INV-001 etc.

- **Consent/input discovery/holdings minimization:** allocation is
  [input service](../../src/tradingagents/runapi/input_service.py),
  [CLI adapter](../../src/cli/input_ui.py), immutable context and redaction; independent
  probes are C's discovery/consent/privacy suites. `input.consent` and
  `input.mode_resolved` are actual post-confirmation events. Unconfirmed calls
  are refused before dispatch; there is no claim that a rejected pre-run request
  emits a completed run event. Registry coverage remains partial (B's OQ-16 /
  unregistered holdings-minimization scope).
- **Role restrictions and safety/ADR review:** [permission model](permission-model.md),
  [structural constraints](../code-governance/structural-constraints.md),
  [native configuration](../../.opencode/permissions.jsonc),
  [launcher](../../scripts/run_role_agent.py) and
  [permission probes](../verification/opencode-permission-probes-2026-11-25.json)
  give tool-level restrictions when launched in the tested configuration. They
  do not establish OS ACLs, member identity, universal tool activation or an
  automatic GitHub safety-critical reviewer/ADR gate. Follow
  [ADR001](adr/001-portfolio-aware-cli.md),
  [ADR002](adr/002-extended-result-evidence-budget.md),
  [ADR003](adr/003-concise-intermediate-context.md) and
  [ADR004](adr/004-cumulative-token-admission.md); a design ADR is not enforcement.
- **Static analysis and regression:** CI invokes full configured pytest/install
  checks, Ruff, scoped mypy, dependency audits and security/API/permission probes.
  [API snapshot](../code-governance/public-api-contract.json),
  [boundary tests](../../test/offline/member_d_verification/test_security_gate_boundaries.py),
  [type probes](../../test/offline/member_d_verification/test_type_gate.py) and
  [workflow-permission checker](../../scripts/ci/check_workflow_permissions.py)
  provide concrete boundaries. Read coverage limits; passing scans do not certify
  absence of every security defect. Contract probes remain inside pytest.
- **Evidence-preserving evaluation:** the scorer/replay store retains started
  denominators and evidence identity; [B's engineering traces](traceability-inputs-member-b.md)
  and C's harness/scorer tests describe the contribution. Portable evidence and
  independent human scoring are still required for formal semantic acceptance.
- **Token context optimization:**
  [concise-context tests](../../test/offline/member_d_verification/test_token_input_reduction.py)
  and [B's review](../reviews/token-context-architecture-review-2026-11-24.md)
  provide scope/limitations. Measurements are configuration-specific, not proof
  of an adopted cumulative token ceiling. H1 is specifically a call cap.

## Canonical path, ownership and maintenance

`docs/architecture/trace-matrix.md` is the sole editable final matrix. Any earlier
ownership-agreement reference to a CSV is superseded **for the repository artifact
location** by this Markdown path. A CSV may only be a clearly labelled derived
export pointing back here; do not maintain a competing matrix. No ownership
agreement/CSV file was located in this checkout, so no external document is
claimed edited or approved. B's inputs and C's mapping remain contributor source
records, not competing final matrices.

E refreshes affected rows after registry, architecture, implementation, tests,
monitors or protection changes and again before the delivery freeze. Changes
must retain requirement identity, source revision and evidence limits. A verifies
meaning/status and resolves adoption; B verifies components/monitors and CSV
references; C verifies coverage/results and outstanding negative evidence; D
verifies runnable links and measurement controls. No sign-off is inferred.

Document completeness means all 36 active IDs and the three withdrawals below
are accounted for, not that all requirements pass. Open requirements remain
visible above; do not remove them to obtain an all-green matrix.

## Withdrawn IDs — not active acceptance obligations

- **REQ-TA-FR-002** — GUI out of scope; a GUI is a feature, not a quality attribute. The v0.7.1 CLI is the only input.
- **REQ-TA-NFR-SAFETY-001** — Research-only scope: no position sizing is validated.
- **REQ-TA-NFR-SAFETY-002** — Research-only scope. Replaced by REQ-TA-FR-007 part 3 (no ownership wording).
