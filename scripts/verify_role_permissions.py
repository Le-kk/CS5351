#!/usr/bin/env python3
"""Exercise native OpenCode tool permission checks on synthetic files, without a model."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from run_role_agent import VERSION, check_tree, checked_agent


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def verify(output: Path) -> None:
    source = Path(__file__).resolve().parents[1]
    binary = shutil.which("opencode")
    if not binary or subprocess.check_output([binary, "--version"], text=True).strip() != VERSION:
        raise ValueError(f"Verification requires OpenCode {VERSION} on PATH.")
    policy_hash = digest(source / ".opencode/permissions.jsonc")
    rules_hash = digest(source / ".opencode/rules.md")
    covenant_hash = digest(source / ".agent/rules.md")
    rows = []
    with tempfile.TemporaryDirectory(prefix="cs5351-e5-") as directory:
        base = Path(directory).resolve()
        root = base / "workspace"
        (root / ".opencode").mkdir(parents=True)
        shutil.copyfile(source / ".opencode/permissions.jsonc", root / ".opencode/permissions.jsonc")
        shutil.copyfile(source / ".opencode/rules.md", root / ".opencode/rules.md")
        (root / ".agent").mkdir()
        shutil.copyfile(source / ".agent/rules.md", root / ".agent/rules.md")
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        env = dict(os.environ)
        for name in list(env):
            if name.startswith(("OPENCODE_", "GIT_")):
                env.pop(name)
        for kind in ("CONFIG", "DATA", "CACHE", "STATE"):
            path = base / kind.lower()
            path.mkdir()
            env[f"XDG_{kind}_HOME"] = str(path)
        env["OPENCODE_CONFIG"] = str(root / ".opencode/permissions.jsonc")
        # Native debug tools execute directly; no prompt/model inference is used.
        def call(role: str, tool: str, path: str, allowed: bool) -> None:
            target = (root / path).resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            if tool == "read" and not target.exists():
                target.write_text("synthetic permission fixture\n")
            before = digest(target)
            params = {"filePath": str(target)}
            if tool == "edit":
                # Also exercise denial on the existing human-controlled rules file.
                old = target.read_text() if before is not None else ""
                params.update(oldString=old, newString=f"synthetic {role} edit\n")
            result = subprocess.run(
                [binary, "debug", "agent", "member-" + role.lower(), "--pure", "--tool", tool,
                 "--params", json.dumps(params)],
                cwd=root, env=env, capture_output=True, text=True, timeout=45,
            )
            after = digest(target)
            denied = "prevents you from using this specific tool call" in result.stderr or "is disabled for agent" in result.stderr
            passed = ((result.returncode == 0 and (tool == "read" or after != before)) if allowed
                      else (result.returncode != 0 and denied and before == after))
            rows.append({"role": role, "tool": tool, "path": path, "expected": "allow" if allowed else "deny",
                         "exit_code": result.returncode, "permission_denial": denied,
                         "target_unchanged": before == after, "passed": passed})
            if not passed:
                raise RuntimeError(f"Unexpected native permission outcome: {role} {tool} {path}")
        for role, target in {"A":"docs/req/e5-allowed.md", "B":"docs/architecture/adr/e5-allowed.md",
                             "C":"tests/e5-allowed.txt", "D":"tradingagents/e5-allowed.txt",
                             "E":"docs/code-governance/e5-allowed.md"}.items():
            checked_agent(binary, root, role, env)
            rows.append({"role": role, "tool": "resolved-rules-prompt", "expected": "exact rules.md", "passed": True})
            call(role, "read", ".agent/rules.md", True)
            call(role, "read", ".opencode/rules.md", True)
            call(role, "read", "AGENTS.md", True)
            call(role, "edit", target, True)
            call(role, "edit", ".opencode/rules.md", False)
            call(role, "read", f"docs/architecture/.env.{role}", False)
            call(role, "read", "../external-private.txt", False)
            call(role, "read", "docs/architecture/credentials.json", False)
        # Exact human-only file; scope ownership and nested secret probes.
        for role, path in [("A","tradingagents/a-denied.txt"),("B","docs/architecture/trace-matrix.md"),
                           ("C","tradingagents/c-denied.txt"),("D","tests/d-denied.txt"),
                           ("E","docs/req/e-denied.txt"),("E","docs/code-governance/verification-constraints.md"),
                           ("E",".opencode/rules.md"),("D","tradingagents/.env.new")]:
            call(role, "edit", path, False)
        for role in "ABCDE":
            call(role, "read", "portfolios/private.json", False)
        call("C", "edit", "docs/code-governance/verification-constraints.md", True)
        call("E", "edit", "docs/architecture/trace-matrix.md", True)
        call("D", "read", "tests/readable-fixture.txt", True)
        call("E", "edit", ".agent/rules.md", True)
        call("D", "edit", ".agent/rules.md", False)
        # Both native write and edit use the scoped edit permission.
        for role, path, allowed in [("C", "tests/native-write.txt", True), ("D", "tests/denied-write.txt", False)]:
            target = root / path
            before = digest(target)
            result = subprocess.run([binary, "debug", "agent", "member-" + role.lower(), "--pure", "--tool", "write",
                                     "--params", json.dumps({"filePath": str(target), "content": "synthetic write\n"})],
                                    cwd=root, env=env, capture_output=True, text=True, timeout=45)
            denied = "prevents you from using this specific tool call" in result.stderr or "is disabled for agent" in result.stderr
            passed = (result.returncode == 0 and target.exists()) if allowed else (result.returncode != 0 and denied and digest(target) == before)
            if not passed:
                raise RuntimeError("Native write permission probe failed")
            rows.append({"role":role,"tool":"write","path":path,"expected":"allow" if allowed else "deny",
                         "exit_code":result.returncode,"permission_denial":denied,"passed":passed})
        # An unlisted built-in tool cannot be used to bypass scoped file tools.
        result = subprocess.run([binary,"debug","agent","member-d","--pure","--tool","bash",
                                 "--params",json.dumps({"command":"printf bypass", "description":"synthetic bypass probe"})],
                                cwd=root, env=env, capture_output=True, text=True, timeout=45)
        assert result.returncode != 0 and "is disabled for agent" in result.stderr
        rows.append({"role":"D","tool":"bash","expected":"deny","exit_code":result.returncode,"passed":True})
        # A resolved prompt override must be rejected, not silently accepted.
        overridden = dict(env)
        overridden["OPENCODE_CONFIG_CONTENT"] = json.dumps({"agent": {"member-d": {"prompt": "unrelated prompt"}}})
        try:
            checked_agent(binary, root, "D", overridden)
        except ValueError:
            rows.append({"tool":"rules-prompt-mismatch-guard","expected":"deny","passed":True})
        else:
            raise RuntimeError("Mismatched prompt did not refuse startup")
        # A missing required file must also refuse startup.
        rules_file = root / ".opencode/rules.md"
        contents = rules_file.read_text()
        rules_file.unlink()
        try:
            checked_agent(binary, root, "D", env)
        except (ValueError, OSError):
            rows.append({"tool":"missing-rules-guard","expected":"deny","passed":True})
        else:
            raise RuntimeError("Missing rules did not refuse startup")
        finally:
            rules_file.write_text(contents)
        # Startup guard, not a claim that native lexical path rules resolve symlinks.
        (root / "tradingagents/escape").symlink_to(base / "external-private.txt")
        try:
            check_tree(root)
        except ValueError:
            rows.append({"tool":"startup-symlink-guard","expected":"deny","passed":True})
        else:
            raise RuntimeError("Symlink guard did not reject the workspace")
    if digest(source / ".agent/rules.md") != covenant_hash:
        raise RuntimeError("Covenant changed during verification; rerun on a stable version")
    if digest(source / ".opencode/rules.md") != rules_hash:
        raise RuntimeError("Rules changed during verification; rerun on a stable version")
    if digest(source / ".opencode/permissions.jsonc") != policy_hash:
        raise RuntimeError("Policy changed during verification; rerun on a stable version")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"schema_version":1,"tool":"OpenCode","version":VERSION,
                                 "time_utc":datetime.now(UTC).isoformat(),
                                 "policy_sha256":policy_hash, "rules_sha256":rules_hash, "covenant_sha256":covenant_hash,
                                 "mode":"native-debug-tools; synthetic workspace; no model inference",
                                 "passed":all(x["passed"] for x in rows),"cases":rows},indent=2)+"\n")
    print(f"{len(rows)} permission probes passed; evidence: {output.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    verify(parser.parse_args().output)
