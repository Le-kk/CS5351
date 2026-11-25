# Project Delivery Gap Checklist — Member Review

**Review date:** 23 November 2026, Asia/Hong_Kong.  
**Inspected checkout:** `CS5351-new`, commit `3fef2e9`, including locally available documents.  
**Purpose:** Confirm missing deliverables, available source material, handoffs and ownership before final assembly.

This is a local inventory, not a final acceptance verdict or a fresh inspection of every member's working copy or the latest GitHub state. A file absent here may already exist elsewhere. In particular, Member A has reported completing the registry package; it is classified as pending handoff, not unwritten. File presence alone does not establish completeness or approval.

## Sources and interpretation

- `CS5351-2026-2027-project.pdf`, pages 5–10: D1–D9 deliverables, required repository structure and blocking gates.
- `Deliverables-and-Ownership.pdf`: primary ownership, member handoffs, baseline records and final report assembly.
- Recent correspondence from A: the registry handoff, validator integration, semantic evaluation and AI-use logging.
- The inspected repository's architecture, verification, review, AI-log and workflow files.

**Course-required** means the project specification explicitly requires the artifact or behavior. **Team handoff/supporting** means the team ownership agreement or integration process specifies the file, even where the course does not mandate that exact filename. Existing path conventions should be reconciled with the course structure without maintaining competing authoritative copies.

## Member A — Requirements

- [ ] **A1 — `docs/req/requirements.yaml` — Course-required; pending handoff.**
  A reports that the registry is complete, but it is absent from this checkout. Deliver the current version, including its real adoption/status information. Do not regenerate it from the older selected-requirements Markdown or treat a proposed set as approved.
- [ ] **A2 — `docs/req/req-schema.json` — Course-required; pending handoff.**
  Deliver the matching schema together with the registry. This is input to E's schema-validation job.
- [ ] **A3 — `docs/req/validate.py`, `change-log.md`, and `requirement-source-notes.md` — Team handoff/supporting; pending handoff.**
  A reports these already exist. Supply the validator, its dependency/command information, dated decisions and requirement sources. The course does not prescribe each of these filenames individually, but the materials support validation and traceability.

**Main work type:** Receive and integrate existing materials, rather than rewrite A's requirements. A retains ownership of requirement meaning and acceptance criteria.

## Member B — Architecture

- [ ] **B1 — Existing architecture package — Course-required core artifacts; final consistency review needed.**
  The blueprint, ADR, invariants, memory design, permission model, runtime policy catalog and candidate evaluation table already exist. Check them against A's final requirement IDs, the current implementation and D's measurements. Clearly distinguish implemented behavior, design estimates, proposed decisions and unresolved items. This inventory does not imply that the architecture package must be rewritten.

The course lists the evaluation logbook, risk list and option ledger as optional; all three already exist locally. The root `architecture-blueprint.md` is currently authoritative, with a pointer under `docs/architecture/`; do not create two independently edited versions.

**Main work type:** Review and reconcile existing content. B supplies architecture inputs to E's final trace matrix; B does not maintain a competing matrix.

## Member C — Verification and Quality

- [ ] **C1 — `docs/review-memo.md` — Course-required; missing.**
  Produce per-PR review records covering specification alignment, architecture alignment, code/test quality and operational metadata, with security and efficiency considered throughout. Each review needs an actual verdict: APPROVE, CHANGES REQUIRED or REJECT. Existing review/remediation reports provide material, but do not replace missing review judgments.
- [ ] **C2 — `docs/debt-register.md` — Course-required; missing.**
  Consolidate real debt from known limitations and review findings, including its category, impact, owner and treatment decision. A defect list renamed as a debt register is insufficient.
- [ ] **C3 — `docs/bug-diary.md` — Course-required; exists, needs updating.**
  The inspected file contains three earlier entries. Add significant later bugs with symptoms, reproduction, root cause, repair, verification and the invariant gap exposed.
- [ ] **C4 — `docs/code-governance/verification-constraints.md` and `docs/verification/verification-report.md` — Existing verification materials; need a final-version roll-up.**
  Reconcile historical test counts, PASS/PENDING statements and current limitations. Tie evidence to the final revision and distinguish developer self-tests from independent acceptance. Reuse valid evidence; do not silently apply old results to a changed implementation.
- [ ] **C5 — `docs/verification/defect-log.md` — Team-owned supporting deliverable; missing.**
  Establish the agreed defect-status entry point using the existing bug diary and review records. Shared references are preferable to duplicate, inconsistent defect histories.
- [ ] **C6 — `test/offline/` and `test/live/` versus existing `tests/` — Course layout reconciliation; test code already exists.**
  The repository has substantial tests and live/offline organization within its current layout. Confirm the accepted mapping and runnable commands. A different directory name does not mean tests are absent; do not relocate them without checking discovery and imports.

**Main work type:** Consolidate existing evidence, update the final verdicts and fill real review/acceptance gaps. C also supplies evaluation cases/scoring and evidence needed by E's gates.

## Member D — Implementation and Baseline

- [ ] **D1 — Versioned runtime prompts under `prompts/` — Course repository structure; missing as separate files.**
  Runtime prompt text already exists in Python code. Extract actual templates or generate faithful versioned snapshots and document their correspondence to executed code and hashes. Do not fabricate historical prompt versions merely to reproduce the example filenames.
- [ ] **D2 — `src/` versus existing `tradingagents/` and `cli/` — Course layout reconciliation; application code already exists.**
  Confirm whether the agreed existing package layout can be retained, and document the delivery mapping. Do not move working packages solely to match a diagram without validating imports, packaging and execution.
- [ ] **D3 — `docs/experiments/baseline-protocol.md` — Team-owned supporting deliverable; missing.**
  Document a reproducible workload, model/provider configuration, data timing, retries, and runtime/token measurement method. Existing run records can inform the protocol but do not establish an agreed final experiment by themselves.
- [ ] **D4 — `docs/experiments/baseline-results.md` — Team-owned supporting deliverable; missing.**
  Report the final baseline and any optimization comparison under stated conditions, including failures and limitations. Existing diagnostics are reusable only where comparable; conduct additional measurements where evidence is insufficient.
- [ ] **D5 — `docs/experiments/run-manifests/` — Team-owned supporting deliverable; no standard baseline archive here.**
  Some manifests already exist under review evidence. Link or archive those belonging to the reported experiments and supply missing experiment metadata. Moving diagnostic files into a new directory does not create a missing baseline experiment.

**Main work type:** Some prompt/manifest organization can reuse existing data; final baseline methods and results may require substantive writing and new measurements.

## Member E — Governance and Integration

- [ ] **E1 — `docs/architecture/trace-matrix.md` — Course-required; missing final matrix.**
  Combine B's `traceability-inputs-member-b.md` and C's `requirement-test-mapping.md` with A's final IDs and D's implementation links. Include enforcing components, tests/evidence and runtime monitors. E owns assembly; contributors verify their own links. The ownership agreement's alternative CSV path should be reconciled with the course Markdown path, not maintained as a competing source.
- [ ] **E2 — Root `AGENTS.md` — Course-required; missing.**
  Define the agent entry point, architecture reading order, baseline, readable/modifiable/frozen areas, module contracts and required verification. Existing architecture material provides inputs, but the startup instructions still need to be written.
- [ ] **E3 — `docs/code-governance/structural-constraints.md` — Course-required; missing.**
  Consolidate B's boundaries and the actual source layout into explicit module/dependency restrictions and enforcement expectations.
- [ ] **E4 — `docs/code-governance/mcp-tool-manifest.md` — Course-required; missing.**
  Record actual tools, capabilities and allowed roles. State the real tool scope if MCP is not used; do not invent integrations.
- [ ] **E5 — `.opencode/permissions.jsonc` — Course-required; missing executable permission configuration.**
  B's permission design exists. Translate it into configuration supported by the actual tool and demonstrate allowed and denied access. A permission document alone is not enforcement.
- [ ] **E6 — `.opencode/rules.md` — Course-required; missing, human-only.**
  Have a human author/maintain the always-on rules as required by the specification. Do not present AI-authored rules as human-only work.
- [ ] **E7 — `.agent/rules.md` — Course-required; missing.**
  Record the project covenant: abstraction/dependency limits, independent negative tests, safety-critical change approval and rule freshness. Existing governance and architecture material can be consolidated.
- [ ] **E8 — Root `Prompt.md` — Course-required; missing.**
  Define the static launch instruction: execution plan first, stop for human approval, then build and self-verification through the required human gates. Product runtime prompts are not a substitute.
- [ ] **E9 — `docs/ai-use-log.yaml` — Course-required repository artifact; missing.**
  Build a structured index from the available original-language `AI-log/` records, linking important tasks, interventions, changes and verification evidence. Collect outstanding member records. This is mainly aggregation/formatting, but missing source conversations cannot be invented.
- [ ] **E10 — Root `Report.md` — Course-required; missing.**
  E is the sole editor/assembler. A–D supply their technical sections; every member supplies their own reflection, name/student ID and contribution evidence. The brief specifies at most 10,000 words excluding diagrams, more than 15 pages at 12-point single spacing, and individual reflections of approximately 300–500 words. Existing documents are inputs, not a finished process report.
- [ ] **E11 — `README.md` — Course-required; exists, delivery instructions incomplete.**
  Add the team's actual repository link, project purpose/architecture, file organization, exact offline/live/full-suite commands and blocking-gate design. The current README still substantially describes the upstream project.
- [ ] **E12 — `.github/workflows/ci.yml` and associated governance enforcement — Course-required; exists, further mechanisms remain.**
  The current four gate categories have passed real PR checks. Still implement/verify prior test approval, registry schema validation, type checking and semantic evaluation. Ask C to establish the coverage and negative evidence for security, API-surface and permission checks; do not infer that they are either complete or wholly absent from file names alone. Verify branch protection and safety-critical review/ADR enforcement at final acceptance. E integrates; C owns verification, B supplies boundaries and D supplies runnable code/measurements.
- [ ] **E13 — Attributable prior test-approval evidence and its gate — Course-required behavior; mechanism/evidence incomplete.**
  The exact evidence path is a team design choice, not a course-mandated filename. C supplies the test plan, a human approves it, and E retains/verifies evidence before implementation. Post-implementation CI receipts do not replace this requirement. Disclose historical gaps rather than backdating or fabricating approvals.
- [ ] **E14 — `docs/submission/contents-and-build.md` — Team-owned supporting deliverable; missing.**
  Assemble the package inventory, reproducible installation/startup and test commands, known limitations and treatment of secrets. These instructions should match the final archive.
- [ ] **E15 — Final ZIP / `submission/` staging area — Course-required archive; team staging convention.**
  Assemble and verify the required repository structure and links. No final package was identified in the inspected checkout. Exclude credentials, local `.env`, real holdings and unnecessary caches; preserve required deliverables and evidence. The course requires the ZIP, not necessarily a tracked staging directory.

## All Members — Five Annotated Agent-Session Transcripts

- [ ] **T1 — `transcripts/<student-id>-<student-name>.md`, five member submissions — Course-required; delivery directory absent.**
  Each member supplies the original session material and marks their interventions with reasons: interruptions, redirections, approvals and rejections. E assembles/checks the submission. Collectively, the records must demonstrate the supervised pipeline specified in D5.

Existing AI logs provide source leads but are not automatically compliant D5 transcripts. In particular, extracts that omit tool calls, write payloads or long code are not equivalent to the course's full raw transcript requirement. Keep compact AI-use logs and full annotated delivery transcripts as distinct artifacts. Confirm that the selected source sessions actually demonstrate the required work; do not invent a from-scratch session or retrospective approval.

## What Mainly Reuses Existing Material?

- **Pending handoff:** A's registry, schema, validator and supporting records.
- **Primarily aggregation/formatting:** the AI-use YAML index; trace-matrix assembly; README and package instructions; organization of valid existing evidence/manifests.
- **Existing material plus substantive judgment:** review memos, debt register, bug diary updates, final verification report, architecture reconciliation and process report.
- **Not just formatting:** real prior approvals, permission enforcement, missing CI gates, independent semantic acceptance, missing baseline experiments and human annotations on full source transcripts.

## Review and Handoff Instructions

For each assigned item, confirm whether it is already available elsewhere, needs revision, needs implementation, or is ready for final delivery. Supply the authoritative path/revision and the remaining action. Do not create duplicate authoritative artifacts merely to satisfy this checklist.

E assembles approved contributions without silently rewriting A–D's technical conclusions. A completed document or a green CI run must not be treated as evidence for a different revision or a broader acceptance claim than it actually supports.

The next practical priorities are: receive A's registry package; collect each member's report inputs and original transcripts; complete governance artifacts and traceability; and close the real gate/acceptance gaps before final packaging.
