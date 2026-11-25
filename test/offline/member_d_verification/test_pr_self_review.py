"""Self-review receipts distinguish collected facts from human judgments."""

from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts/ci/build_pr_self_review.py"
SHA = "a" * 40


@pytest.fixture
def review(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("self_review_regression", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def snapshot(review):
    policy = SimpleNamespace(roster_confirmed=True, approvers={
        "member": {"github_login": "member", "name": "Member", "role": "E"},
    })
    pull = {"state": "open", "base": {"ref": "main"}, "head": {"sha": SHA},
            "user": {"login": "member"}, "changed_files": 2, "body": "Covers SEL-TA-NFR-003."}
    comment = {"id": 17, "body": f"/self-review {SHA}", "created_at": "2026-11-23T00:00:00Z",
               "html_url": "https://example.test/comment/17", "user": {"login": "member", "type": "User"}}
    sender = {"login": "member"}
    files = [{"filename": "tests/test_sample.py", "status": "added", "additions": 10, "deletions": 0},
             {"filename": "docs/verification/plans/sample.md", "status": "added", "additions": 20, "deletions": 0}]
    checks = [{"id": i + 1, "name": name, "app": {"slug": "github-actions"}, "head_sha": SHA,
               "status": "completed", "conclusion": "success", "html_url": f"https://example.test/check/{i}",
               "started_at": "2026-11-23T00:00:00Z", "completed_at": "2026-11-23T00:01:00Z"}
              for i, name in enumerate(review.REQUIRED_CHECKS)]
    return SimpleNamespace(policy=policy, pull=pull, comment=comment, sender=sender, files=files, checks=checks)


def collect(review, data):
    return review.build_receipt("team/repo", 12, data.pull, data.comment, data.sender, data.policy,
                                data.files, data.checks, ["REQ-TA-FR-001 and SEL-TA-NFR-003"], "99")


def test_successful_self_review_is_explicit_and_does_not_invent_assessments(review, snapshot):
    result = collect(review, snapshot)
    text = review.markdown(result)
    assert result["review_kind"] == "self_review"
    assert result["source_sha"] == SHA
    assert result["verdict"] == "APPROVE"
    assert result["checks"][0]["duration_seconds"] == 60
    assert result["requirement_references"] == ["REQ-TA-FR-001", "SEL-TA-NFR-003"]
    assert "Not assessed by automation" in text
    assert "Self-review is not independent peer review" in text
    assert text.rstrip().endswith("APPROVE")


@pytest.mark.parametrize("name", ["required tests", "ruff (strict, full repo)", "dependency check", "ai-log updated", "test approval"])
def test_missing_required_check_cannot_produce_approve(review, snapshot, name):
    snapshot.checks = [item for item in snapshot.checks if item["name"] != name]
    result = collect(review, snapshot)
    assert result["requested_verdict"] == "APPROVE"
    assert result["verdict"] == "CHANGES REQUIRED"


@pytest.mark.parametrize("conclusion", ["failure", "cancelled", "skipped", "neutral", None])
def test_non_success_is_not_accepted_as_verified(review, snapshot, conclusion):
    snapshot.checks[0]["conclusion"] = conclusion
    assert collect(review, snapshot)["verdict"] == "CHANGES REQUIRED"


def test_latest_failed_attempt_overrides_old_success(review, snapshot):
    snapshot.checks.append({**snapshot.checks[0], "id": 999, "conclusion": "failure"})
    assert collect(review, snapshot)["verdict"] == "CHANGES REQUIRED"


def test_another_apps_status_cannot_replace_required_ci(review, snapshot):
    snapshot.checks[0]["app"] = {"slug": "unrelated-app"}
    assert collect(review, snapshot)["verdict"] == "CHANGES REQUIRED"


def test_check_results_from_other_sha_do_not_satisfy_review(review, snapshot):
    snapshot.checks[0]["head_sha"] = "b" * 40
    assert collect(review, snapshot)["verdict"] == "CHANGES REQUIRED"


def test_stale_review_command_is_rejected(review, snapshot):
    snapshot.comment["body"] = "/self-review " + "b" * 40
    with pytest.raises(ValueError):
        collect(review, snapshot)


def test_non_author_cannot_be_mislabelled_as_self_reviewer(review, snapshot):
    snapshot.pull["user"]["login"] = "another-member"
    with pytest.raises(ValueError):
        collect(review, snapshot)


def test_unauthorized_or_unconfirmed_member_is_rejected(review, snapshot):
    snapshot.policy.roster_confirmed = False
    with pytest.raises(ValueError):
        collect(review, snapshot)
    snapshot.policy.roster_confirmed = True
    snapshot.policy.approvers = {}
    with pytest.raises(ValueError):
        collect(review, snapshot)


def test_bot_or_different_event_sender_is_rejected(review, snapshot):
    snapshot.comment["user"]["type"] = "Bot"
    with pytest.raises(ValueError):
        collect(review, snapshot)
    snapshot.comment["user"]["type"] = "User"
    snapshot.sender["login"] = "moderator"
    with pytest.raises(ValueError):
        collect(review, snapshot)


def test_incomplete_change_inventory_is_rejected(review, snapshot):
    snapshot.pull["changed_files"] = 3
    with pytest.raises(ValueError):
        collect(review, snapshot)


def test_human_notes_are_attributed_and_credentials_are_scrubbed(review, snapshot, monkeypatch):
    planted = "synthetic-sensitive-value-not-a-real-token"
    monkeypatch.setenv("GITHUB_TOKEN", planted)
    snapshot.comment["body"] += "\n" + json.dumps({"architecture": "Boundary checked. " + planted,
                                                   "code_and_tests": "Four scenarios inspected.", "verdict": "REJECT"})
    result = collect(review, snapshot)
    text = review.markdown(result)
    assert result["verdict"] == "REJECT"
    assert "Four scenarios inspected." in text
    assert planted not in json.dumps(result)
    assert planted not in text
    assert "[REDACTED]" in text


@pytest.mark.parametrize("body", ["/self-review abc", "/self-review " + SHA + " extra",
                                  "/self-review " + SHA + '\n{"unknown":"x"}',
                                  "/self-review " + SHA + '\n{"verdict":"PASSED"}'])
def test_invalid_commands_and_notes_are_rejected(review, body):
    with pytest.raises(ValueError):
        review.parse_request(body)


def test_cli_writes_both_review_files_without_mutating_github(review, snapshot, tmp_path, monkeypatch):
    event = {"action": "created", "issue": {"number": 12, "pull_request": {"url": "https://example.test/12"}},
             "comment": snapshot.comment, "sender": snapshot.sender}
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps(event))
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_path))
    monkeypatch.setenv("GITHUB_REPOSITORY", "team/repo")
    monkeypatch.setenv("GITHUB_TOKEN", "synthetic-token")
    monkeypatch.setenv("GITHUB_RUN_ID", "99")
    monkeypatch.chdir(tmp_path)
    policy_file = tmp_path / "docs/code-governance/test-approval-policy.yaml"
    policy_file.parent.mkdir(parents=True)
    policy_file.write_text("fixture")
    monkeypatch.setattr(review, "load_policy", lambda _text: snapshot.policy)

    def api(url, _token):
        if "/contents/" in url:
            data = b"SEL-TA-NFR-003"
            return {"encoding": "base64", "content": base64.b64encode(data).decode(), "size": len(data)}
        return snapshot.pull

    monkeypatch.setattr(review, "github_json", api)
    monkeypatch.setattr(review, "github_pages", lambda url, *_a: snapshot.files if "/files?" in url else snapshot.checks)
    output = tmp_path / "output"
    assert review.main(["--output", str(output)]) == 0
    assert (output / "docs/review-memo.md").is_file()
    result = json.loads((output / "review-receipt.json").read_text())
    assert result["source_sha"] == SHA
    assert result["review_kind"] == "self_review"


def test_closed_pr_is_not_retrospectively_approved(review, snapshot):
    snapshot.pull["state"] = "closed"
    with pytest.raises(ValueError):
        collect(review, snapshot)
