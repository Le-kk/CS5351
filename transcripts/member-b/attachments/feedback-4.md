# One final reproduced regression — pending records bypass eligibility

Continue SAME session/approved plan. Independent probes now PASS terminal dedup, 10-way cross-process retention, containment, empty-ledger rejection, all missing manifest keys/schema, identical mirror acceptance, conflicting mirror rejection, counterfeit body metadata rejection, actual application-generated 10/10 PASS, actual runner interruption stop, legacy durable row, and truthful post-commit callback failure. Keep these repairs; no redesign, live calls, secrets, subagents, commits/pushes or unrelated changes.

There is ONE remaining scoring regression introduced by your item-8 change. Against an actual-API synthetic 10/10 PASS population, add one unresolved start (so 10/11 >=90%):

- model_config={} -> prints `Ineligible ... pending start lacks pre-dispatch configuration` but FINAL VERDICT PASS.
- model_config={**FIXED_CONFIG, 'llm_provider':'wrong-provider'}, controls copied from frozen cohort -> prints `Ineligible ... Pending start fixed configuration mismatch` but FINAL VERDICT PASS.

The cause is `no_bad_evidence = all(a.eligible or a.pending_start for a in attempts)` (or equivalent). pending_start is provenance of a record, NOT permission to bypass eligibility! Also the unknown-config branch currently appends a reason and returns without setting eligible=false.

Make a minimal bounded correction, tests first:

1. Gate acceptance on ALL attempts being eligible, including pending starts. An eligible pending record is still noncompleted and never a quality sample. No `or pending_start` exception.
2. For a pending start, validate case/trial, known FIXED_CONFIG, and captured pre-dispatch controls against authoritative frozen cohort controls (ticker/date/revision/prompt hash as supplied by the formal runner). Reject missing/unknown/mismatching binding as ineligible; retain it in the denominator. Do not fabricate model settings from a result. This distinction was already requested in feedback 3: unknown configuration may legitimately block acceptance and must be documented.
3. Keep legitimate control-bound 9 completed + 1 pending PASS at unchanged thresholds, with at least one completed per case and scores only for actual completed artifacts. Add regressions for pending wrong provider, missing config, wrong date/control and missing binding -> FAIL even if all completed rows are excellent. Verify portable package/rescore retains this distinction.
4. If the positive pending fixture currently omits the required pre-dispatch binding, improve it to match what the actual runner now records; do not weaken validation to make it pass.

Run the focused scorer/replay regressions, then one stable full offline suite/Ruff/pip/diff check after the code change. Update the repair report and evidence guide precisely; do not repeat the full suite after docs-only changes. No new exploratory feature work. Native raw session and independent probes will be retained by coordinator. Finish REPAIRS_READY_FOR_REVIEW with actual results and honest live/C/F8 limits.
