# AI use — type checking and security coverage

Date: 2026-11-25 (Asia/Hong_Kong). Tool: Codex. Scope: Member E CI implementation requested by the user. No internal reasoning or full write/code payloads are reproduced.

## Original user request

> 因为补测试事前批准对开发效率是重大打击，所以我准备在所有做完后再启用，请你实施：**补静态类型检查，并核实补齐安全相关专项检查的覆盖范围。**

## Public assistant response

> 我会补上静态类型检查，并逐项核对契约、安全、API 表面和权限测试的覆盖范围，针对缺口补测试与 CI 检查。测试事前批准门继续保持暂停。

## Work and interventions

Initial full-application mypy exploration found 187 errors in 38 of 105 files; the selected shared API/portfolio/output boundary had nine errors. Chose an explicit incremental 14-file type scope and corrected the boundary annotations/narrowing without blanket error suppression. Added actual valid/invalid type probes; the first command-mode fixture conflicted with configured file targets, so it was corrected to use explicit temporary fixture files.

Added a complete application Bandit scan, fail-closed report/coverage checks, a public API surface snapshot, workflow token/checkout permission checks and negative probes. Existing consent, freezing, privacy, layering, replay and terminal/persistence tests are explicitly included in an independent security job. Fixed external XML parsing with defusedxml, guarded the two initial social-feed HTTPS URLs and replaced interpolated fixed-table SQL with literal statements. The fixed market prompt text is unchanged after refactoring its constant assembly to remove a scanner false positive.

Two precise guarded-url B310 suppressions are documented and exercised by unsafe-URL probes; arbitrary new or blanket suppressions fail. OpenCode per-role ACL enforcement remains uninstalled and is explicitly excluded from success claims. No actual model calls were made and test pre-approval remains paused.

## Files and volume

The PR diff records exact line counts. Application changes are limited to shared API/result/rating typing, the two social feeds, fixed checkpoint SQL and unchanged market-prompt assembly. Governance changes include CI, dev/runtime dependency declarations/reviews, API snapshot, AI-log coverage, scanner/permission entry points, focused tests and the coverage guide. Full patches are intentionally omitted here.

## Validation

Observed before the final three suppression-negative probes: mypy passed all 14 files; Bandit covered 105 files with zero medium/high findings and no parse errors; workflow boundary checks passed five workflows. The independent security suite passed 263 tests; full regression passed 1,837 tests with 2 skips, 1 deselected and 100 subtests. Final counts and real GitHub activation evidence are recorded after the completed run; these earlier numbers are not claimed as the final result. Ruff and actionlint passed. No human approval or role ACL deployment is fabricated.

## Final local verification

Full offline regression: 1,840 passed, 2 skipped, 1 deselected, 100 subtests passed. Targeted type/security/RSS tests passed; the final three added probes reject new or blanket scanner suppressions. Mypy: 14 files, zero issues. Bandit wrapper: 105 application files, zero medium/high findings and complete coverage. Workflow checks: five files passed. Ruff, actionlint and the existing 36-entry requirements gate passed. GitHub deployment remains pending at this commit; pre-approval is not re-enabled.
