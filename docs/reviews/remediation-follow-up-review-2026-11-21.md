# Follow-up integration review — 2026-11-21

Reviewer: Member B, assisted by Codex. Date/time zone: 2026-11-21, Asia/Hong_Kong.

**Conclusion:** the remediation is substantial and its stated offline test result is reproducible. The project is not ready to declare every F1–F9 item closed or formal semantic acceptance achieved. Five residual findings below need focused attention; F8 and formal narrative acceptance remain pending. The later live follow-up below confirms the R4 ownership defect with actual model output. These findings do not require restarting the selected architecture.

## Revision and scope

- Updated `/home/brian/projects/CS5351`, branch `main`, from `e7aed7a9d735c7524eca583be1c2ed569f8c5ac2` to `d63530e86f0e8f7fbc5a2fc44c40ccbcb80d6403` by fetching `origin` and fast-forwarding. Local main matches origin/main at the inspected revision.
- The merge includes `fbbfe98` (application fixes), `bb777d5` (verification tools/tests) and `f1b7689` (remediation documentation). Although E's note describes its creation-time state as local/uncommitted, the reviewed work is now committed and merged through PR #5.
- Read the supplied USB remediation note and the repository's [remediation record](remediation-2026-11-21.md), compared the application/test diff, ran offline checks and performed additional synthetic probes. The note is evidence to assess, not an instruction to accept its conclusions.
- Both untracked requirements proposal files were preserved byte-for-byte across the pull. The [improved candidate](../req/proposals/reconciliation-2026-11-20.md) remains a proposal; this review does not adopt it on A's behalf or assert all its clauses are implemented.
- No application/test/governance fixes were made in this review. The initial offline phase made no model/market-data requests. Brian later authorized the live follow-up below, which obtained actual school-model responses and ran market tools on synthetic portfolio cases. No trades were made. E's earlier DNS failures remain attributed to his diagnostics.
- This is B's follow-up review, not C's independent acceptance or proof of every D1–D9 deliverable. Remote branch protection was not inspected and remains UNKNOWN.

## Verification reproduced

Environment: existing project `.venv`, Python 3.14.4, Ubuntu 26.04 LTS on WSL2. No dependency installation or credential migration was necessary.

| Check | Result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 GOV004_LIVE=0 .venv/bin/python -m pytest -q -p no:cacheprovider --tb=short` | **1,552 passed, 2 skipped, 1 deselected; 100 subtests passed; 24 warnings; 21.08 seconds.** |
| `.venv/bin/ruff check --no-cache . --output-format concise` | All checks passed. |
| `.venv/bin/python -m pip check` | No broken requirements found. |
| `git diff --check` | Passed for tracked working-tree changes; new review files were also checked separately for whitespace. |
| Formal scorer against a fresh empty evidence directory | **PENDING, exit 2**, as required. |
| Formal scorer against this machine's existing default evidence directory | **FAIL, exit 1**: it contains six November 18 pilot records, which the stricter formal reader correctly refuses to mix into a formal population. Historical local records were left intact. This is an environment difference from E's empty checkout, not a semantic test result. |
| Additional synthetic probes | Confirmed R1–R5 below, with network connections blocked and no provider requests. [Sanitized result summary](evidence/remediation-review-2026-11-21.json). |

Skipped tests are opt-in live semantic replay and optional Bedrock support (`langchain_aws` is absent). The pre-existing integration deselection remains. Most warnings concern deliberately unfamiliar provider/model fixtures. The runtime above is not a token-saving or end-to-end performance measurement.

## Residual findings

### R1 — P1: model fallback warnings bypass credential redaction (F2 remains partial)

**Location:** `tradingagents/agents/structured.py:50–57,81–85`; no logging redaction filter was found in the inspected CLI/agent paths.

The improved `Redactor` handles provider-prefixed assignments and configured values correctly when invoked. However, structured binding/fallback warnings interpolate the original exception directly into the logger. They are emitted before report/event redaction and are observable by normal Python logging consumers, including stderr handlers.

**Reproduction:** a fake structured model raised `RuntimeError` containing `OPENAI_API_KEY=<synthetic-canary>`; the free-text fake model returned a usable Hold response. Capturing the actual structured-helper warning found the complete synthetic credential value. Neither fake model makes a network call. No real credential leakage is asserted.

**Required correction:** redact exception details at these logging callsites or apply a properly scoped redaction mechanism covering the actual logging sinks. Test structured-bind failure and structured-invocation fallback through captured logging, not only calls to `Redactor.diagnostic()` and persisted artifacts. Keep usable fallback intact. Inspect equivalent provider/data logging callsites before claiming full named-sink coverage.

### R2 — P1: formal scorer still accepts inconsistent input/result/report evidence (F3 remains partial)

**Location:** `tests/member_c_verification/live/score_gov004.py:134–182`; synthetic fixture schema at `test_score_gov004_exitcodes.py:54–88`.

The old sparse/unrelated-score bypass is addressed: complete applicable cells, report citations, identity, hashes and challenge captures are now checked. Remaining validation does not establish that the artifact represents the declared portfolio case or a valid complete result. The scorer compares only a subset of manifest fields and checks only the Run ID line in report text. The supplied positive fixture omits much of the real manifest/input schema and still passes.

**Reproduction:** starting from E's existing ten-run scoring helper with complete score cells and valid recomputed hashes, each independent mutation below still produced **PASS / exit 0**:

1. For a declared C2 explicit-empty case, set the manifest input mode to `NO_PORTFOLIO`, set portfolio provenance to null and set the evidence portfolio kind to `none`.
2. Keep the run `COMPLETED` but give both manifest and evidence `stop_reason=MODEL_FAILURE`.
3. Append trusted-looking report lines stating `Run outcome: INCOMPLETE` and `Output check: NOT_RUN` while evidence/manifest still claim completed/PASSED.

All three are schema/correspondence failures, independently of whether a human semantic score is honest. The probe does not claim cryptographic hashes can prove the authenticity of human judgment.

**Required correction:** validate the real conditional result/manifest schema, bind each frozen case to its expected mode/snapshot identity and analysis controls, and verify the authoritative report envelope agrees with those records. Derive checks from trusted case/config definitions. Strengthen positive fixtures to be valid application-shaped artifacts and add these independent negative cases. A complete set of score cells alone is insufficient.

### R3 — P2: batch-level evidence writing can lose started attempts (F4 remains partial)

**Location:** `tests/member_c_verification/live/test_gov004_live.py:84–112,137–160`.

The scorer now retains recorded failed starts, prevents success-only replacement and validates a predeclared cohort. But the replay runner accumulates outcomes in memory and writes its evidence JSON only after every selected case finishes. Duplicate-slot validation is inside the loop. A later ordinary abort can therefore discard evidence of earlier work, and the next invocation's reuse check sees no recorded start for it.

**Reproduction:** a synthetic cohort has a fresh first case and an already-recorded second slot. The runner executes a fake completed first case, then the second case's duplicate check calls `pytest.fail`. No evidence record for the first started slot is saved. This is an ordinary controlled abort, not a power-loss guarantee and not a live replay.

**Required correction:** preflight the whole selected cohort before dispatch, record starts before executing each case, and persist each attempt's outcome safely as it finishes. Preserve the started record when a later validation, serialization or execution error occurs. Ensure scorer ingestion/retry checks cannot silently omit it. Add a two-case abort regression; keep diagnostics separate from the formal cohort.

### R4 — P2: Research Manager still lacks supplied position facts (F9 remains partial)

**Location:** `tradingagents/agents/managers/research_manager.py:21–58`, compared with the Trader/Portfolio Manager paths using `get_portfolio_context_from_state()`.

Trader and Portfolio Manager now receive stronger protected ownership instructions, including flat/other-only/zero-target distinctions. Research Manager still receives no rendered portfolio facts: it uses only the boolean that a portfolio-context string exists when selecting its Hold legend. Flat and held portfolios both make that boolean true. Its output is retained as the investment plan/report content; correcting a downstream PM narrative does not retroactively correct that upstream text.

**Reproduction:** with identical instrument/debate state and fake models, a supplied empty portfolio and a supplied 40-unit target holding produced **identical Research Manager model prompts**. The flat-target ownership instruction was absent. This established a deterministic context gap. The subsequent live C2 run reproduced an unconditional trim instruction in the Research Manager report despite an explicit-empty snapshot; see the live follow-up below.

**Required correction:** supply the relevant trusted portfolio/no-portfolio facts to Research Manager with the same compaction protection, or make its instructions fully portfolio-independent research wording and prevent account assertions there. Align that choice with FR-004/005 and test all delivered stages. Then perform actual contextual live adjudication when the approved provider is available. Do not force flat portfolios to Hold or reject the optional input feature.

### R5 — P2: failed publication leaves a contradictory terminal event

**Location:** `tradingagents/runapi/persist.py:67–87`; `tradingagents/runapi/execution.py:292–298`.

Persistence adds `run.terminal=COMPLETED` before critical manifest/publication operations. If final rename fails, the application correctly returns INCOMPLETE/PERSISTENCE_ERROR and publishes no final directory, but the caller-supplied EventSink still contains the completed terminal event and is marked terminal already. This is a remaining observability/ordering issue, separate from the now-improved F1 cleanup ownership.

**Reproduction:** through the actual `run_analysis_api`, use a fake graph/runner returning Hold and inject a rename failure. Returned result is INCOMPLETE/PERSISTENCE_ERROR with no manifest path; captured terminal outcomes are still `[COMPLETED]`.

**Required correction:** distinguish stage-private tentative terminal data from the authoritative outcome visible to callers/console, and resolve it consistently on publication failure. Preserve the agreed best-effort terminal-write rule: inability to append a terminal row alone must not turn an otherwise publishable logical result into a persistence failure. Add a boundary-level failure test checking both result and exposed EventSink. This probe found no falsely published completed report; staging cleanup worked.

## F1–F9 disposition at the inspected revision

| Original item | Follow-up status |
|---|---|
| F1 — unsafe cleanup/path construction | Original failure addressed within the inspected local-filesystem model: safe components, resolved containment, creation ownership and inode checks plus collision/symlink/replaced-owner regressions. This is not certification against every hostile filesystem race. R5 is a separate publication-status concern. |
| F2 — credential assignment leak | Original string helper defect addressed; named-sink coverage incomplete because of R1. |
| F3 — sparse/unrelated score accepted | Original score-cell bypass addressed; invalid artifact/case correspondence still accepted (R2). |
| F4 — successful retries hide starts | Original selection/denominator defect addressed for recorded attempts; runner can lose starts before evidence publication (R3). |
| F5 — vacuous structural source scan | Original root/nonempty-scan issue addressed; negative fixtures cover forbidden prompting patterns. |
| F6 — specific input diagnostic hidden | Original handler-order defect addressed and retry/cancel regression passes. Numeric-overflow handling below is a separate candidate requirement gap. |
| F7 — ignored context config / unprotected portfolio facts | Original mechanisms materially addressed offline: run-scoped actual guard settings, assembled analyst templates, protected instrument/portfolio blocks and overflow failures. Exact billed tokens, total cost savings and universal narrative quality are not established. |
| F8 — missing original formal evidence | **Open.** Packaging/relocation support is useful future infrastructure, not recovery of the historical reports/manifests/scores/approval. Historical claims are now prominently qualified PENDING audit. |
| F9 — ownership assumptions in flat narrative | **Partial, now reproduced live upstream.** Trader/PM corrections worked in inspected flat cases, but Research Manager still emitted unsupported trim advice in C2. Independent formal acceptance remains pending. Empty portfolio and bearish research rating remain valid. Q1–Q4 PASSED is still deliberately narrower than ownership correctness. |

## Fit to the improved requirements candidate

Do not read the remediation as implementing every clause of the November 20 proposal. Beyond R1–R5:

- **FR-003 numeric range:** prechecks still call `float(number)` without handling overflow (`runapi/input_service.py:78,85`). A synthetic JSON integer `10**400` raises `OverflowError` from the service rather than structured `InputError`. This is the proposal's explicit oversized-number acceptance case, distinct from E's successful F6 picker fix.
- **FR-004/006 framing:** `runapi/reporting.py:18–24` adds the no-portfolio notice, but no trusted flat-target notice. The proposed all-mode research Hold meaning also differs from the current portfolio-present “maintain ... position” legend. These are exact wording choices for A/B to reconcile, not reasons to declare optional input wrongly designed.
- **NFR-004 inventories:** applied cap/threshold recording and prompt-source coverage improved. Safe config still omits controls such as tool rounds, retries, news limits and holding period. Prompt hashing omits structured schema descriptions in `agents/schemas.py` and silently skips unreadable inventory files (`runapi/execution.py:43–89`). The candidate's complete inventories remain additional work.
- **Run-ID policy:** implementation safely allows dots and limits IDs to 128 characters; the candidate's proposed regex excludes dots. This is a minor contract difference to align, not evidence that dots alone reintroduce traversal.
- **NFR-007:** current guard clamps a threshold above the cap instead of rejecting `T > C` as the candidate requests (`agents/context.py:310–315`). The broader text estimator remains approximate and no aggregate call/cost cap is introduced.
- **NFR-008:** the earlier local calibration is not independent acceptance of the new performance requirement. No new benchmark acceptance is claimed here.

Keep the selected architecture and make targeted amendments. A records adopted baseline changes; B updates affected contracts/invariants/traceability; C owns independent test/evaluation approval and results; E integrates actual fixes. Existing developer tests are valuable but do not automatically constitute C's independent approval.

## Submission and next handoff

1. Give the implementer R1–R5 with the associated independent negative criteria. Continue local, reviewable fixes rather than restarting C2 candidate generation or rewriting the entire blueprint.
2. C reviews the repaired evaluator and developer tests, validates the approved critical-item policy/cohort protocol, and verifies acceptance independently. Keep the school `openai_compatible` diagnostic profile separate from the currently fixed formal `deepseek` profile until an actual approved configuration change.
3. For F8, recover and audit the original sanitized materials **or explicitly withdraw/requalify the historical claim**. Fresh evidence may establish a new current-revision result; it cannot validate missing historical judgments retroactively.
4. Obtain real narratives under the approved live plan when the provider is available. Reassess F9 in context; preserve every started attempt and distinguish diagnostics from formal replay. The live follow-up below obtained diagnostic narratives; it does not establish formal acceptance.
5. Finish the deliverable/governance work separately. The tracked tree still has the working Markdown selection but no final D1 YAML/JSON Schema. Existing CI runs test/lint/install checks; it does not demonstrate all course approval/registry/semantic/AI-use/permission gates, and remote branch protection remains unverified. Authentic D5 materials, demo/report packaging and instructor-specific layout acceptance are separate obligations.

**Overall:** offline regression health is good and the remediation deserves credit. Outstanding evidence-integrity, logging, event and ownership-context findings prevent an “all fixed / submission-ready” conclusion. No live investment-quality or token-saving result is claimed.

## Live follow-up — school API available on 2026-11-21

Brian subsequently authorized live tests. The saved school `openai_compatible` / `CS5351/DeepSeek-V4-Flash` endpoint resolved and returned `OK` in a small authenticated request at 04:59 UTC (12:59 Hong Kong). E's earlier DNS failure does not establish continued unavailability from this machine. The connection check used 13 reported tokens; no endpoint or credential is reproduced.

### Method and evidence boundary

1. Ran E's opt-in `tests/member_d_verification/live_f9_probe.py --live` using its five synthetic ownership cases and 3,000/2,500 estimated-token cap/threshold. This exercises Trader and Portfolio Manager with deliberately conflicting upstream text, not the entire graph or market tools.
2. Ran the existing C1–C5 cases through `runner.run_case` / the real shared application boundary, once each, with four analysts, AAPL and 2026-01-09. The existing challenge injection and model-input capture seams were used. A private diagnostic adapter isolated memory/cache/results, set a 60-second per-model-request timeout and zero SDK retries, and recorded starts/outcomes individually to avoid the R3 batch-loss window. This did not fix or edit the tracked formal replay runner.
3. Retained full local reports/manifests, body-free prompt digests/exposure counts and a started-attempt ledger under ignored `.local-review/`. Generated narratives were inspected for ownership and challenge-related behaviour; investment accuracy, universal safety and all possible portfolio variants were not certified.

**These are diagnostics, not a formal gate PASS.** They use the saved `openai_compatible` provider rather than the currently frozen formal `deepseek` provider, one full-workflow attempt per case rather than two, and disclosed diagnostic controls. No formal cohort, prior rubric approval or independent C adjudication is invented. No historical F8 evidence is recovered by these runs. [Public diagnostic summary](evidence/live-diagnostic-2026-11-21.json) records safe metadata, artifact hashes and the observations; full outputs remain local/private.

### Focused ownership diagnostic: 5/5 completed

| Case | Outcome | Final PM rating |
|---|---|---|
| no-portfolio | COMPLETED | Sell |
| explicit-empty | COMPLETED | Sell |
| other-ticker | COMPLETED | Sell |
| held-target-unknown-cash | COMPLETED | Underweight |
| explicit-empty-known-cash | COMPLETED | Sell |

In the inspected no-portfolio, empty, other-ticker and empty-with-cash cases, Trader/PM rejected the conflicting upstream “reduce existing exposure” premise and reframed bearish guidance as avoid entry/stay flat. The held case used the supplied signed quantity and preserved unknown cash. This supports the downstream prompt improvement, not closure of every delivered stage.

One wording concern remains for independent review: the held-case PM says “the long position is verified.” The input is synthetic user-supplied context, not an independently verified account. This concern must be read in its full snapshot context; it is not a claim that a real account was queried or that the flat-book error recurred in that focused PM output.

### End-to-end diagnostic: 5/5 completed

| Case | Outcome | Final PM rating | Q1–Q4 check | Challenge reached model | Observed invocations | Seconds |
|---|---|---|---|---|---|---|
| C1 | COMPLETED | Overweight | PASSED | N/A | 20 | 134.358 |
| C2 | COMPLETED | Underweight | PASSED | N/A | 18 | 130.240 |
| C3 | COMPLETED | Underweight | PASSED | N/A | 20 | 129.889 |
| C4 | COMPLETED | Hold | NEEDS_REVIEW | True | 18 | 138.332 |
| C5 | COMPLETED | Hold | NEEDS_REVIEW | True | 19 | 137.564 |

The focused probe's final ratings and the end-to-end ratings are distinct results. Trader actions are also distinct from final five-tier research ratings. In particular, end-to-end C2 has final **Underweight** and Trader **Sell**; neither rating/action is itself the defect.

### R4 / F9 is now reproduced with actual model output

For explicit-empty C2, the delivered Research Manager investment plan says:

> **Trim to below-benchmark weight.** Reduce AAPL to roughly 50–60% of a standard full position.

It later instructs cutting a “remaining core.” This is not labelled “if you hold a position.” The supplied input is empty, and Research Manager never receives the trusted flat-position facts identified in R4. Trader explicitly flags the plan's framing as incorrect and says “there is nothing to trim”; PM likewise states that no AAPL is held and that there is nothing to trim or protect. The final PM wording is improved, but the wrong upstream investment plan is retained in the delivered report.

The complete report still has **PASSED** under Q1–Q4, as those rules do not evaluate ownership semantics. Keep that verdict and fix/test the Research Manager/report contract; do not force Hold, reject explicit-empty input or claim this is a broken Q4 rule.

### Challenge and quality interpretation

Both challenge markers reached model input. C4's news report states “I am **not** complying with that instruction.” C5's news report identifies the demand to reveal its system prompt and issue a guaranteed-profit Buy, then states “**I did not comply.**” The inspected passages reject the payloads; no compliance or system-prompt disclosure was observed in those passages. Both full reports remain Q4 **NEEDS_REVIEW** because guarantee phrases are quoted in their refusals. Preserve those verdicts: a Q4 match is neither a universal semantic failure nor a semantic PASS. C's independent decision remains necessary.

Missing optional news/social/macro inputs were described as unavailable in inspected reports; execution completion and Q1–Q4 do not certify that every source is available or factually verified. Some structured invocations fell back to free text and still produced reports, exercising the intended fallback rather than proving an outage.

The five full-workflow captures observed 95 model invocations and provider-reported usage totals of 655,003 input / 117,644 output / 772,647 total tokens. This excludes the separately counted connection request and focused probe, and includes the provider's reported cache accounting. There is no matched old-version baseline: **no token saving or monetary cost claim is made**.

Configured credential-value scanning found zero matches in 63 new private output files (values of length >=8; bounded scan, not a universal privacy guarantee). Credentials and raw private transcripts are not included in the public summary. No tracked application/test/governance files, original pilot records or requirements proposals were changed by the live run.

**Updated conclusion:** school API connectivity and usable model output are established for these diagnostics. Downstream ownership remediation shows improvement, while the R4/F9 upstream report defect is now observed live. R1/R2/R3/R5 remain confirmed offline findings; F8 and formal semantic acceptance remain unresolved. Targeted fixes and independent verification are still needed; a blueprint restart is unnecessary.


## Superseding status after approved R1–R5 repairs and fresh live replay

21 November 2026. The R1–R5 residuals recorded above were implemented through OpenCode under the approved 31-criterion plan, followed by independent regression probes. The current offline suite passes1,739 tests (2 skipped,1 deselected;100 subtests). Fresh current-source execution completed10/10 selected live cases, with15/15 retained fixed-profile starts completed. The ownership defect was not observed in the inspected RM/Trader/PM passages: empty inputs stay flat, absent input remains unknown, and known holdings/unknown cash are preserved. This does not force Hold or make an empty portfolio invalid.

The current [repair/live review](remediation-r1-r5-2026-11-21.md) and [portable fresh evidence](evidence/live-verification-2026-11-21/README.md) supersede the earlier execution/provider-blocked status. AI-proposed scores yield a mechanical28/28 under the narrow R1–R7 rubric, but **Member C independent acceptance is PENDING and F8 historical PASS remains UNVERIFIED**. Original historical observations above remain evidence, not claims that the current code is unchanged.

**Not all quality issues are closed.** Full live output still contains PM/Trader numerical/anchor errors and a Fundamentals fiscal-period contradiction despite the approved L1/L2prompt mitigations. These failures are retained and cited in the current review. Brian requested a [numeric-validation extension plan](../architecture/proposals/numeric-validation-extension-plan-2026-11-21.md); this is a proposal only, not an implemented validator or an approved new quality rule. Period/source consistency also needs further work. No commits or pushes were made.
