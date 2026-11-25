# Review memo

Owner: Member C
Date: 25 November 2026
Reviewer: Codex, working in the Member C verification role
Review method: closeout inspection of retained PR reviews, source and test files.

## Review index

| Entry | PR | Reviewed reference | Verdict | Follow-up |
|---|---|---|---|---|
| RM-001 | [#26](https://github.com/kelepawuqiusi/CS5351/pull/26) | Schema-gate integration at recorded main 2efbf0f | APPROVE — schema checker and test scope | E retains hosted check evidence in the submission package |
| RM-002 | [#27](https://github.com/kelepawuqiusi/CS5351/pull/27) | Deliberately invalid priority probe | REJECT — invalid registry input | Retain as negative evidence |
| RM-003 | [#18](https://github.com/kelepawuqiusi/CS5351/pull/18) | Feature 9102759caaa59d778ba49cd57a1306f5f2ee5d88 | CHANGES REQUIRED — quality evidence and compaction boundary | D repairs the boundary; C evaluates the result |

## RM-001 — Requirements schema gate

**Specification and design.** The checker runs A's registry validator and enforces a nonempty completed validation summary with zero errors. It integrates the existing schema and cross-record rules into CI.

**Code and tests.** The source rejects missing files, validator failure, timeout, malformed output and incomplete summaries. The retained review records 16 passing targeted probes and a valid 36-requirement control.

**Security and efficiency.** Validation is local, timeout-bounded and does not dispatch a model. Dependency additions and their reviews are included in the recorded PR scope.

**Evidence.** [Schema-gate review](reviews/requirements-schema-gate-review-2026-11-24.md), [checker](../scripts/ci/check_requirement_schema.py), [regression tests](../tests/member_d_verification/test_requirement_schema_gate.py).

**Verdict: APPROVE** for the reviewed schema-checker scope.

## RM-002 — Invalid-priority negative probe

**Specification.** Priority Essential is outside the registry's permitted vocabulary.

**Observed behavior.** The retained schema-gate review records the probe's failing requirements-schema job and identifies PR #27 as closed and unmerged.

**Quality assessment.** The invalid input exercises the deployed validator path. The failed job provides the rejection evidence.

**Evidence.** [Recorded probe outcome](reviews/requirements-schema-gate-review-2026-11-24.md#observed-verification).

**Verdict: REJECT** the invalid registry change; retain its failing check as the negative control.

## RM-003 — Concise intermediate context

**Specification and design.** The feature adds advisory brevity guidance and removes an exact repeated opponent argument when the same text is present in history. A configuration flag restores the prior behavior.

**Code and tests.** The retained review records 49 passing focused tests. Its reference/compaction probe identifies a boundary where a longer reference notice can exceed the guard target while the reconstructed original remains below it.

**Security and quality.** Portfolio/context regressions exercise protected input propagation. Semantic quality and evidence retention require the agreed report evaluation.

**Efficiency.** Retained measurements describe a fixed workload. The benchmark and the proposed run-wide budget controller are separate mechanisms.

**Evidence.** [Architecture review](reviews/token-context-architecture-review-2026-11-24.md), [reference probe](reviews/evidence/token-context-reference-probe-2026-11-24.json), [feature tests](../tests/member_d_verification/test_token_input_reduction.py).

**Verdict: CHANGES REQUIRED.** Repair or explicitly resolve the reference/guard boundary, then record its valid and negative regressions. Complete the planned semantic quality evaluation for the selected configuration.

## E integration review — course layout and local/remote synchronization, 2026-11-25

Scope: merge origin/main be6b902 without rewriting contributor updates; preserve local demo/token/recovery work; move physical sources/tests to course D8 paths with compatibility aliases; refresh delivery documents/index. Requirement meaning and proposed status are unchanged. Source/package contracts and test assertions are retained; only path calculation and fixture imports were adapted. Current static and full regression evidence is recorded in the integration log. Operationally, credentials/private runtime data/generated builds are excluded; archives retain superseded instructions. Verdict: APPROVE for integration PR submission based on passing local regression, clean wheel installation and current-link checks; merge remains conditional on successful hosted required checks. Missing owner acceptance and D5/D6 inputs remain explicit. This is E developer/integration review, not another member's approval.
