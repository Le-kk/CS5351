# AI use — root AGENTS startup instructions

Date: 2026-11-25 (Asia/Hong_Kong). Tool: Codex. Task: E2 documentation, no application changes or model calls.

## Original user request

> 请你创建：**\*\*E2 — Root `AGENTS.md` — Course-required; missing.\*\***
> Define the agent entry point, architecture reading order, baseline, readable/modifiable/frozen areas, module contracts and required verification. Existing architecture material provides inputs, but the startup instructions still need to be written.

## Public assistant response

> 我会先阅读最新架构、权限设计和 CI 配置，再创建根目录 `AGENTS.md`，写清启动阅读顺序、角色边界、模块契约和验证要求。会明确区分已生效的门禁、暂停的测试批准门，以及尚未部署的角色权限机制。

## Work and boundaries

Created root `AGENTS.md` from the canonical blueprint, current requirement package, interface/invariant/runtime-policy documents, permission model, verification constraints and actual CI settings. It covers checkout identity, a dated source baseline, ordered reading, role ownership, readable/modifiable/frozen material, public versus legacy application entry points, module contracts, verification commands and honest evidence/handoff rules.

The user explicitly requested `AGENTS.md`; the create-rule skill's general writing guidance was used without creating an unrelated `.cursor` rule. Existing user authorization takes precedence over default role boundaries, and no redundant pre-approval is introduced. Test-plan approval remains paused; seven other required checks are recorded as a dated snapshot. OpenCode role ACLs remain uninstalled; documentation is not represented as OS enforcement. Missing Prompt/Report/trace-matrix artifacts are named as missing, not fabricated.

Two documentation files only. No requirement text, architecture-owner file, test, workflow, dependency or business code was changed. Validation consists of local reference/required-section checks and normal GitHub CI; no new behavioral tests are invented for this documentation change.
