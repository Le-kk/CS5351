# Test-approval workflow validation correction — 2026-11-23

## Original user request

请尝试在GitHub上实施新增门禁，并创建一次测试提交，让我明白新提交的流程和格式

## Observed deployment issue

After bootstrap PR #9 was merged with explicit one-time authorization, GitHub rejected the test-approval workflow before running any job. Local YAML parsing had not detected the GitHub-specific expression restriction. Official actionlint 1.7.12 reproduced the error: calling `cancelled()` in a run-script expression is not allowed; status functions belong in job/step conditions.

## Correction

One workflow file is corrected: pass `job.status` through a step environment variable, and inspect that variable in the shell. The failure/cancellation step condition remains unchanged. No approval rule, reviewer roster or branch-protection requirement is weakened. This log is the second changed file. No successful receipt or human review is fabricated.

Tool calls, edit payloads and internal reasoning are omitted. The corrected workflows are checked using actionlint; actual GitHub validation remains part of deployment verification. A follow-up PR is needed because the earlier administrator authorization applied only to PR #9.
