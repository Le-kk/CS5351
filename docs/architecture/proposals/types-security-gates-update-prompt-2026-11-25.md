# OpenCode architecture alignment — type/security gates and AGENTS.md

Prepared 25 November 2026; **unexecuted**. Continue the existing DeepSeek V4 Flash architecture session. This authorizes documentation drafting only, not application implementation, commits or pushes.

## Establish evidence

Work in `/home/brian/projects/CS5351`; expected HEAD `14b06a57e3e779435614d066dfd6ab94510b0d2b`. First read **AGENTS.md in full**, then follow its startup order. Inspect branch/dirty files and preserve all unrelated drafts. Read:
- `docs/reviews/types-security-gates-review-2026-11-25.md` and its `evidence/types-security-gates-review-2026-11-25.json`;
- `docs/code-governance/types-and-security-coverage.md`, `public-api-contract.json`;
- affected `.github/workflows/ci.yml`, `pyproject.toml`, CI checkers, new tests and source diffs from `32f2be8`.

The supervising reviewer verified mypy on 14 files, a complete 105-file medium/high security scan, five workflow boundaries, 282 scoped offline regressions, repository Ruff, pip consistency and the 36-entry schema gate. The market prompt expression is equivalent by AST substitution. These were local source/offline checks, not paid calls, independent semantic acceptance or E's full-suite rerun. GitHub job outcomes and probe state are in the facts. Seven required checks are E-reported; administrative settings were not directly inspected (HTTP 401).

## Bounded write set

Edit only:
1. `architecture-blueprint.md`
2. `docs/architecture/permission-model.md`
3. `docs/architecture/risk-list.md`
4. `docs/architecture/traceability-inputs-member-b.md`
5. `docs/architecture/evaluation-logbook.md`
6. `docs/architecture/interface-contracts.md` (current status and integration/migration guidance only)
7. `docs/architecture/memory-design.md` (checkpoint/security integration status only, if needed)
8. `docs/architecture/proposals/implementation-prompt-pack-2026-11-24.md`
9. `docs/req/README.md` (guidance/status only)

## Required corrections and limits

- Replace current claims that AGENTS.md is absent. It exists as startup/ownership guidance, while `.opencode` role ACLs and OS enforcement remain absent. Do not confuse workflow-token checks with per-agent filesystem controls.
- Record the seven exact check names from AGENTS.md; attribute required-setting activation to E and cite observed job/probe evidence. Preserve the administrative read limitation. Do not equate check count with course categories.
- Describe actual type/security scope and exclusions, reviewed suppressions, endpoint/redirect limits, and coverage validation. Trace real helper/test/source paths with correct ownership and seven-column table alignment. Existing C acceptance remains separate.
- Record the public API snapshot as a compatibility guard: intentional planned budget/checker contract changes must coordinate E-owned snapshot updates, implementation, tests, versions and AI log under explicit authorization. Do not edit that snapshot now or weaken its tests.
- Reconcile active prompt-pack and interface-handoff receipt requirements with AGENTS.md's paused mandatory merge prerequisite. Retain human supervision, explicit authorization and proposed test criteria. Preserve the receipt protocol as inactive/historical until explicitly re-enabled; do not fabricate prior approvals, adopt A's requirements, waive course obligations or erase any requirement/enforcement mismatch.
- Document the small runtime hardening accurately. No new financial policy, stop reason or checker rule is introduced. Market instruction text is unchanged but the source-based prompt hash can differ. Literal checkpoint deletes do not introduce resume identity redesign.
- Preserve C1/C2/C3, C2 choice, ADR-002/003/004, token ledger/support-mode limits and all original evidence. No new original-SE claim or tested ADD experiment is implied by adding mandated CI checks.
- Append a dated integration entry with source/evidence provenance. Update current pending lists by meaning without rewriting dated historical observations. Registry remains proposed_for_adoption/proposed; semantic acceptance, OQ-16/OQ-17 and other owner items stay separate.

Do not edit AGENTS.md, application, tests, requirements YAML/schema/validator, governance/CI configuration, API snapshot, reviews/evidence or existing AI logs. No paid calls, broad-suite rerun, commits or pushes. If a real source contradiction appears, stop only the dependent edit and report it.

Finish with exact changed-section mappings; meaningful table checks; links checked against tracked files plus the declared review/evidence/prompt publication bundle; fences/whitespace; verification of unchanged protected paths and unrelated drafts. State remaining owner items and stop for review.
