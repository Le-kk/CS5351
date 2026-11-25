# Debt register

Owner: Member C
Date: 25 November 2026

This register tracks engineering work remaining at project closeout. The [bug diary](bug-diary.md) records concrete defects; the [verification report](verification/verification-report.md#open-decisions-and-next-owners) records delivery decisions.

| ID | Area | Remaining work | Priority / owner | Closure evidence |
|---|---|---|---|---|
| DR-001 | Evaluation evidence | Complete a formally scored semantic cohort; retain reports, manifests, genuine scores and all started attempts | Deferred optional replay — A/C | Approved cohort/configuration, portable package and scorer result under the agreed rubric |
| DR-002 | Source provenance | Bind the final verification package to the team's delivery revision | Submission blocker — C/E | Team remote, full SHA, dirty-state record and applicable checks at that source/configuration |
| DR-003 | Guardrails and cost | Implement aggregate budget admission and settlement across retries, tools and fallback | Scope decision — A/B/D | Agreed budget contract plus dispatch/cancellation and accounting regressions |
| DR-004 | Evidence and coverage | Complete evidence-ID resolution, channel/core coverage and freshness rules | Scope decision — A/B/D | Agreed channel catalog and fit criteria, implemented evidence/coverage records and passing positive/negative tests |
| DR-005 | Type coverage | Extend typing beyond the configured run boundary and portfolio/output contracts | Follow-up — D/E | Reviewed additions to mypy scope, resolved diagnostics and CI results |
| DR-006 | Context maintenance | Resolve the repeated-argument reference/compaction boundary and evaluate concise-context quality | Quality follow-up — D/C | Boundary regression and controlled semantic comparison; see RM-003 |
| DR-007 | Human review | Retain the remaining attributable owner decisions and final review | Submission input — A/B/C/E | Decision references tied to scope/revision; final trace-matrix review |
| DR-008 | Evidence packaging | Restore or replace broken current-document references with an auditable submission index | Packaging follow-up — C/E | Checked current links and a durable sanitized package matching the evidence index |
| DR-009 | Personal submission | Supply Member C's full session export, personal reflection and contribution/time record | Submission input — Member C | Named export, 300–500-word personal reflection and actual contribution data |

## Source records

- [Requirement mapping](verification/requirement-test-mapping.md): budget, evidence, coverage, sentiment and fit-criterion gaps.
- [Semantic contract](verification/gov004-evidence-package.md): frozen cohort, eligibility, scoring and packaging.
- [Type/security coverage](code-governance/types-and-security-coverage.md): selected type scope and scanning boundaries.
- [Token-context review](reviews/token-context-architecture-review-2026-11-24.md): reference/compaction behavior and quality work.
- [Evidence index](verification/evidence-index.md): retained regression logs and source bindings.
- [Deliverables and ownership](../project-deliverables-and-ownership.md): final submission responsibilities.

## Closeout rule

A/B settle scope and contract decisions, D supplies fixes, C records verification and E integrates the accepted package. Each item closes against the evidence in its final column.
