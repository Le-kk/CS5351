"""R2/R3 differential pins: the repaired logic rejects what the pre-repair code did.

These encode the review's reproductions as permanent negatives against the
*current* scorer/harness. The original baseline comparison is kept in the private
session record; permanent project tests must not import an arbitrary local file.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

LIVE_DIR = Path(__file__).resolve().parents[1] / "member_c_verification" / "live"

pytestmark = pytest.mark.unit


def _helper():
    import importlib
    spec = importlib.util.spec_from_file_location(
        "diff_exit_fixture", LIVE_DIR / "test_score_gov004_exitcodes.py")
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    return helper


def _population(tmp_path, monkeypatch):
    helper = _helper()
    root = tmp_path / "evidence"
    scorer = helper._fresh_scorer(root, monkeypatch)
    rows = []
    for case in helper.FIXED_CASES:
        marker = helper.CHALLENGE_MARKERS.get(case)
        for label in ("a", "b"):
            rows.append(helper._make_run(root, case, f"{case}-{label}",
                                         challenge_marker=marker,
                                         challenge_reached=True if marker else None))
    helper._write_evidence(root, "1", rows)
    scores = root / "gov004_scores.json"
    helper._scores_all_pass(scores, [r["run_id"] for r in rows])
    return helper, scorer, root, scores, rows


def _substitute_no_portfolio(helper, root, scores, rows):
    row = next(r for r in rows if r["case_id"] == "GOV004-C2-explicit-empty")
    path = Path(row["manifest_path"])
    data = json.loads(path.read_text())
    data.update(input_mode="NO_PORTFOLIO", fingerprint_sha256=None,
                portfolio_as_of=None, as_of_basis=None, basename=None)
    path.write_text(json.dumps(data), encoding="utf-8")
    row["manifest_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    (root / "gov004_T1.json").write_text(json.dumps(
        {"gate": "GOV-004", "kind": "formal", "trial": "1", "cases": rows}))


def test_r2_repaired_scorer_rejects_no_portfolio_substitution(tmp_path, monkeypatch):
    helper, scorer, root, scores, rows = _population(tmp_path, monkeypatch)
    _substitute_no_portfolio(helper, root, scores, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r3_fixed_loop_persists_first_start_before_later_abort(tmp_path):
    """The fixed harness keeps the first started attempt when a later case fails."""
    sys.path.insert(0, str(LIVE_DIR))
    import replay_store

    store = tmp_path / "evidence"
    store.mkdir()

    def run_fn(slot):
        if slot["run_id"] == "slot-2":
            raise RuntimeError("second case aborted")
        return {"case_id": slot["case_id"], "run_id": slot["run_id"],
                "trial": slot["trial"], "outcome": "COMPLETED", "stop_reason": None,
                "final_rating": "Hold", "output_check": "PASSED", "findings": [],
                "challenge_marker": None, "challenge_reached_model": None,
                "prompt_capture": {"model_calls": 1, "calls": []}, "model_config": {},
                "report_path": None, "manifest_path": None, "run_dir": None,
                "source_revision": "git:test", "error": None, "notes": []}

    planned = [
        {"case_id": "GOV004-C1-no-portfolio", "trial": "1", "run_id": "slot-1"},
        {"case_id": "GOV004-C2-explicit-empty", "trial": "1", "run_id": "slot-2"},
    ]
    replay_store.dispatch_slots(store, planned, run_fn,
                                started_at_fn=lambda: "2026-11-21T00:00:00Z")
    # First attempt's outcome persisted; the second start retained as noncompleted.
    assert (store / "gov004_attempt_slot-1.json").is_file()
    starts = {s["run_id"]: s for s in replay_store.load_starts(store)}
    assert starts["slot-1"]["status"] == "RESOLVED"
    assert starts["slot-2"]["outcome"] == "ERROR"
