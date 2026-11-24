# Dependency reviews

The dependency gate compares direct dependency names in `pyproject.toml` and `requirements.txt` with the base revision. A pull request that adds a package name must add a line naming that package to this file in the same change.

Changing a version bound, or removing a package, does not need a new line. `pip check` failures and known vulnerabilities cannot be waived here.

## Reviews

- 2026-11-24 — PyYAML (dev): explicitly declares the existing registry validator's YAML parser for clean CI installs. Uses SafeLoader with the existing duplicate-key rejection. Implementation review: Codex for Member E; vulnerability results remain subject to the dependency gate.
- 2026-11-24 — jsonschema (dev): explicitly declares the existing Draft 2020-12 schema validator for CI and negative fixtures. Kept out of runtime dependencies; pip check and pip-audit remain required. Implementation review: Codex for Member E; no vulnerability waiver is granted.
