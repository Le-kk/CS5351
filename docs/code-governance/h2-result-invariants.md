# H2 — result structure correction

Date: 2026-11-25. Scope: the two result-model defects in H2, not full R5 implementation.

`CheckResult` and completed `RunResult` now share one verdict validator:

- No findings, or only `CORRECTED` findings: `PASSED`.
- Any `BLOCKING` finding, including a mixture with corrections: `NEEDS_REVIEW`.
- `NEEDS_REVIEW` without a blocking finding is rejected.
- `NOT_RUN` has no findings; incomplete runs remain `NOT_RUN` with no rating.
- A `REVIEW` rating still requires `NEEDS_REVIEW` (H4).
- Unknown finding severities and output-check states fail closed.

Finding type annotations now include the contract's R1–R8 vocabulary and
`CORRECTED` severity. This does not implement those rules. Existing finding
serialization retains every finding and its severity; no public result fields
are added or removed. Existing Q1–Q4 producers are unchanged.

## Compatibility and remaining work

This is a preparatory data-model change. It does not authorize callers to label
an uncorrected report as corrected. No automatic sentiment-confidence correction,
safe correction projection, normalization/re-render pipeline, or rule-version-2
publisher is introduced. These must be implemented and verified together before
publishing corrected findings as a production checker result, as required by
interface-contracts sections 14.3, 14.5 and 16.7.

The current legacy/budget rule-version-1 scorer intentionally still rejects
corrected records and unsupported rule versions. It has not been weakened to
accept a partially implemented rule-version-2 artifact. Structural acceptance
in these Python data models is not semantic acceptance or artifact compatibility.

H1 and H4 local changes form the test baseline and are preserved. Historical H1
hashes remain a record of that earlier snapshot, not hashes of this later source.
The new tests are developer regression probes, not independent member-C sign-off.
