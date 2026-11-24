# Requirements schema merge gate

Requirement: `REQ-TA-GOV-004` (crosswalk `SEL-TA-GOV-002`). Fixed GitHub check: `requirements schema`.

Every PR and main push runs the independent job in `ci.yml`, including changes outside the registry. The job installs declared dev dependencies, invokes `python scripts/ci/check_requirement_schema.py`, then runs positive/negative acceptance probes. No model, API key or paid call is needed.

The entry point reuses Member A's `docs/req/validate.py`: registry/schema conformance and its existing cross-record rules both must pass. It requires the registry, JSON schema and validator files to exist, a zero validator exit code, and one completed summary with a nonempty registry and zero errors. Missing files, invalid YAML/JSON, schema errors, cross-record errors, crashes, timeouts and empty/no-op output produce a nonzero gate exit and one named blocking finding, followed by subordinate diagnostics. Existing warnings remain visible as counts and do not become errors.

Acceptance probes cover the real valid registry and the five required negatives: missing required top-level key, invalid priority, missing schema, invalid YAML and a validator that raises. Additional probes cover a schema-valid duplicate requirement ID, missing registry/validator, invalid JSON/schema definitions, duplicate YAML keys, empty output, a nonzero exit despite a zero-error summary, a zero-requirement summary and a hung validator. Fixtures are temporary copies; the actual registry is not weakened or rewritten.

Local reproduction after `pip install -e ".[dev]"`:

```sh
python -m pytest -q tests/member_d_verification/test_requirement_schema_gate.py
python scripts/ci/check_requirement_schema.py
```

Activation: first obtain a real successful `requirements schema` run, then add that exact check to main's required checks while retaining the existing four and strict up-to-date setting. Do not make the paused `test approval` check required as part of this change. Validate an intentionally invalid PR is blocked, then close the probe without merging. Repository protection is a GitHub setting, not something this workflow can enable itself.

This check establishes structural/cross-record validity, not semantic adequacy, product implementation, human adoption, or live-model quality. Adoption status and requirement text remain Member A's authority. The existing note in the registry describes the earlier pre-gate baseline; deployment evidence records subsequent implementation rather than rewriting historical observations.
