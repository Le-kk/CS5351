# Upload-package review after latest main update — 25 November 2026

## Result

**Do not upload the previously reviewed six-document package unchanged.** Main advanced from f83aaf7 to **6b57aadff96798a8832baa0215f37ef407b356dc**. It changes the actual H3 contract, H5 exporter coverage and call-budget mechanisms. All 29 pre-existing local files were privately snapshotted and preserved byte-for-byte during the fast-forward; no incoming path overlapped them. There are 49 incoming paths. Your reviewed six canonical edits and unrelated numeric draft remain local, uncommitted modifications.

This review records observed code and tests, not a requirements adoption, independent semantic acceptance or source-code repair. See [compact evidence](evidence/pre-upload-sync-review-2026-11-25.json).

## Required architecture deltas before upload

| Area | Actual new implementation | What the old upload now gets wrong |
|---|---|---|
| H3 interface | EvaluationPopulation exists; summarize_records(records, *, population=None); four extra optional RunRecord binding fields | Old signature, no-population claim, unconditional aggregate=1 and no-duplicate-validation claim are stale |
| H3 controls | Declared population_id/source_revision/prompt_hash/configuration_fingerprint/case_ids; nonblank IDs, SHA256 control hashes, unique tuple cases; started records must match controls/membership; duplicate attempt IDs/unknown categories/invalid present case IDs reject | Distinguish implemented binding validation from remaining full expected-case coverage, accepted cohort/profile and comparison work |
| H3 outputs | Known case IDs still establish distinct_case_count without population; population_result_count is null for nonempty unscoped input, 1 for bound nonempty input, 0 for no STARTED | Replace the previously accepted 1-for-all-nonempty rule in §10, INV-21, traceability and risk/status prose |
| Real evaluator | score_gov004.py prints Evaluation counts JSON after eligibility, cohort and actual manifest/pre-start control checks | The pure summary alone does not authenticate evidence; document the adapter/evidence boundary and its retained protections |
| H5 | Legacy write_report_tree prefixes complete Markdown; HTML notice is unconditional, including metadata None/empty; runapi leading envelope plus footer remains | Remove current metadata-only/metadata-less exporter limitation; keep unprobed reader and per-agent-section limits honest |
| Budget | Opt-in RunBudgetController and actual synchronous SDK transport cap; finalizer emits BUDGET on refusal | Old no-controller/no-BUDGET-emitter/unimplemented Slice C status is stale |
| Budget compatibility | Disabled: schema_version string '1', no budget/version extensions; enabled: schema_version integer 2, check_rules_version integer 1, run_budget exact safe five counters; scorer validates | Update EffectiveConfig, finalization/publication, artifact schema/version and reader examples; preserve unknown-version fail-closed policy |
| Delivery | E added trace-matrix.md, AI-use index and token optimization report/compact JSON | Missing-artifact and missing-final-matrix claims may now be stale; do not edit E's final matrix or inflate evidence into semantic acceptance |
| A crosswalk | A2 handoff explicitly corrects mapping by meaning | B FR-003 should map partially to INV-014; NFR-001 also needs RUN-001; GOV-003 CI gates has no registered counterpart (OQ-10), unlike GOV-005 AI-log → REQ-TA-GOV-003. Keep other relationship disputes explicit rather than copying every row uncritically |

The new population is a **single configuration declaration**, not the earlier deferred richer per-case sidecar design. Generic binding values are caller declarations, not signatures; source_revision is nonblank, not necessarily a 40-hex commit. Different expected cases can be listed, but the helper does not require every listed case to be observed. Synthetic probe with expected C1/C2 and only C1 observed returns distinct=1/population=1; that is not N_EVAL or full coverage. Truthy controlled_change is refused for a supplied population; the unscoped path does not enforce that comparison rule. Do not claim a full controlled before/after comparison reporter exists. Formal current scorer profile remains five cases/ten planned attempts; the twenty-case fixture is not a new formal acceptance cohort.

Call cap is config call_cap / TRADINGAGENTS_CALL_CAP; None disables, zero allows no requests. Supported tier factories: deepseek/openai_compatible, synchronous SDK HTTP transport, SDK retries disabled, async denied. Granted tickets are single-use/run-bound and never refunded; seal waits for active responses and exposes safe counts. Client-side cap is not a token cap, elapsed-time cancellation guarantee, protection against arbitrary custom code, or count of gateway-internal retries. Persistence failure remains primary, with safe secondary budget diagnostics. Cumulative token admission §15A/ADR004 remains proposed; R1–R8/evidence/coverage remain unimplemented.

## Requirements issues for A — do not silently repair in B docs

1. **H3 fit/threshold versus its own note and implementation.** NFR-EVAL-001's fit says both counts are null when no population is declared. Its reconciled note and code preserve distinct_case_count from explicit case IDs and only make population_result_count unknown. A synthetic started C1 with no population yields 1/null. The threshold also says null otherwise, while the note and implementation explicitly yield aggregate=0 with no STARTED. A should reconcile unknown population, unknown case identity and empty input separately. B can document observed behavior and link this unresolved conflict without inventing adoption or weakening C's tests.
2. **Stale H5 implementation note.** SEC-003's reconciled note says runapi is not compliant because its disclaimer is only in the footer. reporting.build_envelope already starts with DISCLAIMER, so that implementation claim is false at this revision. The normative first-rendered-visible-content wording and permission for a retained footer are useful and align with current renderers. B should not copy the false status claim.
3. **Comparison coverage remains a claim to verify.** A's note refers to a comparison path satisfying rule-6 fixtures, while E's generic helper explicitly refuses controlled comparisons and requests a separate agreed interface. No full rule-6 acceptance was established by this review. Maintain partial coverage rather than infer acceptance from the passing binding/negative tests.
4. Minor editorial issue: INV-008's fit repeats the final zero-tolerance sentence. It is not a blocker to B documenting the observed interface.

COUNTS_CASES and H3/H5 amendments are now published; stop saying they are absent. The registry remains proposed_for_adoption, not adopted (36 entries, 3 withdrawn). Do not replace actual implementation truth with contradictory explanatory notes just because schema validation passes.

## Additional as-built contract deviation to disclose

execution.py currently appends the trusted Call budget section **after** OutputChecker has evaluated the narrative body. Existing architecture claims that the exact final delivered body is checked. The new counters are trusted static data, but the full-byte claim no longer literally holds. Document the actual narrative-check versus trusted-post-check-audit boundary and flag the invariant mismatch for B/D/E. Do not silently certify byte equality or weaken normative requirements; a later choice is needed between moving rendering before the check and explicitly authorizing/narrowing the checked subject. This review makes no code change and does not designate this deviation accepted.

## Observed checks

- Requirements CI gate: PASS, 36 requirements / 3 withdrawn / 0 errors / 0 warnings.
- Registry negative fixtures: 32/32 reject for their specified reasons.
- Focused incoming-change regressions: 75 passed.
- Full default suite: **1974 passed, 2 skipped, 1 deselected, 24 warnings, 100 subtests passed**, 36.89 s. Skips: opt-in semantic live replay and absent optional langchain_aws. Integration exclusion remains.
- Synthetic accounting probes independently reproduce unscoped known-case 1/null, empty aggregate=0, and declared subset aggregate=1.

Focused/full counts overlap; no new model run, new cohort, scores, formal acceptance, current remote-protection audit or source repair. All commands use the existing WSL .venv; no dependency changes. New CI coverage reported by E is 15 type files / 107 application scan files, not a fresh mypy/security run by this review. Historical 14/105 results remain dated evidence.

## Next step

Use [the new OpenCode alignment prompt](../architecture/proposals/post-sync-architecture-update-prompt-2026-11-25.md). The old six-file plan was correct at f83aaf7 but is superseded for current upload preparation. OpenCode should inspect current instructions/source, propose the exact expanded documentation write set, stop at H1 unless that precise plan already has genuine approval, and then align current claims while retaining historical logs/ADR rationale. No new code is needed merely to describe these merged mechanisms. A's contradictions and the post-check budget-text mismatch remain explicit owner follow-ups.
