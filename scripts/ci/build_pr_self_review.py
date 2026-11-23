"""Collect factual PR evidence and explicitly attributed self-review notes.

Uses trusted baseline code and GitHub metadata only. Never executes PR code,
submits a GitHub approving Review, or writes to a protected branch.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import platform
import re
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

from check_test_approval import FULL_SHA, github_json, github_pages, load_policy

REQUIRED_CHECKS = (
    "required tests", "ruff (strict, full repo)", "dependency check",
    "ai-log updated", "test approval",
)
NOTE_FIELDS = {"requirements", "architecture", "code_and_tests", "security", "efficiency", "verdict"}
VERDICTS = {"APPROVE", "CHANGES REQUIRED", "REJECT"}
REQ_ID = re.compile(r"\b(?:REQ|SEL)-TA-[A-Z0-9]+(?:-[A-Z0-9]+)+\b")


def scrub(value: str) -> str:
    for key, secret in os.environ.items():
        if len(secret) >= 8 and any(word in key.upper() for word in ("TOKEN", "SECRET", "PASSWORD", "API_KEY")):
            value = value.replace(secret, "[REDACTED]")
    value = re.sub(r"\b(?:sk-|gh[pousr]_)[A-Za-z0-9_-]{12,}\b", "[REDACTED]", value)
    return re.sub(r"(?i)(\bbearer\s+)[A-Za-z0-9._~+/=-]+", r"\1[REDACTED]", value)


def parse_request(body: str) -> tuple[str, dict[str, str]]:
    lines = body.strip().splitlines()
    match = re.fullmatch(r"/self-review ([0-9a-f]{40})", lines[0] if lines else "")
    if not match:
        raise ValueError("Use /self-review followed by one full 40-character SHA.")
    notes = json.loads("\n".join(lines[1:]).strip() or "{}")
    if not isinstance(notes, dict) or set(notes) - NOTE_FIELDS:
        raise ValueError("Unknown self-review note fields.")
    if any(not isinstance(value, str) or len(value) > 4000 for value in notes.values()):
        raise ValueError("Self-review notes must be strings of at most 4000 characters.")
    if notes.get("verdict", "APPROVE") not in VERDICTS:
        raise ValueError("Use APPROVE, CHANGES REQUIRED, or REJECT.")
    return match[1], {key: scrub(value) for key, value in notes.items()}


def latest_checks(checks: list[dict]) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for check in checks:
        # Native required CI and the trusted approval check use GitHub Actions.
        if (check.get("app") or {}).get("slug") != "github-actions":
            continue
        name = check.get("name", "")
        if name not in latest or check.get("id", 0) > latest[name].get("id", 0):
            latest[name] = check
    return latest


def duration_seconds(started, completed):
    try:
        start = datetime.fromisoformat(started.replace("Z", "+00:00"))
        end = datetime.fromisoformat(completed.replace("Z", "+00:00"))
        seconds = (end - start).total_seconds()
        return seconds if seconds >= 0 else None
    except (AttributeError, TypeError, ValueError):
        return None


def build_receipt(repository: str, number: int, pull: dict, comment: dict,
                  sender: dict, policy, files: list[dict], checks: list[dict],
                  plan_texts: list[str], run_id: str) -> dict:
    sha, notes = parse_request(comment.get("body", ""))
    actor = (comment.get("user") or {}).get("login", "")
    author = (pull.get("user") or {}).get("login", "")
    if (comment.get("user") or {}).get("type") != "User" or sender.get("login") != actor:
        raise ValueError("A real user's own comment is required.")
    if not policy.roster_confirmed or actor not in policy.approvers:
        raise ValueError("Self-reviewer is not on the confirmed baseline roster.")
    if actor != author:
        raise ValueError("/self-review is for the PR author; it is not a peer-review command.")
    if pull.get("state") != "open" or (pull.get("base") or {}).get("ref") != "main":
        raise ValueError("Use an open PR targeting main.")
    if sha != (pull.get("head") or {}).get("sha") or not FULL_SHA.fullmatch(sha):
        raise ValueError("The requested SHA is not the current PR head.")
    if len(files) != pull.get("changed_files"):
        raise ValueError("The changed-file inventory is incomplete.")
    latest = latest_checks(checks)
    evidence = []
    problems = []
    for name in REQUIRED_CHECKS:
        item = latest.get(name)
        if item is None:
            problems.append(f"{name}: missing")
            evidence.append({"name": name, "status": "missing", "conclusion": None})
            continue
        if item.get("head_sha") != sha or item.get("status") != "completed" or item.get("conclusion") != "success":
            problems.append(f"{name}: not a successful completed check for this SHA")
        entry = {key: item.get(key) for key in (
            "name", "head_sha", "status", "conclusion", "started_at", "completed_at", "html_url",
        )}
        entry["duration_seconds"] = duration_seconds(item.get("started_at"), item.get("completed_at"))
        evidence.append(entry)
    requested = notes.get("verdict", "APPROVE")
    # An APPROVE declaration cannot turn incomplete or failed checks into PASS.
    verdict = "CHANGES REQUIRED" if problems and requested == "APPROVE" else requested
    references = "\n".join([pull.get("body") or "", *plan_texts])
    return {
        "schema_version": "1", "review_kind": "self_review", "repository": repository,
        "pull_request": number, "source_sha": sha,
        "reviewer": policy.approvers[actor], "pr_author": author,
        "reviewed_at": comment["created_at"], "generated_at": datetime.now(UTC).isoformat(),
        "comment_id": str(comment["id"]), "comment_url": comment["html_url"],
        "workflow_run_id": run_id,
        "receipt_runtime": {"runner_os": os.environ.get("RUNNER_OS"), "python": platform.python_version()},
        "requirement_references": sorted(set(REQ_ID.findall(references))),
        "architecture_files": sorted(item["filename"] for item in files
                                     if item["filename"].startswith("docs/architecture/")
                                     or item["filename"] == "architecture-blueprint.md"),
        "files": [{key: item.get(key) for key in (
            "filename", "previous_filename", "status", "additions", "deletions",
        )} for item in files],
        "checks": evidence, "check_problems": problems,
        "human_notes": notes, "requested_verdict": requested, "verdict": verdict,
        "limitations": [
            "Self-review is not independent peer review or a native GitHub approving Review.",
            "Requirement IDs and architecture files are references, not proof of alignment.",
            "CI success is not proof of semantic correctness or comprehensive test quality.",
            "No application/model runtime, token or cost measurements are inferred from CI.",
            "This record covers source_sha only; subsequent source changes need a new review.",
        ],
    }


def markdown(receipt: dict) -> str:
    notes = receipt["human_notes"]
    absent = "Not assessed by automation; no human assessment supplied."
    lines = [f"# PR #{receipt['pull_request']} — self-review memo", "",
             f"Repository: `{receipt['repository']}`", f"Reviewed source SHA: `{receipt['source_sha']}`",
             f"Reviewer / PR author: `{receipt['pr_author']}`", f"Review time: {receipt['reviewed_at']}",
             f"Approval comment: {receipt['comment_url']}", "", "## Requirements alignment", "",
             "Referenced IDs: " + (", ".join(receipt["requirement_references"]) or "None found."),
             notes.get("requirements", absent), "", "## Architecture alignment", "",
             "Changed architecture files: " + (", ".join(receipt["architecture_files"]) or "None."),
             notes.get("architecture", absent), "", "## Code and test quality", "",
             notes.get("code_and_tests", absent), "", "Changed files:", ""]
    for item in receipt["files"]:
        lines.append(f"- `{item['filename']}` — {item['status']}; +{item['additions']} / -{item['deletions']}.")
    lines += ["", "## Security and efficiency", "", "Security: " + notes.get("security", absent),
              "Efficiency: " + notes.get("efficiency", absent), "", "## Operational metadata and CI", "",
              f"Receipt workflow run: `{receipt['workflow_run_id']}`",
              f"Receipt environment: {receipt['receipt_runtime']}", ""]
    for item in receipt["checks"]:
        lines.append(f"- {item['name']}: {item['status']} / {item.get('conclusion')}; "
                     f"started {item.get('started_at')}, completed {item.get('completed_at')}, duration {item.get('duration_seconds')} seconds; "
                     f"{item.get('html_url') or 'no run URL'}")
    lines += ["", "Application/model runtime, token usage and cost: not collected by this review.",
              "", "## Scope and limitations", ""]
    lines.extend("- " + item for item in receipt["limitations"])
    if receipt["check_problems"]:
        lines += ["", "Blocking evidence gaps:", "", *["- " + item for item in receipt["check_problems"]]]
    lines += ["", f"Human-requested verdict: {receipt['requested_verdict']} (self-declared).",
              "An automatic evidence check may downgrade APPROVE when required checks are missing or unsuccessful.",
              "", "## Verdict", "", receipt["verdict"], ""]
    return scrub("\n".join(lines))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    issue = event.get("issue") or {}
    if event.get("action") != "created" or not issue.get("pull_request"):
        raise ValueError("Only a newly submitted PR self-review command is accepted.")
    repository, token = os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"]
    number = int(issue["number"])
    pull = github_json(f"https://api.github.com/repos/{repository}/pulls/{number}", token)
    sha = (pull.get("head") or {}).get("sha", "")
    if not FULL_SHA.fullmatch(sha):
        raise ValueError("Invalid PR head.")
    files = github_pages(f"https://api.github.com/repos/{repository}/pulls/{number}/files?per_page=100", token)
    checks = github_pages(f"https://api.github.com/repos/{repository}/commits/{sha}/check-runs?per_page=100", token, "check_runs")
    plans = []
    for item in files:
        path = item["filename"]
        if path.startswith("docs/verification/plans/") and path.endswith(".md") and item["status"] != "removed":
            content = github_json(f"https://api.github.com/repos/{repository}/contents/{quote(path, safe='/')}?ref={sha}", token)
            if content.get("encoding") != "base64" or content.get("size", 0) > 100000:
                raise ValueError("Plan content is unavailable or too large.")
            plans.append(base64.b64decode(content["content"]).decode("utf-8"))
    policy = load_policy(Path("docs/code-governance/test-approval-policy.yaml").read_text())
    receipt = build_receipt(repository, number, pull, event.get("comment") or {}, event.get("sender") or {},
                            policy, files, checks, plans, os.environ["GITHUB_RUN_ID"])
    latest = github_json(f"https://api.github.com/repos/{repository}/pulls/{number}", token)
    if (latest.get("head") or {}).get("sha") != sha:
        raise ValueError("The PR changed while review evidence was being collected; resubmit for its current SHA.")
    args.output.mkdir(parents=True, exist_ok=True)
    docs = args.output / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "review-memo.md").write_text(markdown(receipt), encoding="utf-8")
    (args.output / "review-receipt.json").write_text(scrub(json.dumps(receipt, ensure_ascii=False, indent=2)) + "\n")
    print(f"Self-review files generated for PR #{number}: {receipt['verdict']}")
    return 0 if receipt["verdict"] == "APPROVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
