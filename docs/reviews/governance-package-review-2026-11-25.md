# Governance package integration review — 25 November 2026

Local main is **`32ec858`**, combining our architecture commit `3de2f1c` and E's governance update `345d983` (PR #32). The fast-forward preserved all **17** existing draft/review files byte-for-byte. E's update adds 21 governance/configuration/helper/evidence files or changes; application code, requirements, dependencies and CI jobs are unchanged relative to our previous reviewed upload.

## What is now present

- [Structural constraints](../code-governance/structural-constraints.md): SC-01..07 source/dependency responsibilities, links to existing checks, explicit review-only restrictions and legacy exceptions; no complete cycle/import sandbox is claimed.
- [Capability manifest](../code-governance/mcp-tool-manifest.md): development/runtime capability inventory, not evidence that the application gained an MCP integration. Native strict profiles deny unspecified external/MCP tools.
- [Native permissions](../../.opencode/permissions.jsonc), [launcher](../../scripts/run_role_agent.py) and [permission guide](../code-governance/opencode-permissions.md): explicitly loaded OpenCode V1 **1.19.5** profiles A–E. Native rules use **last matching rule wins**, with broad denies before allowances and sensitive denies last. This differs from B's abstract blanket deny-wins wording and needs an as-built clarification.
- [Operating rules](../../.opencode/rules.md): shared role prompt, exact loading checked by launcher; human-only for agent writes. [Covenant](../../.agent/rules.md): startup-read process document, E-owned edits, negative-test/safety/freshness obligations. Covenant availability does not mean automatic prompt injection.
- Root [Prompt.md](../../Prompt.md): static H1 plan approval, conditional H2 scope decisions, H3 review/delivery process. It is not a runtime trading prompt or an automatic approval recorder. Existing explicit authorization persists; the SHA receipt gate remains paused.

## Verified evidence and local limitation

The latest retained [E7 record](../verification/project-covenant-probes-2026-11-25.json) has **69 passing cases**, with policy/rules/covenant hashes all matching current files. Older E5/E6 records report 50/62 cases for their historical policies; their policy hashes intentionally differ. Do not relabel those older records as verification of today's policy.

The known local WSL executable `/home/brian/.opencode/bin/opencode` reports **1.18.34**. With that directory supplied on PATH, the launcher refuses B startup: `Expected OpenCode 1.19.5; validate migrations before using another version.` This is an observed safe refusal, **not** a passing local native permission demonstration. Native probes were not continued after this refusal. No version upgrade, session migration or model invocation was performed. A bare login-shell command initially did not find OpenCode on PATH; activation also needs the intended binary available there.

Independent local checks: helper Ruff passed; requirements schema passed (36 entries, 3 withdrawn, zero errors/warnings); existing layering regressions **7 passed**. E's native evidence was parsed and hash-checked, not reproduced locally. No paid calls, broad-suite rerun, new gate or branch-protection change is implied.

## Important handoff implications

1. Replace global claims that permission files are absent with **configured and E-native-verified, conditional on explicit compatible launcher activation**. Keep OS ACLs, authenticated member identity, unrestricted-host bypass and continuous symlink isolation outside the guarantee. The startup symlink guard is not race-free isolation and skips denied generated/Git contents.
2. Existing OpenCode sessions are not retroactively governed by these files. The launcher starts a fresh session, selects a role, passes OPENCODE_CONFIG and checks version/resolved policy/prompt; it does not resume old sessions or enforce H1–H3 human decisions.
3. Strict B denies shell/Git/tests, broad search, delegation and external tools. Its edit whitelist excludes the implementation-prompt-pack proposal and requirements README; the review directory is not explicitly readable. User-provided facts/authorized external verification and owner/configuration handoffs are needed. Do not ask B to evade denials with another tool or self-edit policy.
4. Align active architecture handoff with H1/H2/H3, while preserving actual chronology, historical approvals, paused `/approve-tests`, human-only rule ownership and independent C acceptance. Review/semantic acceptance and A's adoption are not established by a permission grant.
5. Update permission-model native precedence, startup read/role rights, traceability and risks; update blueprint/logbook/interface external-owner status. No application/checker/budget redesign or new runtime-policy ID is required. Prompt-pack/README edits need an authorized owner/session because the strict B whitelist does not grant them.

Some E guides explicitly retain old baseline absence statements under dated superseding supplements. Prefer the current supplement plus native hashes; request E clarification where a sentence could still be read as current. Do not rewrite E-owned rules or historical probe records in B's pass.

Details: [review facts](evidence/governance-package-review-2026-11-25.json). A self-contained [OpenCode planning prompt](../architecture/proposals/governance-package-update-prompt-2026-11-25.md) prepares the next bounded documentation pass. Canonical architecture remains untouched by this review; no commit or push was made.
