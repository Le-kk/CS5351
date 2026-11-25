# H2 structural result fixes — 2026-11-25

Selected original-language conversation; tool payloads, complete edits and internal
reasoning are omitted. This is a developer work record, not independent acceptance.

## User request (verbatim)

> 请尝试修复H2中的两个结构性问题

## Public assistant explanation (verbatim)

> H2 的两处问题都来自把“存在记录”等同于“仍有错误”：已经纠正的 `CORRECTED` 记录也会被拒绝。我会按“是否仍有 `BLOCKING`”判断结果，并保留未完成运行和 `REVIEW` 的限制。这次只修结果结构，不宣称已实现 R5 的自动纠正逻辑。

## Changes and verification

User-authorized implementation and developer probes cross the default role areas.
An isolated worktree preserves the existing local H1/H4 baseline. Changed
`tradingagents/runapi/result.py`: extend finding vocabulary/severity, validate
severity and output status, determine verdict by blocking findings, reuse
CheckResult validation for completed RunResult. No field deletion or new public
result fields. Added 24 developer probes in
`tests/member_d_verification/test_h2_corrected_findings.py`, a scope/compatibility
note in `docs/code-governance/h2-result-invariants.md`, and hashed verification
record in `docs/verification/h2-result-invariants-2026-11-25.json`.

Before: 11 failed / 13 passed in the new probes. After: 24/24 H2 probes;
31/31 combined H2/H4 probes. Full declared-development-environment suite:
1908 passed, 2 skipped, 1 deselected, 100 subtests passed. Skips: opt-in live
semantic replay; absent optional langchain_aws. Ruff, mypy (15 files), security
scan (107 files, zero medium/high), requirement schema and workflow permission
checks passed. Full tests required local loopback access for authentication
fixtures; no tests were weakened or removed.

No real-model evaluation, complete R5 correction pipeline, version-2 checker
publisher, independent C approval, dependency vulnerability audit, commit or
GitHub deployment is claimed. The existing artifact scorer still fails closed
on unsupported corrected records/versions. H1's earlier evidence is preserved
as a historical snapshot, with new source hashes recorded separately here.
