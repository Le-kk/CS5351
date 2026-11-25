# Bug diary — closeout dispositions

Date: 25 November 2026

## Closeout dispositions

| Entry | Classification | Final recorded disposition | Evidence |
|---|---|---|---|
| BD-001 | Test isolation | Repaired; 6 Bedrock tests pass under ordinary and conflicting AWS environments | ER-04/06; final full regression ER-07 |
| BD-002 | Verification boundary | Closed by targeting the as-of guard in resolve_run_context | Original reproduction below |
| BD-003 | Test expectation | Closed by testing provider-specific classification and preserving bare ConnectionError behavior | Original reproduction below |
| BD-004 | Result contract | Repaired in the recorded focused batch | ER-01 |
| BD-005 | Population accounting | Repaired in the recorded focused batch | ER-01 |
| BD-006 | Report layout | Repaired in the recorded focused batch | ER-01 |

[Evidence index](verification/evidence-index.md) · [Review memo](review-memo.md) · [Remaining engineering work](debt-register.md)

## BD-001 — Final isolation repair

**Symptom.** Bedrock construction used ambient credential/proxy configuration. An initial repair still allowed a conflicting AWS region to affect the bearer-token test.

**Root cause.** Constructor setup and test execution shared the process AWS environment and cached SDK state.

**Repair.** The module fixture removes ambient AWS overrides, uses synthetic credentials and empty configuration files, and disables metadata discovery. The real-construction case resets the SDK session and blocks HTTP sends.

**Verification.** ER-05 retains the initial 1-failed/5-passed probe. ER-04 and ER-06 each record 6 passes; ER-07 records the final full regression.

**Invariant gap addressed.** Offline constructor tests require controlled provider configuration and network isolation.

## BD-004 — Result and finding consistency

**Symptom.** The registry tests exposed missing BUDGET vocabulary, rejected corrected-only PASSED envelopes and accepted REVIEW/PASSED combinations.

**Reproduction.** Run the focused command in the [evidence index](verification/evidence-index.md#recorded-commands), including the output-check, failure and registry-gap modules.

**Root cause.** Result vocabulary and validation did not represent the required combinations consistently.

**Fix.** The result contract represents BUDGET, retains corrected findings and rejects invalid verdict/finding combinations.

**Verification.** The post-repair focused batch records 237 passes. [Repair regressions](../tests/member_c_verification/test_registry_result_repairs.py) cover valid corrected findings, mixed blocking findings and invalid combinations.

**Invariant gap addressed.** Public result fields must agree with deterministic check authority.

## BD-005 — Cases and attempts in population accounting

**Symptom.** The distinct-case probe failed, and the summary did not expose the required case identity.

**Reproduction.** Run test_case_identity_is_not_attempt_identity in the [population module](../tests/member_c_verification/offline/test_nfr006_population.py).

**Root cause.** Attempt identity and case identity were not represented separately in the observable population summary.

**Fix.** Explicit case identity drives distinct-case counts; unresolved starts remain in the attempt denominator.

**Verification.** ER-01 includes the repaired population tests and developer regressions for missing case identity and unresolved attempts.

**Invariant gap addressed.** Completion accounting must retain every started attempt while counting distinct cases separately.

## BD-006 — Leading disclaimer placement

**Symptom.** Twenty report fixtures failed the required leading-disclaimer layout.

**Reproduction.** Run test_sec003_rendered_report_starts_with_disclaimer in the [registry-gap module](../tests/member_c_verification/offline/test_registry_gaps.py).

**Root cause.** The rendered report placed its title and metadata before the disclaimer.

**Fix.** The report layout places the disclaimer before the title and trusted metadata.

**Verification.** ER-01 includes the repaired disclaimer fixtures and the HTML notice-order regression.

**Invariant gap addressed.** Report presentation must preserve the required disclosure ordering.

## Historical bug records

<details>
<summary>Earlier reproductions and investigation records</summary>

> Latest results: Linux rerun below reports 1882 passed / 26 failed; earlier Windows counts remain historical.

# Bug Diary (Member C)

Significant defects and verification-relevant discrepancies: symptom,
reproduction, classification, root cause, fix/status, and invariant gap. Only
entries supported by observed evidence are listed; nothing is inferred.

---

## BD-001 — Bedrock provider test fails under a stale global HTTP proxy

- **Symptom:** `tests/test_bedrock_provider.py::test_construction_when_extra_installed`
  fails in the offline baseline (`1 failed`).
- **Reproduction:**
  `.venv/bin/python -m pytest "tests/test_bedrock_provider.py::test_construction_when_extra_installed" -p no:cacheprovider`
  → exit 1, `ValidationError … Failed to connect to proxy URL: "http://127.0.0.1:7890"`.
  Re-run with `env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY …`
  → exit 0, 1 passed.
- **Classification:** environment / test-isolation (not an application regression).
- **Root cause:** `langchain_aws` is installed, so the test actually constructs a
  Bedrock client, which attempts credential/endpoint resolution through the
  ambient `http(s)_proxy`. No local proxy is listening.
- **Fix / status:** none applied (tests must not be changed during baseline).
  Recommended: run with proxy vars unset, or skip when a proxy is set. **Open** —
  needs A/E to record as a known exception for GOV-003.
- **Invariant gap:** none in the `SEL-TA-*` design; it is an upstream test's
  dependence on ambient env.

---

## BD-002 — As-of guard located in `resolve_run_context`, not the CLI entry

- **Symptom (found while writing TC-FR002-c):** a naive test at `cli/main.py`
  expected zero-run for `--portfolio` without `--portfolio-as-of`, but `run_analysis`
  was invoked (as-of `None` forwarded in `flags`).
- **Reproduction:** invoke the CLI with `--portfolio PATH` (no `--portfolio-as-of`)
  and observe that `cli/main.py` does not block; the typed `AS_OF_MISMATCH` is
  raised later by `cli/input_ui.resolve_run_context`.
- **Classification:** verification-boundary discrepancy (documentation/contract
  placement), **not** an application defect — enforcement exists in the designed
  guard.
- **Root cause:** contract §4 assigns the as-of rule to the input/consent service;
  the CLI entry only pre-checks the *both-flags* and *as-of-without-portfolio*
  combinations.
- **Fix / status:** test retargeted to `resolve_run_context` (TC-FR002-c now
  asserts `FLAG_CONFLICT` and `AS_OF_MISMATCH`). Test-plan change logged. **Closed.**
- **Invariant gap:** none; INV-09 is upheld by the shared guard.

---

## BD-003 — Bare `ConnectionError` is INTERNAL_ERROR, not MODEL_FAILURE

- **Symptom (found while writing TC-NFR001-d):** expectation that a raised
  `ConnectionError` maps to `MODEL_FAILURE` failed; code returns `INTERNAL_ERROR`.
- **Reproduction:**
  `classify_exception(ConnectionError("c"))` → `"INTERNAL_ERROR"`.
- **Classification:** test-expectation error (design is intentional).
- **Root cause:** `runapi/finalize.classify_exception` classifies by exception
  name/module; bare built-in connection errors are not provider-tagged, so they
  fall through to `INTERNAL_ERROR`. Real provider failures are `langchain`/`openai`/
  `anthropic`/`google` module exceptions (mapped to `MODEL_FAILURE`).
- **Fix / status:** test corrected to use a provider-module exception and
  `TimeoutError` for MODEL_FAILURE; added TC-NFR001-d2 pinning
  `ConnectionError → INTERNAL_ERROR`. **Closed** (no code change needed).
- **Invariant gap:** none; documents the intended classification boundary.

## 2026-11-25 investigation addendum (preserves original entries)

BD-001 reproduced with ambient proxy/credential discovery. A subprocess-only synthetic credential and disabled-metadata probe passes without a real AWS call. Do not follow the historical suggestion to skip when proxy is set: retain assertions and repair offline fixture isolation through E/D ownership. Full root-cause reconciliation, all 37 additional node IDs, owner dependencies and acceptance criteria: [classified handoff](verification/registry-test-update-2026-11-25.md#failure-investigation-and-owner-handoff--2026-11-25). No exemption or acceptance granted.

## Linux registry verification rerun — 2026-11-25

This dated addendum supersedes the earlier Windows-only missing-evidence statements for H6/H8/H10, without changing their historical results. Tested local main `14b06a57e3e779435614d066dfd6ab94510b0d2b` plus the pre-existing dirty C tests/documents (including untracked `test_registry_gaps.py`); origin is `hedyliu-574/CS5351`, not the instructed team remote. No current team-main equivalence is claimed. Ubuntu-24.04 WSL, Python 3.12.3, declared editable `.[dev]` install succeeded. Registry remains schema 1.2.0, proposed_for_adoption, 36 active/3 withdrawn.

Commands use `.venv/bin/python` from the repository root:

- `-m pytest -q -p no:cacheprovider --tb=short tests/member_c_verification/offline tests/test_checkpoint_lifecycle.py tests/test_checkpoint_resume.py tests/member_b_remediation/test_r3_replay_durability.py tests/member_b_remediation/test_r2_r3_differential_pins.py tests/member_d_verification/test_requirement_schema_gate.py`: **202 passed, 25 failed**, no skips, 4.40 s. Raw local evidence: `.local-review/registry-linux-20261125.txt`. Pytest reports failure; the surrounding shell wrapper returned zero, so that wrapper status is not a passing verdict.
- `-m pytest -q -p no:cacheprovider --tb=short`: **1882 passed, 26 failed, 1 skipped, 1 deselected, 24 warnings, 100 subtests passed**, 16.83 s, exit 1. Raw local evidence: `.local-review/registry-linux-full-20261125.txt`. Skip is the opt-in live semantic replay; integration deselection remains in force.
- `scripts/ci/check_requirement_schema.py`: PASS, 36 requirements/3 withdrawn, zero errors/warnings. Ruff full repository PASS; mypy PASS (14 configured files); workflow permissions PASS (5 workflows); security scan PASS (105 application files, zero medium/high).

### Mapping and bug disposition

H1–H5 remain open with exactly the same 25 failing nodes: BUDGET vocabulary (1), corrected-only findings rejected (2), distinct-case population interface ambiguity (1), REVIEW/PASSED accepted (1), leading-disclaimer contract mismatch (20). Existing requirement-row coverage classifications remain unchanged; passing schema validation does not establish implementation or adoption. Owners and next acceptance evidence remain as in the classified handoff.

H6 replay locking, H7 schema-gate fixtures, H8 symlink isolation and H10 loopback authentication now execute successfully on Linux in the full run. This supplies the missing Linux evidence, not Windows portability or a Windows fixture repair. The remaining additional full-suite failure is H9 / BD-001: Bedrock construction still attempts ambient credential discovery and fails against the stale localhost proxy. No waiver, implementation fix or new defect category is claimed. E/D test-isolation follow-up remains open.

Only verification documentation was changed in this rerun; prior test edits are preserved. No live model replay, human semantic scoring, remote CI/branch-protection inspection, commit or publication occurred. Full registry acceptance remains blocked; prior historical records are retained.

Documentation check: default Linux git diff --check flags CRLF in pre-existing dirty files; the CR-at-EOL-aware check is recorded separately. No test line endings were changed.

</details>
