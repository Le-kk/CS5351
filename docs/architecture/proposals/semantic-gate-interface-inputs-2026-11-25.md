# Semantic-gate technical boundary and interface — B input for E

Date: 25 November 2026 (Asia/Hong_Kong). Source inspected: `6b57aadff96798a8832baa0215f37ef407b356dc`.
Status: **concrete proposed B interface for the canonical architecture update and E's integration review**. Current replay/scorer/packager exist; the path classifier, gate wrapper/metadata and formal CI blocking described below are **not installed by this proposal**. No paid execution, threshold/profile adoption, requirements amendment, owner approval or required-check activation is authorized here.

Reference: REQ-TA-GOV-001 (semantic gate) / historical SEL-TA-GOV-004; these are distinct from REQ-TA-GOV-004 (requirements schema gate). Root Prompt.md human H1/H2/H3 are unrelated to the report defect labels.

## 1. Coverage of E's request and canonical destination

The existing post-sync plan covers evaluator counts and artifact compatibility, but not a complete semantic CI contract. Add a short, self-contained semantic-gate section in interface-contracts.md (next unused top-level section, expected §17 after checking the file). Cross-reference it from blueprint, traceability, risks and runtime policies as needed. An ADR is unnecessary merely to repeat this section; propose one only for a genuinely new architectural alternative requiring a decision. Do not rebuild the evaluator or rewrite existing architecture history.

The canonical section must distinguish three layers: (1) the opt-in replay/score/package tools already present; (2) this proposed trigger/current-head/CI adapter; (3) acceptance policy and formal activation owned by A/C/D/E. The current seven required checks do not include a mandatory semantic check; ci.yml explicitly keeps live replay opt-in. GOV_PATHS currently appears as a requirement reference, not a defined/enforced path list in code.

## 2. GOV_PATHS v1 — concrete proposed matching policy

This list is a file-level conservative trigger, not a claim that every listed edit changes financial prose. Even comment-only edits inside a matched source file trigger; no ad-hoc per-PR exemption. A coarse over-trigger is preferable to an unexplained semantic bypass; E owns implementing/adopting the policy and controls actual paid dispatch.

Paths are case-sensitive repository-relative POSIX paths, with no leading slash. A trailing slash below means prefix matching over all descendants; other entries are exact paths. No ambiguous glob engine is needed. Use trusted base/head diff information. Add/modify/delete/type-change/copy and both old/new paths of a rename are checked; moving a governed file out still triggers. Multiple matching files produce one evaluation decision per candidate commit, not one job per file. If diff/classification fails, applicability is UNKNOWN, not NOT_APPLICABLE.

**Prefix entries:**

```text
tradingagents/
cli/
prompts/
config/
configs/
.github/workflows/
```

prompts/config/configs are reserved future locations if absent now. The production prefix deliberately includes context assembly, prompts, agents, provider/model factories, data/vendor handling, portfolio semantics, report/check/finalization and budget dispatch: all can change the evaluated output even when the prompt-source hash stays unchanged. cli/main.py/defaults and root main.py are included for integration effects; replay still evaluates the supported runapi path, not all legacy-entry behavior.

**Exact entries:**

```text
main.py
pyproject.toml
requirements.txt
uv.lock
poetry.lock
tests/member_c_verification/live/cases.py
tests/member_c_verification/live/conftest.py
tests/member_c_verification/live/runner.py
tests/member_c_verification/live/replay_store.py
tests/member_c_verification/live/score_gov004.py
tests/member_c_verification/live/package_gov004.py
tests/member_c_verification/live/test_gov004_live.py
docs/verification/semantic-evaluation.md
docs/verification/gov004-evidence-package.md
docs/code-governance/verification-constraints.md
docs/req/requirements.yaml
docs/architecture/interface-contracts.md
scripts/ci/check_semantic_gate.py
docs/code-governance/semantic-gate-policy.json
```

The last two are **proposed future E-owned implementation/policy locations**, not files asserted to exist. Dependency files may contain dev-only changes: v1 conservatively triggers at file level. The canonical contract is included because a changed gate boundary must not silently reuse an old approval. Case/rubric/profile/scorer/packager/policy changes require owner review/freeze before evaluation; this list does not let a PR weaken its own grading policy. Compare under the trusted previously approved policy and the proposed policy (union of matched paths); a policy modification cannot remove its own obligation. E chooses the trusted execution/reviewer mechanism; do not run arbitrary fork workflow code with school credentials merely because a path matched.

**No automatic live-replay trigger** for changes confined to: AI-log/, docs/reviews/, docs/submission/, ordinary architecture/ADR/README prose other than the explicitly listed contract, images/video, tests/member_c_verification/offline/, live/test_harness_selfcheck.py, live/test_score_gov004_exitcodes.py, other test-only files, or generated/sanitized evidence artifacts. This does not exempt them from ordinary tests, evidence-integrity review or owner review. Path matching above takes precedence; there is no exclusion that cancels a matched path. Raw .env/credentials/private holdings are never expected PR inputs; changing private runtime configuration still changes the actual config fingerprint and invalidates unmatched evidence, even though it is not a committed path change.

## 3. Reuse the existing entry points; bind the evaluated candidate

Reuse, without a second implementation of counting/scoring:

- Replay: `.venv/bin/python -m pytest -q -s -p no:cacheprovider tests/member_c_verification/live/test_gov004_live.py`, internally runner.run_case -> run_analysis_api and replay_store.dispatch_slots. GOV004_LIVE=1 enables paid replay; GOV004_TRIAL=1/2 selects formal slots; GOV004_EVIDENCE_DIR isolates each run. Formal GOV004_TICKER/GOV004_DATE must match the frozen cohort. No trial is diagnostic, not formal evidence.
- Score: `GOV004_EVIDENCE_DIR=<root> .venv/bin/python tests/member_c_verification/live/score_gov004.py <scores.json>`. Preserve its fixed config/threshold floor and source/case/exposure/eligibility checks.
- Package: `.venv/bin/python tests/member_c_verification/live/package_gov004.py <root> <new-destination> --scores <scores.json>`, then re-score the portable package from a fresh directory using GOV004_EVIDENCE_DIR=<new-destination>. The destination must be new and independent. Packaging success alone is not a semantic verdict.

The proposed E gate adapter records one GateEvaluation envelope outside the existing formal evidence directory/package; do not silently add fields to RunResult, application manifests or existing formal schemas. Minimum envelope:

```text
gate_contract_version: 1
gate_mode: PILOT | BLOCKING
applicability: REQUIRED | NOT_APPLICABLE | UNKNOWN
policy_digest: SHA256 of approved GOV_PATHS/mode/profile/rubric policy
base_sha, target_head_sha, evaluated_head_sha: full commit IDs
runner_revision, scorer_revision, packager_revision: immutable approved tool revisions
case_catalog_sha256, rubric_sha256, cohort_sha256, config_sha256, prompt_hash: full digests
evidence_root_ref, portable_package_ref, package_integrity_sha256, scores_sha256: safe refs/digests or null
raw_scorer_exit: 0 | 1 | 2 | null
semantic_verdict: PASS | FAIL | PENDING | null
reason_code: bounded safe code
```

Fields not yet available are null with PENDING; null is never accepted as a matching binding. NOT_APPLICABLE has semantic_verdict=null, not PASS. The exact metadata serialization/location is an E implementation concern, but these semantics must be retained. Candidate choice is the PR's exact full head commit, not a mutable branch name or an unspecified merge checkout. Use a clean isolated checkout of that commit for formal approval. Existing `_source_revision()` stores a short git label and can append +dirty: it is not sufficient to prove exact PR-head correspondence. The adapter must independently bind the full SHA to that label and require evaluated_head_sha == current target_head_sha immediately before posting/using the result. New head commit invalidates approval; this initial design offers no cross-commit cache reuse. Dirty runs may be diagnostics only, with an identified snapshot; they do not approve a later clean commit.

Freeze cohort.json and the actual approved tool/rubric/case/config digests before dispatch. Changed grading tools/policies require C/E review, not use of a candidate-controlled scorer that can self-award PASS. The current runner preflights actual source/prompt identity, full cohort schema/slots/chronology, selected ticker/date, model IDs and both tier providers before graph calls; reuse those checks. Source-template prompt_hash and per-call PromptCapture prompt_sha256 are different: the former identifies source inventory, the latter hashes actual assembled prompts without storing raw prompts. Keep both definitions and never replace a commit/config binding with a matching prompt hash alone.

The application's prompt hash currently skips unreadable source files. Before claiming the new formal gate ready, E/D must provide a preflight check that the selected expected inventory is readable/complete (or explicitly resolve the existing R-HASH risk); do not claim the existing hash proves completeness. Proposed full-SHA/policy/tool-inventory checks are gate-adapter prerequisites, not retroactively implemented protections.

## 4. Scoring/evidence interface and H3 boundary

Use a fresh GOV004_EVIDENCE_DIR per target/cohort. Retain cohort.json (formal schema 2), gov004_starts.json (versioned STARTED ledger), gov004_attempt_<run_id>.json mirrors/batches, and runs/<stamp>/<case>/ artifacts. Reports and manifests are referenced by portable relative path and SHA256; actual effective config/prompt/source/run/case controls must agree with the declared cohort. STARTED is durably claimed before dispatch; retries do not overwrite old starts or silently replace failed slots. Missing/pending/failed attempts stay in completion accounting.

Human scores enter via the scorer's explicit positional scores-file argument. JSON has a real reviewer and answers with case_id/run_id/trial/item/integer score 0-or-1 and an exact nonempty citation in the corresponding report. The scorer derives applicability; do not fabricate N/A, missing scores, reviewer identity or citations. Keep applicable rubric decisions/critical items and scores under C/authorized human review. Q1–Q4 output checks are not semantic score cells or proof of factual correctness.

package_gov004.py copies the referenced artifacts/cohort/evidence/scores into a new destination and emits integrity.json with file digests. It rejects detected credential text rather than rewriting scored evidence; remaining privacy needs review. Original private evidence stays ignored; deliberate sanitized reviewed packages need agreed durable retention (E-owned CI artifacts/archive/review location). Commit only authorized sanitized artifacts. Retain GateEvaluation beside, not inside, the tool's package so the existing exporter is unchanged; an E outer index must bind its digest to integrity.json and the scores/package refs. An expiring CI artifact without an archived owner-approved copy is not durable final-submission evidence.

H3 source of counters: score_gov004.evaluation_counts uses RunRecord + EvaluationPopulation + summarize_records(records, *, population=...). Reuse its ten outputs: started_count, completed_count, completion_fraction, needs_review_count, incomplete_reason_counts, pre_run_rejected, pre_run_cancelled, distinct_case_count, population_result_count, status. Show counts beside quality results. Pure helper counts declared bindings; scorer additionally checks actual manifest/pre-start evidence and cohort. No STARTED gives aggregate 0 and case count null; started without declared population gives aggregate null; known explicit case IDs remain countable even then. Missing case identities give case count null. Duplicate attempts and mismatched bound controls reject. Summary AVAILABLE or population_result_count=1 is not semantic PASS.

The supported evaluation is one fixed configuration and population. A truthy controlled_change with supplied population is refused; changed population/control versions cannot be merged into a repeat. No general before/after prompt/model/budget comparison reporter is currently supplied by this H3 helper. A's rule-6 comparison acceptance remains separate. The actual legacy formal scorer uses five named cases / two trials / minimum nine eligible completed, completion >=90%, semantic score >=0.90, per-case coverage and critical/challenge-exposure rules. These constants are existing implementation, not approval of the registry's N_EVAL=20 population or all its absence/freshness checks. A/C/D/E must reconcile that policy before claiming formal REQ-TA-GOV-001 compliance. Saved school openai_compatible settings are diagnostic unless the fixed formal provider/profile is explicitly reconciled; do not silently switch providers to make a gate pass.

## 5. Results, exceptions and lifecycle

Preserve the real scorer semantics and raw exit: PASS=0, FAIL=1, PENDING=2. Do not implement a second permissive scorer, infer acceptance from pytest success/package creation, lower thresholds or convert missing work to green semantic PASS.

| Situation | Reported semantic result / handling |
|---|---|
| Valid target-bound evidence, applicable real score cells, current fixed scorer conditions satisfied | PASS / 0; still limited to the declared profile and gate mode |
| Actual scorer below threshold, critical violation, failed exposure/completion/eligibility, malformed evidence or invalid score schema | Preserve FAIL / 1 and safe reason; distinguish invalid evidence from bad financial narrative |
| No evidence yet, missing score file, human scoring not completed | PENDING / 2, never PASS; a supplied but malformed/partial score matrix is FAIL according to the existing scorer |
| API unavailable before any start, no score/verdict can be produced, wrapper interrupted/timeout with no valid final scorer result | PENDING with infrastructure/interruption reason; retain logs/starts/artifacts; formal merge is blocked. Do not overwrite an already produced FAIL with this category |
| API failure or interruption after STARTED | Retain INCOMPLETE/MODEL_FAILURE or INTERRUPTED/unresolved entry as applicable; no fabricated completed rating. Run scorer on retained evidence when possible and preserve its actual verdict. It need not be PENDING merely because the cause was infrastructural; PASS is possible only if all existing acceptance conditions still hold, with the incomplete attempt explicitly reported |
| Existing report/package hash mismatch or evidence for a different head presented as current | FAIL binding/integrity validation; an old valid result is not current PASS. If no current-head run has been supplied, current state is PENDING |
| Classifier unavailable, job skipped/cancelled for a required path, unsupported profile, missing formal policy adoption | PENDING / no acceptance, with explicit reason; do not treat as no impacted path |
| Trusted classification finds no GOV_PATHS changes | NOT_APPLICABLE with null semantic verdict; no live calls; ordinary checks still apply |

**Evaluation unfinished versus an incomplete application attempt.** Missing required evidence, unperformed scoring or an unfinished gate has no accepted PASS. This does not introduce a new 100%-completion requirement: the existing formal policy can accept nine eligible completed plus one correctly bound pending start when completion is 9/10, every case has the required completed coverage, applicable human scores are complete and all other scorer conditions hold. The result must still show that one attempt is incomplete. Do not turn this documented 90% policy into 100%, and do not label the whole evaluation finished merely because some attempts completed.

PILOT: report raw PASS/FAIL/PENDING with target/profile and infrastructure status; the semantic job is not a required merge check. FAIL/PENDING may be nonblocking **because it is not required**, not because their semantic verdict is changed to PASS. If the CI wrapper completes successfully merely to upload a report, label that execution success separately from semantic verdict. Never use blanket continue-on-error/`|| true` as evidence of semantic success. A non-required failure is still a reported failure.

BLOCKING (future, explicit E/team activation): only REQUIRED + current-head valid semantic PASS may satisfy the semantic required check. FAIL and PENDING both block; missing/cancelled/skipped required execution must not become success. The always-run classifier/summary must distinguish NOT_APPLICABLE from a required job that never finished, so path-filtered skips cannot accidentally satisfy the gate. E owns workflow/check naming/protection activation and execution permissions; this proposal adds no actual required check. Enter BLOCKING only after profile/rubric/critical policy/QUALITY_THRESHOLD and N_EVAL scope are resolved by their real owners, trigger/preflight/result-adapter tests exist, evidence/scoring access is available, and E records activation. Existing MIN_SCORE=0.90 and green offline tests do not automatically satisfy that transition.

## 6. Owner handoff and proposed verification

B owns the technical section and current-vs-proposed boundaries; C owns cases/rubric/scores/independent acceptance; D/E implement adapter/workflow/retention with approved scope; A owns requirement meaning/scope/adoption. No change to seven existing checks, live credentials, provider/profile, thresholds, gate mode or PR permissions occurs by writing the architecture.

Proposed meaningful E/C/D probes (not executed by this documentation task): source/model/context edit triggers; docs-only no trigger; rename/delete from governed path triggers; path-list edits cannot exclude themselves; classification error becomes PENDING; wrong/new PR head cannot reuse PASS; prompt/config/case/cohort mismatch spends zero model calls; pending/invalid scores retain the right result; invalid hashes fail; API interruption retains denominator; PENDING nonblocking in PILOT but blocking in BLOCKING; NOT_APPLICABLE is never called semantic PASS; package relocates with hashes/citations/ledger preserved. Use scripted/offline probes before any owner-authorized live run.
