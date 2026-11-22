# Dependency reviews

The dependency gate compares direct dependency names in `pyproject.toml` and `requirements.txt` with the base revision. A pull request that adds a package name must add a line naming that package to this file in the same change.

Changing a version bound, or removing a package, does not need a new line. `pip check` failures and known vulnerabilities cannot be waived here.

## Reviews
