# Staged implementation prompt pack (Member B) — UNEXECUTED TEMPLATES

Status: **unexecuted templates, 2026-11-24; approval-protocol status reconciled 2026-11-25.** These are drafting artifacts for a *future* implementation handoff. **Architecture approval does not authorize code implementation.** Each slice's execution plan and test criteria still require prior human approval before any build, and the model-provider access constraint is stated below. No template here has been run; no code, tests, approvals or results are claimed.

> **Approval-protocol status (reconciled with root `AGENTS.md`).** Root `AGENTS.md` states that **test-plan pre-approval is paused as a required merge check** by the user's instruction. The `/approve-tests <SHA>` receipt protocol described in Template 2 below is therefore **inactive/historical for current use** — it can still run and show a result, but it must **not** be imposed as a mandatory prerequisite for the current development workflow, and it must **not** be reactivated until explicitly instructed. What remains required today: **human supervision, explicit authorization for any commit/PR/build, and defined proposed test criteria** (Templates 1/4/5). The receipt workflow is preserved as a documented, executable mechanism for a possible later re-enable; **no prior approval may be fabricated** and the paused-policy gap must be recorded separately, not erased. This reconciliation changes no requirement, course obligation, or runtime contract.

Scope of these templates: the prioritised slices in [interface-contracts.md](../interface-contracts.md) §13–§16 and [ADR 002](../adr/002-extended-result-evidence-budget.md):
- **Slice C — run budget controller + `BUDGET`** (first handoff; §15).
- **Slice A — evidence & coverage** (§13).
- **Slice B — output-check v2 R1–R8** (§14).

**Model access constraint (access, not a mandate).** As of drafting, DeepSeek V4 Flash is the only model available to Member B's OpenCode work via the school API key. This is an access constraint for this implementation route; it is **not** a course requirement, an evaluated model choice, or a restriction on TradingAgents' inherited provider capabilities. No model comparison or model-saving claim is made. **No credentials belong in any prompt or document**; provide keys only through the environment, never pasted into a prompt.

**Baseline to cite in every prompt (verify before use):** repository `Le-kk/CS5351`; recorded local revision for this planning pack `a62b801a51e6310f3b46860f6d2790583a95e0e0` (or the then-current integration HEAD named by E). Read `docs/req/requirements.yaml` (`schema_version 1.2.0`, `proposed_for_adoption`), `docs/req/selected-requirements.md`, the named architecture contracts, and `docs/reviews/project-integration-review-2026-11-24.md`.

---

## Template 1 — Read-only planning prompt

Copy the block for the chosen slice. This stage **must not modify files**.

```
You are planning (NOT implementing) a bounded change in the CS5351 TradingAgents
repository. READ-ONLY: do not edit, create, delete, commit, push, pull, switch
branches, reset or stash. Do not read .env, credentials, provider auth stores, or
private raw transcripts. Do not run paid/live model tests.

Slice: <C_budget | A_evidence_coverage | B_checker_v2>
Baseline revision to inspect: <integration HEAD; planning pack used a62b801...>

Read first:
- docs/req/requirements.yaml (schema_version 1.2.0, status proposed_for_adoption) — note
  <REQ-TA-... IDs for this slice>; treat status/priority as A owns meaning.
- docs/req/selected-requirements.md (implemented baseline scope).
- docs/architecture/interface-contracts.md §<13|14|15> and §16.
- docs/architecture/adr/002-extended-result-evidence-budget.md.
- docs/architecture/invariants.md, runtime-policy-catalog.md (namespaces!).
- The REAL source seams for this slice:
    C_budget: tradingagents/runapi/{result.py,finalize.py,execution.py},
      agents/structured.py, memory/settlement.py, graph memory step,
      llm_clients/factory.py, runapi/reporting.py, report/manifest validators.
    A_evidence_coverage: tradingagents/dataflows/router.py (+ the two router
      bypass call sites), runapi/{persist.py,execution.py}.
    B_checker_v2: tradingagents/runapi/{checks.py,result.py,reporting.py},
      agents/schemas.py (SentimentReport); tests/member_c_verification/... for seam style.

Produce a PLAN ONLY:
1. Component/module boundary and exact proposed file paths (new vs edited).
2. Interface signatures + field-level contracts (nullability + authority).
3. Normal sequence and state transitions.
4. Failure, concurrency, retry, privacy, persistence policies.
5. Compatibility/migration (schemas, readers, version gates).
6. Proposed verification scenarios: inputs, expected outputs/counters, and >=1
   violating negative per behaviour. Label them PROPOSED C inputs; do not claim
   accepted test IDs or results.
7. Dependency order and the first handoff.
8. Open decisions and feasibility limits (label ESTIMATE).

Do not propose changes outside this slice. Do not adopt requirements, declare
gates enforced, or claim test results. End by listing every file you would touch.
You may inspect code/tests read-only; do not run the suite or live tests.
```

---

## Template 2 — Human checkpoint via the installed approval protocol

This is a **human gate**. Sub-stage **(2a) prepare plan + proposed tests + human review** remains required. Sub-stage **(2b) the `/approve-tests` receipt protocol** is **inactive/historical for current use** (pre-approval is paused per `AGENTS.md`); it is documented as a possible later re-enable and must not be imposed as a mandatory prerequisite today. A filled chat block is **not** a workflow receipt, and no approval may be fabricated.

```
2a — AUTHORIZED PREPARATION (before product implementation)
Produce, on a branch/commit (execution still requires your authorization; do not
run during a documentation task):
- One front-matter plan at  docs/verification/plans/<feature-id>.md  with the
  REQUIRED fields read by scripts/ci/check_test_approval.py:
    feature_id, requirements[], implementation_paths[], test_files[], cases[],
    pass_condition
  Cases must include at least one each of kind: normal | boundary | error | security,
  each with an explicit expected result.
- The NAMED test files listed in test_files[] (proposed tests), committed in the
  SAME commit as the plan. Their file fingerprints are what the receipt binds.
- implementation_paths[] = the exact approved write set (no vague categories).
Reviewer reads the plan + proposed tests and records adequacy, incl. negatives.

2b — APPROVAL THROUGH THE TRUSTED WORKFLOW (not chat) — INACTIVE/HISTORICAL unless explicitly re-enabled
- The authorized reviewer posts the EXACT comment command **on the OPEN FEATURE PR**
  (its `issue_comment`; the workflow requires `github.event.issue.pull_request`):
      /approve-tests <FULL 40-CHARACTER COMMIT SHA>
  The comment must match exactly (a short SHA, extra text or an edited comment is
  rejected). The SHA names the plan+test commit on that PR.
- The trusted workflow (test-approval.yml -> test-approval-complete.yml) produces
  a RECEIPT bound to the comment, the approved commit and the test-file
  fingerprints. Archive the accepted record under docs/verification/approvals/.
- **Unless re-enabled by explicit instruction, pre-approval is paused:** product implementation is gated on **explicit human authorization for this change**, not on the (inactive) receipt. If re-enabled, implementation starts only after a successful receipt for that commit.
- **Approved test files are FROZEN during product implementation.** Do not edit
  them to make implementation pass; changed test fingerprints are rejected. If a
  test must change, use the policy's RENEWED / SPLIT-SCOPE procedure (re-approve
  the new test commit) — never silently rewrite frozen tests.
- Revocation uses /revoke-tests (a revocation receipt stays in force).
- Self-approval is permitted but is labelled `self_review`; it is NOT independent
  human acceptance. Retain actual reviewer attribution.

Reviewer confirmations (recorded, not backdated):
1. Scope bounded; no edits to canonical requirements, other members' tests/CI/
   evidence, or files outside implementation_paths[].
2. Test criteria adequate BEFORE implementation; a failing/violating test defined
   before product code.
3. Result-contract/compat + version-gate plan acceptable.
4. Provider/model access constraint acknowledged; no credentials in any file.
5. One-slice approval does not approve other slices.

Receipt reference to record:  approval_id: ______  approved_commit (40): ______
NOTE: This gate approves PLAN + TESTS via the pinned receipt. It does not adopt
requirements or certify verification. Any commit/PR/approval/archive action needs
explicit authorization when executed and is not performed in a documentation task.
```

---

## Template 3 — Build prompt (only after explicit human authorization; receipt gated only if re-enabled)

```
You are implementing an APPROVED, bounded slice in CS5351 TradingAgents.
Pre-approval is PAUSED (per AGENTS.md): proceed ONLY with EXPLICIT human
authorization for this change. If the `/approve-tests` receipt protocol is
re-enabled by instruction, also require a successful receipt for this exact
commit (trusted workflow; `/approve-tests <FULL 40-CHAR SHA>` on the OPEN FEATURE
PR; archived under docs/verification/approvals/) and reject absent/mismatched
receipts or differing test-file fingerprints.
APPROVED TEST FILES ARE FROZEN during implementation (when a plan/test set was
approved): a needed test change uses the renewed/split-scope procedure, never a
silent rewrite.
Do not expand scope. Do not edit files outside the APPROVED implementation_paths[]
from the plan. Do not touch canonical requirements, other members' tests/CI/
evidence, or secrets. Work offline with the scripted/offline profile; no paid/live.

Slice: <C_budget | A_evidence_coverage | B_checker_v2>
Authorization: explicit human authorization ______ (required today)
Approval receipt: OPTIONAL/INACTIVE while paused — approval_id ______  approved_commit (40) ______ (fill only if `/approve-tests` is explicitly re-enabled)

PERMITTED FILES = the EXACT implementation_paths[] from the approved plan plus the
approved test_files[]. Do not use category names. The approved set must explicitly
include every mandatory hook for the slice; if it does not, STOP and escalate
(Template 5) rather than editing an unapproved file. Authoritative examples the
plan must have covered (exact repo-relative paths):
  C_budget (metering + budget): new tradingagents/runapi/budget.py;
    tradingagents/graph/trading_graph.py (attach controller to deep/quick llm at
    :79-80; budget-aware _memory_step); tradingagents/agents/structured.py
    (re-raise budget); tradingagents/memory/settlement.py (re-raise budget);
    tradingagents/llm_clients/factory.py (force max_retries=0 in budget mode,
    reject unsupported clients); tradingagents/runapi/result.py, finalize.py,
    execution.py, reporting.py, persist.py (manifest), events.py (log fields).
  A_evidence_coverage: new tradingagents/runapi/evidence.py, coverage.py;
    tradingagents/dataflows/router.py; the direct-source call sites
    tradingagents/agents/analysts/sentiment_analyst.py,
    tradingagents/agents/context.py, tradingagents/agents/tools.py;
    tradingagents/runapi/persist.py, execution.py.
  B_checker_v2: tradingagents/runapi/checks.py, result.py, reporting.py;
    tradingagents/agents/schemas.py (only if a field is required); manifest field
    additions (separate schema_version vs check_rules_version).
TESTS: named in the approved plan test_files[]; do not modify existing C-owned
    tests unless the plan explicitly lists them (otherwise renewed/split-scope).

MET/POINTS (budget): reserve() single-use atomic; dispatch() pairs GRANTED->CONSUMED;
  invalidation never refunds cumulative admission (monotonic granted<=CALL_CAP);
  wrap the run's deep/quick chat models so plain invoke, bind_tools(...).invoke and
  with_structured_output(...).invoke each consume EXACTLY ONE reservation (no missed
  or double charge); RunBudgetExhausted survives structured/settlement/memory broad
  handlers; budget recognized BEFORE generic classification; PERSISTENCE_ERROR stays
  primary over BUDGET. Do NOT claim a runtime metering guarantee before the
  verification probes (B-variants) pass.

ACCEPTANCE CRITERIA (must hold; mirror the approved test list):
  <paste the approved proposed scenarios for the slice (e.g. B1-B7 / E1-E12 / K1-K16)>
  Each criterion needs a passing positive and at least one violating negative.
  For the budget slice these MUST include the metering probes:
    - plain llm.invoke -> exactly one reservation consumed
    - llm.bind_tools(...).invoke -> exactly one reservation consumed
    - llm.with_structured_output(...).invoke -> exactly one reservation consumed
    - a path that would double-wrap/double-count is rejected by the probe
    - structured/settlement/memory broad handlers do not swallow RunBudgetExhausted
    - invalidate/reserve/re-reserve at cap is denied (monotonic admission)
    - wrong-run / reuse of a reservation is rejected (BudgetProtocolError)

SCOPE LIMITS:
- No change to public engine signatures beyond what the slice requires; preserve
  upstream tests where unaffected.
- No new provider/model, no credentials, no live tests, no network.
- Do not mark requirements satisfied, do not claim verification, do not adopt scope.
- If a genuine ambiguity affects correctness, STOP and ask (see Template 5).

DELIVERABLES: code + regression tests + a short note of exact commands run
(offline) and their outcomes captured in the interaction. Do not commit/push.
```

---

## Template 4 — Verification prompt (checks, outcomes, negatives, evidence)

```
You are verifying an implemented, approved slice in CS5351. You are NOT the
implementer. Verify against the approved plan and acceptance criteria. Do not
modify application code or the implementation's tests to make them pass.

Slice: <C_budget | A_evidence_coverage | B_checker_v2>
Approved plan/acceptance revision/hash: <from Template 2/3> (receipt only if `/approve-tests` re-enabled)

CHECKS TO RUN (offline; scripted model; record exact commands + results):
- Targeted slice tests, then the prior offline suite, Ruff, dependency and
  whitespace checks. Use the project virtual environment; no paid/live calls.
- Positive cases: each approved scenario passes.
- NEGATIVE cases (must fail as designed):
    C_budget: >CALL_CAP attempts admitted; exhaustion swallowed by fallback;
      shared counter across runs; budget relabelled INTERNAL_ERROR; BUDGET stop
      overriding a co-occurring persistence failure.
    A_evidence_coverage: dangling cited ID passes; unrequested channel mislabelled
      as gap; core-gap completes; coverage section differs under prose change.
    B_checker_v2: CORRECTED treated as NEEDS_REVIEW; BLOCKING treated as PASSED;
      Q2 and R2 conflated; R3 phrase downgraded to corrected; model "PASSED" text
      overriding a blocking rule.
- Compatibility: a reader that enumerates old StopReason / old finding status
  fails closed on the new value (not silent coercion); schema_version behavior.

EXPECTED OUTCOMES: state precisely per case (counters, fields, status, stop_reason,
output_check, paths null/not-null). Compare to the approved criteria; do not relax.

EVIDENCE TO RETAIN: the exact commands, stdout/exit codes, the new/changed test
files (paths), and any captured manifests/events for the positive and negative
runs. Do not overwrite existing retained evidence; write to a new path if live is
ever used (it is not in this template). Distinguish test DEFINITION, developer
diagnostic and independent acceptance.

VERDICT: report PASS/FAIL/PENDING per criterion with the evidence path. This is a
verification recommendation; independent acceptance remains C's recorded decision.
Do not claim team adoption or requirement satisfaction.
```

---

## Template 5 — Review and escalation conditions

```
STOP AND ESCALATE (to the human approver / B / C) if any of the following occurs;
do not silently work around it:

1. A required change falls OUTSIDE the permitted file set (Template 3).
2. A genuine ambiguity or conflicting contract affects correctness (e.g. channel
   map or bypass indices unknown; whether BUDGET is retained; R5/R3 scope unresolved;
   resume identity). Surface it; do not decide A/C/team scope.
3. A negative test cannot be made to fail as designed (criterion unmet).
4. The result-contract/compat change would break an existing reader without a
   version gate; propose the gate, do not weaken validation.
5. A failure would tempt relabelling a stop reason, hiding an attempt, skipping a
   gate, or editing retained evidence to go green.
6. Any request to edit canonical requirements, other members' files/tests/CI/
   evidence, or to run paid/live tests.
7. Provider/model access: if the only available model for this route cannot satisfy
   the offline/scripted requirement or would require credentials in a file, stop.

REVIEW EXPECTATIONS:
- Implementer and verifier are different people where practical.
- The verifier reproduces original negatives with black-box/synthetic probes, not
  only the implementer's new tests.
- All chronology (plan approval -> tests -> implementation -> verification) is
  recorded in the authentic interaction; nothing is backdated.
- Historical F8 stays unverified; current acceptance is a separate result.

On escalation: state the concrete choice, the options, the impact and the exact
minimum approval needed. Do not proceed past the approved scope without it.
```

---

## Template usage notes (human, not agent)

- Run per slice; do not bundle all three into one unapproved mega-change.
- **First handoff = Slice C (budget + BUDGET)** (interface-contracts §16.1): most isolated, offline-testable, unblocks a Must plus `BUDGET`.
- **Evidence/coverage data contracts (Slice A §13) must be agreed before** Slice B's R2/R7 checker integration (approved dependency order).
- These are **unexecuted templates**: no build, test, approval or result has occurred. Each single in a new interaction with **explicit human authorization**; the (currently **paused**) `/approve-tests <full 40-char SHA>` receipt protocol (Template 2b) is preserved as inactive/historical and applies only if explicitly re-enabled.
- **Do not claim a runtime metering guarantee** (or any "exactly once" property) before the verification probes pass; before that, ≤1-attempt intent and the tests are the only evidence.
- Preserve authentic interactions for D5; do not backdate approvals; a handoff summary is not a raw transcript.
