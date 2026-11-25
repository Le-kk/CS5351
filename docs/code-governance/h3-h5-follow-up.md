# H3/H5 implementation follow-up — 2026-11-25

Baseline: main d82d24e, including C PR34 and H1 PR36. User-authorized follow-up;
not requirements adoption or independent member-C acceptance. H2/H4 verdict
invariants, semantic scoring thresholds, model configuration, and the paused
prior-test-approval policy are unchanged.

## H3: explicit populations and actual evaluator output

`runapi.result.summarize_records(records, *, population=None)` preserves all
started attempts in the completion denominator, including unresolved starts.
Duplicate attempt IDs, unknown categories and present-but-blank case identities
are refused, rather than silently changing completion/case counts.

`EvaluationPopulation` declares one population ID, source revision, SHA-256 prompt
hash, SHA-256 effective-configuration fingerprint, and unique nonblank case IDs.
Every started `RunRecord` must carry matching population/revision/prompt/config
bindings and a case from that declared set. Mixed/unbound records fail. A
`controlled_change` comparison is refused in this single-configuration API;
comparison acceptance needs its own agreed interface, not an assumed population.
These are declared controls, not signatures, human approvals or proof against a
caller deliberately fabricating records.

- Known case identities: `distinct_case_count` counts cases, not attempts.
- Legacy records missing case identities: distinct count is `null` (unknown).
- Started records without explicit population controls: `population_result_count`
  is `null`, replacing the earlier unconditional `1`.
- Explicit matching population with started records: population result count is
  `1`. No started records: `0`. Neither value is an acceptance verdict.
- Zero completed records retain `INSUFFICIENT_EVIDENCE`.

The real `score_gov004.py` entry prints a machine-readable `Evaluation counts:`
JSON line beside its completion/review results. It asserts a population only
after existing evidence/config/pending-start eligibility checks and frozen-cohort
identity, chronology and revision checks. The population identity hashes the
validated cohort; configuration identity includes fixed model configuration and
analysis/budget controls. Invalid evidence cannot become a validated population
merely because it was present in the directory. Missing scores remain PENDING;
a validated population is also required for PASS. Scoring thresholds, critical
failures, denominator and exposure policy otherwise remain unchanged. Actual
manifest/pre-start controls are checked for every started attempt, including
outside-cohort retries; they are not copied from the desired configuration.

The existing formal profile remains 5 cases / 10 planned attempts. This change
does not adopt the registry's provisional 20-case gate. A separate developer
fixture verifies 20 cases / 40 attempts / one explicitly bound population.

Two C fixtures were intentionally updated: the 20-case positive now provides
explicit controls; the legacy unresolved-attempt fixture expects unknown
population count without them. No tests were removed. Public RunResult fields
and runapi exports remain unchanged; population controls are evaluation records,
not new application manifest fields.

## H5: every complete-report exporter

Both `write_report_tree` (also used by `TradingAgentsGraph.save_reports`) and the
shared run API now put the canonical disclaimer before title/provenance in
complete Markdown. HTML `render_report` emits it as the first body notice even
when metadata is absent or empty; structural head/style markup may precede it.
Existing provenance, body checking and compatibility disclaimer/footer copies
are retained. Per-agent section files remain source sections rather than being
changed into standalone complete reports. No model-supplied disclaimer is needed
for the trusted complete-report notice.

## Verification scope

Developer probes cover legacy Markdown/HTML, metadata None/empty/present,
duplicate attempts, blank cases, unknown populations, mixed revisions/prompts/
configuration/IDs, unknown cases, unsupported comparisons, unresolved starts,
20/40 counting, and empty evidence. The existing synthetic PASS test asserts
actual scorer output: 10 started / 5 cases / 1 validated population.
No paid model calls or fresh human semantic judgments are implied.

The H5 position contract also has a negative probe, `TC-SEC003-c`
(`tests/member_c_verification/offline/test_registry_gaps.py::test_inv008_disclaimer_only_later_is_a_violation`,
Markdown + HTML): a disclaimer that is present but appears only after a
title/header is rejected as a violation of "first rendered visible content",
not accepted as "contains". Presence-only checking (rule Q3) cannot detect this,
so compliance rests on the exporter layout the positive nodes assert.
