# Runtime Policy Catalog (Member B)

Status: architecture draft (implementation-aligned 2026-11-24). Maps each supported failure/degraded path to trigger, responsible component, fallback/action, output and diagnostic/monitor, consistent with the selected result/check contract (`SEL-TA-FR-007`, `SEL-TA-NFR-001`). Components exist in the `a62b801` checkout (verified); test evidence is C's; enforcement wiring is D/E's. No measured results are claimed.

> **Label namespace warning:** the `R1`, `R2`, … in the **first column of the table below are trigger-row identifiers in this catalog only**. They are **not** the output-check rules `R1–R8` of proposed `REQ-TA-ARCH-002`, and **not** the checker codes `Q1–Q4` in `runapi/checks.py`. For example, catalog `R1` here is a recoverable-data sentinel path, whereas `REQ-TA-ARCH-002`'s `R1` is "final rating readable". Do not equate them by number.

## Result contract reminder
- `run_outcome = COMPLETED | INCOMPLETE`.
- `COMPLETED`: graph returned; final `rating ∈ {Buy, Overweight, Hold, Underweight, Sell, REVIEW}`.
- `INCOMPLETE`: no final rating; `stop_reason ∈ {MODEL_FAILURE, DATA_FAILURE, INTERNAL_ERROR, PERSISTENCE_ERROR, INTERRUPTED}`.
- `output_check = PASSED | NEEDS_REVIEW | NOT_RUN`; incomplete ⇒ NOT_RUN.
- Progress vocabulary (events) is separate from terminal `run_outcome`.

| # | Trigger | Responsible component | Fallback / action | Output | Diagnostic / monitor |
|---|---|---|---|---|---|
| R1 | Recoverable non-core data unavailable (upstream sentinel) | Engine/tools (baseline behaviour preserved) | Continue run with the sentinel/absent marker; **do not** classify fatal | COMPLETED (or normal) | Event notes degraded node; **not** an incomplete reason |
| R2 | Structured-output invocation fails, free text usable | `structured.py` path → PM text fallback | Use free-text; parse rating deterministically; the warning's exception detail is passed through the shared `Redactor` before logging (R1) | COMPLETED; rating if readable else REVIEW | Existing structured-fallback warning retained, redacted |
| R3 | Model/provider output exhausted | `runapi/finalize.py` | Stop; no final rating | INCOMPLETE, `stop_reason=MODEL_FAILURE` | `event=run.terminal`; redacted cause |
| R4 | Raised vendor/data exception (unrecovered) | `runapi/finalize.py` | Stop; typed result | INCOMPLETE, `stop_reason=DATA_FAILURE` | Redacted data exception message |
| R5 | Ordinary internal exception | `runapi/finalize.py` | Stop; typed result, no escape past public entry | INCOMPLETE, `stop_reason=INTERNAL_ERROR` | Redacted traceback summary |
| R6 | Malformed/invalid portfolio input | `runapi/input_service.py` (precheck + upstream model) | Stop **before dispatch**; filename + bad field/path, no contents/credentials | No run (pre-run rejection) | Input diagnostic; zero LLM calls |
| R7 | As-of mismatch (`--portfolio-as-of` ≠ analysis date) | `runapi/input_service.py` | Stop before dispatch | Pre-run input error | Field-level diagnostic |
| R8 | Selected file changed after confirmation | (no reread) | **Ignore** changed bytes; use frozen snapshot | Normal run with frozen identity | (no silent change; provenance records frozen digest) |
| R9 | Output check rule broken (Q1–Q4) | `runapi/checks.py` | Do not pass; mark review needed | If graph returned: COMPLETED + NEEDS_REVIEW + blocking finding(s) | `event=output.check` findings |
| R10 | Checker raises exception | `runapi/checks.py` (fail closed) | Blocking `CHECK_ERROR` | COMPLETED retained if graph returned, but NEEDS_REVIEW | `event=output.check` `CHECK_ERROR` |
| R11 | Model text claims "OUTPUT CHECK: PASSED" but a rule fails | `runapi/checks.py` authority | Model claim ignored | NEEDS_REVIEW | Authority-source tag on check event |
| R12 | Cooperative cancellation | `runapi/execution` + CLI coordinator | Stop cooperatively (if during run) or zero-start (pre-run) | Pre-run: no completed run; during run: INCOMPLETE, `stop_reason=INTERRUPTED` | `event=input.consent`/`run.terminal` |
| R13a | Critical report/manifest staging or commit failure before rename (terminal-event append excluded) | `runapi/persist.py` + `runapi/finalize.py` | No rename; nothing visible at published path; revise logical outcome | INCOMPLETE, `stop_reason=PERSISTENCE_ERROR`, `final_rating=null`, `output_check=NOT_RUN`, `report_path=null`, `manifest_path=null` | Redacted persistence diagnostic; `_staging` not treated as published | 
| R13b | Best-effort sink failure (state JSON or message log) | `runapi/persist.py` | Continue; redacted note; does not flip a completed decision | Normal outcome unchanged | Redacted note | 
| R14 | Terminal-event JSONL append to staging fails (best-effort, non-critical) | `runapi/events.py` | Commit still publishes; logical outcome preserved (not PERSISTENCE_ERROR); manifest states non-durable terminal | Normal logical outcome; `terminal_event.durable=false` in manifest | Redacted diagnostic; later progress append never changes manifest | 
| R13c | Critical report/manifest staging/commit failure (R13a) after a tentative terminal was staged (R5) | `runapi/events.py` + `runapi/persist.py` + `runapi/execution.py` | Discard the stage-private tentative terminal; never expose a caller-visible COMPLETED; emit exactly one INCOMPLETE terminal matching the returned result | INCOMPLETE/PERSISTENCE_ERROR/NOT_RUN; single INCOMPLETE terminal in caller sink | Redacted persistence diagnostic; no stale COMPLETED |
| R15 | Workflow returns unreadable final text | `runapi/finalize.py` + `runapi/checks.py` | Complete with REVIEW | COMPLETED + rating REVIEW + NEEDS_REVIEW | Q1 finding |
| R16 | Same-ticker/date second fresh run | `runapi/persist.py` / coordinator (run-ID isolation) | Write to a **new** run dir; refuse overwrite of prior artifacts | New isolated artifacts; first run unchanged | `event=output.persist` |

## Ordering and conditions
- Every incomplete result has `output_check=NOT_RUN`; every completed result has a rating (REVIEW allowed) and a check result.
- `MODEL_FAILURE` is used **only** for exhausted model/provider output failures; recoverable optional-data sentinels (R1) are never reclassified as fatal.
- Diagnostics are redacted (NFR-003) before delivery; secrets/holdings never appear.
- Durability across total disk failure/power loss is **not** promised; PERSISTENCE_ERROR is the cooperative failure contract.

## As-built status at `a62b801` (verified 2026-11-24)
Rows R3–R5 (`MODEL_FAILURE`/`DATA_FAILURE`/`INTERNAL_ERROR`) and R12 (`INTERRUPTED`) map to `runapi/finalize.py::classify_exception`; R13a/R13c/R14 map to `runapi/persist.py` (single `os.rename`, truthful `terminal_event.durable`) and `runapi/events.py` (stage-private tentative terminal). R9–R11, R15 map to `runapi/checks.py` (`Q1–Q4`, `CHECK_ERROR`). The vocabulary is **five** stop reasons; there is **no `BUDGET` row** implemented. Proposed budget rows (`REQ-TA-NFR-PERF-002`/`COST-001/002` → `BUDGET`) are **not** in this catalog as implemented behaviour; they would require a sixth `stop_reason` and every reader updated.

## Proposed rows for the extended checks (2026-11-24; **PROPOSED, not implemented**)

These are **catalog triggers** (the `R*` prefix here is the catalog namespace, **not** ARCH-002 rules or Q1–Q4). They accompany interface-contracts §13–§15 and ADR 002.

| # | Trigger | Responsible component | Fallback / action | Output | Diagnostic / monitor |
|---|---|---|---|---|---|
| R17 | A **required** model request is refused by an adopted run budget (`CALL_CAP`) | `runapi/budget.py` → shared execution boundary → finalizer | Refuse the request; stop new admission; account for in-flight; preserve partial content through normal publication | `INCOMPLETE`, `stop_reason=BUDGET`, `final_rating=null`, `output_check=NOT_RUN` | Budget kind, configured cap, counters, run/attempt id; no prompts/secrets |
| R18 | **Mandatory core** data channel has code ≠ `OK` — including `NOT_REQUESTED` when the core channel was mandated but never requested (price `UNAVAILABLE`/`NO_DATA`/`STALE`/`NOT_REQUESTED`) | `runapi/coverage.py` + finalizer | Stop as data failure; do not publish a successful analysis. **Strict published rule:** an unrequested mandatory core channel is NOT auto-exempt; excluding it requires an adopted A/team exemption (not applied) | `INCOMPLETE`, `stop_reason=DATA_FAILURE`, `NOT_RUN` | Channel + code; source metadata |
| R19 | Non-core channel gap / statement `STALE` | `runapi/coverage.py` | Continue; code the channel; show `STALE` with filing date | `COMPLETED` (or normal) | Coverage section reflects code |
| R20 | Output check produces **corrected only** finding (e.g. R5 confidence) | `runapi/checks.py` | Apply correction; record original+corrected | `COMPLETED` + `PASSED` + CORRECTED finding | `output.check` corrected finding |
| R21 | Output check blocking rule fails (R1–R4,R6–R8) or checker raises | `runapi/checks.py` | Do not pass; retain findings | `COMPLETED` + `NEEDS_REVIEW` | Blocking finding / `CHECK_ERROR` |

**Precedence:** if a budget stop (R17) and a critical persistence failure co-occur, `PERSISTENCE_ERROR` is primary and the budget cause is secondary (R13a unchanged). Reaching `CALL_CAP` after the last needed request does not itself trigger R17.

## Concise intermediate context — integrated at `adb4dfc` (PR #18)

> **Namespace note.** The `R22` row below is a **catalog trigger row** in this document's namespace — **not** a proposed output-check rule `R1–R8` (`REQ-TA-ARCH-002`), **not** the as-built checker codes `Q1–Q4`, and **not** the proposed run-budget row `R17`. It is **integrated into main via PR #18 (merge `adb4dfc`, ancestor of current `HEAD`)**; the dangling-reference boundary, quality acceptance and prior approval remain **open** (see R-CONCISE). It introduces no aggregate budget or forced truncation.

| # | Trigger | Responsible component | Fallback / action | Output | Diagnostic / monitor |
|---|---|---|---|---|---|
| R22 | Concise intermediate context enabled (`concise_intermediate_reports`, default True; integrated at `adb4dfc`) | `agents/context.py` (`concise_analysis_instruction`, `opponent_argument_or_opening(...,history)`, `bound_debate_prompt`); `agents/analysts/turn.py` (assembled system message); Bull/Bear/risk agents (assembled prompt strings) | Advisory evidence-first brevity; exact Python string-substring opponent reference; restore explicit copies before the existing guard when reconstructed-original length > `min(cap,threshold)*4` (reduces, does not eliminate, dangling-reference risk); legacy path via switch | Normal run; `prompt_hash` reflects the touched sources | `EffectiveConfig.concise_intermediate_reports`; no new forced truncation |

## Cumulative token admission — proposed (Alt-B; not implemented)

> **Namespace note.** `R23`/`R24` are **catalog trigger rows** (this document's namespace) — not checker `R1–R8`, not `Q1–Q4`, not call-cap `R17`. Token admission (`REQ-TA-NFR-COST-001`, interface-contracts §15A) is **proposed, not implemented**.

| # | Trigger | Responsible component | Fallback / action | Output | Diagnostic / monitor |
|---|---|---|---|---|---|
| R23 | A **required** model request cannot fit the remaining **token** budget (`K+R+U+need > TOKEN_BUDGET`) | `runapi/token_admission.py` + §15 `AdmissionCoordinator` (atomic with call cap) → finalizer | Refuse admission for both limits; account in-flight; preserve partial content through normal publication | `INCOMPLETE`, `stop_reason=BUDGET`, `final_rating=null`, `output_check=NOT_RUN`, `findings=[]` | budget kind, `TOKEN_BUDGET`, `K/R/U`, ticket id; no prompts/secrets |
| R24 | **Bound/protocol violation:** provider-reported actual usage **exceeds** its reservation allowance (may occur while total < `TOKEN_BUDGET`) | `runapi/token_admission.py` → finalizer | Record actual usage **without clamping**; halt new admissions; propagate typed `TokenBoundViolation` through broad handlers; account in-flight before finalization | `INCOMPLETE`, `stop_reason=INTERNAL_ERROR` (safe diagnostic names overage), no rating, `NOT_RUN` | allowance, actual, ticket id, cumulative; no prompts/secrets |

**Precedence:** if a token violation (R24) or budget stop (R23) coincides with a **critical report/manifest persistence failure**, `PERSISTENCE_ERROR` is primary (§R13a unchanged); the token/budget cause is secondary. Reaching `TOKEN_BUDGET` exactly after the last needed request does not itself trigger R23. **No new serialized stop reason** is introduced.
