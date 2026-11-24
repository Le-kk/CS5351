# Requirements schema gate — integration review, 24 November 2026

Reviewed by Codex after updating the local project from `daa9caa` to **`2efbf0f`**. All 17 pre-existing local draft/review files were backed up privately and verified byte-for-byte unchanged.

The update is sound for the checks performed. It adds a working CI schema/cross-record gate; the architecture needs a focused governance-status alignment, with no application or token-design restart.

## What changed

[PR #26](https://github.com/kelepawuqiusi/CS5351/pull/26) adds the fixed `requirements schema` job in [ci.yml](../../.github/workflows/ci.yml), [a checker](../../scripts/ci/check_requirement_schema.py), [16 regression probes](../../tests/member_d_verification/test_requirement_schema_gate.py), [governance instructions](../code-governance/requirements-schema-gate.md), dev dependency declarations/reviews and E's AI-use note. The seven-file update does not alter `tradingagents/`, `cli/`, the requirements YAML, its JSON schema or A's validator.

The checker reuses A's validator. It requires files to exist, a successful validator exit and exactly one completed summary reporting a nonempty registry with zero errors. Missing/broken inputs, cross-record failures, crashes, timeout and incomplete output produce one named gate failure. Warnings remain warning counts. The independent job runs on every PR and main push; it makes no model calls.

## Observed verification

- Local checker: **36 requirements, 3 withdrawn, 0 errors, 0 warnings**.
- Local targeted probes: **16 passed**; dependency consistency and targeted Ruff passed.
- The existing local virtual environment initially lacked `jsonschema`. The newly declared validation dependencies were installed there; the check then passed. No dependency source files were edited during review.
- Main's [schema job passed](https://github.com/kelepawuqiusi/CS5351/actions/runs/45426035382/job/138558179212).
- E's [negative probe PR #27](https://github.com/kelepawuqiusi/CS5351/pull/27) changed a priority to invalid `Essential`. Its [schema job failed](https://github.com/kelepawuqiusi/CS5351/actions/runs/45426291403/job/138559098065); the PR is closed and unmerged. Other required test jobs also failed, so that observation alone does not isolate which protection rule prevented merging.
- E's deployment update in PR #26 reports that main requires `requirements schema` alongside the original four checks, retains strict up-to-date protection and was observed to block the probe. **Attribution:** source/check outcomes above were independently read; the administrative required-check endpoint returned HTTP 401, so the exact protected setting remains owner-reported in this review. An empty public rulesets response does not establish that classic branch protection is absent.

## Architecture updates needed

| File | Focused correction |
|---|---|
| `architecture-blueprint.md` | Separate the now implemented/tested schema CI job from the remaining governance work. Record current review baseline and evidence provenance. |
| `docs/architecture/permission-model.md` | Correct header and §4 claims that schema validation is unwired or that no fifth gate exists. Keep OpenCode permission enforcement and paused test-approval enforcement separate. |
| `docs/architecture/risk-list.md` | Narrow R-GOV/R-REQ-IDS and open decisions; retain adoption, permission, approval and administrative-evidence residuals. |
| `docs/architecture/traceability-inputs-member-b.md` | Map `SEL-TA-GOV-002` to `REQ-TA-GOV-004` and the real checker, validator, CI job, tests and observed evidence. Do not confuse the semantic GOV-004 namespace. |
| `docs/architecture/evaluation-logbook.md` | Append a source/evidence-based governance integration entry; preserve historical drafting observations. |
| `docs/architecture/interface-contracts.md` | Update only external-owner/governance status text, including the stale header about publication of the two already-present IDs. Runtime contracts are unchanged. |
| `docs/req/README.md` | Link the gate/reproduction instructions and qualify the old schema-installation limitation as historical. Preserve registry authority/adoption status. |

This is `REQ-TA-GOV-004` / `SEL-TA-GOV-002` schema validation. **`SEL-TA-GOV-004` is semantic evaluation**, whose counterpart is `REQ-TA-GOV-001`. Green schema CI does not establish semantic adequacy, product implementation, human adoption, D5 transcript completeness or an original engineering contribution by itself. The registry still says `proposed_for_adoption` and its requirement entry still says `proposed`; B must not change A's status.

No ADR restart, runtime-policy number, checker rule, budget design or input/report contract change is required. Current canonical architecture files were left untouched for the established OpenCode drafting workflow. A prepared [update prompt](../architecture/proposals/requirements-schema-gate-update-prompt-2026-11-24.md) supplies a bounded documentation write set. Detailed facts: [review evidence](evidence/requirements-schema-gate-review-2026-11-24.json).
