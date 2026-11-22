#!/usr/bin/env python3
"""Dependency gate: install consistency, known vulnerabilities, new-package review.

Rules:
- ``pip check`` must pass. Nothing in the exception file can waive it.
- A pip-audit finding fails unless dependency-audit-exceptions.txt has a matching
  package, vulnerability id, unexpired UTC date, approver, and reason.
- No vulnerability entries is a pass only when pip-audit exited 0 and returned a
  non-empty dependency list in which every package was audited. A non-zero status
  without a vulnerability, an empty result, or a skipped package is a failure.
- Adding a direct dependency name fails unless dependency-reviews.md gains a
  line naming that package in the same change. Version changes and removals do not.
- This gate does not upgrade packages.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

EXCEPTIONS = "docs/code-governance/dependency-audit-exceptions.txt"
REVIEWS = "docs/code-governance/dependency-reviews.md"


@dataclass(frozen=True)
class ExceptionRule:
    package: str
    vuln_id: str
    expiry: date
    approver: str
    reason: str


@dataclass(frozen=True)
class Finding:
    package: str
    version: str
    vuln_id: str
    aliases: tuple[str, ...]
    fix_versions: tuple[str, ...]


def normalize_name(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def requirement_name(spec: str) -> str | None:
    body = spec.split(";", 1)[0].strip()
    if not body or body.startswith(("#", "-")) or body in {".", "-e ."}:
        return None
    if "@" in body:
        body = body.split("@", 1)[0].strip()
    for separator in ("[", " ", "=", "<", ">", "!", "~"):
        if separator in body:
            body = body.split(separator, 1)[0]
    name = normalize_name(body)
    if not name or not re.fullmatch(r"[a-z0-9][a-z0-9.-]*", name):
        raise ValueError(f"Cannot read dependency name from {spec!r}")
    return name


def names_from_requirements(text: str) -> set[str]:
    names: set[str] = set()
    for line in text.splitlines():
        name = requirement_name(line.strip())
        if name:
            names.add(name)
    return names


def names_from_pyproject(text: str) -> set[str]:
    if not text.strip():
        return set()
    data = tomllib.loads(text)
    project = data.get("project", {})
    specs = list(project.get("dependencies") or [])
    extras = project.get("optional-dependencies") or {}
    for group in extras.values():
        specs.extend(group)
    names: set[str] = set()
    for spec in specs:
        name = requirement_name(str(spec))
        if name:
            names.add(name)
    return names


def parse_exceptions(text: str, today: date) -> tuple[list[ExceptionRule], list[str]]:
    rules: list[ExceptionRule] = []
    errors: list[str] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = [field.strip() for field in line.split("|")]
        if len(fields) != 5 or any(not field for field in fields):
            errors.append(f"{EXCEPTIONS}:{line_number}: expected package | id | YYYY-MM-DD | approver | reason")
            continue
        package, vuln_id, expiry_text, approver, reason = fields
        try:
            expiry = date.fromisoformat(expiry_text)
        except ValueError:
            errors.append(f"{EXCEPTIONS}:{line_number}: expiry must be YYYY-MM-DD")
            continue
        if expiry < today:
            errors.append(f"{EXCEPTIONS}:{line_number}: exception for {vuln_id} expired on {expiry_text}")
            continue
        rules.append(ExceptionRule(normalize_name(package), vuln_id.casefold(), expiry, approver, reason))
    return rules, errors


def unwaived(findings: list[Finding], rules: list[ExceptionRule]) -> list[Finding]:
    open_findings: list[Finding] = []
    for finding in findings:
        identifiers = {finding.vuln_id.casefold(), *(alias.casefold() for alias in finding.aliases)}
        waived = any(rule.package == finding.package and rule.vuln_id in identifiers for rule in rules)
        if not waived:
            open_findings.append(finding)
    return open_findings


def missing_reviews(added: set[str], review_lines: list[str]) -> list[str]:
    missing: list[str] = []
    for name in sorted(added):
        pattern = re.compile(rf"(?<![A-Za-z0-9._-]){re.escape(name)}(?![A-Za-z0-9._-])", re.IGNORECASE)
        if not any(pattern.search(line) for line in review_lines):
            missing.append(name)
    return missing


def audit_result_errors(payload: object, returncode: int) -> list[str]:
    """Reject a result that did not actually audit the installed packages."""
    if not isinstance(payload, dict) or "dependencies" not in payload:
        return [f"pip-audit exited {returncode} and did not return a dependency list."]
    dependencies = payload["dependencies"]
    if not isinstance(dependencies, list):
        return ["pip-audit dependencies field is not a list."]
    if not dependencies:
        return ["pip-audit returned no dependencies, so this is not a completed audit."]
    errors: list[str] = []
    vulnerability_count = 0
    for index, dependency in enumerate(dependencies, start=1):
        if not isinstance(dependency, dict):
            errors.append(f"dependency {index} is not an object.")
            continue
        name = str(dependency.get("name") or "").strip()
        if not name:
            errors.append(f"dependency {index} has no package name.")
            continue
        skip_reason = dependency.get("skip_reason")
        if skip_reason:
            errors.append(f"{name} was not audited: {skip_reason}")
            continue
        vulns = dependency.get("vulns")
        version = dependency.get("version")
        if not isinstance(vulns, list) or not isinstance(version, str) or not version.strip():
            errors.append(f"{name} has no completed vulnerability result.")
            continue
        if any(not isinstance(vuln, dict) for vuln in vulns):
            errors.append(f"{name} has a vulnerability entry that is not an object.")
            continue
        vulnerability_count += len(vulns)
    if returncode != 0 and vulnerability_count == 0 and not errors:
        errors.append(f"pip-audit exited {returncode} without reporting a vulnerability.")
    return errors


def parse_audit(payload: dict) -> list[Finding]:
    findings: list[Finding] = []
    for dependency in payload["dependencies"]:
        if dependency.get("skip_reason"):
            continue
        package = normalize_name(str(dependency.get("name", "")))
        version = str(dependency.get("version", ""))
        for vuln in dependency.get("vulns") or []:
            findings.append(
                Finding(
                    package,
                    version,
                    str(vuln.get("id") or ""),
                    tuple(str(alias) for alias in vuln.get("aliases") or []),
                    tuple(str(fix) for fix in vuln.get("fix_versions") or []),
                )
            )
    return findings


def git_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in list(env):
        if key.startswith("GIT_"):
            env.pop(key)
    return env


def git_show(rev: str, path: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", "show", f"{rev}:{path}"],
        cwd=cwd,
        env=git_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def added_lines(left: str, right: str, path: str, cwd: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "-U0", left, right, "--", path],
        cwd=cwd,
        env=git_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "git diff failed"
        raise RuntimeError(message)
    lines: list[str] = []
    for line in result.stdout.splitlines():
        if line.startswith(("+++", "---", "@@")):
            continue
        if line.startswith("+"):
            lines.append(line[1:])
    return lines


def direct_names(pyproject: str, requirements: str) -> set[str]:
    return names_from_pyproject(pyproject) | names_from_requirements(requirements)


def blank_base(base: str) -> bool:
    return bool(base) and set(base) == {"0"}


def resolve_revs(args: argparse.Namespace) -> tuple[str, str] | None:
    event = os.environ.get("GATE_EVENT", "")
    base = args.base or os.environ.get("GATE_BASE", "")
    head = args.head or os.environ.get("GATE_HEAD", "")
    if not (args.base or args.head or event):
        return None
    if not base or not head:
        raise RuntimeError("Pass --base and --head, or set GATE_BASE and GATE_HEAD.")
    if blank_base(base):
        return None
    if event == "pull_request" or args.pull_request:
        merge_base = subprocess.run(
            ["git", "merge-base", base, head],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return merge_base, head
    return base, head


def review_new_dependencies(left: str, right: str, cwd: Path) -> list[str]:
    before = direct_names(git_show(left, "pyproject.toml", cwd), git_show(left, "requirements.txt", cwd))
    after = direct_names(git_show(right, "pyproject.toml", cwd), git_show(right, "requirements.txt", cwd))
    return missing_reviews(after - before, added_lines(left, right, REVIEWS, cwd))


def run_pip_check() -> int:
    result = subprocess.run([sys.executable, "-m", "pip", "check"], check=False)
    if result.returncode != 0:
        print("Dependency check failed: pip check reported an inconsistent installation.")
        print("This failure cannot be waived.")
    return result.returncode


def run_audit(today: date, cwd: Path) -> int:
    exception_path = cwd / EXCEPTIONS
    text = exception_path.read_text(encoding="utf-8") if exception_path.is_file() else ""
    rules, errors = parse_exceptions(text, today)
    if errors:
        print("Dependency check failed: vulnerability exception file is not usable.")
        print("\n".join(errors))
        return 1
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip_audit",
            "--format=json",
            "--progress-spinner=off",
            "--skip-editable",
        ],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in {0, 1}:
        print("Dependency check failed: pip-audit could not finish.")
        print(result.stderr.strip() or result.stdout.strip())
        return 1
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Dependency check failed: pip-audit did not return JSON.")
        print(result.stdout.strip() or result.stderr.strip())
        return 1
    result_errors = audit_result_errors(payload, result.returncode)
    if result_errors:
        print("Dependency check failed: pip-audit did not produce a completed vulnerability audit.")
        print("\n".join(result_errors))
        return 1
    open_findings = unwaived(parse_audit(payload), rules)
    if not open_findings:
        print("Known-vulnerability check passed.")
        return 0
    print("Dependency check failed: known vulnerabilities have no current exception.")
    for finding in open_findings:
        fixes = ", ".join(finding.fix_versions) if finding.fix_versions else "none listed"
        print(f"{finding.package} {finding.version} {finding.vuln_id} fix: {fixes}")
    print(f"Record a reviewed exception in {EXCEPTIONS}, or upgrade the package.")
    print("This gate does not upgrade dependencies.")
    return 1


def expect(condition: bool, label: str, failures: list[str]) -> None:
    print(("pass: " if condition else "fail: ") + label)
    if not condition:
        failures.append(label)


def self_test() -> int:
    failures: list[str] = []
    today = date(2026, 11, 22)
    rules, errors = parse_exceptions(
        "\n".join(
            [
                "# comment",
                "Requests | PYSEC-1 | 2026-12-31 | Ada | waiting for a fixed release",
                "bad line",
                "flask | PYSEC-2 | 2020-01-01 | Ada | expired",
            ]
        ),
        today,
    )
    expect(len(rules) == 1 and len(errors) == 2, "malformed and expired exceptions fail", failures)
    expect(
        bool(audit_result_errors({}, 1)),
        "non-zero pip-audit output {} is not a pass",
        failures,
    )
    expect(
        bool(audit_result_errors({"dependencies": []}, 0)),
        "an empty dependency list is not a pass",
        failures,
    )
    expect(
        bool(
            audit_result_errors(
                {"dependencies": [{"name": "flask", "skip_reason": "could not be audited"}]},
                0,
            )
        ),
        "a skipped package is not a pass",
        failures,
    )
    clean_audit = {"dependencies": [{"name": "flask", "version": "1.0", "vulns": []}], "fixes": []}
    expect(audit_result_errors(clean_audit, 0) == [], "a completed audit with no vulnerabilities passes", failures)
    expect(
        bool(audit_result_errors({"dependencies": [{"name": "flask", "version": None, "vulns": []}]}, 0)),
        "a null version is not a pass",
        failures,
    )
    expect(
        bool(audit_result_errors({"dependencies": [{"name": "flask", "version": "", "vulns": []}]}, 0)),
        "an empty version is not a pass",
        failures,
    )
    expect(
        bool(audit_result_errors({"dependencies": [{"name": "flask", "version": "  ", "vulns": []}]}, 0)),
        "a blank version is not a pass",
        failures,
    )
    listed_vulnerability = {
        "dependencies": [
            {"name": "flask", "version": "1.0", "vulns": [{"id": "PYSEC-1", "fix_versions": [], "aliases": []}]}
        ]
    }
    expect(
        audit_result_errors(listed_vulnerability, 1) == [],
        "a non-zero audit that lists vulnerabilities remains an audit result",
        failures,
    )
    findings = [
        Finding("requests", "2.0", "PYSEC-1", ("CVE-1",), ()),
        Finding("flask", "1.0", "PYSEC-9", (), ("2.0",)),
        Finding("other", "1.0", "PYSEC-1", (), ()),
    ]
    left = unwaived(findings, rules)
    expect(
        [item.package for item in left] == ["flask", "other"],
        "an exception waives only the named package and id",
        failures,
    )
    expect(not missing_reviews(set(), ["unused"]), "no new package needs a review", failures)
    expect(missing_reviews({"requests"}, ["reviewed flask"]) == ["requests"], "unreviewed package fails", failures)
    expect(missing_reviews({"requests"}, ["use requests here"]) == [], "review line naming the package passes", failures)
    before = names_from_pyproject('[project]\ndependencies = ["Pandas>=1"]\n')
    after = names_from_pyproject(
        '[project]\ndependencies = ["pandas>=3"]\n[project.optional-dependencies]\ndev = ["Ruff>=1"]\n'
    )
    expect(after - before == {"ruff"}, "a version change is not a new package; a new extra is", failures)
    expect(names_from_requirements("# comment\n.\n-e .\nrequests==2\n") == {"requests"}, "requirements.txt names are read", failures)

    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        env = git_env()

        def run(*args: str) -> None:
            subprocess.run(args, cwd=root, env=env, check=True, capture_output=True, text=True)

        run("git", "init", "-b", "main")
        run("git", "config", "user.email", "gate@example.com")
        run("git", "config", "user.name", "gate")
        (root / "pyproject.toml").write_text('[project]\ndependencies = ["pandas>=1"]\n', encoding="utf-8")
        (root / "requirements.txt").write_text(".\n", encoding="utf-8")
        reviews = root / REVIEWS
        reviews.parent.mkdir(parents=True)
        reviews.write_text("# Dependency reviews\n", encoding="utf-8")
        run("git", "add", ".")
        run("git", "commit", "-m", "base")
        base = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, env=env, check=True, capture_output=True, text=True
        ).stdout.strip()
        (root / "pyproject.toml").write_text(
            '[project]\ndependencies = ["pandas>=1", "requests>=2"]\n', encoding="utf-8"
        )
        run("git", "add", ".")
        run("git", "commit", "-m", "add requests")
        added = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, env=env, check=True, capture_output=True, text=True
        ).stdout.strip()
        expect(review_new_dependencies(base, added, root) == ["requests"], "git diff without a review fails", failures)
        reviews.write_text("# Dependency reviews\nrequests | HTTP client\n", encoding="utf-8")
        run("git", "add", ".")
        run("git", "commit", "-m", "review requests")
        reviewed = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, env=env, check=True, capture_output=True, text=True
        ).stdout.strip()
        expect(review_new_dependencies(base, reviewed, root) == [], "git diff with a review passes", failures)

    if failures:
        print(f"{len(failures)} dependency self-test(s) failed.")
        return 1
    print("Dependency self-test passed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the dependency gate.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--pull-request", action="store_true")
    parser.add_argument("--skip-install-audit", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()

    status = 0
    if not args.skip_install_audit:
        if run_pip_check() != 0:
            status = 1
        else:
            root = Path(
                subprocess.run(
                    ["git", "rev-parse", "--show-toplevel"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            )
            if run_audit(datetime.now(UTC).date(), root) != 0:
                status = 1
    try:
        revs = resolve_revs(args)
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Dependency check failed: {exc}")
        return 1
    if revs is None and (args.base or args.head or os.environ.get("GATE_EVENT")):
        print("New-dependency review skipped: this push has no previous commit.")
        return status
    if revs is None:
        print("New-dependency review skipped: pass --base and --head to check it.")
        return status
    root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    try:
        missing = review_new_dependencies(revs[0], revs[1], root)
    except (RuntimeError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"Dependency check failed: {exc}")
        return 1
    if missing:
        print("Dependency check failed: new direct dependencies have no review line.")
        print(", ".join(missing))
        print(f"Add a line containing each package name to {REVIEWS} in this change.")
        return 1
    print("New-dependency review passed.")
    return status


if __name__ == "__main__":
    sys.exit(main())
