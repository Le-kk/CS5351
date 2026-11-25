# Selected AI-use record — executable role permissions

Date: 2026-11-25. Role: E. Task: E5.

## Original user request

[Original request excerpt. Nontechnical framing omitted at the user’s request; the technical task below is unchanged.]

> E5 — `.opencode/permissions.jsonc` — Course-required; missing executable permission configuration.
> B's permission design exists. Translate it into configuration supported by the actual tool and demonstrate allowed and denied access.

## Public assistant replies (selected)

> 我会按 OpenCode 支持的配置格式编写权限规则，并对照 B 的角色设计验证允许与拒绝访问。配置和测试结果会分开记录，只有实际验证过的行为才会标为通过。

> 发现一个兼容性问题：当前安装的 OpenCode 1.19.5 使用 V1 权限格式，与官网新版格式不同。我会以本机实际可运行的格式为准；课程指定的 `permissions.jsonc` 也需要显式加载，不能只放在那里就算生效。

## Changes and verification

Created the native V1 A–E role configuration, explicit loader/checking launcher, synthetic native-tool probe runner, usage/limits guide and retained JSON verification record. Updated root startup instructions and the local E3/E4 documents with a dated E5 supplement. Added this AI-use record. Full write/code payloads and internal reasoning are omitted.

Observed results: 50 permission probes passed using OpenCode 1.19.5 native debug tools, including allowed reads/creation, cross-role and secret/private/external denials, human-only writes, native write-tool permissions, blocked shell and the startup symlink guard. The evidence binds the policy SHA-256 and uses synthetic files. The actual project role launcher also accepted `D --check`. No model inference, paid evaluation or change to business code, dependencies, CI jobs, branch protection or the paused test-approval setting was made. The guide records native precedence, loader requirements and OS/identity/race/managed-output limitations; it makes no claim of an unrelated historical workflow or course-wide compliance.
