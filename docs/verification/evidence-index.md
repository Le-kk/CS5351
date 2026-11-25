# Verification evidence index

Date: 25 November 2026

## Source and environment

The recorded repair runs used local main 1bf6e17dd0ecdd5e5f38b157fafc4c632105a933 with the dirty result/report repairs and regression tests described in the [test plan](history/test-plan-2026-11-25.md#post-repair-verification--2026-11-25). Environment: Ubuntu 24.04 WSL, Python 3.12, project virtual environment.

The final Bedrock fixture is identified in the recorded run by SHA-256 3794f02e0a704d710941dc78c18fde3c1e917a9120ad6719ed9dbdf936aba6d2. The final delivery-source binding is tracked as DR-002.

## Retained run evidence

The summaries and hashes below were read from existing local logs during submission preparation.

| Record | Scope | Observed summary | Retained path | SHA-256 |
|---|---|---|---|---|
| ER-01 | Focused repair regression | 237 passed in 4.34s | .local-review/rerun-focused-20261125.txt | d9b7338df1114adc7999fc6ea2e2f797fe58d41ffed24a5cece819ddd291a83a |
| ER-02 | Post-repair full regression | 1 failed, 1917 passed, 1 skipped, 1 deselected, 24 warnings, 100 subtests passed in 16.78s | .local-review/rerun-full-20261125.txt | 8493e9812b174c6c29d7afb1df5eb09882d0526ec55037291d20c749aae1201f |
| ER-03 | Semantic mechanism self-check | 8 passed in 1.69s | .local-review/rerun-semantic-20261125.txt | 31daae2377f06a36beaff4ae504a8fac4ee40dacf77fe490cd00899d96a7d030 |
| ER-04 | Bedrock final control | 6 passed in 0.84s | .local-review/bedrock-isolation-focused-final.txt | 3203da9a6568ec5379469a9996e349706c94be424dac52aab20f1a055bba846a |
| ER-05 | Initial hostile-environment probe | 1 failed, 5 passed in 0.94s | .local-review/bedrock-isolation-conflicting-env.txt | d91bfbb649ff4dba51aab04c7214fca327a90f82d34b01882e33c14421c5f5e0 |
| ER-06 | Bedrock final hostile-environment probe | 6 passed in 0.75s | .local-review/bedrock-isolation-conflicting-env-final.txt | d3c75c9d953237d073631a24c7b34684b4025bdd95bd24aefe222c2a0e7964f3 |
| ER-07 | Final full regression | 1918 passed, 1 skipped, 1 deselected, 24 warnings, 100 subtests passed in 15.52s | .local-review/bedrock-isolation-full-final.txt | 03a0718c059d91801ae4beb4c42ad3b9923cbf527f190289c9a9064a4ff564f1 |

## Recorded commands

The recorded commands use .venv/bin/python from the repository root.

~~~sh
.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/member_c_verification/offline tests/member_c_verification/test_registry_result_repairs.py tests/test_checkpoint_lifecycle.py tests/test_checkpoint_resume.py tests/member_b_remediation/test_r3_replay_durability.py tests/member_b_remediation/test_r2_r3_differential_pins.py tests/member_d_verification/test_requirement_schema_gate.py
.venv/bin/python -m pytest -q -p no:cacheprovider tests/member_c_verification/live/test_harness_selfcheck.py tests/member_c_verification/live/test_score_gov004_exitcodes.py
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_bedrock_provider.py
.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short
~~~

ER-01 records the first command; ER-03 the second; ER-04/05/06 the third; ER-02/07 the fourth. ER-05/06 additionally set conflicting synthetic AWS profile, region, bearer-token and web-identity variables; the test plan records the probe context.

## Outcome and provenance records

| Record | Result and source |
|---|---|
| ER-01 | 237 passed; recorded exit 0 |
| ER-02 | 1917 passed, 1 failed; Bedrock discovery failure |
| ER-03 | 8 passed; recorded exit 0 |
| ER-04 / ER-06 | 6 passed each; recorded exit 0 |
| ER-05 | 1 failed, 5 passed; exposed region leakage before the final fixture |
| ER-07 | 1918 passed, 1 skipped, 1 deselected; recorded exit 0 |

The [verification session record](../../AI-log/Member-C/2026_11_25_verification_and_evidence_session.md) identify the authorized work and retained results. The repair regression module identifies its tests as developer regressions.

## Evidence for final packaging

E receives this index and the reviewed local logs in the sanitized submission package. Formal semantic evidence is listed separately in the [semantic status](semantic-evaluation.md) and [packaging contract](gov004-evidence-package.md). Earlier reports remain in the [history index](history/README.md).
