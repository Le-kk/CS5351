# Selected AI-use record — operating rules

Date: 2026-11-25. Role: E. Task: E6.

## Original user requests

The same request was sent twice during this task; both occurrences are retained:

> 请实现：E6 — `.opencode/rules.md` ，opencode模型需要遵循的规则

> 请实现：E6 — `.opencode/rules.md` ，opencode模型需要遵循的规则

## Public assistant replies (selected)

> 我会创建英文规则文件，涵盖角色权限、架构边界、验证和证据要求，并检查 OpenCode 如何加载它，使规则能在启动时生效。

> 正在完成这项工作。规则正文已写好，接下来会验证 A–E 五个角色启动时都能加载它，同时仍然无法修改规则文件。

## Changes and verification

Created the requested rules file under explicit user authorization; future model writes remain denied for every role. Connected it to all five V1 agent prompts through the native file reference, added exact prompt-loading checks to the role launcher, extended the synthetic probe runner, and documented activation/limits. Added the E6 record rather than overwriting the earlier E5 evidence. Updated root startup instructions and the permission guide. Full write payloads and internal reasoning are omitted.

Observed result: 62 probes passed, including all five native resolved prompts, rules reads, human-only write denials, existing scope/privacy checks and missing/mismatched-rule startup refusals. The initial probe helper assumed edit targets were absent; it was adapted to test the now-existing rules file before the successful rerun. No failed probe was counted as passed. Native debug tools were used without model inference. No business code, dependency, CI gate or branch-protection behavior was changed. Rules guide behavior; loading them does not prove perfect model compliance or OS isolation.

## File sizes after this task

These are current file lengths, not added-line counts or full code payloads.

- `.opencode/rules.md`: 40 lines.
- `.opencode/permissions.jsonc`: 692 lines.
- `scripts/run_role_agent.py`: 91 lines.
- `scripts/verify_role_permissions.py`: 159 lines.
- `docs/code-governance/opencode-operating-rules.md`: 38 lines.
- `docs/code-governance/opencode-permissions.md`: 64 lines.
- `docs/verification/opencode-rules-probes-2026-11-25.json`: 592 lines.
- `AGENTS.md`: 84 lines.

Final checks: actual-project `D --check`, full-repository Ruff, document links/whitespace and configuration/rules hash consistency all passed.
