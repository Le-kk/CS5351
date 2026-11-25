# Selected AI-use record — project covenant

Date: 2026-11-25. Role: E. Task: E7.

## Original user request

> 请完成**E7 — `.agent/rules.md` — Course-required; missing.\*\***
>   Record the project covenant: abstraction/dependency limits, independent negative tests, safety-critical change approval and rule freshness. Existing governance and architecture material can be consolidated.

## Public assistant replies (selected)

> 我会把架构和治理材料整理成项目约章，明确依赖边界、独立负面测试、安全关键变更的批准要求及规则更新方式，并区分已有检查和人工审核要求。

> 约章正文已完成，明确区分了开发者自测与独立验收，也保留了“测试事前批准门暂停”的现状。它不会新增 PR 审批步骤；我正在验证所有角色都能读取约章，默认只有 E 能修改。

## Work summary

Created the English project covenant covering abstraction/dependency limits, independently owned negative-test criteria, authorized safety-critical change review/evidence, change-triggered rule freshness and honest handoff. Added it to the root startup reading order, granted all five roles read access while retaining E's default write authority, and extended the existing native permission probes and current-evidence references. The separate human-controlled operating rules were not edited. Added this record. Full write payloads and internal reasoning are omitted.

The first extended negative fixture attempted identical replacement text after a successful control edit; the runner correctly refused to count that non-permission error as a successful denial. Replacement text was made role-specific and the native probes rerun. No permission failure was waived. No application code, dependency, workflow, required merge check, mandatory peer Review or paused pre-approval setting was changed. Covenant process obligations are distinguished from automatically enforced checks; independent acceptance is not fabricated.

## Observed verification and file sizes

69 native permission probes passed; actual-project `E --check` passed; full-repository Ruff and affected document links/whitespace passed. Evidence hashes match the current permission policy, operating rules and covenant. No model inference was used. Earlier E5/E6 evidence remains preserved for its original hashes.

Current file lengths (not added-line counts):

- `.agent/rules.md`: 77 lines.
- `.opencode/permissions.jsonc`: 696 lines.
- `scripts/verify_role_permissions.py`: 167 lines.
- `AGENTS.md`: 84 lines.
- `docs/code-governance/opencode-permissions.md`: 66 lines.
- `docs/code-governance/opencode-operating-rules.md`: 38 lines.
- `docs/verification/project-covenant-probes-2026-11-25.json`: 663 lines.
