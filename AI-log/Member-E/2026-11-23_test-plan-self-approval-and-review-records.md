# Test-plan self-approval and implementation self-review records — 2026-11-23

## Original user request

能修改新门禁，使每个人能自我审查并在批准后把需求、架构、代码及测试质量、运行信息自动写在文件里吗

## Original scope confirmation

允许测试计划自批，并另生成实现后的自查记录

## Implementation summary

The confirmed roster may self-approve a test plan only when the explicit baseline policy flag allows it. Approval receipt schema 2 records the actual PR author and labels self_review versus peer_review. Pre-implementation order, scope, hashes, roster checks and revocation remain enforced. Governance self-approval and native GitHub approving Reviews are not changed.

A separate read-only workflow accepts a newly submitted `/self-review <full current SHA>` command from the real authorized PR author. It generates `docs/review-memo.md` and a JSON receipt as Actions artifacts, collecting requirement references, changed architecture/code/test files, required CI results/timestamps/durations and receipt runtime metadata. Optional human judgments are attributed; absent assessments are marked unassessed. Missing/failed/skipped/stale checks cannot yield APPROVE. No paid model call is used and no protected-branch write or peer approval is fabricated.

Generated files are downloadable evidence, not automatically merged repository files. Archiving into protected main still uses the normal repository process. This changes the proposed PR #11 implementation; it does not claim that the pending gate is already active on main.

Modified: the approval policy/checker, approval archive instructions and completion regression fixture. Added: the self-review collector, workflow, usage instructions, regression tests and this log. Full code/write payloads, tool results and internal reasoning are omitted. Actual test results are reported separately rather than invented here.

## Change quantities and validation

Relative to the previous local PR #11 head `201eed0`; the following figures exclude this AI-log file.

- `scripts/ci/check_test_approval.py` — modified; +43 / -12 lines.
- `scripts/ci/build_pr_self_review.py` — added; 213 lines.
- `.github/workflows/pr-self-review.yml` — added; 38 lines.
- `docs/code-governance/test-approval-policy.yaml` — modified; +4 / -0 lines.
- `docs/verification/approvals/README.md` — modified; +5 / -1 lines.
- `docs/code-governance/self-review-workflow.md` — added; 38 lines.
- `tests/member_d_verification/test_test_approval_completion.py` — modified; +1 / -1 lines.
- `tests/member_d_verification/test_pr_self_review.py` — added; 186 lines.

Validation: 1,789 passed, 2 skipped, 1 deselected and 100 subtests passed in the full local offline suite. The two gate/self-review test modules contain 50 passing cases. Verifier self-tests, full-repository Ruff and all three relevant workflows under actionlint passed. No real self-approval command, receipt or model call was fabricated during testing.
