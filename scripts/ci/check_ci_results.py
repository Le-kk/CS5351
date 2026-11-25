#!/usr/bin/env python3
"""Stable required names may accept intentional skips only after successful document verification."""
from __future__ import annotations

import json
import os

GATES = {"required tests": ("test", "smoke-install"), "ruff (strict, full repo)": ("lint",),
         "dependency check": ("dependency-check",), "ai-log updated": ("ai-log-updated",),
         "requirements schema": ("requirements-schema",), "type check": ("type-check",),
         "security checks": ("security-checks",)}


def problems(gate: str, needs: dict) -> list[str]:
    errors = []
    if gate not in GATES:
        return ["unknown required gate"]
    scope = needs.get("scope", {})
    selected = scope.get("outputs", {}).get("mode")
    if scope.get("result") != "success" or selected not in {"docs", "full"}:
        return ["scope classification failed or missing"]
    if selected == "docs":
        if needs.get("documents", {}).get("result") != "success":
            errors.append("document validation did not succeed")
        # Verify every worker is an intentional skip; never mask failure/cancellation.
        for job in {j for jobs in GATES.values() for j in jobs}:
            if needs.get(job, {}).get("result") != "skipped":
                errors.append(f"{job}: expected intentional docs-only skip")
    else:
        for job in GATES[gate]:
            if needs.get(job, {}).get("result") != "success":
                errors.append(f"{job}: required success, got {needs.get(job, {}).get('result', 'missing')}")
    return errors


def main() -> int:
    try:
        needs = json.loads(os.environ["CI_NEEDS"])
        gate = os.environ["CI_GATE"]
        errors = problems(gate, needs)
    except (KeyError, ValueError, TypeError, AttributeError) as exc:
        print(f"FAIL: invalid summary input ({type(exc).__name__})")
        return 1
    for error in errors:
        print(f"FAIL: {error}")
    if not errors:
        print(f"PASS {gate}: {needs['scope']['outputs']['mode']} route verified; live replay is not implied.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
