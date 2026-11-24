# OpenCode follow-up — requirements schema gate alignment

Status: prepared by the supervising reviewer; **unexecuted**. This is a documentation-only follow-up, not approval of product implementation or requirement adoption. Use the existing architecture session with DeepSeek V4 Flash.

Work in `/home/brian/projects/CS5351`.

## Baseline and evidence

The local branch is now `2efbf0fdedeb488a3fe9eb28f8c0daf7af3b06b0`, including our architecture PR #25 and E's schema-gate PR #26. Read:
- `docs/reviews/requirements-schema-gate-review-2026-11-24.md`
- `docs/reviews/evidence/requirements-schema-gate-review-2026-11-24.json`
- `.github/workflows/ci.yml`
- `scripts/ci/check_requirement_schema.py`
- `tests/member_d_verification/test_requirement_schema_gate.py`
- `docs/code-governance/requirements-schema-gate.md`

The supervising review observed the current registry pass (36 entries/3 withdrawn/0 errors/0 warnings), 16 targeted probes pass, dependency/style checks pass, main's schema job succeed and the negative probe's schema job fail. The probe is closed unmerged. E reports that the schema check is required alongside the original four, with strict protection retained. Administrative settings could not be independently read (HTTP 401): attribute E's report rather than claiming this session inspected those settings. No live model calls occurred. Registry/schema/validator/application files are unchanged by this incoming update.

## Objective and permitted write set

Correct factual governance status only in these seven files:
1. `architecture-blueprint.md`
2. `docs/architecture/permission-model.md`
3. `docs/architecture/risk-list.md`
4. `docs/architecture/traceability-inputs-member-b.md`
5. `docs/architecture/evaluation-logbook.md`
6. `docs/architecture/interface-contracts.md` (status/external-owner prose only)
7. `docs/req/README.md` (guidance/status only)

First inspect HEAD and the dirty set. Preserve all pre-existing local files, including the numeric-validation draft and review artifacts. If baseline or source contradicts these facts, stop the dependent edit and explain the concrete difference.

## Required distinctions

- Describe the schema CI job as **implemented and locally/hosted verified**. Record merge-protection activation as **E-reported**, with evidence and the direct-read limitation. Do not retain a current claim that the schema job is absent/unwired.
- Trace `SEL-TA-GOV-002` → `REQ-TA-GOV-004` → A's validator + new checker + named CI job + real tests/evidence. `SEL-TA-GOV-004` remains semantic evaluation (`REQ-TA-GOV-001`), not this schema gate.
- Narrow governance risks rather than closing all governance: OpenCode role-permission enforcement, paused test-approval enforcement, independent semantic acceptance, adoption, consent OQ-16 and evaluation OQ-17 remain separate.
- Preserve the YAML's `proposed_for_adoption`/`proposed` states. Installed checks are not A's adoption decision. Do not rewrite the explicitly historical requirement note about the older pre-gate baseline.
- Append a dated logbook integration entry; preserve C1/C2/C3, C2 selection, ADR-002/003/004 reasoning and authentic historical observations. This adds no architecture experiment, candidate comparison, approval, original-engineering claim or runtime behavior.
- Add the gate's safe local reproduction command/link to requirements guidance. Do not edit requirements, schema or validator.
- Clear current-status contradictions in headers, risk rows and pending lists by meaning. Keep genuinely historical revision pins and label their scope.

No application/test/CI/governance implementation/evidence/AI-log edits; no paid calls, commits or pushes. Do not run a broad suite again merely to repeat the recorded review. Finish with exact changed-section mappings, a publication-aware link/fence/whitespace check, scope/preservation verification and accurately separated remaining owner items. Stop for review.
