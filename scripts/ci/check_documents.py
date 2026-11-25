#!/usr/bin/env python3
"""Dependency-free document checks; Ruby's bundled safe YAML parser handles the AI-use index."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

from ci_scope import changes


def prose(text: str) -> str:
    return re.sub(r"(?m)^([`~]{3,}).*?\n.*?^\1\s*$", "", text, flags=re.S)


def markdown_errors(path: Path, text: str, root: Path, removed: set[Path] | None = None) -> list[str]:
    errors = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if match:
            token = match[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
    if fence and removed is None:
        errors.append("unclosed Markdown code fence")
    body = prose(text)
    # Inline/image links plus reference definitions. External links are syntax-only,
    # not network requests (avoids provider/DNS dependence and private endpoints).
    links = re.findall(r"!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", body)
    links += re.findall(r"(?m)^ {0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", body)
    for raw in links:
        target = raw.strip("<>")
        if removed is not None:
            parsed_target = urlsplit(target)
            if parsed_target.scheme or not parsed_target.path:
                continue
            if (path.parent / unquote(parsed_target.path)).resolve() not in removed:
                continue
        parsed = urlsplit(target)
        if parsed.scheme in {"http", "https", "mailto", "plugin", "app", "codex"}:
            if parsed.scheme in {"http", "https"} and not parsed.netloc:
                errors.append("malformed external link")
            continue
        if parsed.scheme:
            errors.append(f"unsupported link scheme: {parsed.scheme}")
            continue
        relative = unquote(parsed.path)
        if not relative:
            continue  # Heading fragment checks are outside this basic validator.
        candidate = (path.parent / relative).resolve()
        if not candidate.is_relative_to(root.resolve()) or not candidate.exists():
            errors.append(f"missing or outside-repository local link: {target}")
    return errors


def yaml_index(root: Path) -> dict:
    command = ["ruby", "-ryaml", "-rjson", "-e",
               "puts JSON.generate(YAML.safe_load(File.read(ARGV.fetch(0)), aliases: false))",
               str(root / "docs/ai-use-log.yaml")]
    return json.loads(subprocess.check_output(command, stderr=subprocess.PIPE, timeout=30))


def check(root: Path, rows: list[dict[str, str]]) -> list[str]:
    errors = []
    changed = {row["path"] for row in rows}
    for row in rows:
        name = row["path"]
        if row["status"] == "D":
            continue
        path = root / name
        try:
            data = path.read_bytes()
            suffix = path.suffix.lower()
            if suffix in {".md", ".txt", ".json", ".yaml", ".svg"}:
                text = data.decode("utf-8")
                if "\x00" in text or "<<<<<<< " in text or ">>>>>>> " in text:
                    raise ValueError("NUL byte or unresolved merge marker")
                if suffix == ".md":
                    errors.extend(f"{name}: {e}" for e in markdown_errors(path, text, root))
                elif suffix == ".json":
                    json.loads(text)
                elif suffix == ".svg":
                    ET.fromstring(text)
            elif suffix == ".pdf" and not (data.startswith(b"%PDF-") and b"%%EOF" in data[-2048:]):
                raise ValueError("invalid PDF signature/trailer")
        except (OSError, ValueError, ET.ParseError) as exc:
            errors.append(f"{name}: invalid document ({type(exc).__name__})")
    removed = {(root / row["path"]).resolve() for row in rows if row["status"] == "D"}
    if removed:
        try:
            tracked = subprocess.check_output(["git", "ls-files", "-z", "--", "*.md"], cwd=root)
            for name in tracked.decode().split("\0"):
                if name and (root / name).is_file():
                    text = (root / name).read_text(encoding="utf-8")
                    errors.extend(f"{name}: {e}" for e in markdown_errors(root / name, text, root, removed))
        except (OSError, ValueError, subprocess.SubprocessError):
            errors.append("cannot validate inbound links to deleted documents")
    # Do not leave a delivered report/PDF pair out of sync in the same PR.
    if bool("Report.md" in changed) != bool("Report.pdf" in changed):
        errors.append("Report.md and Report.pdf must be updated together")
    if changed & {"Report.md", "Report.pdf", "report-assets/integration-verification.json"}:
        try:
            meta = json.loads((root / "report-assets/integration-verification.json").read_text())
            digest = hashlib.sha256((root / "Report.pdf").read_bytes()).hexdigest()
            if meta.get("pdf_sha256") != digest:
                errors.append("report PDF hash does not match integration metadata")
        except (OSError, ValueError):
            errors.append("report integration metadata missing or invalid")
    if "docs/ai-use-log.yaml" in changed or any(p.startswith("AI-log/") for p in changed):
        try:
            index = yaml_index(root)
            records = index["source_records"]
            if not isinstance(records, list) or not records:
                raise ValueError("empty source records")
            seen = set()
            for record in records:
                path = (root / record["path"]).resolve()
                if not path.is_relative_to(root.resolve()) or record["path"] in seen:
                    raise ValueError("unsafe or duplicate record path")
                seen.add(record["path"])
                if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
                    errors.append(f"AI-use source hash mismatch: {record['path']}")
            indexed = {r["path"] for r in records}
            for row in rows:
                if row["path"].startswith("AI-log/Member-") and row["path"].endswith(".md") and row["status"] != "D" and not row["path"].endswith("/README.md") and row["path"] not in indexed:
                    errors.append(f"AI-use record not indexed: {row['path']}")
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
            errors.append("AI-use YAML/index validation failed (safe parser, paths and hashes required)")
    return errors


def main() -> int:
    try:
        errors = check(Path.cwd(), changes(os.environ["GATE_BASE"], os.environ["GATE_HEAD"]))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        errors = ["cannot read complete document change set"]
    for error in errors:
        print(f"FAIL documents: {error}")
    if not errors:
        print("PASS documents: formats, local links and applicable report/index consistency. External targets and heading fragments are not fetched/validated.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
