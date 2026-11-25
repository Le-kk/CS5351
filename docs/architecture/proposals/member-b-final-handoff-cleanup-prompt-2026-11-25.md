# OpenCode prompt — final Member B handoff cleanup

Work in `/home/brian/projects/CS5351` using the existing architecture session and DeepSeek V4 Flash. This is a small documentation-only cleanup for E's **B1/B2 handoff request**, not another architecture redesign, new feature or approval of the full requirement set.

## Context and source evidence

Your previously reviewed architecture was committed as `b33fe41ce7b2d93c5625a9e4bcee90c0486155f9` and merged into team main by PR42 at `1b3310f4de39bef12291deada5f476db0b2655f1`; the supervising audit verified those two Git trees are identical. Local HEAD remained b33fe41 during that audit. Check the actual permitted baseline/dirty state; do not assume no later changes. Preserve all unrelated local drafts, especially numeric-validation-extension-plan-2026-11-21.md.

Read [the prepared B1/B2 handoff response and correction list](member-b-handoff-response-2026-11-25.md) and [compact source audit](../../reviews/evidence/member-b-handoff-audit-2026-11-25.json). If the active role denies these reads, obtain their contents through an authorized human/supervisor handoff; do not bypass the tool policy. They are supervising evidence, not an invented human approval or C acceptance.

Follow current AGENTS.md, .agent/rules.md, .opencode/rules.md and root Prompt.md. First present one exact-file plan and cite genuine existing authorization where it covers the concrete cleanup. If no applicable H1 approval covers that plan, stop at H1; do not fabricate it. Do not require paused /approve-tests receipts or claim strict-B activation from tool availability. No new model run, dependency install or Git publication is authorized.

## Exact candidate write set

1. `docs/architecture/traceability-inputs-member-b.md`
2. `docs/architecture/invariants.md`
3. `docs/architecture/evaluation-logbook.md`
4. `docs/architecture/proposals/member-b-handoff-response-2026-11-25.md` — finalize this existing response draft only if the active policy permits that write; otherwise defer this file to the authorized supervisor and finish the permitted canonical cleanup.

No other write paths. The newly supplied prompt and original compact audit are read-only inputs. Snapshot the permitted target files before editing; rollback must remove only this pass's changes.

## 1. Correct monitor labels without implementing new events

Supervising static AST inspection of production source found actual literal emission names: input.mode_resolved, input.consent, run.started, run.budget, output.check, output.persist, message_log.capture and run.terminal. Normal terminal visibility also uses events.py staging/commit methods. This inventory is static evidence of emission sites, not a guarantee every branch/run emits every event.

Four labels in B's §1 monitor column and corresponding invariant rows have **no emitted production event**:

| Label | Affected B rows | What to document instead |
|---|---|---|
| input.selection | SEL-TA-FR-001; INV-01 | Explicitly proposed/not emitted. Existing observations are PortfolioInputService.discover and CLI _choose_file/resolve_run_context; do not claim pre-run cancel has a completed artifact |
| output.provenance | SEL-TA-FR-006; INV-04/05/05b | No dedicated event. Cite RunContext.safe_input_metadata/snapshot_fingerprint, trusted report/header guard and manifest fingerprint/provenance fields |
| security.redaction | SEL-TA-NFR-003; INV-06 | No dedicated event. Cite Redactor and real sink/log-warning scrub points, sanitized artifacts and existing privacy tests, with no newly executed PASS claim |
| api.entry | SEL-TA-NFR-005; INV-10 if relevant | No dedicated event. Cite run_analysis_api consent guard and actual post-confirmation input.mode_resolved/input.consent/run.started sites |

Update the table legends so emitted events, artifact/code observations and proposed labels cannot be confused. Keep invariant meanings, numbering, fallbacks and requirement IDs unchanged. Do not pretend repeated case IDs are invalid attempts or weaken existing protections.

Read actual source to verify symbols and conditions: input_service.py, context.py, execution.py, reporting.py, checks.py, persist.py, events.py, redact.py, agents/structured.py and cli/input_ui.py as needed. Cite real source locations/observation points. Events are conditional: for example input.consent is post-confirmation, and output.check occurs when the checker is invoked, not automatically for every incomplete/pre-run call. Do not add source code or new logging to make a design table true.

Retained published run artifacts are `<results_dir>/<ticker>/<run_id>/events.jsonl`, manifest and reports as specified by persist.py/contracts §7. Event durability may be false; critical publication failure does not promise durable artifacts. Preserve this distinction.

## 2. Label the historical budget rollout correctly

B trace-inputs §5 is dated 24-Nov and preserves the original implementation order. It still says the call-cap enforcer is unbuilt/first handoff and describes model-object invoke metering. Preserve the original historical rationale, but clearly label it as the **24-Nov proposed rollout**, with an explicit current-status correction: call-count admission is shipped for the bounded profile and enforced at the synchronous SDK transport (`runapi/budget.py`, `llm_clients/budget_transport.py`), as contracts §15/ADR002's implementation addendum describe. Point to actual run.budget and safe manifest counters.

Ensure readers cannot treat the historical model-wrapper sketch or “all enforcers unbuilt” sentence as current implementation. R1–R8/evidence/coverage, cumulative token/time caps and generic comparison acceptance remain proposed/unestablished. Do not rewrite ADR decisions, pretend independent acceptance, or relabel old probe proposals as executed tests.

## 3. Finalize the B1/B2 handoff response, without editing E's matrix

Retain the response's exact correction list for E:
- Final-matrix historical FR-003 crosswalk → REQ-TA-INV-014 partial, not checkpoint/resume by matching suffix.
- NFR-001 also needs REQ-TA-RUN-001 for typed stop reasons.
- CI SEL GOV-003 has no registered counterpart (OQ-10); AI-log SEL GOV-005 maps to REQ GOV-003.
- E's matrix can update its still-pending B layout/observed entry-point references using the merged contracts: leading disclaimer plus permitted footer; OQ-19 observation acknowledged; general comparison acceptance remains open.

Do **not** edit `docs/architecture/trace-matrix.md`; E owns assembly. The response is contributor correction/confirmation input, not a second final matrix.

After permitted B corrections are verified, B1 may read **“Ready as architecture inputs/correction list; E matrix integration and human handoff approval pending”**. Do not claim E applied the corrections or that all requirements pass. B2 remains **Ready as technical input**, with genuine human review/send status clearly pending unless evidence proves otherwise. Replace completed B cleanup actions with observed completion, leaving E/C owner actions open.

Preserve B2's existing boundary/ADR review index. ADR updates are needed when a real architecture decision changes, not for every factual wording correction. Existing exact-scope human authorization remains valid; do not invent an approval or enforce a new receipt.

Preserve the CSV reconciliation: the supplied `Deliverables-and-Ownership.pdf`, page 4 §4, names `docs/traceability/trace-matrix.csv` with E owner; the repository's sole editable final matrix is `docs/architecture/trace-matrix.md`, E-owned. E should annotate/reconcile the external agreement reference. Do not modify that PDF or create a competing CSV.

## 4. Logbook and verification

Append one dated documentation-cleanup entry recording the actual source baseline, this B1/B2 task, corrected monitor classifications, historical budget annotation and remaining E/C actions. Keep earlier dated history unchanged. No fabricated experiment, ADD cycle, native permission activation, C semantic/security acceptance, team adoption or new test result.

Verification appropriate for this task:
- Direct paragraph/source comparison for each affected row and legend; no unqualified claim the four proposed labels are emitted.
- Confirm actual source methods and event conditions; link existing tests only as references, not new runs.
- Preserve 19 unique SEL rows, invariant numbering, working/final namespace distinctions and current partial-coverage labels.
- Check relative links, tables, fences, whitespace, exact approved scope and preservation of unrelated work through permitted tools. Attribute supervisor checks; report denied/unavailable tools honestly.
- No behavioral/full-suite/model rerun solely for these documentation changes. No new runtime events or safety decisions are needed.

Out of scope: source/tests/requirements/schema/validator/CI/governance/permissions/API snapshot, E's final matrix, original audit/evidence/PDF, other ADRs, AI-log rewriting, commits/pushes/PRs or messages to teammates. The human/supervisor will package the authentic transcript/log update and upload after review.

Final response: exact changed-section table, source/event-vs-observation mapping, checks actually run and their limits, B1/B2 readiness separated from human acceptance/E integration, and any deferred response-file write. Stop at human H3 review. Do not claim publication.
