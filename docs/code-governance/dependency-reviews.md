# Dependency reviews

The dependency gate compares direct dependency names in `pyproject.toml` and `requirements.txt` with the base revision. A pull request that adds a package name must add a line naming that package to this file in the same change.

Changing a version bound, or removing a package, does not need a new line. `pip check` failures and known vulnerabilities cannot be waived here.

## Reviews

- 2026-11-25 — mypy (dev, pinned 1.20.2): reproducible static checks of shared API/portfolio/output contracts. Implementation review by Codex for Member E; third-party imports remain partially typed and are not claimed as fully verified. Subject to the dependency audit.
- 2026-11-25 — bandit (dev): security AST scan of application Python, with explicit medium/high failure policy, coverage verification and negative fixtures. Implementation review by Codex for Member E; no broad scanner waiver.
- 2026-11-25 — defusedxml (runtime): replaces ordinary ElementTree parsing of untrusted Reddit RSS to reject entity-expansion payloads, while preserving graceful unavailable-data behavior. Implementation review by Codex for Member E; covered by a malicious XML fixture and existing RSS tests. Subject to the dependency audit.

- 2026-11-24 — PyYAML (dev): explicitly declares the existing registry validator's YAML parser for clean CI installs. Uses SafeLoader with the existing duplicate-key rejection. Implementation review: Codex for Member E; vulnerability results remain subject to the dependency gate.
- 2026-11-24 — jsonschema (dev): explicitly declares the existing Draft 2020-12 schema validator for CI and negative fixtures. Kept out of runtime dependencies; pip check and pip-audit remain required. Implementation review: Codex for Member E; no vulnerability waiver is granted.

## 2026-11-25 — imported presentation frontend

The existing exported React frontend is now versioned under src/frontend with npm package-lock.json as its only active lock. No new Python runtime dependency was introduced. Removed unused zod after a concrete high-severity audit finding; updated compatible dependencies and then Vite to 8.3.8 with @vitejs/plugin-react 6.3.0 because the old Vite series remained vulnerable. Local production build passed. npm audit reports zero high/critical and five moderate findings at inspection; CI blocks high/critical and does not claim a vulnerability-free frontend. Runtime API remains same-origin, credentials server-side, development host loopback. Node 24 is used in CI. Further dependency simplification/moderate findings remain debt.
