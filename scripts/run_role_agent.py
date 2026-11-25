#!/usr/bin/env python3
"""Load and check the repository's version-pinned OpenCode role permissions."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = "1.19.5"


def load_policy(root: Path) -> dict:
    text = (root / ".opencode/permissions.jsonc").read_text(encoding="utf-8")
    return json.loads("\n".join(x for x in text.splitlines() if not x.lstrip().startswith("//")))


def check_tree(root: Path) -> None:
    """Refuse symlinks at startup rather than trust lexical permission patterns."""
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(directory) / name
            if path.is_symlink():
                raise ValueError("Workspace contains a symlink; use a clean regular-file checkout.")
        # Git internals are not agent-readable; large generated environments are denied.
        dirs[:] = [x for x in dirs if x not in {".git", ".venv", "__pycache__", ".pytest_cache"}]


def checked_agent(binary: str, root: Path, role: str, env: dict[str, str]) -> dict:
    expected = load_policy(root)["agent"]["member-" + role.lower()]["permission"]
    result = subprocess.run(
        [binary, "debug", "agent", "member-" + role.lower(), "--pure"],
        cwd=root, env=env, capture_output=True, text=True, timeout=45, check=False,
    )
    if result.returncode:
        raise ValueError("OpenCode could not load the selected role configuration.")
    resolved = json.loads(result.stdout)
    rules = (root / ".opencode/rules.md").read_text(encoding="utf-8").strip()
    if not rules or resolved.get("prompt", "").strip() != rules:
        raise ValueError("The selected role did not load the required rules.md prompt.")
    actual = resolved.get("permission", [])
    # Check native merging rather than assume project config overrides everything.
    for tool, spec in expected.items():
        pairs = list(spec.items()) if isinstance(spec, dict) else [("*", spec)]
        seen = [(r["pattern"], r["action"]) for r in actual if r["permission"] == tool]
        if tool == "external_directory":
            # V1 appends a tool-output directory allowance. Check the explicit deny,
            # and retain this native managed-output exception in the coverage record.
            if ("*", "deny") not in seen:
                raise ValueError("External-directory deny did not load.")
            continue
        if seen[-len(pairs):] != pairs:
            raise ValueError("Resolved role permissions differ from the checked policy.")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=list("ABCDE"))
    parser.add_argument("--check", action="store_true", help="validate without starting a model session")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        check_tree(root)
        binary = shutil.which("opencode")
        if not binary:
            raise ValueError("OpenCode is not on PATH.")
        version = subprocess.check_output([binary, "--version"], text=True, timeout=15).strip()
        if version != VERSION:
            raise ValueError(f"Expected OpenCode {VERSION}; validate migrations before using another version.")
        env = dict(os.environ)
        env.pop("OPENCODE_CONFIG_CONTENT", None)
        env.pop("OPENCODE_PERMISSION", None)
        env["OPENCODE_CONFIG"] = str(root / ".opencode/permissions.jsonc")
        checked_agent(binary, root, args.role, env)
        if args.check:
            print(f"OpenCode {VERSION}: member-{args.role.lower()} permissions loaded and checked.")
            return 0
        os.chdir(root)
        os.execve(binary, [binary, "--pure", "--agent", "member-" + args.role.lower()], env)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Role startup refused: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
