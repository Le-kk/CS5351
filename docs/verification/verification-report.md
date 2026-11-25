# Member C verification report

Date: 25 November 2026

The closeout package contains the test plan, requirement mapping, regression evidence, review memo, debt register and bug diary. [Document index](README.md) · [Evidence index](evidence-index.md)

## Verification source

The recorded repair runs used local main 1bf6e17dd0ecdd5e5f38b157fafc4c632105a933 with the result/report repairs and regression tests identified in the [test plan](history/test-plan-2026-11-25.md#post-repair-verification--2026-11-25). The final fixture hash and retained log hashes are in the evidence index.

Final delivery-source verification remains open. Git revision/status commands in the current session fail with “Function not implemented”.

## Results

| Verification | Recorded outcome | Evidence |
|---|---|---|
| Focused repair regression | 237 passed | ER-01 |
| Post-repair full regression | 1917 passed, 1 failed; Bedrock discovery failure | ER-02 |
| Semantic harness and scorer | 8 passed | ER-03 |
| Bedrock control | 6 passed | ER-04 |
| Initial conflicting AWS environment | 1 failed, 5 passed; region leakage identified | ER-05 |
| Final conflicting AWS environment | 6 passed | ER-06 |
| Final Linux regression | 1918 passed, 1 skipped, 1 deselected; exit 0 | ER-07 |

The final regression's skip is the opt-in live semantic replay; the deselection follows the configured integration exclusion. The [evidence index](evidence-index.md) provides commands, source bindings and retained logs.

The [bug diary](../bug-diary.md) records repair dispositions. The [mapping](requirement-test-mapping.md) identifies remaining fit-criterion work. Formal semantic evaluation is pending; its [status and contract](semantic-evaluation.md) define the next evaluation.

## Open decisions and next owners

| Decision | Owner | Status | Closeout action |
|---|---|---|---|
| VC-DEC-01 — Requirement basis | A | Reporting complete; adoption open | Use registry 1.2.0 with proposed_for_adoption status; A supplies the final scope/adoption record. |
| VC-DEC-02 — Engineering gaps | A/B/D | Deferral proposed | Resolve submission-critical defects; assign remaining work through the debt register. |
| VC-DEC-03 — Delivery-source verification | C/E | Open | Bind the final team SHA/configuration to applicable checks and evidence. |
| VC-DEC-04 — Formal semantic replay | A/C | Deferred optional work | Complete the approved cohort and scoring when resumed. Historical PASS remains unverified. |
| VC-DEC-05 — Final integration | E | Ready for handoff | Integrate C's mapping, quality records and report contribution; retain test-plan pre-approval as paused. |
| VC-DEC-06 — Evidence index | C | Index prepared | Use the new index for retained logs and commands. Locate missing original semantic evidence before formal scoring. |

## Delivery

The [document index](README.md) lists the verification materials prepared for E. [Review memo](../review-memo.md) and [debt register](../debt-register.md) provide the quality decisions and follow-up owners.

## Addendum — INV-008 negative disclaimer-position probe (25 November 2026)

The H5 reconciliation (`REQ-TA-SEC-003` / `REQ-TA-INV-008`) states that a report whose disclaimer appears only later is a blocking violation, not merely a "contains" gap. The recorded twenty leading-disclaimer nodes were positive-only. A negative probe was added: `TC-SEC003-c` in `tests/member_c_verification/offline/test_registry_gaps.py::test_inv008_disclaimer_only_later_is_a_violation` (parametrized Markdown / HTML).

It renders a document whose disclaimer is present but placed after a title/header and asserts the position contract is violated — Markdown first non-blank line, HTML first visible element inside `<body>` with structure markup excluded — matching the requirement's own measurement. It also records that presence-only checking (rule Q3) cannot catch this, so the invariant is upheld at the exporter layout the positive nodes assert.

| Verification | Recorded outcome | Evidence |
|---|---|---|
| `test_registry_gaps.py` (whole module, incl. `TC-SEC003-c`) | 42 passed | developer regression, this checkout |

This is a developer regression for the exercised offline module, not independent C acceptance, not a live/semantic result, and not a claim that the full guarantee-phrase / R8 corpus is covered. Registry status for both entries remains `partial` / `proposed`, not adopted. The 40 positive nodes and 2 new negative nodes are unit-level assertions over the shared boundary.

## Historical reference

[Earlier records](history/verification-report-2026-11-25.md)
