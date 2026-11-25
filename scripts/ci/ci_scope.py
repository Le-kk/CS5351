#!/usr/bin/env python3
"""Fail-closed PR scope classification, using complete Git objects rather than API file limits."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath

PROTECTED = ("src/", "test/", "tests/", "tradingagents/", "cli/", "demo/", "scripts/",
             "prompts/", ".github/", ".opencode/", ".agent/", "docs/req/", "docs/code-governance/")
TEXT = {".md", ".txt"}
MEDIA = {".pdf", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def changes(base: str, head: str) -> list[dict[str, str]]:
    for revision in (base, head):
        if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
            raise ValueError("Expected full commit SHA")
    fields = git("diff", "--raw", "--no-abbrev", "--no-renames", "-z", base, head).split(b"\0")
    result = []
    for i in range(0, len(fields) - 1, 2):
        old, new, _old_sha, _new_sha, status = fields[i].decode().lstrip(":").split()
        result.append({"path": fields[i + 1].decode("utf-8"), "old_mode": old,
                       "new_mode": new, "status": status})
    return result


def is_document(row: dict[str, str]) -> bool:
    path = row["path"]
    p = PurePosixPath(path)
    if p.is_absolute() or ".." in p.parts or path.startswith(PROTECTED):
        return False
    if path in {"AGENTS.md", "Prompt.md", "requirements.txt"}:
        return False
    # Symlinks, executable documents, type changes and submodules require full CI.
    if any(row[k] not in {"000000", "100644"} for k in ("old_mode", "new_mode")):
        return False
    if path in {"docs/ai-use-log.yaml", "Report.pdf"}:
        return True
    if p.suffix.lower() in TEXT:
        return path.startswith(("docs/", "AI-log/", "transcripts/", "history/")) or len(p.parts) == 1
    return (path.startswith(("docs/", "report-assets/")) and p.suffix.lower() in MEDIA
            or path.startswith("report-assets/") and p.suffix.lower() == ".json")


def mode(rows: list[dict[str, str]], event: str) -> str:
    return "docs" if event == "pull_request" and rows and all(map(is_document, rows)) else "full"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    event = os.environ.get("GATE_EVENT", "")
    base, head = os.environ.get("GATE_BASE", ""), os.environ.get("GATE_HEAD", "")
    rows = []
    # Pushes (including initial branch creation) always get complete CI.
    if event == "pull_request":
        base = git("merge-base", base, head).decode().strip() if re.fullmatch(r"[0-9a-fA-F]{40}", base) and re.fullmatch(r"[0-9a-fA-F]{40}", head) else ""
        rows = changes(base, head)
    selected = mode(rows, event)
    if args.output:
        with args.output.open("a") as output:
            output.write(f"mode={selected}\nbase={base}\nhead={head}\n")
    print(json.dumps({"mode": selected, "changed_paths": [r["path"] for r in rows]}))


if __name__ == "__main__":
    main()
