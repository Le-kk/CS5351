"""Fail-closed CI entry point for A's registry/schema and cross-record validator."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUMMARY = re.compile(r"(\d+) requirements; (\d+) withdrawn; (\d+) error\(s\), (\d+) warning\(s\)")


def failure(code: str, detail: str, diagnostics: str = "") -> int:
    # Exactly one named blocking finding, with optional subordinate diagnostics.
    print(f"FAIL {code}: {detail}")
    if diagnostics.strip():
        print("Validator diagnostics:")
        for line in diagnostics.strip().splitlines():
            print(f"  {line}")
    return 1


def check(registry: Path, schema: Path, validator: Path, timeout: float = 30) -> int:
    for name, path in (("REGISTRY", registry), ("SCHEMA", schema), ("VALIDATOR", validator)):
        if not path.is_file():
            return failure(f"REQ_{name}_MISSING", f"Required file not found: {path}")
    try:
        result = subprocess.run(
            [sys.executable, str(validator), "--registry", str(registry), "--schema", str(schema)],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return failure("REQ_VALIDATOR_TIMEOUT", "Registry validator did not finish within its timeout.")
    except (OSError, UnicodeError) as exc:
        return failure("REQ_VALIDATOR_ERROR", f"Could not execute/read validator: {type(exc).__name__}")
    diagnostics = result.stdout + result.stderr
    if result.returncode != 0:
        code = "REQ_VALIDATOR_ERROR" if "Traceback (most recent call last)" in diagnostics else "REQ_VALIDATION_FAILED"
        return failure(code, f"Registry/schema or cross-record validation failed (exit {result.returncode}).", diagnostics)
    summaries = [SUMMARY.fullmatch(line.strip()) for line in result.stdout.splitlines()]
    summaries = [match for match in summaries if match]
    if len(summaries) != 1:
        return failure("REQ_VALIDATOR_INCOMPLETE", "Expected exactly one completed validation summary.", diagnostics)
    count, withdrawn, errors, warnings = map(int, summaries[0].groups())
    if count < 1 or errors != 0 or any(line.lstrip().startswith("ERROR ") for line in diagnostics.splitlines()):
        return failure("REQ_VALIDATION_FAILED", "Validator did not establish a nonempty registry with zero errors.", diagnostics)
    print(f"PASS requirements schema: {count} requirements; {withdrawn} withdrawn; 0 errors; {warnings} warnings")
    print("Schema and cross-record checks passed; no semantic, implementation or adoption approval is implied.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=ROOT / "docs/req/requirements.yaml")
    parser.add_argument("--schema", type=Path, default=ROOT / "docs/req/req-schema.json")
    parser.add_argument("--validator", type=Path, default=ROOT / "docs/req/validate.py")
    args = parser.parse_args()
    return check(args.registry.resolve(), args.schema.resolve(), args.validator.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
