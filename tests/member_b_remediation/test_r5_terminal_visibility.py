"""R5 — a failed publication must not leave a caller-visible COMPLETED terminal.

``publish_run`` used to emit ``run.terminal=COMPLETED`` directly into the
caller-supplied ``EventSink`` *before* the critical commit. When the final rename
failed the result was correctly INCOMPLETE/PERSISTENCE_ERROR, but the caller's
sink already held a COMPLETED terminal. These tests drive the real
``run_analysis_api`` boundary and inspect both the returned result and the
caller-owned sink. Fake graph/runner only; no provider or network.
"""

from __future__ import annotations

import json

import pytest

from tradingagents.runapi.events import EventSink
from tradingagents.runapi.execution import run_analysis_api
from tradingagents.runapi.input_service import freeze_explicit

pytestmark = pytest.mark.unit

STATE = {
    "market_report": "MKT",
    "investment_debate_state": {"bull_history": "BULL", "bear_history": "BEAR"},
    "investment_plan": "RESEARCH PLAN",
    "trader_investment_plan": "TRADE PLAN",
    "risk_debate_state": {"neutral_history": "NEUTRAL"},
    "final_trade_decision": "**Rating**: Hold\n\nBalanced view.",
    "final_rating": "Hold",
}


def _run(tmp_path, sink, *, raises=None):
    class _Engine:
        pass

    def factory(*_a, **_k):
        return _Engine()

    def runner(_graph, _context):
        if raises is not None:
            raise raises
        return STATE

    ctx = freeze_explicit("AAPL", "2026-11-12", None).confirm()
    return run_analysis_api(
        ctx, config={"results_dir": str(tmp_path), "selected_analysts": ["market"]},
        selected_analysts=["market"], graph_factory=factory, engine_runner=runner,
        event_sink=sink,
    )


def _terminal_outcomes(sink):
    return [e["event_outcome"] for e in sink.events if e["event"] == "run.terminal"]


def test_r5_01_rename_failure_exposes_incomplete_terminal_only(tmp_path, monkeypatch):
    from tradingagents.runapi import persist

    monkeypatch.setattr(persist.os, "rename", lambda *_a, **_k: (_ for _ in ()).throw(
        OSError("simulated commit rename failure")))
    sink = EventSink("r5-01", "AAPL")
    result = _run(tmp_path, sink)

    assert result.run_outcome == "INCOMPLETE"
    assert result.stop_reason == "PERSISTENCE_ERROR"
    assert result.output_check == "NOT_RUN"
    assert result.final_rating is None
    assert result.manifest_path is None and result.report_path is None
    assert not (tmp_path / "AAPL" / result.run_id).exists()

    terminals = _terminal_outcomes(sink)
    assert terminals == ["INCOMPLETE"], terminals


def test_r5_02_critical_manifest_write_failure_is_consistent(tmp_path, monkeypatch):
    import pathlib

    original = pathlib.Path.write_text

    def flaky(self, *a, **k):
        if self.name == "manifest.json.tmp":
            raise OSError("simulated manifest write failure")
        return original(self, *a, **k)

    monkeypatch.setattr(pathlib.Path, "write_text", flaky)
    sink = EventSink("r5-02", "AAPL")
    result = _run(tmp_path, sink)

    assert result.run_outcome == "INCOMPLETE"
    assert result.stop_reason == "PERSISTENCE_ERROR"
    assert result.manifest_path is None
    assert _terminal_outcomes(sink) == ["INCOMPLETE"]


def test_r5_03_terminal_append_failure_keeps_logical_outcome(tmp_path, monkeypatch):
    from pathlib import Path

    from tradingagents.runapi import events as events_module

    original_replace = events_module.os.replace

    def flaky_replace(src, dst, *a, **k):
        if Path(dst).name == "events.jsonl":
            raise OSError("simulated terminal append failure")
        return original_replace(src, dst, *a, **k)

    monkeypatch.setattr(events_module.os, "replace", flaky_replace)
    sink = EventSink("r5-03", "AAPL")
    result = _run(tmp_path, sink)

    assert result.run_outcome == "COMPLETED"
    assert result.final_rating == "Hold"
    assert _terminal_outcomes(sink) == ["COMPLETED"]
    data = json.loads((tmp_path / "AAPL" / result.run_id / "manifest.json").read_text())
    assert data["terminal_event"]["durable"] is False


def test_r5_04_normal_completed_has_one_matching_terminal(tmp_path):
    sink = EventSink("r5-04", "AAPL")
    result = _run(tmp_path, sink)

    assert result.run_outcome == "COMPLETED"
    assert _terminal_outcomes(sink) == ["COMPLETED"]
    record = [e for e in sink.events if e["event"] == "run.terminal"][0]
    assert record["node"] == "output" and record["ts"]


def test_r5_04_normal_engine_incomplete_has_one_matching_terminal(tmp_path):
    sink = EventSink("r5-04b", "AAPL")
    result = _run(tmp_path, sink, raises=RuntimeError("engine failed"))

    assert result.run_outcome == "INCOMPLETE"
    assert _terminal_outcomes(sink) == ["INCOMPLETE"]


def test_r5_05_tentative_terminal_not_exposed_before_commit(tmp_path, monkeypatch):
    """While the critical manifest write is pending, no terminal is caller-visible."""
    import pathlib

    from tradingagents.runapi import persist

    original_text = pathlib.Path.write_text
    original_rename = persist.os.rename
    seen = {}

    def failing_manifest(self, *a, **k):
        if self.name == "manifest.json.tmp":
            raise OSError("simulated manifest failure")
        return original_text(self, *a, **k)

    sink = EventSink("r5-05", "AAPL")

    def spy_rename(src, dst, *a, **k):
        return original_rename(src, dst, *a, **k)

    monkeypatch.setattr(pathlib.Path, "write_text", failing_manifest)
    monkeypatch.setattr(persist.os, "rename", spy_rename)
    result = _run(tmp_path, sink)
    seen["terminals"] = _terminal_outcomes(sink)

    assert result.run_outcome == "INCOMPLETE"
    assert seen["terminals"] == ["INCOMPLETE"]


def test_r5_06_committed_terminal_blocks_a_second_terminal():
    """After commit_terminal, emit(run.terminal) must be rejected (single terminal)."""
    sink = EventSink("r5-06", "AAPL")
    sink.stage_tentative_terminal("COMPLETED")
    sink.commit_terminal()
    with pytest.raises(ValueError):
        sink.emit("output", "run.terminal", "INCOMPLETE")
    assert _terminal_outcomes(sink) == ["COMPLETED"]


def test_r5_06_committed_terminal_blocks_a_second_commit():
    sink = EventSink("r5-06b", "AAPL")
    sink.stage_tentative_terminal("COMPLETED")
    sink.commit_terminal()
    with pytest.raises(ValueError):
        sink.stage_tentative_terminal("INCOMPLETE")
    assert _terminal_outcomes(sink) == ["COMPLETED"]


def test_r5_06_staged_then_emit_terminal_is_rejected():
    """A staged (not yet committed) terminal also blocks a direct emit."""
    sink = EventSink("r5-06c", "AAPL")
    sink.stage_tentative_terminal("COMPLETED")
    with pytest.raises(ValueError):
        sink.emit("output", "run.terminal", "COMPLETED")
    # The caller still sees no terminal until the stage resolves.
    assert sink.events == []


def test_r5_07_legacy_sink_without_staging_still_commits_on_success(tmp_path):
    """A supported legacy sink lacking staging support keeps best-effort behaviour."""
    class LegacySink(EventSink):
        # Simulate a pre-R5 sink: no staging/commit protocol.
        stage_tentative_terminal = None
        commit_terminal = None
        discard_tentative_terminal = None

    sink = LegacySink("r5-07", "AAPL")
    result = _run(tmp_path, sink)
    assert result.run_outcome == "COMPLETED"
    assert _terminal_outcomes(sink) == ["COMPLETED"]


def test_r5_07_legacy_sink_failure_does_not_leave_completed(tmp_path, monkeypatch):
    """A legacy sink must not retain COMPLETED after a critical rename failure."""
    from tradingagents.runapi import persist

    monkeypatch.setattr(persist.os, "rename", lambda *_a, **_k: (_ for _ in ()).throw(
        OSError("simulated commit rename failure")))

    class LegacySink(EventSink):
        stage_tentative_terminal = None
        commit_terminal = None
        discard_tentative_terminal = None

    sink = LegacySink("r5-07b", "AAPL")
    result = _run(tmp_path, sink)
    assert result.run_outcome == "INCOMPLETE"
    # No stale COMPLETED terminal may survive; exactly one INCOMPLETE is visible.
    terminals = _terminal_outcomes(sink)
    assert "COMPLETED" not in terminals, terminals
    assert terminals == ["INCOMPLETE"], terminals


def test_r5_08_post_commit_bookkeeping_error_keeps_published_outcome(tmp_path, monkeypatch):
    """A non-critical bookkeeping error after publication must not report PERSISTENCE_ERROR."""
    class _Graph:
        memory_log = None

        def record_decision(self, *_a, **_k):
            raise RuntimeError("synthetic post-publication bookkeeping failure")

    def factory(*_a, **_k):
        return _Graph()

    def runner(_graph, _context):
        return STATE

    ctx = freeze_explicit("AAPL", "2026-11-12", None).confirm()
    sink = EventSink("r5-08", "AAPL")
    result = run_analysis_api(
        ctx, config={"results_dir": str(tmp_path), "selected_analysts": ["market"]},
        selected_analysts=["market"], graph_factory=factory, engine_runner=runner,
        event_sink=sink,
    )
    # The run is published COMPLETED; a downstream bookkeeping error is best-effort.
    assert result.run_outcome == "COMPLETED"
    assert result.manifest_path is not None
    assert _terminal_outcomes(sink) == ["COMPLETED"]


class _OldSignatureSink:
    """A genuine pre-R5 sink: ``emit`` + ``write_to(path)`` only.

    No ``stage_tentative_terminal``/``commit_terminal``/``discard_tentative_terminal``
    and a ``write_to`` that takes only ``path`` (not the new ``terminal_override``).
    """

    def __init__(self, run_id, ticker, redactor=None):
        self.run_id = run_id
        self.ticker = ticker
        self.redactor = redactor
        self.events = []

    def emit(self, node, event, event_outcome):
        entry = {"run_id": self.run_id, "ticker": self.ticker, "node": node,
                 "event": event, "event_outcome": event_outcome,
                 "ts": "2026-11-21T00:00:00Z", "elapsed_ms": 0}
        self.events.append(entry)
        return entry

    def write_to(self, path):
        path.write_text("".join(json.dumps(e) + "\n" for e in self.events), encoding="utf-8")
        return True


def test_r5_09_old_signature_sink_durability_is_truthful(tmp_path):
    """A genuine old-signature sink must not claim durable without a terminal row."""
    sink = _OldSignatureSink("r5-09", "AAPL")
    result = _run(tmp_path, sink)
    assert result.run_outcome == "COMPLETED"
    events_path = tmp_path / "AAPL" / result.run_id / "events.jsonl"
    lines = [json.loads(line) for line in events_path.read_text().splitlines() if line.strip()]
    terminals = [e for e in lines if e.get("event") == "run.terminal"]
    manifest = json.loads((tmp_path / "AAPL" / result.run_id / "manifest.json").read_text())
    durable = manifest["terminal_event"]["durable"]
    if durable:
        # If it claims durable, the terminal MUST be present with a valid timestamp.
        assert terminals, "durable=true but no terminal row in events.jsonl"
        assert terminals[0].get("ts") and terminals[0]["ts"] not in (None, "null")
        assert terminals[0]["event_outcome"] == "COMPLETED"
    # The caller still sees exactly one terminal.
    assert [e["event_outcome"] for e in sink.events if e["event"] == "run.terminal"] == ["COMPLETED"]


def test_r5_09_old_signature_sink_never_false_durable(tmp_path):
    """If the old sink's write cannot include the terminal, durable must be false."""
    sink = _OldSignatureSink("r5-09b", "AAPL")
    result = _run(tmp_path, sink)
    manifest = json.loads((tmp_path / "AAPL" / result.run_id / "manifest.json").read_text())
    events_path = tmp_path / "AAPL" / result.run_id / "events.jsonl"
    has_terminal = any(json.loads(line).get("event") == "run.terminal"
                       for line in events_path.read_text().splitlines() if line.strip())
    assert manifest["terminal_event"]["durable"] == has_terminal
    assert result.run_outcome == "COMPLETED"


def test_r5_10_commit_terminal_callback_failure_keeps_published_outcome(tmp_path):
    """A post-commit commit_terminal failure must not flip the published outcome."""
    class RaisingCommitSink(EventSink):
        def commit_terminal(self):
            raise OSError("synthetic post-commit sink callback failure")

    sink = RaisingCommitSink("r5-10", "AAPL")
    result = _run(tmp_path, sink)

    # The single rename is authoritative: the run is published COMPLETED.
    assert result.run_outcome == "COMPLETED"
    assert result.manifest_path is not None
    manifest = json.loads((tmp_path / "AAPL" / result.run_id / "manifest.json").read_text())
    assert manifest["run_outcome"] == "COMPLETED"
    # The report artifact exists and is COMPLETED too.
    report = (tmp_path / "AAPL" / result.run_id / "reports" / "complete_report.md").read_text()
    assert "- Run outcome: COMPLETED" in report
