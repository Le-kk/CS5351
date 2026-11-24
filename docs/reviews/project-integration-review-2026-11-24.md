# Project integration review 24 November 2026

**Reviewed revision:** `a62b801a51e6310f3b46860f6d2790583a95e0e0`, local `main`.<br>
**Compared with:** `98b82c991fecbd58b25b4617f378fd0930a65df4`.<br>
**Audience:** Brian and the project team.<br>
**Review date:** 24 November 2026, Asia/Hong_Kong.<br>
**Conclusion:** The update adds useful requirements, measurement records and governance tooling, but it is not ready to serve as the adopted final requirements and delivery baseline. Resolve the integration findings below before claiming those obligations are satisfied.

## 1. Update and verification results

Local `main` was fast-forwarded to `a62b801`, matching both `Le-kk/CS5351` main and `kelepawuqiusi/CS5351` main at the synchronization check. All eight pre-existing modified/untracked local draft files were checked by SHA-256 before and after the update and preserved unchanged.

The 29 changed files add A's requirements package, D's two measurement notes, and E's test-approval/self-review tooling and supporting tests. There are **no changes to `tradingagents/` or `cli/` in this update**. In particular, the update is not a token-optimization implementation or a repair of the earlier numerical-report limitations.

| Verification | Observed result |
|---|---|
| New CI-support regression files `test_pr_self_review.py` and `test_test_approval_completion.py` | **50 passed**, 4.11 s, project virtual environment |
| `scripts/ci/check_test_approval.py --self-test` | Passed |
| `ruff check .` and `git diff --check` | Passed |
| Hosted main-commit CI on both repositories | Existing test/install, lint, dependency and AI-log jobs succeeded |
| Documented `python3 docs/req/validate.py` | Failed: script is absent at that location |
| Root validator with Ubuntu system Python | Failed: `docs/req/requirements.yaml` is absent |
| Root validator with project virtual environment | Failed earlier: `jsonschema` is not installed there |
| Validator in a temporary directory with the intended `docs/req/` layout | **34 requirements; 3 withdrawn; 0 errors; 0 warnings** |
| Controlled defective registry variants | Several incorrectly passed; details below |

The temporary validation runs used the existing Ubuntu system Python with PyYAML and jsonschema. No dependency was installed and no canonical file was relocated or edited. The two new regression files and the checker self-tests were run locally; the entire local application suite was not repeated. Hosted CI supplied the broader regression result for this unchanged application revision. No fresh paid model calls were made for this review.

## 2. Findings requiring follow-up

### I24 01 Requirements package cannot run from its documented location

**Priority: P1. Suggested coordination: A and E.**

The six uploaded files are at the repository root: `requirements.yaml`, `req-schema.json`, `validate.py`, `requirement-source-notes.md`, `negative-fixtures.md`, and `change-log.md`. The validator hard-codes `docs/req/requirements.yaml` and `docs/req/req-schema.json` at [validate.py](../../validate.py), lines 18–29. The reproduction instructions also invoke `docs/req/validate.py`. Those files are not present at the expected locations.

This is a reproducible integration failure, not evidence that the registry cannot satisfy its schema: copying the registry/schema into the intended layout in an isolated temporary directory makes the baseline pass. The project virtual environment additionally lacks `jsonschema`, so E must ensure the validation job has its declared dependencies.

No current workflow invokes this validator. Existing green CI therefore does not establish requirements/schema validity. Put the canonical package in its agreed `docs/req/` location, make the validator command reliable, and wire a blocking check with valid/invalid/error fixtures. Avoid maintaining divergent root and nested copies.

### I24 02 Uploaded requirements do not include the latest reported reconciliation

**Priority: P1. Suggested coordination: A, with the team confirming scope.**

The uploaded [requirements.yaml](../../requirements.yaml) contains **34 active entries and 3 withdrawn IDs**, with **24 proposed and 10 partial**. Its document status is `proposed_for_adoption`. It has neither `REQ-TA-INV-014` nor `REQ-TA-GOV-004`, although A's later `reply-to-B-2026-11-23.md` reports those additions and 36 active entries. This establishes a difference between the uploaded snapshot and the later correspondence; it does not establish that A's unpublished working copy is wrong.

The uploaded scope at lines 24–28 still excludes portfolio files and says every fixture runs without one. Its fixture profiles at lines 1404 onward explicitly contain confirmed portfolio inputs. The source notes acknowledge the optional-input decision remains open. The main statement and profiles therefore do not describe one coherent scope.

Other stale references remain in the fixture appendix, including withdrawn `FR-002`, the malformed shorthand `NFR-FR-003`, and candidate `REQ-TA-INV-010` as though it were a registry entry. The embedded profile prose also assigns credential testing differently from the structured assignment.

Publish the reconciled version A actually intends the team to review, including the corrected scope, candidate dispositions, traceability and source/adoption records. Preserve optional no-portfolio use; accepting an explicitly empty portfolio is not a defect. Separately resolve whether the output policy permits conditional sizing guidance: the current `TraderProposal.position_sizing` supports it, while the uploaded scope says the system does not size positions.

### I24 03 Test approval is implemented but is not a required merge check

**Priority: P1. Suggested coordination: E.**

The new checker is useful: its local self-tests exercise prior-approval ordering, scope/hash correspondence, revocation, trusted baseline policy, and explicitly labelled self-review. The new regression files pass. Self-review receipts are accurately distinguished from independent peer review.

However, the public branch metadata for E's main lists only four required checks: `ai-log updated`, `dependency check`, `required tests`, and `ruff (strict, full repo)`. It does **not** include `test approval`. Its reported enforcement level is `non_admins`; full administrator-only protection settings were not accessible without authentication.

[Requirements PR 16](https://github.com/kelepawuqiusi/CS5351/pull/16) merged with a failed [test approval check](https://github.com/kelepawuqiusi/CS5351/runs/137728306251). The producer workflow also failed. The available check summary says the approval workflow did not finish successfully; this review does not attribute the producer failure to a particular approval or path-classification defect.

Fix the producer failure, demonstrate a valid approval path and rejection of an invalid one, then require the exact check on the integration branch. Keep the historical failed/missing evidence visible rather than retrospectively describing the merge as approved. A workflow existing in the repository is not the same as a blocking merge gate.

### I24 04 Validator accepts defective records and fixture instructions overstate coverage

**Priority: P2, with final-delivery impact. Suggested coordination: A and E.**

The isolated baseline and an invalid-priority negative control behaved correctly: the baseline passed and priority `Essential` failed. The following variants nevertheless exited 0 with zero findings:

| Mutation | Why it matters |
|---|---|
| Remove `CALL_CAP` from the parameter appendix | Negative-fixture row 6 claims this fails. The validator checks existing parameters' `used_by` references, not that every used parameter is defined. |
| Replace withdrawn `REQ-TA-FR-002` with `REQ-TA-FR-999`, retaining three entries | The purported exact withdrawn-set check only checks a minimum count, so it does not preserve the recorded identities. |
| Set an invariant's `enforced_by` to nonexistent `REQ-TA-FR-999` | The schema checks identifier syntax, but no cross-record rule resolves this reference. |
| Add an earlier duplicate top-level `schema_version: 0.0.0` before the real value | `yaml.safe_load` silently keeps the later value; duplicate mapping keys are not rejected. |
| Change only `REQ-TA-GOV-003` to type `functional` | Negative-fixture row 8 predicts loss of governance-type coverage, but two other governance entries remain. This is an incorrect negative fixture, not evidence that the type-coverage rule itself is broken. |

The documented `--registry` command is also unsupported: `validate.py` treats its first argument as the filename, and the proposed `validate(registry_path)` fallback function does not exist. In addition, lines 163–167 unconditionally reject `document.status: adopted`; an adoption-verification path is still needed before an adopted registry can pass.

Correct the reference checks, reject duplicate YAML keys, preserve the required withdrawn identities, and turn the documented mutations into executable checks asserting the expected reason. A missing dependency, wrong filename or unrelated exception must not count as a successful negative test.

See the retained [registry diagnostics](evidence/integration-review-2026-11-24/registry-checks.json) for exact exit codes/output. All mutations were made in temporary copies.

### I24 05 D adds diagnostic measurements rather than an optimization patch

**Priority: P2. Suggested coordination: D and C, with B for boundary interpretation.**

D's [after-build note](../../AI-log/Member-D/2026-11-23_15-25-00.md) reports three completed after-build runs averaging 148,392 tokens and about 114.4 s, versus about 138,897 tokens and 114.1 s for two baseline runs. The reported +6.8% token increase is arithmetically consistent. It is a measurement of current overhead, not a demonstrated token saving.

The [attribution note](../../AI-log/Member-D/2026-11-23_16-15-00.md) usefully identifies the Market Analyst and repeated risk/research context as input-token consumers. It is one exploratory run, so the shares should guide investigation rather than become fixed budget allocations.

Two stalls were excluded from the completed-run averages and disclosed. Retain that completed-run statistic, but also report the documented three completions and two stalls separately. This is not yet an auditable formal completion rate without the attempt inventory. The notes identify different network conditions and measurement-only timeout/retry settings; do not present the comparison as a controlled causal proof of a particular prompt or optimization effect.

The harnesses, per-call JSON and run logs are described as local/untracked and are absent from this upload. Retain sanitized versions, exact commands/configuration/revision, and attempt outcomes so C can reproduce and assess the measurements. These measurement notes also do not substitute for the team's requested representative full coding-agent interactions or D5's raw session evidence.

Most importantly, direct `graph.propagate()` measurements exercise the declared raw compatibility primitive. The note's claim that saved product reports lack run status does not establish a defect in the supported CLI/API path: [runapi/reporting.py](../../tradingagents/runapi/reporting.py), lines 28–44, already renders run outcome, stop reason when applicable, and output-check status; `run_analysis_api` publishes that envelope. Confirm product-report behavior through the supported boundary and distinguish it from raw-engine instrumentation.

### I24 06 Broader proposed requirements are not current implementation acceptance

**Priority: P1 for scope and delivery claims. Suggested coordination: A, C, D and E.**

The working implementation still has Q1–Q4, while the uploaded proposal additionally specifies evidence-ID resolution, sentiment/coverage rules, a run-wide call-reservation controller and `BUDGET` handling. The current `StopReason` literal has five values and no `BUDGET`; no application changes were included in this pull. These proposed obligations cannot be claimed satisfied by the previous selected-requirements tests or the new governance tests.

The token/call parameters and quality threshold remain open, and `N_EVAL=20 cases` remains provisional. These are acceptance decisions and implementation/evidence gaps, not matters settled by a schema passing. An executable schema is also not human adoption.

Before final claims, freeze the adopted scope, map each retained obligation to implementation and evidence, and identify genuine remaining work. Use explicit, approved deferrals where appropriate; do not remove unmet obligations merely to obtain a green result. Earlier numerical-validation-extension and independent semantic-acceptance limitations are not resolved by this documentation/CI update.

### I24 07 Some acceptance criteria need conditional result semantics

**Priority: P1 for a coherent acceptance contract. Suggested coordination: A, C and B.**

`REQ-TA-RUN-001` makes the stop reason present only for incomplete runs and the rating present only for completed runs. However, `REQ-TA-NFR-REPRO-001` fit (b) requires the RUN-001 fields to be non-null in every record. Those assertions cannot both hold as written. Validate field presence and nullability against the validity table, rather than inventing a stop reason or rating to satisfy a blanket non-null test.

The same reproduction requirement promises a record/report for every run without a critical-persistence-failure exception. Preserve the existing distinction between a returned logical result and successful artifact publication: failed critical publication must not claim that the report/manifest was written. These are bounded contract corrections, not reasons to redesign the architecture.

The proposal also permits `PASSED` with corrected findings under R5. Current `Finding` allows only `BLOCKING`, and current `CheckResult` rejects `PASSED` with any findings. This is a proposed result-contract extension, not a compatible description of existing behavior. If retained, update the checker/result/report/scorer interfaces and their tests together. Finally, clarify that `INCOMPLETE(MODEL)` / `INCOMPLETE(DATA)` in fixture descriptions are human shorthand; serialized values remain `MODEL_FAILURE` / `DATA_FAILURE` under RUN-001.

## 3. Architecture work that can proceed now

The two missing IDs do not require architecture work to stop. A's supplied `reply-to-B-2026-11-23.md` explicitly says the entries were added; the uploaded notes still record their decisions as open. There is no supplied withdrawal of either entry. Treat this as inconsistent published snapshots until synchronized, rather than infer that A intentionally removed the obligations.

The course requires invariant coverage and schema validation, not these particular ID numbers or an exact total of 36. Input immutability could instead be represented by a complete existing requirement with its own testable clause. Schema validation similarly needs explicit governance coverage and an enforced gate. Omitting or merging an ID does not remove the underlying duty.

| Architecture subject | Basis available now | Treatment while A synchronizes |
|---|---|---|
| Frozen snapshot and fingerprint | `SEL-TA-FR-003`, `SEL-TA-FR-006`; architecture INV-04/05/05b; existing input/context components | Keep the design and actual implementation links. Record prospective `REQ-TA-INV-014` as pending publication, not an already-resolving registry reference. |
| Schema validation | `SEL-TA-GOV-002`, course D1/CI obligations, supplied A correspondence | Describe the validator/CI boundary and the known installation/enforcement gaps. The missing `REQ-TA-GOV-004` identifier does not change the product data flow. |
| Optional portfolio with explicit confirmation | Working selection and implemented CLI/API contract | Continue the C2 input-service/immutable-context/shared-execution design. State that the replacement registry's contradictory exclusion remains unresolved. |
| Evidence registry, channel coverage, R1–R8 extensions, aggregate budgets and resume | Broader proposed requirements, with substantial implementation gaps | Document proposed components/contracts and impacts separately from implemented behavior. Do not claim that existing Q1–Q4 or fresh-run handling already implements them. |

B can update the existing blueprint, interfaces, invariant links and implementation/evidence references in parallel. Preserve C2's rationale and candidate history; a new candidate-generation cycle is not justified by two missing registry entries. Fully qualify existing `SEL-TA-*` references, then map meanings to `REQ-TA-*`; identical numeric suffixes are not a mapping (`SEL-TA-FR-003` concerns input freezing, whereas `REQ-TA-FR-003` concerns checkpoint resume).

Final handoff still needs one agreed requirements version and an honest implementation/evidence crosswalk. The old 19-ID working selection alone is not a substitute for the full course-required D1 coverage, including performance, cost and governance. Independent drafting can proceed while the team closes that consolidated scope decision.

## 4. Recommended order before submission

1. **A:** publish the intended reconciled requirements snapshot under `docs/req/`, reconcile optional portfolio/sizing scope and references, and retain the necessary source/adoption material. Apply the independent candidate-fit corrections without waiting for D's resume decision.
2. **A and E:** make validation executable and test its meaningful negative cases; add and require the schema check. Repair the approval workflow and demonstrate its positive/negative paths before making `test approval` required.
3. **D:** share reproducible measurement artifacts and distinguish baseline/profiling work from an actual optimization or budget-controller implementation. Keep raw-engine measurements and supported-product results separate.
4. **C with the team:** map the adopted registry to the existing tests, inspect fresh semantic evidence under agreed parameters, and identify any remaining mandatory implementation. Preserve existing evidence and approval chronology.

The deadline remains **25 November 2026 at 23:59 Hong Kong time**. The immediate priority is one coherent scope and demonstrably enforced gates, followed by the implementation/evidence work that scope actually requires.

## 5. Evidence and review boundaries

- [Registry diagnostics](evidence/integration-review-2026-11-24/registry-checks.json): real command failures, isolated baseline/control and defective variants.
- [GitHub check snapshot](evidence/integration-review-2026-11-24/github-checks.json): PR 16 approval failure, merge revision/time and public required-check metadata.
- [Verification facts](evidence/integration-review-2026-11-24/review-facts.json): sync preservation, local checks and hosted main-commit checks.

This is an integration review of the pulled changes and their relationship to the working implementation. It does not certify every proposed requirement or replace C's independent acceptance. Apart from these review/evidence files, product code, canonical requirements, tests, CI policy and earlier drafts were not edited. No commit or push was made.
