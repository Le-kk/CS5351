"""Stable checkout location for src layout and installed-package fallbacks."""
from pathlib import Path


def project_root() -> Path:
    package = Path(__file__).resolve().parent
    for parent in package.parents:
        if (parent / "pyproject.toml").is_file():
            return parent
    return package.parent
