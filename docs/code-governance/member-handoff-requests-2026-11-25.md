# Member handoff requests — AI-use evidence, traceability and governance verification

Prepared by E, 25 November 2026. Reference checkout: main `345d983`, with the local E9 event index. Please provide the items under your own section and identify any unavailable material honestly. Existing valid material can be linked rather than rewritten.

This round requests contributions from **A, B and C**. No additional submission is requested from D: E will use the current source and the latest architecture's implementation links for assembly, as agreed. Contributors still verify their own requirement, architecture and verification claims.

## Current scope and status

- **AI-use index:** E has prepared [docs/ai-use-log.yaml](../ai-use-log.yaml) from the available records. A currently has no substantive record in the repository; outstanding source/confirmation gaps are listed in the index.
- **Final trace matrix:** [B's inputs](../architecture/traceability-inputs-member-b.md) and [C's mapping](../verification/requirement-test-mapping.md) exist. E assembles the final `docs/architecture/trace-matrix.md`, using A's confirmed IDs, actual implementation paths, enforcing components, tests/evidence and runtime monitors.
- **CI:** the original four gate categories are historical starting scope. The last verified main protection has seven required check names: `required tests`, `ruff (strict, full repo)`, `dependency check`, `ai-log updated`, `requirements schema`, `type check` and `security checks`. Schema and incremental typing already exist. Security/API/permission checks have concrete implementations and limits; C should verify their coverage instead of inferring completeness or absence from filenames.
- **Separate remaining mechanisms:** test-plan pre-approval tooling exists but remains paused as a required merge check. Live semantic acceptance is not a default required gate. Human safety/ADR review requirements are not automatically established by the presence of governance documents. E will verify final activation and protection settings at acceptance.

## To Member A — Requirements and AI-use records

### A1. Supply project-related AI-use records

Please ask your assistant to locate the relevant project conversations in its actual local history, including the relevant hidden session/log directories when necessary, and prepare selected records under `AI-log/Member-A/`. Focus on important requirement drafting/revisions, registry/schema work, human decisions, final IDs/adoption and acceptance-criteria changes. Do not send an unfiltered native export or an entire session database.

Use the prompt below. It follows the current selected-extract practice documented in [Member E's recording guidance](../../AI-log/Member-E/README.md) and recent dated records. The team format remains flexible; truthful source coverage matters more than rigid formatting.

### Copyable prompt for A's assistant

```text
Prepare my CS5351 project AI-use records from authentic local conversation history.

1. Locate actual project-related sessions using the assistant's history/export
   facilities and, where necessary, its relevant hidden session/log directories.
   Identify the installed tool's real history locations rather than inventing
   paths. Match the repository/workspace, project titles, relevant dates and
   requirement work. Do not scan unrelated personal material, credentials,
   authentication stores or private portfolio data. If the active role/tool
   permissions prevent access, report the restriction and request a human
   export or authorized execution; do not weaken or bypass permissions.

2. Select important work: requirement discussions, conflicts and corrections,
   registry/schema/validator changes, acceptance criteria, final IDs, adoption
   decisions and human interventions. Do not reconstruct missing conversations
   from code, memory, another member's statements or a later summary. Label
   partial exports, missing timestamps and unavailable approvals explicitly.

3. Save readable Markdown records under AI-log/Member-A/. Use the true first
   message date/time in Asia/Hong_Kong when established. A descriptive dated
   filename is also acceptable, as in recent team records. Never invent a
   timestamp or silently assume a timezone the source does not establish.

4. Begin each record with a short English task summary and record identity:
   member, actual tool/model where known, date/timezone, session/source label
   and selected scope. Keep source locators short; do not publish long machine
   paths, credentials or the native database itself. Mark unknown fields as
   unknown. Do not relabel the tool/model to fit an expected environment.

5. Include selected original user questions and corresponding public assistant
   replies/progress messages, preserving their original language and wording.
   Keep the questions belonging to the selected task; do not retain only the
   answer. This is an edited excerpt, not an unfiltered raw export. Clearly
   label selection, omissions and any redactions. Add only brief necessary
   English context. Do not include internal reasoning, system/developer
   instructions, full tool calls/results, complete patches, file-write bodies
   or long code/command payloads embedded in replies. Mark where they were
   omitted without silently rewriting the surrounding original text.

6. Add an English work/change summary: what changed and why, relevant files,
   actual additions/modifications/deletions or line counts where established,
   and the human decisions that affected the work. Mark unavailable counts
   as unknown; distinguish a daily change from a cumulative branch total.

7. Add actual verification: commands when available, source revision/config,
   observed pass/fail/skip/not-run results, evidence links and remaining gaps.
   Preserve failed attempts and later corrections. Separate proposed changes,
   completed code, measurements, human approval and independent acceptance.
   A claimed result is not independently verified merely because it appears
   in the conversation. Do not invent missing decisions or retroactive PASS.

8. Remove secrets, personal/private account details and sensitive endpoints.
   Preserve original local sessions unchanged. If available, provide a small
   provenance index with source/session labels, coverage/omission notes and
   hashes, without publishing private absolute paths or raw exports.

9. Finish with the created record paths and any missing conversations or
   approvals I still need to provide. Do not commit, push or contact other
   people unless separately authorized.
```

For the consolidated `docs/ai-use-log.yaml`, E will write **event descriptions only** and link to these selected records. A does not need to copy conversation text into that YAML or create a competing team index.

### A2. Confirm final requirement identity and adoption for the matrix

Please provide or confirm:

- The authoritative registry/schema revision and actual adoption status. The available registry has been recorded as `proposed_for_adoption`; please confirm whether this remains true and supply the real decision reference if it changed.
- The final IDs and acceptance criteria to use in each matrix row, including withdrawn/superseded requirements and deliberately deferred items.
- The semantic crosswalk from historical `SEL-TA-*` to final `REQ-TA-*`, with full/partial/no coverage identified. Numeric suffixes must not be treated as equivalent IDs. Resolve any requirement-meaning ambiguity B/C flag.
- Which requirement wording governs semantic evaluation, negative cases and safety-critical review. A schema validation pass is not adoption or proof that all requirements are implemented.

Suggested handoff: update/link the existing `docs/req/` registry, change log and source notes, then send E the revision and a concise list of confirmed decisions/open issues. No rewrite of already valid requirement files is requested.

## To Member B — Architecture inputs and boundary confirmation

### B1. Verify the architecture side of the final trace matrix

Please review your existing `traceability-inputs-member-b.md` against the current source and A's confirmed final IDs. Supply only corrections, missing rows or a dated confirmation for unchanged valid rows. Each relevant row should identify:

- Requirement ID/crosswalk, enforcing component and real source location.
- Architecture invariant/contract and relevant ADR.
- Runtime monitor/event, its actual emission/observation point and retained evidence if available. Distinguish implemented monitors from proposed event names.
- Fallback/failure behavior, and any partial coverage, reduced-coverage entry point or unimplemented design.

E will assemble the final Markdown matrix and use the existing implementation links/source; D is not being asked for another handoff in this round. B verifies architecture interpretation and B-owned links; C verifies test/evidence claims.

### B2. Identify safety-critical boundaries and review requirements

Please identify which boundary/permission/privacy/publication/model-dispatch or budget changes require an ADR or human safety decision, and the applicable existing ADR/contract. Confirm the distinction between implemented behavior and the proposed extended checker/evidence/token-admission designs. Correct stale governance-status statements with a dated update where necessary; preserve historical records.

Please reconcile any ownership-agreement reference to an alternative CSV matrix with the course path `docs/architecture/trace-matrix.md`. Provide a pointer or agreed path correction rather than maintain a second independently edited matrix. Flag the location of any conflicting reference for E to reconcile.

## To Member C — Verification mapping, semantic gate and negative evidence

### C1. Confirm test/evidence rows for final traceability

Please reconcile `requirement-test-mapping.md` with A's confirmed IDs and the final tested source revision. Supply test file/node IDs, exact command/configuration, observed result, evidence paths and limitations. Distinguish passing tests, developer probes, independent acceptance, not-run cases and unavailable evidence. An existing file alone is not a verified pass.

Please reconcile historical GOV-004 PASS/PENDING statements and counts with the later evidence/eligibility findings. Do not reconstruct missing historical reports or scores through a fresh run; label the old claim unverified and retain a separately identified new cohort if needed.

### C2. Provide a runnable semantic-evaluation contract
（这一部分难度高，可以不做或者有时间最后做）
Please establish the fixed replay cases, eligibility/input requirements, scoring rubric, quality/critical-violation thresholds, required attempts and handling of failures/retries. Provide the command/exit-code contract and sanitized evidence packaging needed for E to integrate the gate. Identify the actual trigger scope for prompt/model changes and cost/credential prerequisites.

Include negative evidence that demonstrates rejection of missing scores, wrong-run or mismatched report/manifest evidence, duplicate/incomplete populations and below-threshold/critical-violation outcomes, as applicable to the final evaluator. Retain all started attempts so retries cannot improve the denominator by hiding failures. Keep deterministic Q1–Q4 status separate from semantic acceptance. If the mechanism is not ready, state the blockers; E should not deploy a placeholder that reports success.

### C3. Independently establish security, API and permission coverage

Please use the existing [coverage guide](types-and-security-coverage.md), tests and scripts as starting material. They already include incremental typing, application scanning, API snapshots, workflow-token/checkout rules and local role-permission probes. Assess actual scope and omissions, rather than assuming either complete coverage or no coverage.

Provide a compact verification record for each applicable area:

- Security: scanner scope/completeness, severity/suppression handling, redaction/privacy, input consent/immutability, unsafe XML/URLs and publication boundaries. Verify a valid control and the relevant deliberately unsafe/malformed case.
- API surface and layering: supported entry/result contract, intentional-versus-unreviewed snapshot drift, `runapi`/CLI dependency direction and nonempty source scanning. Show the actual failure caused by a planted violation.
- Permissions: distinguish CI token/trusted-code rules from local role file permissions and OS isolation. Check allowed role reads/writes, protected/human-only writes, external paths and denied bypass tools within the documented scope. Review the existing dated 50/62/69-case snapshots by their hashes; do not add their totals together or treat startup symlink checks as continuous isolation.
- Type/schema gates: confirm the current selected type scope and registry validation behavior, including a valid control and invalid type/schema input. These mechanisms already exist; independent confirmation or identified gaps are requested, not duplicate implementations.

For each case, report boundary/requirement, source/configuration revision, command, valid-control outcome, negative-case outcome, evidence location, residual risk and reviewer identity. A negative case is successful only when the intended protection rejects it, not when an unrelated error occurs. Clearly label self-test versus independent verification and any unexecuted case.

### C4. Support the final governance enforcement review

Provide C's evidence for applicable test-approval scope/timing/provenance/revocation and human safety/ADR review expectations. The test-approval gate remains paused until the human decides to enable it; please do not activate or change branch protection as part of this handoff. If an expected approval/review cannot currently be enforced or demonstrated, record that gap explicitly for E's final acceptance review.

## E's integration work after the handoffs

E will merge the AI-use descriptions into `docs/ai-use-log.yaml`, assemble the sole final `docs/architecture/trace-matrix.md`, check links/ownership and integrate C's ready verification mechanisms. E will inspect the live branch-protection names/settings and retain real positive/negative PR evidence at final acceptance. Schema/type checks will be verified in their existing jobs; the human will separately decide activation of paused prior-test approval and the ready semantic gate.

E will also check whether safety-critical human review/ADR requirements are actually enforced or remain process-only, and record any gap without claiming document presence equals enforcement. Existing required checks and the user's current merge/review policy must be preserved unless a change is explicitly authorized.

## Requested reply format

Please reply under your member/task labels with: **Ready / Partial / Blocked**, the exact repository file paths and source revision, a brief account of what was supplied/confirmed, real verification/evidence links, and unresolved items with an owner. Existing materials may be linked. Do not invent an approval, missing conversation, test result or completed handoff. No fixed deadline is asserted by this document.
