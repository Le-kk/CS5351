#!/usr/bin/env python3
"""Aggregate the pytest matrix and clean-install smoke into one check.

The check passes only when both GitHub job results are exactly ``success``.
Failure, cancellation, skip, or a missing result fails the check. Success means
those workflow jobs succeeded. It does not mean skipped live model tests ran.
"""

from __future__ import annotations

import argparse
import os
import sys

JOBS = ("pytest", "clean-install smoke")


def unsuccessful(results: dict[str, str]) -> list[str]:
    problems: list[str] = []
    for name in JOBS:
        result = results.get(name, "")
        if result != "success":
            problems.append(f"{name}: {result or 'missing'}")
    return problems


def expect(condition: bool, label: str, failures: list[str]) -> None:
    print(("pass: " if condition else "fail: ") + label)
    if not condition:
        failures.append(label)


def self_test() -> int:
    failures: list[str] = []
    expect(unsuccessful({"pytest": "success", "clean-install smoke": "success"}) == [], "both successes pass", failures)
    expect(
        bool(unsuccessful({"pytest": "failure", "clean-install smoke": "success"})),
        "a failed pytest job fails the summary",
        failures,
    )
    expect(
        bool(unsuccessful({"pytest": "success", "clean-install smoke": "cancelled"})),
        "a cancelled install job fails the summary",
        failures,
    )
    expect(
        bool(unsuccessful({"pytest": "skipped", "clean-install smoke": "skipped"})),
        "skipped jobs fail the summary",
        failures,
    )
    expect(bool(unsuccessful({})), "missing job results fail the summary", failures)
    if failures:
        print(f"{len(failures)} required-tests self-test(s) failed.")
        return 1
    print("required-tests self-test passed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Require the pytest and clean-install jobs to succeed.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    problems = unsuccessful(
        {
            "pytest": os.environ.get("PYTEST_RESULT", ""),
            "clean-install smoke": os.environ.get("SMOKE_RESULT", ""),
        }
    )
    if problems:
        print("required tests failed. A skipped, failed, or cancelled job does not pass.")
        print("\n".join(problems))
        return 1
    print("required tests passed: pytest jobs and clean-install smoke succeeded.")
    print("This does not mean skipped live model tests ran.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
