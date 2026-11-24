# Memory and State Design (Member B)

Status: architecture draft (implementation-aligned 2026-11-24). Distinguishes pre-run cancellation, fresh started runs, transient state, immutable final artifacts, user-supplied portfolio data, provider transmission and retention/privacy. Named components exist in the `a62b801` checkout (verified); independent verification is C's. Resume changes are **deferred** in this selection and are **not** designed here (see §6 for the proposed D-5 conflict).

## 1. Lifecycle states

| State | Meaning | Persisted? | LLM calls |
|---|---|---|---|
| Pre-run cancellation/rejection | Discovered/cancelled/invalid input before consent, or consent declined | **No completed run**; no artifact; counted separately (NFR-006) | Zero |
| Fresh started run | A new invocation after consent; gets a unique `run_id` | Transient during run; final artifacts after finalization | Yes |
| Transient run state | In-memory graph state, message buffer, intermediate chunks | In-memory (plus existing log files) | — |
| Immutable final artifacts | Final report (MD/HTML), manifest (published run directory) | **Yes, write-once** | — |
| User-supplied portfolio data | Frozen snapshot from selected file | Held in `RunContext`; **not** written whole to new sinks | — |
| Provider transmission | Holdings sent to configured model provider | Intentionally disclosed pre-consent as a notice; actual transmission **after** consent | Yes (during run) |
| Retention/privacy | What persists locally and what is redacted | Per §4 | — |

A fresh invocation always creates a fresh `run_id` (no resume in this selection).

## 2. Owned state
- **`RunContext`** owns the immutable input identity (mode, frozen snapshot reference, full-64 fingerprint, as-of/basis, consent state). It is the authoritative provenance for report/result/manifest/check.
- **Transient graph state** (`tradingagents/graph/propagation.py`, `agents/state.py`) carries rendered `portfolio_context` (string) to the decision agents — upstream behaviour preserved. The rendered string is derived once at run start (`trading_graph.py:293-307`).
- **User-supplied portfolio data** is read **once**, validated, frozen; the file is never re-read after freeze (interface-contracts §4).

## 3. Write/retrieval policy
- Each fresh run writes into its **own run-ID-isolated** location. Same-ticker/same-date runs must not overwrite a prior run's artifacts (INV-12); the legacy date-keyed state log (`full_states_log_{trade_date}.json`, `trading_graph.py:472`) is addressed in §5.
- The manifest is written **atomically once** after artifact/check finalization, from the `SafeRunMetadata` projection — never the full `RunContext`/payload.
- Retrieval for reads (e.g., console "where is my report") uses redacted paths; no secrets.
- Resume: **deferred**. A final record is never mutated to simulate a resume.

## 4. Retention, retrieval and privacy (B3-09)

- **Transient snapshot lifetime:** the frozen snapshot value tuples live only in `RunContext` for the duration of the process/run; they are **never written** to durable sinks and are released on process exit. No durable copy of holdings is created by this extension.
- **Durable retention:** by default, artifacts persist under the run's isolated results directory **until the user deletes them**. This selection does **not** introduce automatic deletion or a cross-run catalogue (deferred). **Deletion owner:** the end user (application role); E/ops may define a later retention policy but must not silently delete user artifacts.
- **Retrieval policy:** reads for provenance/console use the redacted `SafeInputMetadata`/`SafeRunMetadata`; the portfolio source file is not re-read after freeze; no full payload is retrieved from manifests/logs.
- **Redaction ≠ suppression:** masking secrets (NFR-003) is **distinct** from suppressing raw holdings/prompt dumps. Both are required: raw portfolio bytes, full `RunContext`, raw provider prompts/payloads are **not persisted** in new sinks regardless of redaction.
- **Provider retention:** holdings **transmitted to the provider after consent** are subject to the **provider's own retention/logging policy, outside application control**; the notice states this is intentional provider transmission. The application is not represented as local-only.
- **Secrets:** never persisted; redaction boundary at every sink (§5).
- **Source files:** portfolio source files are kept **read-only**; their bytes are not copied into manifests/transcripts.

## 5. Sink handling (existing + new)

Each sink: decision (retain/adapt/disable/replace), output location, run-ID isolation, overwrite prevention, permitted content, redaction boundary, raw-payload suppression, failure handling, responsible component. Criticality and ordering are in `interface-contracts.md` §7.

| Sink | Decision | Output location | Run-ID isolation & overwrite prevention | Permitted content | Redaction boundary | Raw payload suppression | Failure handling | Responsible component |
|---|---|---|---|---|---|---|---|---|
| `message_tool.log` (`cli/run.py:139-164`) | **Adapt** | per-run results dir (`results_dir/<ticker>/<run_id>/message_tool.log`) | Under run-ID-isolated dir; never append across runs | Model/system narrative; no raw portfolio bytes/other-position dump | `Redactor` per line | Yes | **Best-effort:** failure ⇒ redacted note; does not flip COMPLETED (not a promised artifact) | Persist + Redactor |
| Graph state JSON `full_states_log_{trade_date}.json` (`trading_graph.py:472`) | **Adapt (replace path keying)** | per-run results dir | **Legacy date-keyed overwrites same ticker+date.** Replace with run-ID-qualified filename; refuse-if-exists | Existing narrative fields + safe provenance projection; never raw payload | `Redactor` on serialized entry | Yes | **Best-effort:** failure ⇒ redacted note; prior run preserved | Persist (path) + Redactor |
| Markdown report (`reporting.py`) | **Adapt** | per-run dir (`reports/complete_report.md`) | Run-ID-qualified; **critical**: written to `_staging`, published only by the single directory commit (§interface-contracts §7); refuse silent overwrite | Checked body + trusted envelope from safe projection | Redact body **before** check; escape/redact provenance | Yes | **Critical:** staging/commit failure ⇒ INCOMPLETE/PERSISTENCE_ERROR; no success exposed (§7) | reporting + Persist |
| HTML report (`report_html.py`) | **Retain escaping, adapt provenance source** | alongside MD (`complete_report.html`) | Same as MD (critical when enabled) | Same checked body + escaped envelope | Already escapes (`:10,226,255`); extend to provenance | Yes | Same as MD | reporting + Persist |
| **Manifest (new)** | **New** | per-run dir (`manifest.json`) | Run-ID-qualified; **written into `_staging` before the single commit**; immutable after commit; refuse overwrite | `Manifest` (`SafeRunMetadata` + paths + `terminal_event.durable`, decided pre-commit); **no payload/secret endpoints** | `Redactor` before staging write | Yes | **Critical:** staging/commit failure ⇒ INCOMPLETE/PERSISTENCE_ERROR; nothing published | Persist |
| **JSONL event sink (new)** | **New** | per-run dir (`events.jsonl`) | Run-ID-qualified; **terminal event appended to `_staging` before commit (sets `durable`)**; other progress events best-effort | Fixed fields (§interface-contracts §3.9) | `Redactor` per event | Yes | **Best-effort, non-critical: terminal append failure ⇒ `terminal_event.durable=false` (manifest states it) but the logical outcome is preserved and the run is published; progress-event failure ⇒ redacted note, never changes the immutable manifest** | EventSink + Persist |

**Disclosure distinction:** decision-agent narrative necessarily receives provider-summarized context **after consent** (intentional disclosure). This is distinct from copying **raw portfolio bytes / full provider payloads** into manifests/logs/events/state JSON, which is prohibited (INV-06).

## 6. Non-goals
No resume/checkpoint redesign, no cross-run catalogue, no aggregate budget persistence. Upstream checkpoint fingerprint (12-char) remains a checkpoint concern, preserved unchanged.

## 7. Proposed broader changes — impact, not implemented (2026-11-24)

- **Aggregate budgets (`REQ-TA-NFR-PERF-002`, `COST-001/002`, `BUDGET`):** if adopted, a run-scoped budget controller and a sixth `stop_reason` would be added; neither exists in `runapi/result.py` today. This section does **not** design or adopt it.
- **Resume identity (D-5 proposal):** the candidate suggests a resumed run keeps its `run_id` and appends an attempt, whereas this design gives **every fresh invocation a fresh `run_id`** and treats final records as immutable (INV-11/INV-12). These **conflict**; adoption would be a separate contract change (OQ-8), not implied by the current selection. Not implemented.
- **Per-run coverage/evidence records (`REQ-TA-FR-001/005`):** would add durable per-run coverage and evidence registries. The as-built sinks (§5) do not persist these; only input provenance is durable.

## 8. Run-budget controller state (proposed; not implemented)

The `RunBudgetController` (interface-contracts §15) holds **mutable per-run budget state** (reservation/counter state per slot). This state:
- is **separate from the frozen input snapshot** (`RunContext` is immutable and not touched by the budget);
- is **one per run** and never a global counter shared across unrelated runs;
- is not persisted as part of the immutable manifest beyond safe audit counts (cap, attempts, reservations, denials); no prompts/secrets are retained.

**Resume identity remains a separate, undecided contract** (ADR 002 D5): this selection uses a fresh `run_id` per invocation (INV-12) and immutable artifacts; a logical-run + attempt model is **not** adopted here and does not conflict-resolve automatically. Interruption (`INTERRUPTED`) semantics are unchanged and do not themselves settle resume.

## 9. Intermediate context assembly and rollback — concise mode (integrated at `adb4dfc`, PR #18)

Status: describes behaviour **integrated into main via PR #18 (merge `adb4dfc`, ancestor of current HEAD)**; the dangling-reference boundary and quality acceptance remain open. It bears on this document's owned state (prompt/context assembly) but does not alter retention/privacy or the input-snapshot contracts.

- **Assembly location.** Intermediate analyst and debate prompts are assembled in `agents/analysts/turn.py` and the Bull/Bear/risk agents during the analysis-execution stage (blueprint §5 step 6). Concise mode's brevity guidance is appended to the **assembled system message** in the analyst tool loop (`turn.py`) but to the **assembled prompt strings** in the Bull/Bear researchers and risk debaters; a duplicated opponent argument may additionally be replaced with a reference.
- **Exact reference, not semantic dedup.** A reference is emitted only when the exact stripped opponent text already occurs in debate history; otherwise the explicit copy is kept. This is **exact Python string-substring matching**, not summarization.
- **Restore-before-guard.** `bound_debate_prompt` reconstructs the explicit copies before invoking the existing `bound_agent_prompt` guard when the reconstructed-original length would exceed `min(context_cap_tokens, compaction_threshold_tokens) * 4`. The trusted `<protected_context>` portfolio block is unaffected and remains protected by the guard. **No unconditional no-dangling guarantee:** a short argument can be replaced by a longer reference notice, so a reference-form prompt longer than the restored original can still be compacted and lose its cited history (probe `docs/reviews/evidence/token-context-reference-probe-2026-11-24.json`). Restoring a copy before the guard is **not** a promise that all narrative survives compaction.
- **No new forced truncation.** The feature adds no truncation of generated output or tool payloads; the pre-existing character/4 prompt guard can still trim narrative.
- **Trusted facts preserved.** Prompt guidance is **advisory** and cannot change authoritative provenance, check results, or the protected portfolio facts; it is not deterministic semantic enforcement.
- **Effective configuration and rollback.** `concise_intermediate_reports` defaults to `True`; `TRADINGAGENTS_CONCISE_INTERMEDIATE_REPORTS=false` (or programmatic `False`) restores legacy verbosity for a new process. The flag is recorded in `run_settings()`/`EffectiveConfig` (interface-contracts §3.7) and is **not** part of `prompt_hash`; the touched prompt source files are (§3.8), so new runs' `prompt_hash` differs from pre-feature runs.
- **Legacy artifacts.** An existing run record that lacks `concise_intermediate_reports` is **legacy/unknown mode**, not today's `True` default and not `False`; historical runs are not relabeled.
- **Separation from budgets.** This is not the existing per-prompt guard contract change and not ADR-002's proposed run-wide `CALL_CAP`/`BUDGET` controller (Slice C, unimplemented). Observed token savings do not satisfy `REQ-TA-NFR-COST-002`.

## 10. Cumulative token-admission state (proposed; not implemented)

The token-admission controller (interface-contracts §15A, ADR-004, Alt-B) holds **mutable per-run ledger state** — buckets K (known actual), R (reserved/in-flight), U (UNKNOWN retained), plus monotonic `cumulative_admitted`/`cumulative_consumed_known` and the held tickets. This state:
- is **separate from the frozen input snapshot** (`RunContext` is immutable and never carries budget counters);
- is **one per run** (coordinated with the §15 call cap through `AdmissionCoordinator`), never a global counter shared across runs;
- is **not persisted** in the immutable manifest beyond safe audit counts (`K/R/U`, budget, denied/violation flags) — no prompts/secrets;
- **does not** resolve UNKNOWN late: `U` remains until finalization in this version (no `U→K` conversion), and a bound/protocol violation is recorded truthfully (never clamped), not hidden inside the manifest.

**Independence preserved:** this is distinct from the existing per-prompt character/4 guard and the concise-context feature (ADR-003); it is the run-wide cumulative-token design that sits beside ADR-002's call-cap (§15), not a replacement for it.
