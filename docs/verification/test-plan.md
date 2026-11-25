# Member C verification strategy

Updated 2026-11-25. This file defines approach and acceptance criteria. Results belong in the [verification summary](verification-report.md) and [evidence index](evidence-index.md).

## Scope and authority

Use the [registry](../req/requirements.yaml), [schema](../req/req-schema.json) and [mapping](requirement-test-mapping.md). Proposed registry status is distinct from A's adoption decision. Map SEL-TA, REQ-TA and B's INV namespaces by meaning; preserve test/TC identifiers.

C owns criteria/evidence, A requirement meaning, B design, D implementation and E enforcement. Developer probes and self-review are not automatically independent acceptance.

## Execution approach

Use synthetic fixtures, scripted models and blocked network for offline acceptance through run_analysis_api. Raw graph tests are supporting evidence. Keep absent and explicit-empty portfolios distinct. Exercise applicable A-A/A-B/A-C profiles, consent/freezing, deterministic authority, privacy, publication and failure paths.

For each applicable boundary, retain a valid control and a negative rejected by the intended protection. Environment/dependency errors do not prove rejection. Reuse existing mechanisms; do not weaken assertions or alter implementation to obtain a pass.

## Acceptance record

Record requirement/boundary, source/dirty state, configuration/environment, exact command/node IDs, expected behavior, observed result/exit code, evidence, limitations and actual author/reviewer provenance. Separate PASS, FAIL, SKIP, NOT_RUN, UNAVAILABLE and PENDING from coverage and acceptance.

Run affected and required checks under [AGENTS.md](../../AGENTS.md) and current CI as applicable. Documentation-only work needs content/link checks, not invented behavioral tests. Blocked execution remains NOT_RUN until actual output is supplied.

## Semantic and governance constraints

The [semantic contract](gov004-evidence-package.md) governs populations, genuine scores, all-start accounting and portable evidence. See [semantic status](semantic-evaluation.md); Q1–Q4 and mechanism tests do not establish quality.

Follow Prompt.md H1/H2/H3 within existing authorization. Test-plan pre-approval remains paused; do not require /approve-tests or change branch protection. Local tool permissions, CI token policy and OS isolation are distinct.

## Historical reference

[Earlier records](history/test-plan-2026-11-25.md)
