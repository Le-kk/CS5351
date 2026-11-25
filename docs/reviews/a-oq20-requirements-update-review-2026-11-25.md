# A's OQ-20 requirements update — upload-package review

25 November 2026, Asia/Hong_Kong. Inspected main: **6b468546d5d2c1dde9a066f238207d6aab65c061**.

## Outcome

Main fast-forwarded from 6b57aad; only docs/req/requirements.yaml, requirement-source-notes.md and change-log.md changed. All 36 existing local files were privately snapshotted and preserved byte-for-byte during sync. No source/tests/CI/runtime behavior changed. The reviewed nine architecture documents remain local edits. **A small documentation refresh is appropriate; no new architecture or footer-removal implementation is justified by this update.**

## Clarifications that fit the reviewed design

- OQ-20 confirms nonblocking trial reporting while QUALITY_THRESHOLD is open, followed by blocking after the owners establish the required baseline/parameter and integration conditions. Nonblocking describes the gate, not exemption from behavior verification.
- The current five cases/two trials are **five cases**, not ten of twenty. They are an explicitly labelled project trial while provisional N_EVAL remains 20. Existing scorer cohort kind/trial fields and a raw legacy scorer PASS do not by themselves confer registry-level acceptance.
- Missing-data disclosure (FR-005), ownership wording (FR-007), injection resistance (SEC-001), and guarantee/disclaimer checks (SEC-003/INV-008) remain minimum required behaviors in both phases. Four checked behaviors do not establish all 36 entries implemented. Do not claim all four currently pass.
- OQ-19's reporting entry point is acknowledged: summarize_records(records, *, population=None), with score_gov004.py printing its fields. General comparison acceptance remains separate. No need to redesign or ask B again where the fields come from.
- A states D owns a proposed change to provisional N_EVAL, with the reason recorded in the parameter appendix/change log; A does not reduce it to five. Preserve current 20 unless an authorized recorded change exists. QUALITY_THRESHOLD baseline/value remains D/E-owned, and E owns actual CI activation. This is distinct from blanket registry adoption, which remains proposed_for_adoption.

## H5 note remains internally contradictory — keep the compatibility footer

The update correctly acknowledges build_envelope begins with the frozen DISCLAIMER. It then claims envelope + body is noncompliant **because** the body repeats the disclaimer later, and calls removing the footer the fix. Yet the same SEC-003 note and OQ-18 item 2 explicitly permit a retained compatibility footer when the leading copy exists. The normative first-rendered-visible-content rule contains no one-copy-only restriction. A second later copy does not change the first visible element.

B's reviewed design already retains the footer because Q3 checks the rendered body, while the envelope supplies the leading notice. That remains a compatible design under the explicit permission. Do not remove the footer as a wording-driven fix, and do not modify tests to hide the consequences. If the team later chooses a single-copy layout, the checker subject/assembly contract and matching regressions must change together under a separate authorized implementation scope.

Independent synthetic probe used the real render_body/build_envelope/OutputChecker, no graph/provider/network calls:

| Probe | Observed |
|---|---|
| Current concatenated Markdown | First nonblank line is canonical DISCLAIMER; two copies |
| Current rendered-body check | PASSED, no findings |
| Delete only render_body's disclaimer footer | NEEDS_REVIEW, Q3 missing-disclaimer finding |

See [probe evidence](evidence/a-oq20-footer-probe-2026-11-25.json). This is renderer/checker developer evidence, not independent semantic acceptance or proof of the full no-guarantee requirement. A should reconcile the contradictory explanatory text. B can document the actual implementation and the explicit footer permission without waiting to redesign it.

## What needs refreshing before upload

1. interface-contracts §17: cite OQ-20, label the five-case profile as a project trial, distinguish raw legacy tool verdict from registry acceptance, state the four minimum behaviors remain required in both phases and retain existing scorer thresholds unchanged. Record OQ-19 observation closed; comparisons still unestablished.
2. traceability-inputs §5.4 / risk-list: replace the now-obsolete claim that A still denies a leading envelope with the **new** conflict: duplicated footer claimed noncompliant while explicitly permitted. Preserve the independent H3 null-count conflict, which this update does not resolve.
3. evaluation-logbook: append a dated requirements-only refresh; distinguish implementation source baseline 6b57aad from requirement update 6b46854. Do not rewrite the earlier review into a different historical outcome.
4. Within B's traceability table, remove the remaining current phrase “artifacts not uploaded” for token optimization: the report and compact JSON are published. Keep the narrower limit that raw full replay evidence/independent semantic acceptance has not been established; compact evidence is not a substitute.

Keep §6.4/INV-22's leading notice plus retained footer. Keep the post-check Call budget text deviation open. No new ADR, schema, public API, GOV_PATHS list, activation or behavior change is needed for A's clarification.

## Checks observed

- Requirements schema gate: 36 requirements, 3 withdrawn, 0 errors, 0 warnings.
- All 32 negative fixtures reject for the specified reasons.
- Focused report/population regressions: **56 passed** (test_h3_h5_integration.py and test_registry_gaps.py).
- The synthetic footer probe above passed its three assertions.

The prior 1974-pass default suite belongs to 6b57aad, whose source/tests are unchanged by this requirements-only update; it was not rerun here. No paid application model calls, semantic human scores, requirement/code/test/CI edits, commit or push. Preparation artifacts are new local untracked files.
