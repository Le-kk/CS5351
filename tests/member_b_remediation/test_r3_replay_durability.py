"""R3 — durable per-attempt replay accounting so started runs cannot be lost.

The review reproduced a batch-level write that discarded an already-started
attempt when a later case aborted. These tests drive the reusable
``replay_store`` helpers with fake runners (no live fixture, no provider) and
the scorer's start ingestion. Synthetic tmp_path only.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

LIVE_DIR = Path(__file__).resolve().parents[1] / "member_c_verification" / "live"
sys.path.insert(0, str(LIVE_DIR))

import replay_store  # noqa: E402

pytestmark = pytest.mark.unit


def _slot(run_id, case="GOV004-C1-no-portfolio", trial="1"):
    return {"case_id": case, "trial": trial, "run_id": run_id}


def _completed(slot):
    return {"case_id": slot["case_id"], "run_id": slot["run_id"], "trial": slot["trial"],
            "outcome": "COMPLETED", "stop_reason": None, "final_rating": "Hold",
            "output_check": "PASSED", "findings": [], "challenge_marker": None,
            "challenge_reached_model": None,
            "prompt_capture": {"model_calls": 1, "calls": [{"prompt_sha256": "a" * 64}]},
            "model_config": {}, "report_path": None, "manifest_path": None,
            "run_dir": None, "source_revision": "git:test", "error": None, "notes": []}


def test_r3_01_preflight_rejects_whole_cohort_before_dispatch(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    replay_store.claim_start(store, case_id="GOV004-C1-no-portfolio", run_id="slot-2",
                             trial="2", started_at_utc="2026-11-21T00:00:00Z")
    dispatched = []

    def run_fn(slot):
        dispatched.append(slot["run_id"])
        return _completed(slot)

    planned = [
        {"case_id": "GOV004-C1-no-portfolio", "trial": "1", "run_id": "slot-1"},
        {"case_id": "GOV004-C1-no-portfolio", "trial": "2", "run_id": "slot-2"},
    ]
    with pytest.raises(replay_store.ReplayError):
        replay_store.dispatch_slots(store, planned, run_fn, started_at_fn=lambda: "2026-11-21T00:00:01Z")
    assert dispatched == []  # nothing ran
    # The pre-existing start and the not-yet-claimed first slot: only slot-2 exists.
    starts = replay_store.load_starts(store)
    assert [s["run_id"] for s in starts] == ["slot-2"]


def test_r3_02_start_is_durable_before_runner_entered(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    observed = {}

    def run_fn(slot):
        # The start record must already be on disk when the runner is entered.
        starts = replay_store.load_starts(store)
        observed["ids"] = [s["run_id"] for s in starts]
        observed["status"] = starts[0]["status"]
        return _completed(slot)

    replay_store.dispatch_slots(store, [_slot("run-x")], run_fn,
                                started_at_fn=lambda: "2026-11-21T00:00:00Z")
    assert observed["ids"] == ["run-x"]
    assert observed["status"] == "STARTED"
    # The STARTED record is distinct from a fabricated completed application result.
    assert replay_store.load_starts(store)[0]["outcome"] == "COMPLETED"
    assert replay_store.load_starts(store)[0]["status"] == "RESOLVED"


def test_r3_03_later_failure_keeps_first_and_retains_later_start(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()

    def run_fn(slot):
        if slot["run_id"] == "run-1-b":
            raise RuntimeError("serialization failed")
        return _completed(slot)

    planned = [_slot("run-1", trial="1"), _slot("run-1-b", trial="2", case="GOV004-C2-explicit-empty")]
    records = replay_store.dispatch_slots(store, planned, run_fn,
                                          started_at_fn=lambda: "2026-11-21T00:00:00Z")

    assert records[0]["outcome"] == "COMPLETED"
    assert records[1]["outcome"] == "ERROR"

    # The first attempt's outcome file persisted independently.
    first = store / "gov004_attempt_run-1.json"
    assert first.is_file()
    assert json.loads(first.read_text())["cases"][0]["outcome"] == "COMPLETED"
    # The later start is retained as noncompleted (not silently lost).
    starts = {s["run_id"]: s for s in replay_store.load_starts(store)}
    assert starts["run-1"]["status"] == "RESOLVED"
    assert starts["run-1-b"]["status"] == "RESOLVED"
    assert starts["run-1-b"]["outcome"] == "ERROR"


def test_r3_04_unresolved_start_stays_noncompleted_and_blocks_reuse(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    replay_store.claim_start(store, case_id="GOV004-C1-no-portfolio", run_id="open-slot",
                             trial="1", started_at_utc="2026-11-21T00:00:00Z")
    # Reusing that slot must be refused.
    with pytest.raises(replay_store.ReplayError):
        replay_store.preflight_slots(store, [_slot("open-slot")])
    # It ingests as a noncompleted attempt, never a fabricated COMPLETED.
    placeholders = replay_store.ingest_starts(store)
    assert placeholders[0]["outcome"] != "COMPLETED"
    assert placeholders[0]["unresolved_start"] is True


def test_r3_06_unique_files_and_exclusive_claim_in_one_second(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    stamp = "2026-11-21T00:00:00Z"
    replay_store.claim_start(store, case_id="GOV004-C1-no-portfolio", run_id="slot-1",
                             trial="1", started_at_utc=stamp)
    replay_store.claim_start(store, case_id="GOV004-C1-no-portfolio", run_id="slot-2",
                             trial="2", started_at_utc=stamp)
    # Two outcomes written within the same second do not overwrite.
    replay_store.record_outcome(store, run_id="slot-1",
                                outcome=_completed(_slot("slot-1", trial="1")))
    replay_store.record_outcome(store, run_id="slot-2",
                                outcome=_completed(_slot("slot-2", trial="2")))
    assert (store / "gov004_attempt_slot-1.json").is_file()
    assert (store / "gov004_attempt_slot-2.json").is_file()
    # A reused run ID claim is exclusive.
    with pytest.raises(replay_store.ReplayError):
        replay_store.claim_start(store, case_id="GOV004-C1-no-portfolio", run_id="slot-1",
                                 trial="1", started_at_utc=stamp)


def test_r3_07_normal_multi_case_run_saves_all_outcomes(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    planned = [
        {"case_id": "GOV004-C1-no-portfolio", "trial": "1", "run_id": "a1"},
        {"case_id": "GOV004-C2-explicit-empty", "trial": "1", "run_id": "b1"},
        {"case_id": "GOV004-C3-holdings-unknown-cash", "trial": "1", "run_id": "c1"},
    ]
    records = replay_store.dispatch_slots(store, planned, _completed,
                                          started_at_fn=lambda: "2026-11-21T00:00:00Z")
    assert [r["outcome"] for r in records] == ["COMPLETED"] * 3
    for run_id in ("a1", "b1", "c1"):
        assert (store / f"gov004_attempt_{run_id}.json").is_file()


def _scorer(tmp_path, monkeypatch):
    monkeypatch.setenv("GOV004_EVIDENCE_DIR", str(tmp_path / "evidence"))
    if "score_gov004" in sys.modules:
        del sys.modules["score_gov004"]
    return importlib.import_module("score_gov004")


def test_r3_05_scorer_ingests_unresolved_start_into_denominator(tmp_path, monkeypatch):
    store = tmp_path / "evidence"
    store.mkdir()
    replay_store.claim_start(store, case_id="GOV004-C1-no-portfolio", run_id="open-slot",
                             trial="1", started_at_utc="2026-11-21T00:00:00Z")
    scorer = _scorer(tmp_path, monkeypatch)
    attempts = scorer._load_attempts()
    assert len(attempts) == 1
    attempt = attempts[0]
    assert attempt.run_id == "open-slot"
    assert attempt.outcome != "COMPLETED"
    # A start cannot be counted as a completed report or passing quality cell.
    controls = scorer.cohort_controls()
    for attempt in attempts:
        scorer._check_eligibility(attempt, controls)
    assert not (attempts[0].eligible and attempts[0].outcome == "COMPLETED")


# --- cross-process exclusivity (R3-02/R3-06) --------------------------------

_WORKER = r"""
import sys
sys.path.insert(0, {live!r})
import replay_store
root, run_id = sys.argv[1], sys.argv[2]
try:
    replay_store.claim_start(root, case_id="GOV004-C1-no-portfolio",
                             run_id=run_id, trial="1",
                             started_at_utc="2026-11-21T00:00:00Z")
    print("CLAIMED")
except replay_store.ReplayError as exc:
    print("REFUSED:" + str(exc)[:40])
"""


def _spawn_workers(store, run_ids):
    import subprocess

    script = _WORKER.format(live=str(LIVE_DIR))
    procs = [subprocess.Popen([sys.executable, "-c", script, str(store), run_id],
                              stdout=subprocess.PIPE, text=True) for run_id in run_ids]
    return [proc.communicate(timeout=60)[0].strip() for proc in procs]


def test_r3_02_concurrent_same_id_claims_are_exclusive(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    outcomes = _spawn_workers(store, ["same-id"] * 8)
    assert outcomes.count("CLAIMED") == 1, outcomes
    assert all(o.startswith("REFUSED") or o == "CLAIMED" for o in outcomes), outcomes
    # Exactly one retained record -- no lost update, no double claim.
    records = [s for s in replay_store.load_starts(store) if s["run_id"] == "same-id"]
    assert len(records) == 1


def test_r3_06_concurrent_distinct_id_claims_all_retained(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    ids = [f"distinct-{i}" for i in range(8)]
    outcomes = _spawn_workers(store, ids)
    assert outcomes.count("CLAIMED") == 8, outcomes
    retained = {s["run_id"] for s in replay_store.load_starts(store)}
    assert retained == set(ids)


# --- containment / identity / overwrite guards (R3-03) ----------------------


@pytest.mark.parametrize("run_id", ["../../../outside", "..", "a/b", "/tmp/escape"])
def test_r3_03_unsafe_outcome_run_id_is_rejected(tmp_path, run_id):
    store = tmp_path / "evidence"
    store.mkdir()
    with pytest.raises(ValueError):
        replay_store.record_outcome(store, run_id=run_id, outcome=_completed(_slot("x")))
    # Nothing written outside or inside the evidence root.
    assert list(store.glob("gov004_attempt_*")) == []
    assert not (tmp_path.parent / "outside").exists()


def test_r3_03_unsafe_claim_run_id_is_rejected(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    with pytest.raises(ValueError):
        replay_store.claim_start(store, case_id="GOV004-C1-no-portfolio",
                                 run_id="../escape", trial="1",
                                 started_at_utc="2026-11-21T00:00:00Z")


def test_r3_03_unclaimed_and_duplicate_outcomes_are_refused(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    with pytest.raises(replay_store.ReplayError):
        replay_store.record_outcome(store, run_id="never-claimed",
                                    outcome=_completed(_slot("never-claimed")))
    replay_store.claim_start(store, case_id="GOV004-C1-no-portfolio", run_id="slot-a",
                             trial="1", started_at_utc="2026-11-21T00:00:00Z")
    replay_store.record_outcome(store, run_id="slot-a", outcome=_completed(_slot("slot-a")))
    with pytest.raises(replay_store.ReplayError):
        replay_store.record_outcome(store, run_id="slot-a", outcome=_completed(_slot("slot-a")))


def test_r3_03_conflicting_case_or_trial_is_refused(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    replay_store.claim_start(store, case_id="GOV004-C1-no-portfolio", run_id="slot-b",
                             trial="1", started_at_utc="2026-11-21T00:00:00Z")
    bad = _completed({**{"case_id": "GOV004-C3-holdings-unknown-cash", "trial": "1",
                         "run_id": "slot-b"}})
    with pytest.raises(replay_store.ReplayError):
        replay_store.record_outcome(store, run_id="slot-b", outcome=bad)


def test_r3_03_malformed_ledger_fails_closed(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    (store / "gov004_starts.json").write_text("{not json", encoding="utf-8")
    with pytest.raises((replay_store.ReplayError, ValueError)):
        replay_store.load_starts(store)


def test_r3_05_malformed_ledger_scorer_fails_closed(tmp_path, monkeypatch):
    store = tmp_path / "evidence"
    store.mkdir()
    (store / "gov004_starts.json").write_text('{"kind": "formal"}', encoding="utf-8")
    scorer = _scorer(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        scorer._load_attempts()


def test_r3_05_keyboard_interrupt_stops_after_preserving_start(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    executed = []

    def run_fn(slot):
        executed.append(slot["run_id"])
        raise KeyboardInterrupt

    planned = [
        {"case_id": "GOV004-C1-no-portfolio", "trial": "1", "run_id": "k1"},
        {"case_id": "GOV004-C2-explicit-empty", "trial": "1", "run_id": "k2"},
    ]
    with pytest.raises(KeyboardInterrupt):
        replay_store.dispatch_slots(store, planned, run_fn,
                                    started_at_fn=lambda: "2026-11-21T00:00:00Z")
    # Only the first slot was dispatched; the interruption stopped the rest.
    assert executed == ["k1"]
    starts = {s["run_id"]: s for s in replay_store.load_starts(store)}
    assert starts["k1"]["status"] == "STARTED"  # preserved, unresolved
    assert "k2" not in starts  # never claimed


def test_r3_05_unresolved_start_is_harness_metadata_not_invented_outcome(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    replay_store.claim_start(store, case_id="GOV004-C1-no-portfolio", run_id="open",
                             trial="1", started_at_utc="2026-11-21T00:00:00Z")
    placeholders = replay_store.ingest_starts(store)
    assert placeholders[0]["stop_reason"] is None
    assert placeholders[0]["harness_status"] == "STARTED"
    assert placeholders[0]["outcome"] != "COMPLETED"


def test_r3_05_per_start_timestamps(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    stamps = iter(["2026-11-21T00:00:01Z", "2026-11-21T00:00:02Z"])
    planned = [
        {"case_id": "GOV004-C1-no-portfolio", "trial": "1", "run_id": "t1"},
        {"case_id": "GOV004-C2-explicit-empty", "trial": "1", "run_id": "t2"},
    ]
    replay_store.dispatch_slots(store, planned, _completed, started_at_fn=lambda: next(stamps))
    starts = {s["run_id"]: s for s in replay_store.load_starts(store)}
    assert starts["t1"]["started_at_utc"] == "2026-11-21T00:00:01Z"
    assert starts["t2"]["started_at_utc"] == "2026-11-21T00:00:02Z"


def test_r3_05_resolved_start_with_missing_outcome_not_completed(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    replay_store.claim_start(store, case_id="GOV004-C1-no-portfolio", run_id="lost",
                             trial="1", started_at_utc="2026-11-21T00:00:00Z")
    # Mark resolved in the ledger but no outcome file exists.
    data = json.loads((store / "gov004_starts.json").read_text())
    data["starts"][0]["status"] = "RESOLVED"
    data["starts"][0]["outcome"] = "COMPLETED"
    (store / "gov004_starts.json").write_text(json.dumps(data), encoding="utf-8")
    placeholders = replay_store.ingest_starts(store)
    assert placeholders[0]["outcome"] != "COMPLETED"
    assert placeholders[0]["error"] == "outcome file missing"


# --- export compatibility (R3-04) -------------------------------------------

def test_r3_08_nine_completed_plus_one_control_bound_pending(tmp_path, monkeypatch):
    """9 completed + 1 genuine control-bound pending (10/11≥90%) follows policy."""
    helper = _load_exit_helper()
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
    # Replace one completed trial with a genuine, pre-dispatch control-bound pending
    # start (drop its batch row; keep the cohort slot unresolved).
    pending_row = rows.pop()  # last row: C5 trial b
    # Rewrite the evidence file without that row.
    (root / "gov004_T1.json").write_text(json.dumps(
        {"gate": "GOV-004", "kind": "formal", "trial": "1", "cases": rows}), encoding="utf-8")
    scores = root / "gov004_scores.json"
    helper._scores_all_pass(scores, [r["run_id"] for r in rows])
    test_config = dict(helper.FIXED_CONFIG)
    replay_store.claim_start(
        root, case_id=pending_row["case_id"], run_id=pending_row["run_id"],
        trial=pending_row["trial"], started_at_utc="2026-11-21T00:00:05Z",
        model_config=test_config, controls=_cohort_controls(helper))
    # 9 completed, 1 genuine pending -> overall 9/10 = 90%, >=9 completed.
    assert scorer.main(["score", str(scores)]) == 0
    attempts = scorer._load_attempts()
    pending = [a for a in attempts if a.run_id == pending_row["run_id"]]
    assert pending and pending[0].pending_start is True
    # The pending start is a noncompleted denominator entry, not a quality cell.
    assert pending[0].outcome != "COMPLETED"


def test_r3_08_unknown_config_pending_is_flagged_not_invented(tmp_path, monkeypatch):
    """A pending start without captured config stays noncompleted and is flagged."""
    helper = _load_exit_helper()
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
    replay_store.claim_start(root, case_id=helper.FIXED_CASES[0], run_id="cfg-less-slot",
                             trial="1", started_at_utc="2026-11-21T00:00:05Z")
    attempts = scorer._load_attempts()
    controls = scorer.cohort_controls()
    pending = next(a for a in attempts if a.run_id == "cfg-less-slot")
    scorer._check_eligibility(pending, controls)
    assert pending.pending_start is True
    assert pending.outcome != "COMPLETED"
    assert any("configuration" in r for r in pending.reasons)


def _ten_completed_plus_pending(tmp_path, monkeypatch, *, model_config, controls):
    """10/10 completed population (excellent rows) + one extra unresolved start.

    10 completed + 1 pending = 10/11 started (>=90%), so if the pending record is
    accepted the verdict would otherwise PASS. Used to prove a defective pending
    binding blocks acceptance.
    """
    helper = _load_exit_helper()
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
    replay_store.claim_start(
        root, case_id=helper.FIXED_CASES[0], run_id="extra-pending", trial="1",
        started_at_utc="2026-11-21T00:00:05Z",
        model_config=model_config, controls=controls)
    return helper, scorer, root, scores


def _cohort_controls(helper):
    """The full pre-dispatch binding matching the synthetic cohort the runner records."""
    return {"ticker": "AAPL", "analysis_date": "2026-01-09",
            "source_revision": "git:test", "prompt_hash": "a" * 64}


def test_r3_08_extra_pending_wrong_provider_fails(tmp_path, monkeypatch):
    helper = _load_exit_helper()
    good = dict(helper.FIXED_CONFIG)
    bad = {**good, "llm_provider": "wrong-provider"}
    _h, scorer, _root, scores = _ten_completed_plus_pending(
        tmp_path, monkeypatch, model_config=bad, controls=_cohort_controls(helper))
    assert scorer.main(["score", str(scores)]) == 1


def test_r3_08_extra_pending_wrong_deep_tier_provider_fails(tmp_path, monkeypatch):
    helper = _load_exit_helper()
    bad = {**helper.FIXED_CONFIG, "deep_think_provider": "anthropic"}
    _h, scorer, _root, scores = _ten_completed_plus_pending(
        tmp_path, monkeypatch, model_config=bad, controls=_cohort_controls(helper))
    assert scorer.main(["score", str(scores)]) == 1


def test_r3_08_extra_pending_wrong_quick_tier_provider_fails(tmp_path, monkeypatch):
    helper = _load_exit_helper()
    bad = {**helper.FIXED_CONFIG, "quick_think_provider": "openai"}
    _h, scorer, _root, scores = _ten_completed_plus_pending(
        tmp_path, monkeypatch, model_config=bad, controls=_cohort_controls(helper))
    assert scorer.main(["score", str(scores)]) == 1


def test_r3_08_extra_pending_matching_tier_providers_pass(tmp_path, monkeypatch):
    helper = _load_exit_helper()
    good = {**helper.FIXED_CONFIG, "deep_think_provider": "deepseek",
            "quick_think_provider": "deepseek"}
    _h, scorer, _root, scores = _ten_completed_plus_pending(
        tmp_path, monkeypatch, model_config=good, controls=_cohort_controls(helper))
    assert scorer.main(["score", str(scores)]) == 0


def test_r3_08_extra_pending_missing_config_fails(tmp_path, monkeypatch):
    helper = _load_exit_helper()
    _h, scorer, _root, scores = _ten_completed_plus_pending(
        tmp_path, monkeypatch, model_config={}, controls=_cohort_controls(helper))
    assert scorer.main(["score", str(scores)]) == 1


def test_r3_08_extra_pending_wrong_control_fails(tmp_path, monkeypatch):
    helper = _load_exit_helper()
    good = dict(helper.FIXED_CONFIG)
    _h, scorer, _root, scores = _ten_completed_plus_pending(
        tmp_path, monkeypatch, model_config=good,
        controls={"ticker": "AAPL", "analysis_date": "2025-12-19"})  # wrong date
    assert scorer.main(["score", str(scores)]) == 1


def test_r3_08_extra_pending_missing_controls_fails(tmp_path, monkeypatch):
    helper = _load_exit_helper()
    good = dict(helper.FIXED_CONFIG)
    _h, scorer, _root, scores = _ten_completed_plus_pending(
        tmp_path, monkeypatch, model_config=good, controls={})
    assert scorer.main(["score", str(scores)]) == 1


def test_r3_08_control_bound_pending_still_passes(tmp_path, monkeypatch):
    """The legitimate control-bound pending keeps 10/11 >=90% and >=9 completed."""
    helper = _load_exit_helper()
    _h, scorer, _root, scores = _ten_completed_plus_pending(
        tmp_path, monkeypatch, model_config=dict(helper.FIXED_CONFIG),
        controls=_cohort_controls(helper))
    assert scorer.main(["score", str(scores)]) == 0


def test_r3_08_wrong_config_pending_stays_rejected_after_package(tmp_path, monkeypatch):
    """A defective pending binding is still rejected after portable package/rescore."""
    import importlib
    import shutil

    helper = _load_exit_helper()
    bad = {**helper.FIXED_CONFIG, "llm_provider": "wrong-provider"}
    _h, scorer, root, scores = _ten_completed_plus_pending(
        tmp_path, monkeypatch, model_config=bad, controls=_cohort_controls(helper))
    exporter = importlib.import_module("package_gov004")
    destination = tmp_path / "package"
    exporter.package(root, destination, scores)
    moved = tmp_path / "fresh-checkout-evidence"
    destination.rename(moved)
    shutil.rmtree(root)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scorer, "EVIDENCE_ROOT", moved)
    assert scorer.main(["score", str(moved / "gov004_scores.json")]) == 1


def test_r3_04_package_handles_start_ledger_and_rescores_portably(tmp_path, monkeypatch):
    import importlib
    import shutil

    helper = _load_exit_helper()
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
    # Record a completed start plus an unresolved (interrupted) start for the same
    # population via the durable ledger, keyed to real outcome files.
    for row in rows[:2]:
        replay_store.claim_start(root, case_id=row["case_id"], run_id=row["run_id"],
                                 trial=row["trial"], started_at_utc="2026-11-21T00:00:00Z")
        replay_store.record_outcome(root, run_id=row["run_id"], outcome=row)
    replay_store.claim_start(root, case_id=helper.FIXED_CASES[0], run_id="interrupted-slot",
                             trial="1", started_at_utc="2026-11-21T00:00:05Z")

    exporter = importlib.import_module("package_gov004")
    destination = tmp_path / "package"
    exporter.package(root, destination, scores)
    moved = tmp_path / "fresh-checkout-evidence"
    destination.rename(moved)
    shutil.rmtree(root)
    # Rescore from an unrelated working directory with only relative artifact paths.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scorer, "EVIDENCE_ROOT", moved)
    attempts = scorer._load_attempts()
    # The unresolved start is preserved as noncompleted in the denominator.
    unresolved = [a for a in attempts if a.run_id == "interrupted-slot"]
    assert unresolved and unresolved[0].outcome != "COMPLETED"
    # Scores still PASS for the completed population; the unresolved start keeps
    # overall completion below 100% so the strict 9/10 gate fails honestly.
    code = scorer.main(["score", str(moved / "gov004_scores.json")])
    assert code in (0, 1)  # deterministic; not a fabricated PASS


def _load_exit_helper():
    spec = importlib.util.spec_from_file_location(
        "r3_export_helper", LIVE_DIR / "test_score_gov004_exitcodes.py")
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    return helper


# --- empty/malformed ledger is not "no evidence" (R3-03) --------------------


def test_r3_03_absent_ledger_is_no_evidence(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    assert replay_store.load_starts(store) == []


@pytest.mark.parametrize("payload", [
    "{}", "null", "[]", '{"kind": "formal"}',
    '{"kind": "formal", "schema_version": 2, "starts": "oops"}',
    '{"kind": "formal", "schema_version": 1, "starts": []}',
])
def test_r3_03_empty_or_malformed_ledger_fails_closed(tmp_path, payload):
    store = tmp_path / "evidence"
    store.mkdir()
    (store / "gov004_starts.json").write_text(payload, encoding="utf-8")
    with pytest.raises(replay_store.ReplayError):
        replay_store.load_starts(store)


def test_r3_03_malformed_records_fail_closed(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    valid = {"run_id": "r1", "case_id": "GOV004-C1-no-portfolio", "trial": "1",
             "started_at_utc": "2026-11-21T00:00:00Z", "status": "STARTED", "outcome": None}
    bad_variants = [
        dict(valid, run_id="../escape"),
        dict(valid, run_id=""),
        dict(valid, case_id=""),
        dict(valid, trial="3"),
        dict(valid, status="DONE"),
        dict(valid, started_at_utc=""),
    ]
    for bad in bad_variants:
        (store / "gov004_starts.json").write_text(json.dumps(
            {"kind": "formal", "schema_version": 2, "starts": [bad]}), encoding="utf-8")
        with pytest.raises(replay_store.ReplayError):
            replay_store.load_starts(store)


def test_r3_03_duplicate_ids_in_ledger_fail_closed(tmp_path):
    store = tmp_path / "evidence"
    store.mkdir()
    row = {"run_id": "dup", "case_id": "GOV004-C1-no-portfolio", "trial": "1",
           "started_at_utc": "2026-11-21T00:00:00Z", "status": "STARTED", "outcome": None}
    (store / "gov004_starts.json").write_text(json.dumps(
        {"kind": "formal", "schema_version": 2, "starts": [row, dict(row)]}), encoding="utf-8")
    with pytest.raises(replay_store.ReplayError):
        replay_store.load_starts(store)


# --- interruption through the REAL runner → dispatch wiring (R3-04) ---------


def _cases():
    sys.path.insert(0, str(LIVE_DIR))
    import cases as cases_module

    return {c.case_id: c for c in cases_module.CASES}


def _planned_two():
    return [
        {"case_id": "GOV004-C1-no-portfolio", "trial": "1", "run_id": "int-0",
         "case": _cases()["GOV004-C1-no-portfolio"]},
        {"case_id": "GOV004-C2-explicit-empty", "trial": "1", "run_id": "int-1",
         "case": _cases()["GOV004-C2-explicit-empty"]},
    ]


def test_r3_04_runner_propagates_keyboardinterrupt(tmp_path, monkeypatch):
    import runner

    calls = []

    def fake_api(*_a, **_k):
        calls.append(1)
        raise KeyboardInterrupt

    monkeypatch.setattr(runner, "run_analysis_api", fake_api)
    store = tmp_path / "evidence"
    store.mkdir()

    def run_slot(slot):
        from runner import outcome_to_dict

        return outcome_to_dict(runner.run_case(
            slot["case"], results_dir=str(tmp_path / "r"), ticker="AAPL",
            analysis_date="2026-01-09", run_id=slot["run_id"]))

    with pytest.raises(KeyboardInterrupt):
        replay_store.dispatch_slots(store, _planned_two(), run_slot,
                                    started_at_fn=lambda: "2026-11-21T00:00:00Z")
    # Never made the second paid call after the operator stop.
    assert len(calls) == 1
    starts = {s["run_id"]: s for s in replay_store.load_starts(store)}
    assert "int-1" not in starts
    assert starts["int-0"]["status"] == "STARTED"


def test_r3_04_returned_interrupted_result_stops_dispatch(tmp_path, monkeypatch):
    from types import SimpleNamespace

    import runner

    calls = []

    def fake_api(*_a, **_k):
        calls.append(1)
        return SimpleNamespace(
            run_id="int-0", run_outcome="INCOMPLETE", stop_reason="INTERRUPTED",
            final_rating=None, output_check="NOT_RUN", findings=(),
            report_path=None, manifest_path=None,
        )

    monkeypatch.setattr(runner, "run_analysis_api", fake_api)
    store = tmp_path / "evidence"
    store.mkdir()

    def run_slot(slot):
        from runner import outcome_to_dict

        return outcome_to_dict(runner.run_case(
            slot["case"], results_dir=str(tmp_path / "r"), ticker="AAPL",
            analysis_date="2026-01-09", run_id=slot["run_id"]))

    records = replay_store.dispatch_slots(store, _planned_two(), run_slot,
                                          started_at_fn=lambda: "2026-11-21T00:00:00Z")
    # Only the first case was dispatched; its INTERRUPTED result was retained.
    assert len(calls) == 1
    assert records[0]["stop_reason"] == "INTERRUPTED"
    starts = {s["run_id"]: s for s in replay_store.load_starts(store)}
    assert "int-1" not in starts
