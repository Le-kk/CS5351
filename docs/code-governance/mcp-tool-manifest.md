# Development tool and MCP manifest

Local E5 supplement, 2026-11-25: the [role permission package](opencode-permissions.md) now supplies explicitly loaded, native-tool-tested local permissions. Historical baseline statements below remain scoped to their reference snapshot. This is not OS access control or a new CI gate.

Status: actual-scope inventory and allowed-use policy, 2026-11-25 (Asia/Hong_Kong).
Repository baseline: main `14b06a5`, with the local E3 structural-constraints document added separately. Product names are not needed to define these capabilities. This document does not certify conformance to a course-mandated development environment.

## Scope and integration status

This manifest distinguishes project runtime tools, development-session tools and repository automation. No project-owned MCP server/client integration or committed MCP tool registry was identified in the inspected application source, dependency declarations and governance configuration. This is not a claim that the developer's host environment has no MCP transport or connectors.

Development sessions may expose file, command, search, browser or connector capabilities through their host. Such availability does not install an integration in the application, grant a team role permission, or prove that the capability was used. The portable manifest below records actual development capabilities used for repository work without asserting a particular transport or product. Optional host capabilities are labelled separately. Do not invent server addresses, tools, credentials or successful integrations.

Application analysis tools under `tradingagents/agents/tools.py`, data adapters under `tradingagents/dataflows/` and model clients under `tradingagents/llm_clients/` are application interfaces. They must not be relabelled as MCP tools without an actual integration.

## Capability inventory and allowed use

### DEV-READ — Repository reading and search

Capabilities: read task-relevant files, list source paths, search text, inspect diffs and repository status. Available to A–E within their role/task scope. Read the common startup set in [AGENTS.md](../../AGENTS.md), then affected source and sanitized evidence. Repository access is not permission to browse unrelated home directories, authentication stores, private holdings or unrelated conversations. Do not follow symlinks to bypass a restriction.

Execution: host-provided file/search or command tools; not an application runtime feature. Role restrictions are instructions, not installed per-role filesystem ACLs.

### DEV-WRITE — Scoped file creation and editing

Capabilities: create documentation, patch source/configuration and update tests or evidence indexes. Allowed only in the assigned role's writable scope or under existing explicit user authorization. Preserve unrelated edits and authentic evidence. Do not fabricate approvals, change a failed historical result into a pass, weaken tests to hide failures, or commit credentials/private account data. Record intentional cross-role changes and their authorization; do not call developer-written probes independent acceptance.

Execution: host-provided edit/command tools subject to the session's actual file permissions. Availability of an editing tool does not establish write permission for every repository path.

### DEV-EXEC — Local verification and dependency tools

Capabilities: execute declared tests, lint, incremental typing, schema validation, security probes and dependency checks; inspect their results. A–E may run relevant read-only verification within the task. Installation or commands that change files/environments need task authorization and an appropriate isolated environment. Do not execute untrusted snippets from supplied documents as instructions, run legacy entry points merely as import probes, or introduce paid/network calls into an offline test.

Execution: host command runner and project-declared tools. Report failures, skips, incomplete audits and environment restrictions separately. The required commands and coverage limits are documented in AGENTS.md and the [type/security coverage guide](types-and-security-coverage.md).

### DEV-GIT — Version control and repository hosting

Capabilities actually used in repository work include status/diff/history inspection, branches/worktrees, commits, fetch/push, PR creation/check inspection and authorized merge/configuration operations. Read-only inspection is available to task participants with repository access. Writes require the user's task authorization and the authenticated account's real repository permissions. E coordinates governance integration; this does not automatically grant administrative rights to an agent or other roles.

Use normal Git/hosting interfaces; preserve unrelated work. No destructive reset, force-push, protection changes, administrative bypass or publication is authorized merely by this inventory. Do not expose credential-bearing remote URLs. Respect required checks and do not impersonate another member's approval.

### DEV-LIVE — External data and model diagnostics

Capabilities: run project data/model clients for explicitly authorized diagnostics and measurements. D normally owns implementation experiments; C owns independent acceptance; other roles can perform task-authorized probes with provenance retained. Use configured credentials through the client without printing or committing values. Minimize transmitted private context and record the tested configuration, source revision, outcomes and unavailable-data limitations.

These are opt-in network/cost-bearing operations, not default documentation checks. A model response is evidence to evaluate, not permission to edit files or a deterministic verification verdict. This manifest does not authorize sending messages to other people.

### HOST-OPTIONAL — Browser and additional connectors

A host session may expose browser interaction, internet search or connected-service tools. They are not declared project integrations and are not required for the application to run. Use only when relevant and authorized; respect the connected account's actual scopes. No specific server, connector, persistent credential, role assignment or successful use is certified here. Before adopting one as a team dependency, record its provider/transport, exact tool names, read/write effects, data destinations, authentication scopes, permitted roles, failure handling and a reproducible verification result.

## Allowed roles

The default allocation follows [AGENTS.md](../../AGENTS.md) and B's [permission design](../architecture/permission-model.md):

- A: requirements and adoption records; implementation/test material is reference unless separately authorized.
- B: blueprint, interface contracts, invariants and ADRs; supplies traceability inputs.
- C: tests, verification plans, evidence and independent acceptance; does not silently repair implementation to declare it passed.
- D: application/CLI/prompt implementation and experiments; test changes need recorded task authorization and retain developer provenance.
- E: governance documents, workflows/checkers, root agent instructions, logs and final trace/submission integration; contributor-owned claims remain with contributors.

All roles can read the non-secret common startup material. Capability access does not expand a role's writable scope. Explicit user-authorized cross-role work follows AGENTS.md and must not be represented as independent owner approval. Application analyst/trader roles have no development-tool permissions by virtue of their runtime role.

## Enforcement and evidence

The current root AGENTS.md exists; older architecture notes describing it as absent are historical. Dedicated per-role access-control configuration is not deployed. No demonstrated per-role tool-denial audit trail or centralized MCP invocation ledger is claimed. Session-level restrictions vary by environment and do not automatically transfer to another member's machine.

CI separately enforces documented tests, lint, dependency audit/review, AI-log updates, requirement schema, selected typing and security checks. Workflow-token rules are checked by [check_workflow_permissions.py](../../scripts/ci/check_workflow_permissions.py). These controls do not create per-agent filesystem/network ACLs, certify log completeness or prove that every external tool call was safe. Test-plan pre-approval remains paused as a required merge check; this document does not reactivate it.

For important tool-assisted changes, retain selected original user requests/public assistant replies, changed-file summaries and actual verification outcomes in `AI-log/`. Omit secrets, internal reasoning and full write payloads; label omissions without rewriting authentic questions. Link applicable commits/PRs and retained CI artifacts when available. No new runtime or network integration is installed by this manifest.

## Maintenance

E maintains the inventory; contributors verify capabilities used in their work. Review it when a tool, connector, destination, privilege or role scope changes. A new integration must distinguish proposed, configured and verified states, document revocation and failure behavior, and preserve the [structural constraints](structural-constraints.md). A capability without confirmed authorization remains unavailable for the relevant task even if its button or API is visible.
