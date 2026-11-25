"""Run Bandit and require complete application coverage with no medium/high findings."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEWED_NOSEC = {
    "tradingagents/dataflows/vendors/reddit.py",
    "src/tradingagents/dataflows/vendors/reddit.py",
    "tradingagents/dataflows/vendors/stocktwits.py",
    "src/tradingagents/dataflows/vendors/stocktwits.py",
}


def nosec_findings(paths: set[Path], root: Path) -> list[str]:
    """Only the two reviewed, host-guarded urlopen lines may suppress B310."""
    errors = []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        with tokenize.open(path) as handle:
            lines = handle.readlines()
        comments = [token for token in tokenize.generate_tokens(iter(lines).__next__)
                    if token.type == tokenize.COMMENT and "nosec" in token.string.lower()]
        for token in comments:
            line = lines[token.start[0] - 1].strip()
            if (relative not in REVIEWED_NOSEC or token.string != "# nosec B310"
                    or line != "with urlopen(req, timeout=timeout) as resp:  # nosec B310"
                    or len(comments) != 1):
                errors.append(f"unreviewed scanner suppression in {relative}:{token.start[0]}")
    return errors


def validate_report(report: dict, expected: set[Path]) -> list[str]:
    errors = []
    if not isinstance(report.get("errors"), list) or report["errors"]:
        errors.append("scanner errors or missing error inventory")
    results = report.get("results")
    if not isinstance(results, list):
        errors.append("missing findings list")
    elif results:
        errors.append(f"{len(results)} medium/high security finding(s)")
    metrics = report.get("metrics")
    if not isinstance(metrics, dict):
        errors.append("missing coverage metrics")
    else:
        scanned = {Path(name).resolve() for name in metrics if name != "_totals"}
        if not expected or scanned != expected:
            errors.append("scanner coverage does not match application Python files")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".local-review/bandit.json")
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.unlink(missing_ok=True)  # never reuse a previous successful report
    expected = {p.resolve() for name in ("src/tradingagents", "src/cli", "src/demo") for p in (ROOT / name).rglob("*.py")}
    try:
        suppressions = nosec_findings(expected, ROOT)
        if suppressions:
            for error in suppressions:
                print(f"FAIL SECURITY_SCAN: {error}")
            return 1
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", "src/tradingagents", "src/cli", "src/demo", "-ll", "-f", "json", "-o", str(args.output)],
            cwd=ROOT, timeout=120, check=False,
        )
        report = json.loads(args.output.read_text())
        errors = validate_report(report, expected)
        if result.returncode != 0:
            errors.append(f"scanner returned {result.returncode}")
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired) as exc:
        errors = [f"scanner did not complete ({type(exc).__name__})"]
    for error in errors:
        print(f"FAIL SECURITY_SCAN: {error}")
    if not errors:
        print(f"PASS security scan: {len(expected)} Python files; zero medium/high findings")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
