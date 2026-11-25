> Latest Bedrock isolation follow-up (2026-11-25): Bedrock 6 passed, including conflicting AWS settings; full suite 1918 passed / 0 failed / 1 skipped / 1 deselected. Formal semantic acceptance remains pending.

> Latest post-repair rerun (2026-11-25): focused 237 passed; full 1917 passed / 1 failed; semantic harness/scorer 8 passed. See the post-repair verification section below. Formal semantic acceptance remains pending.

# Test plan — registry alignment

Updated 2026-11-25. Scope: all 36 active entries in [requirements.yaml](../req/requirements.yaml), schema 1.2.0, proposed for adoption. Use the baseline, four coverage states and per-requirement evidence/gaps in [requirement-test-mapping.md](requirement-test-mapping.md). No tests or implementation changed, no approval invented, and no live run performed.

Latest execution: [missing-test follow-up](registry-test-update-2026-11-25.md#missing-test-follow-up). New deterministic tests exercise frozen input through publication, conditional result fields, invalid REVIEW/PASSED, corrected findings and twenty disclaimer-placement renders. See the mapping's separate implementation and live-acceptance backlogs. Earlier statements that no tests were run describe the initial documentation pass only.

## Execution and acceptance plan

Use synthetic data, blocked network and scripted models through `run_analysis_api`; raw graph tests are supporting evidence only. Apply registry profiles A-A (no snapshot), A-B (confirmed snapshot without target), A-C (target plus unrelated holding); INV-014 needs all three, credential tests span all inputs. Explicit-empty and absent remain distinct. Reset cache/checkpoint state except checkpoint-specific cases.

For every mapping row, retain existing assertions and add the stated missing fit-criterion cases before upgrading coverage. Prioritize RUN-001/budget outcomes, confirmed input mutation, evidence/coverage contracts, then R1-R8 integration. Preserve Q2 provenance independently. A owns channel enumeration, thresholds and requirement ambiguities; B/D own design/implementation; C owns test oracles and independent acceptance; E owns enforcement. Pending cases are planned work, not passing tests.

Acceptance requires the full row's fit criterion, negative controls and applicable fixture profiles, plus actual recorded command, revision/dirty state, counts, failures, skips and exclusions. Do not use historical test counts as current minimums or silently waive environmental failures. Do not infer semantic quality from Q1-Q4, scorer self-tests or token savings. Live evaluation requires a fixed profile/threshold, durable all-start accounting, portable artifacts and genuine human scores; current independent acceptance is PENDING.

Test-plan pre-approval remains paused as a required merge check; GOV-002 is a clarification item, not permission to reactivate it. Normal CI still applies. Documentation-only validation here checks IDs, paths and whitespace; behavioral tests and live CI are not claimed run. The available Python lacks PyYAML, so registry parsing/schema execution was not performed in this review.

For a subsequent test run use an isolated environment with `python -m pip install -e ".[dev]"`, then `python -m pytest -q`; default integration exclusions and optional skips must be recorded. Required CI also runs Ruff, mypy, requirement schema, workflow permissions/security, dependency and AI-log checks as configured in `.github/workflows/ci.yml`.

## Semantic migration of historical references

Relationships below are partial unless the meanings fully coincide; numeric suffixes never establish equivalence. No active ID owns discovery or the full confirmation flow. Test filenames and TC IDs stay unchanged to preserve evidence links.

| Historical requirement | Current meaning-based allocation |
|---|---|
| SEL-TA-FR-001 | Unmapped discovery/selection obligation (A clarification) |
| SEL-TA-FR-002 | Unmapped confirmation flow (A open item 16); REQ-TA-INV-014 only for frozen authorization |
| SEL-TA-FR-003 | REQ-TA-INV-014 (freeze); validation remainder unmapped |
| SEL-TA-FR-004 | REQ-TA-FR-007 / REQ-TA-INV-003 (partial ownership semantics) |
| SEL-TA-FR-005 | REQ-TA-FR-007 / REQ-TA-INV-001 |
| SEL-TA-FR-006 | REQ-TA-INV-014 / REQ-TA-NFR-REPRO-001 |
| SEL-TA-FR-007 | REQ-TA-ARCH-002 / REQ-TA-INV-001 / REQ-TA-INV-008 (Q rules only) |
| SEL-TA-NFR-001 | REQ-TA-NFR-001 / REQ-TA-RUN-001 |
| SEL-TA-NFR-002 | REQ-TA-NFR-OBS-001 |
| SEL-TA-NFR-003 | REQ-TA-SEC-002 (credentials; extra holdings protection retained) |
| SEL-TA-NFR-004 | REQ-TA-NFR-REPRO-001 / REQ-TA-RUN-001 |
| SEL-TA-NFR-005 | REQ-TA-ARCH-001 (partial; CLI separation is additional scope) |
| SEL-TA-NFR-006 | REQ-TA-NFR-EVAL-001 |
| SEL-TA-GOV-001 | REQ-TA-GOV-002 (paused required gate) |
| SEL-TA-GOV-002 | REQ-TA-GOV-004 (schema) |
| SEL-TA-GOV-003 | Unmapped regression governance; retained CI duty |
| SEL-TA-GOV-004 | REQ-TA-GOV-001 (semantic evaluation) |
| SEL-TA-GOV-005 | REQ-TA-GOV-003 (AI log) |
| SEL-TA-GOV-006 | Unmapped role-permission enforcement; E decision |

## Existing case inventory with current allocations
 (IDs → requirement → expected)

| Test ID | Requirement | Scenario | Expected result |
|---|---|---|---|
| TC-FR001-a | Unmapped discovery/selection obligation (A clarification) | a/b + nested + symlink + .txt present | only `a.json,b.json`, sorted |
| TC-FR001-b | Unmapped discovery/selection obligation (A clarification) | missing dir | empty list, not error |
| TC-FR001-c | Unmapped discovery/selection obligation (A clarification) | empty dir | empty list |
| TC-FR001-d | Unmapped discovery/selection obligation (A clarification) | directory read error | `DirectoryReadError` (not "empty") |
| TC-FR001-e | Unmapped discovery/selection obligation (A clarification) | select b | only b validated; basename `b.json` |
| TC-FR002-a | Unmapped confirmation flow (A open item 16); REQ-TA-INV-014 only for frozen authorization | FROZEN context to entry | `ValueError` (consent required) |
| TC-FR002-b | Unmapped confirmation flow (A open item 16); REQ-TA-INV-014 only for frozen authorization | CONFIRMED context | runs once, COMPLETED |
| TC-FR002-c | Unmapped confirmation flow (A open item 16); REQ-TA-INV-014 only for frozen authorization | both flags / no as-of | `FLAG_CONFLICT` / `AS_OF_MISMATCH` |
| TC-FR002-d | Unmapped confirmation flow (A open item 16); REQ-TA-INV-014 only for frozen authorization | `--without-portfolio` | one run with `portfolio is None` |
| TC-FR003-a | REQ-TA-INV-014 (freeze); validation remainder unmapped | valid populated | loads; provenance fields set |
| TC-FR003-b | REQ-TA-INV-014 (freeze); validation remainder unmapped | explicit empty `positions` | valid flat snapshot |
| TC-FR003-c | REQ-TA-INV-014 (freeze); validation remainder unmapped | `cash:null` | cash preserved as `None` |
| TC-FR003-d | REQ-TA-INV-014 (freeze); validation remainder unmapped | 5 invalid classes (param) | typed `InputError` w/ kind+field |
| TC-FR003-e | REQ-TA-INV-014 (freeze); validation remainder unmapped | unreadable path | `UNREADABLE_PATH` |
| TC-FR003-f | REQ-TA-INV-014 (freeze); validation remainder unmapped | as-of != analysis date | `AS_OF_MISMATCH` |
| TC-FR003-g | REQ-TA-INV-014 (freeze); validation remainder unmapped | edit file after freeze | frozen rows/digest unchanged |
| TC-FR004-a | REQ-TA-FR-007 / REQ-TA-INV-003 (partial ownership semantics) | no portfolio | frozen notice, no "current position" |
| TC-FR004-b | REQ-TA-FR-007 / REQ-TA-INV-003 (partial ownership semantics) | explicit flat | "No current position in AAPL" |
| TC-FR004-c | REQ-TA-FR-007 / REQ-TA-INV-003 (partial ownership semantics) | held + missing cash | holding shown; no invented cash |
| TC-FR004-d | REQ-TA-FR-007 / REQ-TA-INV-003 (partial ownership semantics) | broker alias | alias matched to instrument |
| TC-FR004-e | REQ-TA-FR-007 / REQ-TA-INV-003 (partial ownership semantics) | two selections | no cross-selection holding leak |
| TC-FR005-a | REQ-TA-FR-007 / REQ-TA-INV-001 | 5 ratings + REVIEW (param) | each parsed as itself |
| TC-FR005-b | REQ-TA-FR-007 / REQ-TA-INV-001 | unreadable text | `REVIEW`, never Hold |
| TC-FR005-c | REQ-TA-FR-007 / REQ-TA-INV-001 | completed RunResult | one rating enforced |
| TC-FR005-d | REQ-TA-FR-007 / REQ-TA-INV-001 | report w/ differing RM/Trader/PM judgments | 3 labelled stages; exactly one PM-sourced final rating |
| TC-FR006-a | REQ-TA-INV-014 / REQ-TA-NFR-REPRO-001 | documented Reason-E book | fingerprint = `45f07d9e…cef72`, 64 hex |
| TC-FR006-b | REQ-TA-INV-014 / REQ-TA-NFR-REPRO-001 | reorder / 1 vs 1.0 / null price | equal digests |
| TC-FR006-c | REQ-TA-INV-014 / REQ-TA-NFR-REPRO-001 | none vs explicit empty | distinct mode/fingerprint |
| TC-FR006-d | REQ-TA-INV-014 / REQ-TA-NFR-REPRO-001 | select b | b fingerprint, != a |
| TC-FR006-e | REQ-TA-INV-014 / REQ-TA-NFR-REPRO-001 | 2 runs, same contents/date, fresh IDs, different text | both texts published; provenance identical (minus run ID/ts) |
| TC-FR007-a | REQ-TA-ARCH-002 / REQ-TA-INV-001 / REQ-TA-INV-008 (Q rules only) | all rules hold | PASSED, no findings |
| TC-FR007-b | REQ-TA-ARCH-002 / REQ-TA-INV-001 / REQ-TA-INV-008 (Q rules only) | each Q1/Q2/Q3/Q4 break | matching finding, NEEDS_REVIEW |
| TC-FR007-c | REQ-TA-ARCH-002 / REQ-TA-INV-001 / REQ-TA-INV-008 (Q rules only) | body claims "OUTPUT CHECK: PASSED" | ignored; NEEDS_REVIEW |
| TC-FR007-d | REQ-TA-ARCH-002 / REQ-TA-INV-001 / REQ-TA-INV-008 (Q rules only) | `evaluate` raises inside `run_analysis_api` | called; COMPLETED + NEEDS_REVIEW + one CHECK_ERROR |
| TC-FR007-e | REQ-TA-ARCH-002 / REQ-TA-INV-001 / REQ-TA-INV-008 (Q rules only) | check under blocked sockets | PASSED (no provider) |
| TC-NFR001-a | REQ-TA-NFR-001 / REQ-TA-RUN-001 | unreadable final text | COMPLETED + REVIEW + NEEDS_REVIEW |
| TC-NFR001-b | REQ-TA-NFR-001 / REQ-TA-RUN-001 | internal exception | INCOMPLETE / INTERNAL_ERROR |
| TC-NFR001-c | REQ-TA-NFR-001 / REQ-TA-RUN-001 | vendor exception | DATA_FAILURE |
| TC-NFR001-d | REQ-TA-NFR-001 / REQ-TA-RUN-001 | provider lib / timeout | MODEL_FAILURE |
| TC-NFR001-d2 | REQ-TA-NFR-001 / REQ-TA-RUN-001 | bare ConnectionError | INTERNAL_ERROR (guard) |
| TC-NFR001-e | REQ-TA-NFR-001 / REQ-TA-RUN-001 | raised engine error | no exception escapes |
| TC-NFR002-a | REQ-TA-NFR-OBS-001 | completed run events | all parse, fields non-null, elapsed≥0, 1 terminal |
| TC-NFR002-b | REQ-TA-NFR-OBS-001 | second terminal | rejected |
| TC-NFR002-c | REQ-TA-NFR-OBS-001 | secret in event | redacted |
| TC-NFR003-a | REQ-TA-SEC-002 (credentials; extra holdings protection retained) | 4 secret types (param) | each scrubbed |
| TC-NFR003-b | REQ-TA-SEC-002 (credentials; extra holdings protection retained) | secret-keyed mapping | values redacted |
| TC-NFR003-c | REQ-TA-SEC-002 (credentials; extra holdings protection retained) | diagnostic w/ secret | type kept, secret hidden |
| TC-NFR003-d | REQ-TA-SEC-002 (credentials; extra holdings protection retained) | model error + synthetic portfolio via API | no secret/unrelated-holding leak in result/report/manifest/events; source unchanged |
| TC-NFR003-e | REQ-TA-SEC-002 (credentials; extra holdings protection retained) | CLI pre-run portfolio input error | no secret/unrelated-holding in CLI output; source unchanged |
| TC-NFR003-f | REQ-TA-SEC-002 (credentials; extra holdings protection retained) | mid-run vendor exception via API | INCOMPLETE/DATA_FAILURE/NOT_RUN; no secret/unrelated-holding in result/report(.md/.html)/manifest/events; vendor stub reached; source unchanged |
| TC-NFR003-g | REQ-TA-SEC-002 (credentials; extra holdings protection retained) | completed narrative with planted credential (md+html) | COMPLETED; benign sentence retained; credential omitted in both reports; [REDACTED] present |
| TC-NFR004-a | REQ-TA-NFR-REPRO-001 / REQ-TA-RUN-001 | two same-ticker/date runs | isolated dirs; first bytes unchanged |
| TC-NFR004-b | REQ-TA-NFR-REPRO-001 / REQ-TA-RUN-001 | portfolio provided | manifest omits payload/cash |
| TC-NFR004-c | REQ-TA-NFR-REPRO-001 / REQ-TA-RUN-001 | completed manifest | conditional fields correct (rating present, stop_reason null) |
| TC-NFR004-d | REQ-TA-NFR-REPRO-001 / REQ-TA-RUN-001 | one config value changed | only that key differs in `effective_config`; run IDs differ |
| TC-NFR004-e | REQ-TA-NFR-REPRO-001 / REQ-TA-RUN-001 | prompt-template file edited (simulated) | `prompt_hash` changes; `effective_config` unchanged |
| TC-NFR004-f | REQ-TA-NFR-REPRO-001 / REQ-TA-RUN-001 | engine error → published INCOMPLETE | manifest has `final_rating=null`, `output_check=NOT_RUN`, a `stop_reason` |
| TC-NFR004-g | REQ-TA-NFR-REPRO-001 / REQ-TA-RUN-001 | R13a commit failure (rename fails) | INCOMPLETE/PERSISTENCE_ERROR/NOT_RUN; no rating; nothing published; no `_staging` left |
| TC-NFR004-h | REQ-TA-NFR-REPRO-001 / REQ-TA-RUN-001 | R13b best-effort state.json write fails | COMPLETED outcome preserved; `BEST_EFFORT_FAILED:state.json` in events |
| TC-NFR004-i | REQ-TA-NFR-REPRO-001 / REQ-TA-RUN-001 | R14 terminal-event append fails | COMPLETED preserved; manifest `terminal_event.durable=false` |
| TC-NFR005-a | REQ-TA-ARCH-001 (partial; CLI separation is additional scope) | scan runapi/agents/graph | no terminal-prompt imports |
| TC-NFR005-b | REQ-TA-ARCH-001 (partial; CLI separation is additional scope) | scan runapi imports | no `cli` import |
| TC-NFR006-a | REQ-TA-NFR-EVAL-001 | 6 complete/4 incomplete/2 cancel | 6/10, review 2, cancel 2 |
| TC-NFR006-b | REQ-TA-NFR-EVAL-001 | zero completed | INSUFFICIENT_EVIDENCE |

Parametrised cases expand to 80 collected test items.



## Historical plan (preserved, superseded)

Original approval references, results and change history below describe the earlier selection only. They are not new approval, current acceptance, or the current registry scope. Current coverage and gaps are in the linked mapping; historical semantic claims are subject to its dated correction.

# Test Plan (Member C)

> Remediation update 2026-11-21: current developer regression results and remaining F8/F9 acceptance limitations are recorded in `docs/reviews/remediation-2026-11-21.md`. Historical counts and claims below must not be treated as acceptance of the modified revision without independent review.

Status: **living document.** Approved in principle by the human reviewer for this
verification step. Records the independent offline acceptance tests that exist, how
they are run, and what remains undone. It does **not** claim the semantic-evaluation
gate or CI governance gates are satisfied.

Scope: the working selection `docs/req/selected-requirements.md`
(`SEL-TA-FR-001..007`, `SEL-TA-NFR-001..006`). Governance items
(`SEL-TA-GOV-001..006`) are tracked separately and are **not** yet verifiable here
(no CI/permission enforcement installed, semantic rubric/threshold not frozen).

## 1. Levels, fixtures, environment

- **Tier:** offline behavioural/structural unit tests. No network, no provider
  billing, no real holdings. Synthetic portfolio JSON in per-test `tmp_path`.
- **Engine:** a scripted engine injected through the shared boundary
  `runapi.execution.run_analysis_api(graph_factory=..., engine_runner=...)`.
  This exercises the real check/finalize/persist path with a deterministic state.
- **Location:** `tests/member_c_verification/offline/` (C-owned). It lives under
  the upstream `testpaths=["tests"]`, so the default `pytest` run collects it
  alongside the upstream suite; the offline tests keep the upstream conftest's
  no-network/scripted-model discipline. The `live/` sibling is collected too but
  skipped unless `GOV004_LIVE=1` (opt-in).
- **Helpers:** `tests/member_c_verification/offline/conftest.py` (`make_engine`, `confirmed_context`,
  `GOOD_STATE`, `holding_portfolio`).

### Commands
```
# New independent C suite (separate from upstream)
.venv/bin/python -m pytest tests/member_c_verification/offline -p no:cacheprovider

# Upstream regression baseline (unchanged by this work)
.venv/bin/python -m pytest -q -p no:cacheprovider
```

## 2. Test independence and human approval

- Tests assert observable contract behaviour through public seams; they do not
  import application internals beyond the documented design modules.
- Test files were authored by C after the plan was approved; application code was
  **not** modified for these tests.
- Approval reference: human message approving the plan for this verification work
  (recorded in the session transcript). Formal GOV-001 attributable sign-off in
  `docs/architecture/trace-matrix.md` / CI remains with E.

## 3. Entry / exit criteria

- **Entry:** selection approved as working scope; implementation present at
  `d94c9f8`; offline environment runnable.
- **Exit (per case):** test passes deterministically with no network.
- **Exit (suite):** all offline cases green and upstream suite shows no new
  regressions beyond the known environmental failure (see verification report).

## 4. Case inventory (IDs → requirement → expected)

| Test ID | Requirement | Scenario | Expected result |
|---|---|---|---|
| TC-FR001-a | SEL-TA-FR-001 | a/b + nested + symlink + .txt present | only `a.json,b.json`, sorted |
| TC-FR001-b | SEL-TA-FR-001 | missing dir | empty list, not error |
| TC-FR001-c | SEL-TA-FR-001 | empty dir | empty list |
| TC-FR001-d | SEL-TA-FR-001 | directory read error | `DirectoryReadError` (not "empty") |
| TC-FR001-e | SEL-TA-FR-001 | select b | only b validated; basename `b.json` |
| TC-FR002-a | SEL-TA-FR-002 | FROZEN context to entry | `ValueError` (consent required) |
| TC-FR002-b | SEL-TA-FR-002 | CONFIRMED context | runs once, COMPLETED |
| TC-FR002-c | SEL-TA-FR-002 | both flags / no as-of | `FLAG_CONFLICT` / `AS_OF_MISMATCH` |
| TC-FR002-d | SEL-TA-FR-002 | `--without-portfolio` | one run with `portfolio is None` |
| TC-FR003-a | SEL-TA-FR-003 | valid populated | loads; provenance fields set |
| TC-FR003-b | SEL-TA-FR-003 | explicit empty `positions` | valid flat snapshot |
| TC-FR003-c | SEL-TA-FR-003 | `cash:null` | cash preserved as `None` |
| TC-FR003-d | SEL-TA-FR-003 | 5 invalid classes (param) | typed `InputError` w/ kind+field |
| TC-FR003-e | SEL-TA-FR-003 | unreadable path | `UNREADABLE_PATH` |
| TC-FR003-f | SEL-TA-FR-003 | as-of != analysis date | `AS_OF_MISMATCH` |
| TC-FR003-g | SEL-TA-FR-003 | edit file after freeze | frozen rows/digest unchanged |
| TC-FR004-a | SEL-TA-FR-004 | no portfolio | frozen notice, no "current position" |
| TC-FR004-b | SEL-TA-FR-004 | explicit flat | "No current position in AAPL" |
| TC-FR004-c | SEL-TA-FR-004 | held + missing cash | holding shown; no invented cash |
| TC-FR004-d | SEL-TA-FR-004 | broker alias | alias matched to instrument |
| TC-FR004-e | SEL-TA-FR-004 | two selections | no cross-selection holding leak |
| TC-FR005-a | SEL-TA-FR-005 | 5 ratings + REVIEW (param) | each parsed as itself |
| TC-FR005-b | SEL-TA-FR-005 | unreadable text | `REVIEW`, never Hold |
| TC-FR005-c | SEL-TA-FR-005 | completed RunResult | one rating enforced |
| TC-FR005-d | SEL-TA-FR-005 | report w/ differing RM/Trader/PM judgments | 3 labelled stages; exactly one PM-sourced final rating |
| TC-FR006-a | SEL-TA-FR-006 | documented Reason-E book | fingerprint = `45f07d9e…cef72`, 64 hex |
| TC-FR006-b | SEL-TA-FR-006 | reorder / 1 vs 1.0 / null price | equal digests |
| TC-FR006-c | SEL-TA-FR-006 | none vs explicit empty | distinct mode/fingerprint |
| TC-FR006-d | SEL-TA-FR-006 | select b | b fingerprint, != a |
| TC-FR006-e | SEL-TA-FR-006 | 2 runs, same contents/date, fresh IDs, different text | both texts published; provenance identical (minus run ID/ts) |
| TC-FR007-a | SEL-TA-FR-007 | all rules hold | PASSED, no findings |
| TC-FR007-b | SEL-TA-FR-007 | each Q1/Q2/Q3/Q4 break | matching finding, NEEDS_REVIEW |
| TC-FR007-c | SEL-TA-FR-007 | body claims "OUTPUT CHECK: PASSED" | ignored; NEEDS_REVIEW |
| TC-FR007-d | SEL-TA-FR-007 | `evaluate` raises inside `run_analysis_api` | called; COMPLETED + NEEDS_REVIEW + one CHECK_ERROR |
| TC-FR007-e | SEL-TA-FR-007 | check under blocked sockets | PASSED (no provider) |
| TC-NFR001-a | SEL-TA-NFR-001 | unreadable final text | COMPLETED + REVIEW + NEEDS_REVIEW |
| TC-NFR001-b | SEL-TA-NFR-001 | internal exception | INCOMPLETE / INTERNAL_ERROR |
| TC-NFR001-c | SEL-TA-NFR-001 | vendor exception | DATA_FAILURE |
| TC-NFR001-d | SEL-TA-NFR-001 | provider lib / timeout | MODEL_FAILURE |
| TC-NFR001-d2 | SEL-TA-NFR-001 | bare ConnectionError | INTERNAL_ERROR (guard) |
| TC-NFR001-e | SEL-TA-NFR-001 | raised engine error | no exception escapes |
| TC-NFR002-a | SEL-TA-NFR-002 | completed run events | all parse, fields non-null, elapsed≥0, 1 terminal |
| TC-NFR002-b | SEL-TA-NFR-002 | second terminal | rejected |
| TC-NFR002-c | SEL-TA-NFR-002 | secret in event | redacted |
| TC-NFR003-a | SEL-TA-NFR-003 | 4 secret types (param) | each scrubbed |
| TC-NFR003-b | SEL-TA-NFR-003 | secret-keyed mapping | values redacted |
| TC-NFR003-c | SEL-TA-NFR-003 | diagnostic w/ secret | type kept, secret hidden |
| TC-NFR003-d | SEL-TA-NFR-003 | model error + synthetic portfolio via API | no secret/unrelated-holding leak in result/report/manifest/events; source unchanged |
| TC-NFR003-e | SEL-TA-NFR-003 | CLI pre-run portfolio input error | no secret/unrelated-holding in CLI output; source unchanged |
| TC-NFR003-f | SEL-TA-NFR-003 | mid-run vendor exception via API | INCOMPLETE/DATA_FAILURE/NOT_RUN; no secret/unrelated-holding in result/report(.md/.html)/manifest/events; vendor stub reached; source unchanged |
| TC-NFR003-g | SEL-TA-NFR-003 | completed narrative with planted credential (md+html) | COMPLETED; benign sentence retained; credential omitted in both reports; [REDACTED] present |
| TC-NFR004-a | SEL-TA-NFR-004 | two same-ticker/date runs | isolated dirs; first bytes unchanged |
| TC-NFR004-b | SEL-TA-NFR-004 | portfolio provided | manifest omits payload/cash |
| TC-NFR004-c | SEL-TA-NFR-004 | completed manifest | conditional fields correct (rating present, stop_reason null) |
| TC-NFR004-d | SEL-TA-NFR-004 | one config value changed | only that key differs in `effective_config`; run IDs differ |
| TC-NFR004-e | SEL-TA-NFR-004 | prompt-template file edited (simulated) | `prompt_hash` changes; `effective_config` unchanged |
| TC-NFR004-f | SEL-TA-NFR-004 | engine error → published INCOMPLETE | manifest has `final_rating=null`, `output_check=NOT_RUN`, a `stop_reason` |
| TC-NFR004-g | SEL-TA-NFR-004 | R13a commit failure (rename fails) | INCOMPLETE/PERSISTENCE_ERROR/NOT_RUN; no rating; nothing published; no `_staging` left |
| TC-NFR004-h | SEL-TA-NFR-004 | R13b best-effort state.json write fails | COMPLETED outcome preserved; `BEST_EFFORT_FAILED:state.json` in events |
| TC-NFR004-i | SEL-TA-NFR-004 | R14 terminal-event append fails | COMPLETED preserved; manifest `terminal_event.durable=false` |
| TC-NFR005-a | SEL-TA-NFR-005 | scan runapi/agents/graph | no terminal-prompt imports |
| TC-NFR005-b | SEL-TA-NFR-005 | scan runapi imports | no `cli` import |
| TC-NFR006-a | SEL-TA-NFR-006 | 6 complete/4 incomplete/2 cancel | 6/10, review 2, cancel 2 |
| TC-NFR006-b | SEL-TA-NFR-006 | zero completed | INSUFFICIENT_EVIDENCE |

Parametrised cases expand to 80 collected test items.

## 5. Plan changes made during implementation (with reasons)

1. **FR-002-c boundary retargeted.** The as-of/flag guards are enforced in
   `cli/input_ui.resolve_run_context` (returns typed `InputError`), not in
   `cli/main.py`. Test now targets the enforcing guard rather than the wiring.
2. **NFR-001-d expectation corrected.** `classify_exception` maps by exception
   name/module; a bare `ConnectionError` is genuinely `INTERNAL_ERROR`. The
   MODEL_FAILURE case now uses a provider-library exception + `TimeoutError`, and
   a separate case pins `ConnectionError → INTERNAL_ERROR`.
3. **FR-003 calls fixed** to use an instance (`PortfolioInputService(dir)`), since
   `freeze_path`/`freeze_loaded` are instance methods.
4. **NFR-005 tests are structural** (AST import scan), matching INV-10's
   "testability: structural" note.
5. **TC-FR006-e / TC-FR007-d strengthened** to run through the full
   `run_analysis_api` publish path (two-run provenance identity with differing
   model text; checker raising during the run into the fail-closed branch) rather
   than exercising isolated seams. Both pass.
6. **FR-005 / NFR-003 end-to-end cases added** (existing a–c retained unchanged):
   TC-FR005-d asserts labelled RM/Trader/PM stages and one PM-sourced rating;
   TC-NFR003-d asserts no secret/unrelated-holding leak across result/report/
   manifest/events on a model-error path; TC-NFR003-e asserts the same for a CLI
   pre-run input error. All pass.
7. **TC-NFR003-f added** to close the mid-run data-error gap: a reached vendor
   stub raises an unrecovered `NoMarketDataError` through `run_analysis_api`;
   asserts INCOMPLETE/DATA_FAILURE/NOT_RUN and leak-free result/report(.md/.html)/
   manifest/events with an unchanged source file. Passes.
8. **TC-NFR003-g added**: a completed run whose scripted narrative embeds a fake
   credential publishes Markdown + HTML that retain the benign sentence and omit
   the credential (with `[REDACTED]`). Passes.

## 6. Deferred / not yet covered

- **GOV-001..006** CI and permission-gate tests — blocked on E enforcement and a
  frozen semantic rubric.
- **Semantic evaluation (GOV-004)** — see §7.
- **Persistence-failure walkthroughs** (R13a/R13b/R14): **covered offline** by
  TC-NFR004-g/h/i (injected commit failure, best-effort sink failure, terminal
  event append failure). See `verification-report.md` §3.5.
- **Corrupt-checkpoint / interrupted-run** (R12 INTERRUPTED) behavioural tests.
- `tests/member_c_verification/offline` vs `tests/member_c_verification/live` full course layout split; both exist under `tests/member_c_verification/`.

## Post-repair verification — 2026-11-25

User-authorized rerun on local main `1bf6e17dd0ecdd5e5f38b157fafc4c632105a933` plus pre-existing dirty application files `tradingagents/report_html.py`, `tradingagents/runapi/reporting.py`, `tradingagents/runapi/result.py` and untracked repair regression tests. Existing D AI-log preserved. Origin remains hedyliu-574/CS5351, not the instructed team repository; no team-main equivalence claimed. Existing WSL Ubuntu-24.04 Python 3.12 `.venv` reused without installation/upgrades. Registry 1.2.0 remains proposed_for_adoption, 36 active/3 withdrawn.

### Registry and repaired-node checks

`.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/member_c_verification/offline tests/member_c_verification/test_registry_result_repairs.py tests/test_checkpoint_lifecycle.py tests/test_checkpoint_resume.py tests/member_b_remediation/test_r3_replay_durability.py tests/member_b_remediation/test_r2_r3_differential_pins.py tests/member_d_verification/test_requirement_schema_gate.py`

**237 passed**, 4.34 s, exit 0, no skips. The former 25 H1–H5 failures pass. This verifies the exercised vocabulary, finding/result validation, population arithmetic and disclaimer layout; it does not establish full registry implementation, budget admission or correction mechanisms. Evidence: `.local-review/rerun-focused-20261125.txt`.

### Full regression check

`.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short`

**1917 passed, 1 failed, 1 skipped, 1 deselected; 100 subtests passed, 24 warnings**, 16.78 s, exit 1. Remaining failure: `tests/test_bedrock_provider.py::test_construction_when_extra_installed` (H9/BD-001), AWS credential discovery failing against the configured localhost proxy. Full-suite green status remains blocked. Skip: live semantic replay not opted in. Default integration exclusion remains. Evidence: `.local-review/rerun-full-20261125.txt`.

### Semantic harness and scorer checks

`.venv/bin/python -m pytest -q -p no:cacheprovider tests/member_c_verification/live/test_harness_selfcheck.py tests/member_c_verification/live/test_score_gov004_exitcodes.py`

**8 passed**, 1.69 s, exit 0. Evidence: `.local-review/rerun-semantic-20261125.txt`. These scripted checks verify capture/injection restoration and synthetic PASS/FAIL/PENDING exits. No paid/live replay, new cohort, human scores or sign-off occurred. Formal GOV-004 acceptance remains **PENDING independent audit** under gov004-evidence-package.md; a reviewed frozen cohort and genuine human scores remain necessary. Offline results do not establish narrative quality or restore missing historical evidence.

### Required static checks

All PASS using `.venv/bin/python`: `-m ruff check .`; `-m mypy --config-file pyproject.toml` (14 files); `scripts/ci/check_requirement_schema.py` (36 active/3 withdrawn); `scripts/ci/check_workflow_permissions.py` (5 workflows); `scripts/ci/check_security_scan.py` (105 application files, zero medium/high). Dependency audit, remote CI and branch protection not checked. No implementation/test edits, relaxed assertions, commit, push or publication. Independent human acceptance remains pending. Earlier results are preserved; this addendum supersedes counts only for this checkout and scope.

Dirty application diff SHA256 (`git diff --binary -- tradingagents cli`): `06fda0250500f69c82641c93691a38ed0107c9bd33d3d8d7cf1a38a8587aaf6a`. Untracked repair-test SHA256: `e41aa13600505e83420093d1ccaccd83a11151ee472b4657f476f7aa2763374a`.

## Bedrock isolation follow-up — 2026-11-25

Supersedes the preceding unresolved H9/BD-001 result for this local checkout. User explicitly requested fixing Bedrock test isolation, rerunning tests and updating evidence. Baseline remains local main `1bf6e17dd0ecdd5e5f38b157fafc4c632105a933`, origin hedyliu-574/CS5351 (not team remote), with all previously staged H1–H5 repairs/tests/documents and untracked D isolation log preserved. No team-main equivalence or independent human acceptance claimed.

`tests/test_bedrock_provider.py` now has a module-local autouse fixture removing ambient AWS overrides, supplying synthetic credentials, disabling metadata discovery and pointing AWS/Boto config paths at an empty temporary file. Real construction resets boto3's cached default session and rejects botocore HTTP sends. Monkeypatch restores state after each test. Original real-class/region assertions and optional-extra skip remain unchanged. No application authentication or proxy settings changed.

### Bedrock checks

Existing WSL Ubuntu-24.04 Python 3.12 environment reused. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_bedrock_provider.py`: **6 passed**, 0.84 s, exit 0. Same command with synthetic conflicting AWS_PROFILE, AWS_DEFAULT_PROFILE, AWS_REGION, AWS_BEARER_TOKEN_BEDROCK and AWS_WEB_IDENTITY_TOKEN_FILE: **6 passed**, 0.75 s, exit 0. This retains real offline construction and verifies ambient override isolation. Local evidence: `.local-review/bedrock-isolation-focused-final.txt` and `.local-review/bedrock-isolation-conflicting-env-final.txt`.

The initial construction-only repair left the bearer-token test vulnerable to ambient AWS_REGION: the first conflicting-environment probe recorded **1 failed, 5 passed**. That diagnostic remains in `.local-review/bedrock-isolation-conflicting-env.txt`; the final module-wide fixture resolves the observed leak without weakening assertions.

### Full regression check

`.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short`: **1918 passed, 1 skipped, 1 deselected; 100 subtests passed, 24 warnings**, 15.52 s, exit 0. H9/BD-001 now passes on this Linux environment. Skip is opt-in live semantic replay; configured integration exclusion retained. Local evidence: `.local-review/bedrock-isolation-full-final.txt`. The final pipeline used bash pipefail, preserving pytest status.

### Static checks and limits

Ruff full repository and mypy (14 configured files) passed after the final fixture change. Requirements schema (36 active/3 withdrawn), workflow permissions (5 workflows) and security scan (105 application files, zero medium/high) passed during this repair; the later change was confined to the test fixture. No dependency changes/audit, live AWS/model calls, formal cohort/scoring, remote CI/protection inspection or delivery. Formal semantic acceptance remains PENDING independent audit; these are developer regression results. Registry adoption and broader implementation gaps are unchanged. Historical failures remain preserved. Final test-file SHA256: `3794f02e0a704d710941dc78c18fde3c1e917a9120ad6719ed9dbdf936aba6d2`.
