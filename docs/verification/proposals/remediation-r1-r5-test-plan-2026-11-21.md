# R1–R5 repair acceptance and test plan

Prepared 2026-11-21, Asia/Hong_Kong. Baseline: `9b04330` (merge-only update; tree identical to `9c77b63`).

**Status: approved by Brian before implementation on 2026-11-21.** Approval response: “Approve the unchanged plan and proceed.” The exact pre-approval content is privately retained with SHA-256 `6e36ff7fe5ef78acd083cb788a7a9158b4fbf08cc8c125f17b9b2eecc81ce38f`; this status note does not change the 31 criteria. Brian clarified that the requested review concerned the synced branch, not a change in test scope. Commits 9c77b63 and 9b04330 have the identical tree 90b0da91625b6b4fc71bd68c7663026660de5acf; no code, tests or contracts changed in that update. User authorization to fix the issues is already recorded. This document supplies the concrete test plan for the course sheet's page-10 test-approval requirement; it does not claim that general authorization was approval of a previously unseen test plan. Approval of this version covers the bounded regression tests and implementation scope below. C's independent course acceptance is separate.

Source: [remediation follow-up review](../../reviews/remediation-follow-up-review-2026-11-21.md), residual R1–R5. The work plan is set aside. Existing local planning/readiness drafts, canonical requirements, original evidence and governance files are not part of the implementation write set.

## Scope and preserved decisions

- Repair the five observed failures through supervised OpenCode, retaining its authentic session and human interventions. No application/test implementation by this reviewing assistant before approval.
- Keep two public input modes, five research ratings, Trader's three actions and the Q1–Q4 authority/phrase set. Empty supplied input remains valid and is not forced to Hold.
- Keep the existing shared API, frozen snapshot/canonical fingerprint contract and staged publication architecture under ADR 001. These are repairs to the intended contracts, not adoption of every unapproved requirement-candidate addition.
- Report + manifest remain critical; terminal-event append remains best-effort. No false promise of survival through total disk failure or forced process termination.
- Formal provider/model/rubric thresholds remain unchanged. New metadata needed to bind cohort/case identity or retain pending starts must be explicitly versioned/documented as harness evidence, not added to public application result enums.
- F8 historical materials cannot be manufactured. Do not rewrite old diagnostics or mark formal semantic PASS without a valid approved population and independent score.
- Do not commit/push, alter `.env`/credentials or human-only policy files, make runtime/live model calls, or edit unrelated local drafts as part of this approval. A later live verification step can be arranged after offline checks.

## R1 — captured logging, not just direct scrubber calls

| Test | Fixture and expected result |
|---|---|
| R1-01 | Structured binding raises NotImplementedError/AttributeError with a synthetic provider-prefixed credential assignment and configured fake secret. Capture the actual logger: zero credential values; useful agent/fallback context remains. |
| R1-02 | Structured invocation raises a credential-bearing exception; fake plain model returns usable Hold text. Warning is redacted and fallback result is preserved. |
| R1-03 | Quoted/multiline, bearer and configured-value variants reach the same actual warning path. Zero planted values survive; benign text is not unnecessarily removed. |
| R1-04 | Inspect equivalent nearby model/data diagnostic callsites and add bounded sink tests for any same-class leaks repaired. Inventory exactly which sinks were checked; do not claim all conceivable secret encodings are certified. |

Primary implementation: `tradingagents/agents/structured.py`, reusing central `runapi/redact.py`; other logging callsites only if the same defect is found and documented. Avoid a global logging monkeypatch or circular imports.

## R2 — real result/provenance/case correspondence

| Test | Fixture and expected result |
|---|---|
| R2-01 | A complete synthetic population with application-shaped manifests/report envelopes, fixed cases, full applicable human-score cells, citations and hashes still yields PASS. Use actual rendering/contract helpers where practical; unit fixtures remain explicitly synthetic. |
| R2-02 | Declared explicit-empty case has NO_PORTFOLIO/null snapshot metadata, with valid recomputed hashes: FAIL. Also reject a held-target fixture substituted for an empty case. |
| R2-03 | Mutate fingerprint, basename, portfolio kind/as-of basis or a required provenance field independently: FAIL against the trusted frozen case definition. Do not infer expected input facts from the defective manifest. |
| R2-04 | Wrong ticker/analysis date or case-incompatible target fixture: FAIL against the declared cohort/analysis controls. Supported legitimate declared date values remain usable; do not silently hardcode an unrelated date. |
| R2-05 | COMPLETED plus non-null stop reason, invalid rating/check enum, NOT_RUN or inconsistent findings: FAIL. INCOMPLETE/pending starts are never accepted as completed quality samples; preserve them in completion accounting. |
| R2-06 | Authoritative report envelope contradicts manifest/evidence for outcome, check, rating, mode or provenance: FAIL even when report/manifest hashes have been recomputed. Missing/duplicate/conflicting authoritative metadata is invalid. |
| R2-07 | A legitimate quoted/fenced discussion of a different status in narrative is not accidentally treated as the authoritative envelope. Do not replace header parsing with a global substring test. Counterfeit unquoted metadata-like lines must not create a second conflicting authoritative result. |
| R2-08 | Preserve existing negatives: missing/duplicate/unrelated/N-A/boolean scores, invalid citation, missing artifact, wrong revision/config/prompt hash and unexposed challenge cannot PASS. Thresholds and fixed formal provider remain unchanged. |

Primary implementation: `tests/member_c_verification/live/score_gov004.py`, fixed-case/runner metadata helpers only as necessary; positive fixtures in `test_score_gov004_exitcodes.py` must become genuinely valid, not be weakened to accommodate invalid evidence. Validate conditional fields and case facts, not merely file existence or a Run ID string. Document any versioned evidence/cohort additions; reject incomplete legacy formal evidence rather than silently fabricate fields.

## R3 — durable per-attempt replay accounting

| Test | Fixture and expected result |
|---|---|
| R3-01 | First selected slot is new, second already recorded. Preflight rejects before executing either; zero fake graph/model dispatches. |
| R3-02 | Before a fake runner is entered, its started run ID/case/trial is already in an atomically stored record. Start records are distinct from fabricated completed application results. |
| R3-03 | First case finishes, later case raises/serialization fails. First result remains saved; later start remains saved and noncompleted. No started run is silently lost. |
| R3-04 | Cooperative interruption or retained unresolved start remains noncompleted in the denominator; reusing that formal slot is refused. Do not turn it into a made-up completed result. |
| R3-05 | Scorer ingests the versioned unresolved-start representation, retains it in overall/cohort completion accounting and cannot count it as a completed report or passing quality cell. |
| R3-06 | Unique evidence files/records are not overwritten by two starts in one second. Reused run-ID claim is exclusive before dispatch; a collision cannot invoke the same slot twice. |
| R3-07 | Normal multi-case synthetic run saves all outcomes and still scores correctly. Diagnostics/pilot populations stay separate from formal records; existing all-start/retry/cohort policy remains enforced. |

Primary implementation: `test_gov004_live.py`, narrowly scoped replay helpers/`runner.py` and scorer ingestion needed for the versioned start records. Offline tests must not enable the real live fixture or load actual credentials.

## R4 — all decision stages receive the actual trusted context

| Test | Fixture and expected result |
|---|---|
| R4-01 | Hold debate/evidence fixed, compare absent versus explicit-empty versus supplied target long. Captured RM prompts distinguish the facts; empty and held prompts are no longer identical. All three decision stages receive the relevant trusted context. |
| R4-02 | Empty, other-ticker-only and zero-target fixtures carry no-nonzero-target instructions; the no-portfolio case remains unknown rather than asserted flat. |
| R4-03 | Positive/negative quantities and supported aliases preserve supplied facts; unknown cash is not zero, while explicit cash zero is identified as supplied. Holdings remain user-supplied/unverified, not externally authenticated. |
| R4-04 | Force non-default compaction with facts in the middle and conflicting upstream prose. Protected ownership facts survive; genuinely protected overflow fails before model dispatch under the existing contract. |
| R4-05 | Inspect report-stage propagation with scripted outputs and both structured/free-text paths. Retain RM/Trader/PM sections so an upstream inconsistency is not silently erased. No new universal semantic classifier or Q5 is claimed. |
| R4-06 | Existing final five-tier ratings/Trader actions and explicit-empty Sell/Underweight cases stay valid. No forced Hold and no new public result/input mode. Factual/rating stage distinctions remain labelled. |

Primary implementation: RM prompt/context wiring using the same `get_portfolio_context_from_state` / `protect_context` seam as Trader/PM, with scoped helper/prompt changes if necessary. Supply facts consistently and instructions to correct conflicting upstream ownership premises. Offline prompt tests cannot prove actual narrative compliance; after offline verification, current live narrative review remains necessary for semantic acceptance.

## R5 — publication outcome and terminal-event consistency

| Test | Fixture and expected result |
|---|---|
| R5-01 | Inject final rename failure through real `run_analysis_api`: INCOMPLETE/PERSISTENCE_ERROR/NOT_RUN, no final artifacts/paths and exactly one caller-visible INCOMPLETE terminal event; no visible COMPLETED terminal. |
| R5-02 | Inject critical report or manifest write failure: same consistent result/event behaviour; cleanup preserves another run's work under existing F1 protections. |
| R5-03 | Only terminal-file append fails: successful publication retains the logical outcome with manifest durable=false, not PERSISTENCE_ERROR solely for this failure. Caller sees one matching logical terminal outcome. |
| R5-04 | Normal completed and normal engine-incomplete publication have one matching terminal row/result; final report/manifest remain immutable and conditional fields correct. |
| R5-05 | Tentative stage-private terminal metadata is not exposed as final before commit; critical failure cannot leave a precommitted COMPLETED in a caller-owned sink. Preserve valid timestamps/event shape and the single-terminal rule. |
| R5-06 | Existing EventSink emission/append and publication mocks/negative fixtures remain meaningful. Preserve best-effort enabled legacy sinks and no overwrite behaviour; do not delete a test simply because it exposes the failure. |

Primary implementation: `runapi/events.py`, `persist.py`, `execution.py`, with small documented internal staging/commit helpers if needed. No public result enum/signature change or critical-terminal-append redesign.

## Verification and supervised implementation sequence

1. Record Brian's approval of this plan/version in the authentic interaction. If a materially different contract or wider write set is needed, stop and explain the concrete choice before implementing it.
2. Start/continue a clearly identified OpenCode repair session in the actual repository. Read the review, ADR 001 and relevant contracts; preserve unsent drafts. Request a bounded implementation plan and have it respect this already approved scope.
3. Let OpenCode add meaningful regression cases and establish that new defect negatives fail before the application repair (or are otherwise explicitly demonstrated against the baseline). Unit tests use synthetic credentials/portfolios, fake models, temporary directories and no network.
4. Let OpenCode implement scoped fixes; keep actual session transcript/tool evidence. Do not use `--auto` as a blanket substitute for a bounded permission plan. No commits/pushes or governance rewrites.
5. Reviewing assistant independently inspects the diff and reproduces the original negative cases using black-box/synthetic probes where practical, rather than relying only on the implementer's new tests.
6. Run targeted tests, then the full prior offline suite, Ruff, installed-dependency checks and whitespace checks. Suggested commands (actual outcomes must be recorded):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 GOV004_LIVE=0 .venv/bin/python -m pytest -q -p no:cacheprovider --tb=short
.venv/bin/ruff check --no-cache . --output-format concise
.venv/bin/python -m pip check
git diff --check
```

7. Report what changed, evidence, exact source revision and remaining F8/live/independent-acceptance limits. Update the remediation record and traceable design notes for actual changes without retroactively rewriting old review evidence.

**Approval requested:** the R1–R5 regression/acceptance cases and bounded implementation write set above. This approval is not A's adoption of the full requirements proposal, a formal semantic PASS, or authorization to publish/push.
