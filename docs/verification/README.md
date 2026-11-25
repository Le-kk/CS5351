# Member C verification package

Date: 25 November 2026

Member C delivers the test strategy, executable verification suites, requirement mapping, quality reviews, defect analysis and semantic evaluation contract.

## Submission documents

| Document | Content |
|---|---|
| [Verification report](verification-report.md) | Test outcomes and closeout decisions |
| [Requirement mapping](requirement-test-mapping.md) | Requirement coverage and test references |
| [Test plan](test-plan.md) | Test levels, fixtures, commands and acceptance criteria |
| [Evidence index](evidence-index.md) | Retained run logs, results, source bindings and hashes |
| [Review memo](../review-memo.md) | PR-indexed quality reviews and verdicts |
| [Debt register](../debt-register.md) | Remaining engineering work, owners and closure criteria |
| [Bug diary](../bug-diary.md) | Reproductions, root causes, fixes and regression evidence |
| [Verification constraints](../code-governance/verification-constraints.md) | Structural, regression and behavioral acceptance rules |
| [Semantic evaluation](semantic-evaluation.md) | Evaluation status, cases and scoring references |
| [Semantic evidence contract](gov004-evidence-package.md) | Cohort, rubric, attempt accounting and packaging |
| [History index](history/README.md) | Earlier investigations and preserved records |

## Executable verification

| Suite | Location |
|---|---|
| Deterministic contract tests | [Offline suite](../../tests/member_c_verification/offline/) |
| Semantic replay and evaluator | [Live suite](../../tests/member_c_verification/live/) |
| Repair regressions | [Result repair tests](../../tests/member_c_verification/test_registry_result_repairs.py) |

## Final assembly

E uses the document index above and the requirement mapping to assemble the course trace matrix and final report. The evidence index identifies the recorded test snapshot. The final delivery SHA, personal reflection and full session export are the remaining submission inputs.
