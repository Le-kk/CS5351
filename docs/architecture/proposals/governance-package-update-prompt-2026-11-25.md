# OpenCode planning handoff — governance-package architecture alignment

Prepared 25 November 2026; **unexecuted**. Paste this self-contained prompt into the selected session if reading this file or the supporting review is denied. Human-provided evidence is a handoff, not permission to bypass tool restrictions.

## Objective and reviewer-provided facts

Plan a documentation-only alignment of B's architecture to E's governance package. Expected local checkout is `/home/brian/projects/CS5351`, main `32ec858bc6af2abf387f29e65439cc1d45936d8b`, incorporating B `3de2f1c` and E `345d983`. Seventeen unrelated draft/review files were preserved. Treat this revision as supervising-review evidence until you can inspect it through permitted tools; do not claim you personally ran Git.

Read root AGENTS.md, `.agent/rules.md`, `.opencode/rules.md`, Prompt.md, the canonical blueprint and relevant architecture. Consult permitted governance guides: `structural-constraints.md`, `mcp-tool-manifest.md`, `opencode-permissions.md`. If a path/tool is denied, report it and use the supplied facts or request the needed human/owner handoff. Do not switch tools/roles to bypass it.

Facts observed by the supervising Codex review:
- New E3–E8 documents/config/helpers exist; application, requirements, dependencies and CI jobs did not change in this update.
- Current E7 native evidence records 69 passing synthetic cases on OpenCode V1 1.19.5. Current policy, operating-rule and covenant hashes match. Older E5/E6 policies differ intentionally (50/62 historical cases).
- The known local executable is 1.18.34. B launcher --check was refused by the version guard; native probes were not rerun, no upgrade or model session was started. Do not claim this machine or your existing session has activated the new policy.
- Native permissions use last matching rule wins, not blanket deny-wins. Explicit launcher config and selected profile are needed; operating rules load as the role prompt, while the covenant is startup-read, not automatically injected. Prompt.md H1/H2/H3 decisions are not authenticated/recorded automatically.
- Role B native tools deny shell/Git/tests/search/delegation/web/MCP, edits to the implementation-prompt-pack proposal and docs/req/README.md, and do not explicitly allow the review directory. Separate current task authorization from executable tool capabilities. Do not self-relax policy or edit human-only `.opencode/rules.md`.
- Helper lint, current requirements validation (36/3/0/0) and seven existing layering tests passed. No live calls or broad-suite rerun occurred.

## Plan the bounded update

Propose edits to B-owned canonical files only where needed:
- `architecture-blueprint.md`: present/configured versus locally active controls; startup and launch procedure references.
- `docs/architecture/permission-model.md`: as-built native rule precedence, activation, actual role capabilities, own-log allowance, owner exceptions and enforcement limits. Preserve the historic intended protection outcomes rather than claiming native deny-wins semantics.
- `docs/architecture/risk-list.md`: narrow absent-controls risks to conditional activation, local version compatibility, OS/identity/symlink/rule-freshness and review residuals.
- `docs/architecture/traceability-inputs-member-b.md`: actual configuration/launcher/verification links; 69 E-recorded cases with matching hashes versus local refusal. Keep C acceptance separate and table columns correct.
- `docs/architecture/evaluation-logbook.md`: dated integration/provenance; no invented retroactive role activation, approvals or original-SE experiment.
- `docs/architecture/interface-contracts.md`: external-owner and future handoff guidance only; runtime contracts stay unchanged.

Identify two separately delegated targets: `docs/architecture/proposals/implementation-prompt-pack-2026-11-24.md` and `docs/req/README.md`. Explain the owner/explicit configuration exception or authorized external-session route needed to edit them; do not attempt denied writes. Their intended content is launch H1/H2/H3 and compatible-profile instructions, preserving paused SHA receipts and existing human authorization.

No edits to AGENTS.md, Prompt.md, covenant/rules, permission config, E guides, application, tests, requirements/schema/validator, CI, original evidence or logs during this planning turn. No paid calls, dependency/tool upgrades, commits or pushes. Do not copy the old unrestricted workflow into strict B by asking it to execute denied Git/pytest commands.

Keep registry adoption, semantic acceptance, OQ-16/OQ-17, budget/evidence/checker proposals and C2/ADR history unchanged. This package installs local tool controls only when correctly activated; it adds no OS sandbox, member authentication, project MCP integration or new required merge check. Preserve historical snapshots with dated superseding notes.

Present one compact execution plan: precise readable/writable paths, delegated/blocked items, actual evidence, before/after claims, link/table/fence/publication checks, rollback and remaining owners. **Stop at H1 for approval of this concrete plan unless an existing explicit decision demonstrably covers it.** Do not invent that approval or infer it from this planning request.
