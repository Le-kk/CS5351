# GOV004 portable evidence and frozen population

The November 18 historical live PASS remains **PENDING independent audit**: the original reports, manifests and score file are not present in this checkout. Repairing the scorer or creating fresh diagnostics cannot recover or approve those historical judgments. Preserve the original review and do not fabricate missing scores, timestamps or approval.

## Freeze a formal cohort before outcomes

A/C must approve the actual provider/model configuration, applicability and critical-item policy before formal use. The scorer retains the documented fixed `deepseek` configuration; the saved school `openai_compatible` configuration is diagnostic until that difference is explicitly approved. Critical R1/R2/R3/R5/R6/R7 failures conservatively prevent PASS, regardless of optional caller flags. A/C should ratify this explicit policy rather than infer safety from a missing flag.

Create `tests/member_c_verification/live/evidence/cohort.json` with:

- `schema_version`: integer **2**. Schema 2 newly makes `ticker`/`analysis_date` mandatory; schema 1 is treated as stale and rejected (it is not silently upgraded).
- `approved_by`: attributable real approver, never a generated identity.
- `frozen_at_utc`: actual timezone-aware freeze timestamp, before the recorded run start.
- `source_revision`: exact revision label, including `+dirty` where applicable.
- `prompt_hash`: the application's full SHA256 prompt-source hash.
- `ticker` and `analysis_date`: the **analysis controls** every formal attempt used. The live runner validates these (and the fixed configuration) against the selected run **before any graph call**, spending zero calls on a mismatch, and the scorer binds expected identity to them. A supported declared date (e.g. `2025-12-19`) is usable and is never inferred from a (possibly corrupt) manifest.
- `members`: exactly ten objects with `case_id`, `trial` (`1` or `2`) and unique preallocated safe `run_id`. Each fixed case has one slot per trial.

A full cohort that is malformed, stale or unsupported is rejected before dispatch. Expected per-case portfolio facts and `portfolio_kind` are derived from the authoritative `cases.py`, not duplicated in the scorer, so the definitions cannot drift.

Retain the approval and cohort externally or in version control before execution; editable local timestamps alone cannot prove historical chronology. The application and capture harness record hashes, but that is not a digital signature or a substitute for review.

Set `GOV004_TRIAL=1` or `2` for approved formal replay. The harness reads the cohort, uses its run IDs and refuses to reuse a started slot. A diagnostic run leaves the trial unset. Store diagnostic evidence separately from formal evidence. Every recorded formal start remains in overall completion accounting; retries do not replace failed cohort slots. Completion is reported separately from semantic scores on eligible completed reports.

### Isolated evidence root and live provider selection

- **Isolation.** Both the scorer and the live replay honour `GOV004_EVIDENCE_DIR`. Point it at a fresh directory to replay without mixing old private pilot files; the replay writes `gov004_<stamp>.json`, its run tree, and the start ledger under that root, and `runner.outcome_to_dict(outcome, evidence_root=...)` records relative paths and hashes against it (an artifact outside the root is rejected). Example:

  ```sh
  GOV004_LIVE=1 GOV004_EVIDENCE_DIR=/tmp/gov004-live GOV004_TRIAL=1 \
    GOV004_TICKER=AAPL GOV004_DATE=2026-01-09 \
    .venv/bin/python -m pytest tests/member_c_verification/live/test_gov004_live.py -p no:cacheprovider -q -s
  ```

- **Live provider override.** A narrowly-scoped `GOV004_LLM_PROVIDER` override is applied *after* the saved `.env` settings are restored. It changes the **provider only**: it sets the base provider and aligns both tier providers to it (so the effective adapter for every tier is the requested provider), and it does **not** rewrite the model IDs. Saved or caller-selected model IDs still reach the strict fixed-config validation, so a wrong model ID causes **zero** dispatch rather than being silently converted to a valid one. When unset, the saved settings are used unchanged. It never copies or migrates credentials (the caller supplies the provider's normal credential env var privately) and never lowers thresholds. Example: `GOV004_LLM_PROVIDER=deepseek` selects the `deepseek` provider/adapter for the base and both tiers; the model IDs from the saved/selected config (e.g. `CS5351/DeepSeek-V4-Flash`) are still validated against the fixed formal config.

- **Truthful preflight.** Before any graph call the live runner validates the *entire* frozen cohort: schema 2 controls, safe run IDs, an ISO analysis date, a timezone-aware non-future `frozen_at_utc`, a revision/prompt-hash of the right shape, full slot coverage, the selected ticker/date and the fixed config. It also compares the declared `source_revision`/`prompt_hash` with the actual current source inventory (injectable for offline tests). A missing/malformed/stale/mismatching cohort spends **zero** calls and records no started run. Diagnostics never echo field values. The approval text is attributable caller authorization, separate from C's independent acceptance.

- **Safe backend identifier.** The recorded `backend_host` is the URL's hostname only (via a real parser): `user:password@`, port, path and query are never persisted, and a malformed URL records `None`.

- **Tier-provider correspondence.** The fixed formal provider must be the *effective* provider of **both** model tiers, not only the base `llm_provider`. The scorer requires `(deep_think_provider or llm_provider)` and `(quick_think_provider or llm_provider)` to equal the fixed provider in the recorded evidence config, the manifest `effective_config`, and a pending start's captured binding; the live preflight applies the same rule before dispatch. A missing/`None` tier field means "inherit the base provider" (legacy synthetic fixtures and normal configs stay valid); an explicit conflicting tier provider (e.g. `llm_provider=deepseek` but `quick_think_provider=openai`) fails even with recomputed hashes and full scores.

- **Live credentials are not saturated by test dummies.** The shared pytest fixture `tests/conftest.py::_dummy_api_keys` normally substitutes `"placeholder"` for any missing provider key so offline tests never reach a provider. For an explicitly opted-in live run (`live` marker **and** `GOV004_LIVE=1`) it now skips that injection: the caller's real credentials are used unchanged, missing keys stay absent (so unconfigured auxiliary providers get no fake key), and the Redactor never inventories `"placeholder"` (which previously turned benign sentences like "the feed returned a placeholder" into "[REDACTED]"). All ordinary offline/integration/non-opted tests keep the placeholder behavior, and the upstream network block/blank-setting isolation are unchanged. This is a test-harness guard, not a production-code change.

- **Fundamentals period/source consistency (L2, prompt mitigation).** A live deepseek C1 report (`20261121T095453Z-2a60842e`) opened its Fundamentals section claiming a "record fiscal Q1 (December 2025 quarter)" yet later said no December-2025 income statement was present. The Fundamentals Analyst prompt now instructs: ground each period in the tool-reported period end (calendar date), fiscal label and filing date; never derive a calendar year by copying a fiscal-year label; apply the analysis-date cutoff (a filing dated after the analysis date is not yet known); do not claim a missing/unfiled period reported or invent an earnings-release date; and keep the opening summary, table and caveats consistent about which periods are available, stating stale/missing/unknown facts explicitly. A follow-up L2-03 observation added that **excluded post-cutoff filing metadata, including its future filing date, cannot establish an earnings schedule or event timing** — only independently supplied evidence available on or before the cutoff can support an upcoming report's date (the excluded row/date may be quoted solely to explain exclusion, never to forecast timing). No hardcoded figures/years, no data-source substitution, no new tools/checker/rating, output keys and delegation unchanged. This is a prompt mitigation verified by captured-path tests; live compliance is decided by contextual inspection (L2-02/03), not by the deterministic Q1–Q4 check.

Set `GOV004_TRIAL=1` or `2` for approved formal replay. The harness reads the cohort, uses its run IDs and refuses to reuse a started slot. A diagnostic run leaves the trial unset. Store diagnostic evidence separately from formal evidence.

## Record evidence and human scores

The capture harness records portable relative report and manifest paths and their SHA256 digests. Manifests must match the run identity, result, source revision, fixed configuration, prompt hash and report path. Each report must contain the corresponding trusted Run ID header. A completed record needs all of this evidence; incomplete/error attempts remain counted even without completed artifacts.

### Case/provenance/report correspondence (R2)

A complete set of score cells is not sufficient. The scorer now validates each completed attempt against the trusted frozen case definition, not against the attempt's own (possibly defective) record:

- **Result conditions.** `COMPLETED` requires a valid rating, `stop_reason=null`, and `PASSED`/`NEEDS_REVIEW`; `REVIEW` requires `NEEDS_REVIEW`; `PASSED` carries no findings and `NEEDS_REVIEW` carries at least one valid Q1–Q4/`CHECK_ERROR` finding. A non-completed attempt carries no rating, a known stop reason, `NOT_RUN` and no findings.
- **Case identity and analysis controls.** `ticker`, `analysis_date`, `input_mode`, `basename`, `fingerprint_sha256`, `portfolio_as_of` and `as_of_basis` must equal the values derived from the declared fixed case (from the authoritative `cases.py` via `expected_case_identity`, bound to the cohort controls). Expected input facts are never inferred from the manifest itself, so a held-target file substituted for the explicit-empty case, a `NO_PORTFOLIO` label on an explicit-empty case, or a wrong `portfolio_kind` fails even with recomputed hashes. Required manifest keys must be **present** even when their value is legitimately null (missing ≠ explicit null), and the manifest `schema_version` must be the supported application version.
- **Authoritative report envelope.** The contiguous leading header block of `complete_report.md` (title, then the `- Key: value` lines, then `Findings:`) must agree with the manifest/record for run ID, ticker, analysis date, input mode, portfolio file, fingerprint, as-of/basis, run outcome, stop reason, final rating and output check. A missing, duplicate or conflicting authoritative field fails. Quoted (`>`), fenced (```) or later narrative that references a status is not treated as the authoritative block; a **bare, unquoted** authoritative-looking `- Key: value` line outside the header is rejected by a line/fence/quote-aware rule (not a global substring search).
- **Durability mirror equality.** A per-attempt `gov004_attempt_<run_id>.json` mirror may repeat a run already counted from a batch file **only** when it is identical after parsing (full-row equality). A conflicting copy fails regardless of filename ordering; two genuinely independent attempts sharing a run ID still fail.

Legacy formal evidence that lacks these fields is rejected rather than having the missing fields fabricated. This binds artifacts to the declared case; it does not cryptographically prove the honesty of a human score.

### Durable per-attempt accounting (R3)

`tests/member_c_verification/live/replay_store.py` makes every attempt durable on its own. Before dispatch the whole selected cohort is preflighted (unique run IDs, one slot per case/trial, none already started); nothing runs on failure, and the live runner validates the frozen cohort controls/config first. Each slot is claimed (`STARTED`) in the versioned `gov004_starts.json` (schema 2) *before* `run_case` is called, carrying the pre-dispatch `model_config` and `controls` (ticker, analysis date, source revision, prompt hash), and its outcome is written to its own `gov004_attempt_<run_id>.json` (validated and confined to the evidence root), so two starts in one second cannot overwrite and a later failure cannot discard an earlier attempt. Only an **absent** ledger means “no evidence”: an empty/malformed/duplicate/unsafe ledger fails closed. `KeyboardInterrupt`/`SystemExit`, and an application-reported `INTERRUPTED` result, stop further dispatch after the current start/outcome is preserved.

A retained pending start is an **eligible**, noncompleted denominator entry only when its pre-dispatch binding is trusted and complete: a known fixed configuration and captured controls that match the frozen cohort (ticker, analysis date, and — where declared — source revision and prompt hash). A missing, unknown or mismatching binding is **ineligible yet still counted in the denominator**; it is never a completed quality sample, and model settings are never fabricated from a result. Acceptance requires **every** started attempt (completed or pending) to be eligible, so a wrongly-configured pending start blocks a PASS even when all completed rows are excellent (e.g. 10 completed + 1 defective pending → 10/11 ≥ 90% but FAIL). A genuine control-bound 9 completed + 1 pending (9/10 = 90%, ≥9 completed, ≥1 completed per case) passes at the unchanged thresholds. Reusing a started slot is refused. Diagnostics/pilot populations remain separate from the formal cohort.

The score JSON contains a real `reviewer` and an `answers` list. Each applicable answer has `case_id`, `run_id`, `trial`, `item`, integer `score` (0 or 1), and a nonempty `citation` found in that run's report. Record rationale and disagreements alongside it. Do not submit N/A rows for inapplicable cells. The scorer derives applicability; missing, duplicate, unknown, incorrectly N/A or unrelated cells fail. Challenge markers and actual exposure must be retained and independently checked. Q1–Q4 NEEDS_REVIEW and human semantic judgments remain separate.

## Package and verify from a fresh checkout

After sanitization and human review, run from the repository root:

```sh
python tests/member_c_verification/live/package_gov004.py tests/member_c_verification/live/evidence /tmp/gov004-package --scores tests/member_c_verification/live/evidence/gov004_scores.json
GOV004_EVIDENCE_DIR=/tmp/gov004-package python tests/member_c_verification/live/score_gov004.py /tmp/gov004-package/gov004_scores.json
```

The destination must not already exist. The exporter copies only referenced reports/manifests and the cohort, evidence and scoring files, rewrites paths (including for the versioned `gov004_starts.json` start ledger and per-attempt `gov004_attempt_*.json` files), and emits `integrity.json`. Unresolved starts and all denominators survive the export. It refuses detected credential text rather than silently changing scored evidence. Review other sensitive content manually; automatic scanning cannot certify privacy. Move the package to a second path or fresh checkout (a different working directory) and repeat scoring; only relative artifact paths may be relied on. PASS=0, FAIL=1, PENDING=2. PENDING is never acceptance. Compare integrity hashes after transfer; retain the archive in an agreed durable location.

The tracked ignore rules exclude private generated live evidence. Deliberate sanitized packages may be retained outside that tree after owner review. This workflow is not recovery of missing historical evidence and does not itself grant formal approval.
