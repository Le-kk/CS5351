# AI use — requirements schema gate

Date: 2026-11-24 (Asia/Hong_Kong). Tool: Codex. Owner context: Member E CI implementation.

## Original user request

> 请问现在可以尝试实现模式门：需求注册表根据其 JSON 模式进⾏验证吗，如果可以请实施

## Public assistant reply

> 我会检查最新需求注册表、JSON Schema、校验器和 CI 配置。如果具备条件，就补齐校验与正反例测试，接入独立检查，并提交 PR；验证通过后再将它设为必需检查。

## Work and boundaries

The current 36-entry registry passes Member A's existing validator. Added a fail-closed CI entry point reusing that validator, an independent `requirements schema` job, acceptance probes, explicit PyYAML/jsonschema dev dependencies and their dependency-review entries, plus implementation documentation. No requirement statement, schema, business behavior or paused test-approval rule was changed. Full code/write payloads and internal reasoning are not reproduced here.

Files: workflow, pyproject dev dependencies, dependency review, new gate script, new test file, new governance guide and this log (7 files). The tests include the required positive and five negative cases plus cross-record and incomplete-execution failures. Local and GitHub validation/deployment outcomes are recorded in the subsequent verification entry when observed; no human approval is fabricated.

## Observed local verification

The current registry reports 36 requirements, 3 withdrawn, 0 errors and 0 warnings. All 16 gate probes passed. Full offline regression: 1,813 passed, 2 skipped, 1 deselected, 100 subtests passed. Full-repository Ruff and actionlint for ci.yml passed. No real model calls were used. GitHub activation remains pending real CI results at this commit.
