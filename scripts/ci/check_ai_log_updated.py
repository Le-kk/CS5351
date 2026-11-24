#!/usr/bin/env python3
"""Fail when a critical path changes without an AI-log update.

Critical paths are the listed directories and files. An add, modification,
deletion, or move out of those paths must also add or modify a file under
AI-log/ in the same change. Deleting a log, or touching only .DS_Store, does
not count. Log format and contents are not read. Ordinary docs, images, and
existing run results do not require an update.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

CRITICAL_PREFIXES = (
    "tradingagents/",
    "cli/",
    "tests/",
    "prompts/",
    "scripts/",
    ".github/workflows/",
)
CRITICAL_FILES = frozenset(
    {
        "main.py",
        "pyproject.toml",
        "requirements.txt",
        "AGENTS.md",
        ".opencode/permissions.jsonc",
        "docs/code-governance/dependency-audit-exceptions.txt",
        "docs/code-governance/dependency-reviews.md",
        "docs/code-governance/public-api-contract.json",
    }
)
LOG_PREFIX = "AI-log/"


def is_critical(path: str) -> bool:
    relative = path.removeprefix("./")
    if relative in CRITICAL_FILES:
        return True
    return any(relative.startswith(prefix) for prefix in CRITICAL_PREFIXES)


def counts_as_log_update(status: str, path: str) -> bool:
    relative = path.removeprefix("./")
    if not relative.startswith(LOG_PREFIX) or relative.endswith(".DS_Store"):
        return False
    return status[:1] in {"A", "M", "R", "C", "T"}


def decision(rows: list[tuple[str, str, str | None]]) -> tuple[bool, list[str]]:
    """Return (passed, critical paths that required a log)."""
    critical_paths: list[str] = []
    updated = False
    for status, path, old in rows:
        if is_critical(path) or (old is not None and is_critical(old)):
            critical_paths.append(old if old and is_critical(old) else path)
        if counts_as_log_update(status, path):
            updated = True
    if not critical_paths:
        return True, []
    return updated, critical_paths


def parse_name_status(blob: str) -> list[tuple[str, str, str | None]]:
    parts = blob.split("\0")
    if parts and parts[-1] == "":
        parts.pop()
    rows: list[tuple[str, str, str | None]] = []
    index = 0
    while index < len(parts):
        status = parts[index]
        index += 1
        if status[:1] in {"R", "C"}:
            old, new = parts[index], parts[index + 1]
            index += 2
            rows.append((status, new, old))
        else:
            rows.append((status, parts[index], None))
            index += 1
    return rows


def git_env(parent: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(parent if parent is not None else os.environ)
    for key in list(env):
        if key.startswith("GIT_"):
            env.pop(key)
    return env


def git_rows(left: str, right: str, cwd: Path) -> list[tuple[str, str, str | None]]:
    result = subprocess.run(
        ["git", "diff", "--name-status", "-z", left, right],
        cwd=cwd,
        env=git_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git diff failed"
        raise RuntimeError(message)
    return parse_name_status(result.stdout)


def blank_base(base: str) -> bool:
    return bool(base) and set(base) == {"0"}


def resolve_revs(args: argparse.Namespace) -> tuple[str, str] | None:
    event = os.environ.get("GATE_EVENT", "")
    base = args.base or os.environ.get("GATE_BASE", "")
    head = args.head or os.environ.get("GATE_HEAD", "")
    if not (args.base or args.head or event):
        raise RuntimeError("Pass --base and --head.")
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


def report(passed: bool, critical_paths: list[str]) -> int:
    if passed and not critical_paths:
        print("AI-log update check passed: no critical-path changes.")
        return 0
    if passed:
        print("AI-log update check passed: AI-log/ was updated.")
        return 0
    shown = ", ".join(critical_paths[:20])
    extra = len(critical_paths) - 20
    suffix = f" (+{extra} more)" if extra > 0 else ""
    print("AI-log update check failed.")
    print(f"Critical paths changed without an added or modified file under AI-log/: {shown}{suffix}")
    print("Log format and contents are not checked. Deleting a log does not count as an update.")
    return 1


def expect(condition: bool, label: str, failures: list[str]) -> None:
    print(("pass: " if condition else "fail: ") + label)
    if not condition:
        failures.append(label)


def self_test() -> int:
    failures: list[str] = []
    code_only = parse_name_status("M\0tradingagents/a.py\0")
    passed, paths = decision(code_only)
    expect(not passed and paths == ["tradingagents/a.py"], "code change without a log fails", failures)

    deleted_log = parse_name_status("M\0cli/main.py\0D\0AI-log/Member-A/old.md\0")
    passed, _paths = decision(deleted_log)
    expect(not passed, "deleting a log does not satisfy the update", failures)

    ignored = parse_name_status("M\0tests/test_a.py\0M\0AI-log/.DS_Store\0")
    passed, _paths = decision(ignored)
    expect(not passed, ".DS_Store does not satisfy the update", failures)

    accepted = parse_name_status("M\0scripts/ci/check_ai_log_updated.py\0A\0AI-log/Member-E/note.md\0")
    passed, _paths = decision(accepted)
    expect(passed, "code change with an added log passes", failures)

    docs_only = parse_name_status("M\0docs/readme.md\0M\0docs/figure.png\0M\0results/run.json\0")
    passed, paths = decision(docs_only)
    expect(passed and paths == [], "ordinary docs, images, and run results do not require a log", failures)

    for critical in (
        "main.py",
        ".github/workflows/ci.yml",
        "pyproject.toml",
        "requirements.txt",
        "AGENTS.md",
        ".opencode/permissions.jsonc",
        "docs/code-governance/dependency-audit-exceptions.txt",
        "docs/code-governance/dependency-reviews.md",
    ):
        passed, paths = decision(parse_name_status(f"M\0{critical}\0"))
        expect(not passed and paths == [critical], f"modifying {critical} requires a log", failures)

    deleted = parse_name_status("D\0main.py\0")
    passed, paths = decision(deleted)
    expect(not passed and paths == ["main.py"], "deleting a critical file requires a log", failures)

    renamed = parse_name_status("R100\0tradingagents/a.py\0docs/a.py\0")
    passed, paths = decision(renamed)
    expect(not passed and paths == ["tradingagents/a.py"], "moving code out of the tree still requires a log", failures)

    moved_config = parse_name_status("R100\0pyproject.toml\0docs/pyproject.toml\0")
    passed, paths = decision(moved_config)
    expect(not passed and paths == ["pyproject.toml"], "moving a critical file out still requires a log", failures)

    moved_workflow = parse_name_status("R100\0.github/workflows/ci.yml\0docs/ci.yml\0")
    passed, paths = decision(moved_workflow)
    expect(not passed and paths == [".github/workflows/ci.yml"], "moving a workflow out still requires a log", failures)

    accepted_entry = parse_name_status("M\0main.py\0A\0AI-log/Member-E/note.md\0")
    passed, _paths = decision(accepted_entry)
    expect(passed, "a critical file change with an added log passes", failures)

    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        env = git_env()

        def run(*args: str) -> None:
            subprocess.run(args, cwd=root, env=env, check=True, capture_output=True, text=True)

        run("git", "init", "-b", "main")
        run("git", "config", "user.email", "gate@example.com")
        run("git", "config", "user.name", "gate")
        source = root / "tradingagents"
        source.mkdir()
        (source / "a.py").write_text("one\n", encoding="utf-8")
        run("git", "add", ".")
        run("git", "commit", "-m", "base")
        base = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, env=env, check=True, capture_output=True, text=True
        ).stdout.strip()
        (source / "a.py").write_text("two\n", encoding="utf-8")
        run("git", "add", ".")
        run("git", "commit", "-m", "code only")
        code_head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, env=env, check=True, capture_output=True, text=True
        ).stdout.strip()
        passed, _paths = decision(git_rows(base, code_head, root))
        expect(not passed, "git diff of a code-only commit fails", failures)

        log = root / "AI-log" / "Member-A"
        log.mkdir(parents=True)
        (log / "note.md").write_text("record\n", encoding="utf-8")
        run("git", "add", ".")
        run("git", "commit", "-m", "add log")
        logged_head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, env=env, check=True, capture_output=True, text=True
        ).stdout.strip()
        passed, _paths = decision(git_rows(base, logged_head, root))
        expect(passed, "git diff that includes a new log passes", failures)

    if failures:
        print(f"{len(failures)} AI-log self-test(s) failed.")
        return 1
    print("AI-log self-test passed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check that critical-path changes update AI-log/.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--pull-request", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    try:
        revs = resolve_revs(args)
        if revs is None:
            print("AI-log update check skipped: this push has no previous commit.")
            return 0
        root = Path(
            subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        passed, paths = decision(git_rows(revs[0], revs[1], root))
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"AI-log update check failed: {exc}")
        return 1
    return report(passed, paths)


if __name__ == "__main__":
    sys.exit(main())
