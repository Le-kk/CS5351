# Type/security gates and root agent instructions — review, 25 November 2026

Local main updated from `32f2be8` to **`14b06a5`** (PRs #29/#31; architecture PR #28 included). All 17 existing local drafts/review files were privately backed up and verified unchanged. No blocking regression was found in the checks performed. Canonical architecture documents remain untouched by this review.

## Changes and verified scope

- New `type check` job: mypy 1.20.2, Python 3.12 target, **14** runapi/portfolio/rating/output-schema files. Imported legacy modules and missing third-party typing are tolerated; this is not full-repository strict typing.
- New `security checks` job: Bandit report/coverage verification over **105 application files**, blocking medium/high findings, plus API, consent, privacy, layering, feed and workflow-permission probes. Helper scripts are outside that application scan. Two guarded feed-url B310 suppressions are reviewed; blanket/new suppressions fail.
- API snapshot in `docs/code-governance/public-api-contract.json` freezes runapi exports, entry parameter names/kinds/defaults and RunResult field names. Intentional contract migrations must coordinate the snapshot, tests and AI-use log; it is not an automatic approval of breaking changes.
- Workflow checker validates explicit read permissions for PR-code jobs and trusted default-branch checkout for privileged workflows. This is CI-token/checkout validation, not installed A–E file ACLs or tamper-proof CI.
- Application hardening: defusedxml for Reddit XML, fixed initial HTTPS-host/no-userinfo guards for Reddit/StockTwits, literal parameterized checkpoint deletes, precise result/rating types and optional-value narrowing. Initial URL checks do not guarantee safe redirects/DNS. No new budget, rating/checker rule or serialized stop reason is introduced.
- The market prompt assembly was refactored without changing its expression: independent AST substitution comparison passed. Source contents changed, so source-based `prompt_hash` may change despite identical assembled instruction text. Preserve revision/hash controls in comparisons.
- Root `AGENTS.md` now exists, defines startup/ownership/verification guidance and records the paused test-preapproval merge check. It explicitly does **not** install `.opencode` role permissions or OS controls. Read it first in the next OpenCode turn.

## Independent verification

Installed only the newly declared mypy/Bandit/defusedxml packages and their needed transitive dependencies into the existing project environment. Local results:

- mypy: **14 files**, zero issues.
- Security scan: **105 files**, zero medium/high findings, complete inventory.
- Workflow boundaries: **five workflows** passed.
- Security-job-related regressions, type probes, RSS/StockTwits and checkpoint regressions: **282 passed**. This is the scoped local run, not a rerun of E's reported full suite.
- Full-repository Ruff, pip consistency and requirements schema checks passed (36 entries, 3 withdrawn, zero errors/warnings).
- No live/model calls; no implementation/test/CI edits, commits or pushes during review.

Main's public GitHub checks show both new jobs succeeding. Required-check configuration is owner-reported as seven checks with strict up-to-date protection; the administrative endpoint returned HTTP 401 and was not independently inspected. Probe PR #30 is recorded in the linked evidence, with its observed state and check conclusions. Preserve this distinction rather than treating a green workflow as proof of protection settings. See [PR #29](https://github.com/kelepawuqiusi/CS5351/pull/29), [PR #31](https://github.com/kelepawuqiusi/CS5351/pull/31), [coverage guide](../code-governance/types-and-security-coverage.md), [review facts](evidence/types-security-gates-review-2026-11-25.json).

## Architecture handoff

Update current governance inventory/coverage, root-agent startup status, permission residuals and requirement-to-code/test traces. Keep schema validation distinct from semantic acceptance and retain proposed registry adoption status. Add the API snapshot to intentional future migration planning. Treat `type check`/`security checks` as required-check names reported by E, not as proof that six course gate categories or original SE ideas are complete.

The active implementation prompt pack and interface handoff still demand `/approve-tests` receipts. Reconcile their current-use wording with AGENTS.md's explicitly paused automatic prerequisite. Preserve human review, real authorization, test planning and authentic chronology. Do not erase published approval obligations or invent a course waiver: describe any requirement/enforcement gap separately. Keep the old receipt protocol historical/inactive for possible later reactivation, not a mandatory blocker today.

No new ADR cycle or runtime architecture restart is needed. Prepared [OpenCode update prompt](../architecture/proposals/types-security-gates-update-prompt-2026-11-25.md) specifies nine bounded documentation paths. Existing runtime contracts, ADR history and original evidence remain preserved.
