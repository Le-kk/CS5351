"""Check CI token permissions and trusted-checkout boundaries, not agent role ACLs."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def findings(document: dict, name: str) -> list[str]:
    errors = []
    events = document.get("on", {})
    events = {events} if isinstance(events, str) else set(events)
    privileged = bool(events & {"pull_request_target", "issue_comment", "workflow_run"})
    untrusted = "pull_request" in events
    for job_name, job in document.get("jobs", {}).items():
        label = f"{name}:{job_name}"
        permissions = job.get("permissions", document.get("permissions"))
        if untrusted or privileged:
            if not isinstance(permissions, dict) or permissions.get("contents") != "read":
                errors.append(f"{label}: explicit contents: read is required")
            else:
                allowed_writes = {"checks", "pull-requests"} if privileged and not untrusted else set()
                for scope, value in permissions.items():
                    if value == "write" and scope not in allowed_writes:
                        errors.append(f"{label}: forbidden write permission {scope}")
        if privileged:
            checkouts = 0
            for step in job.get("steps", []):
                if str(step.get("uses", "")).startswith("actions/checkout@"):
                    checkouts += 1
                    options = step.get("with", {})
                    if options.get("ref") != "${{ github.event.repository.default_branch }}":
                        errors.append(f"{label}: privileged checkout must use trusted default branch")
                    if options.get("repository") not in {None, "${{ github.repository }}"}:
                        errors.append(f"{label}: privileged checkout cannot select another repository")
                if "${{ github.event." in str(step.get("run", "")):
                    errors.append(f"{label}: do not interpolate event data directly into shell code")
            if not checkouts:
                errors.append(f"{label}: privileged job has no explicit trusted checkout")
    return errors


def main() -> int:
    paths = sorted((ROOT / ".github/workflows").glob("*.y*ml"))
    errors = []
    if not paths:
        errors.append("No workflow files found")
    for path in paths:
        try:
            # BaseLoader keeps the YAML 1.1 boolean spelling 'on' as a string.
            document = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
            if not isinstance(document, dict) or not document.get("jobs"):
                raise ValueError("workflow must contain jobs")
            errors.extend(findings(document, path.name))
        except (OSError, ValueError, TypeError, yaml.YAMLError) as exc:
            errors.append(f"{path.name}: cannot validate workflow ({type(exc).__name__})")
    for error in errors:
        print(f"FAIL WORKFLOW_PERMISSIONS: {error}")
    if not errors:
        print(f"PASS workflow permission boundaries: {len(paths)} workflow files")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
