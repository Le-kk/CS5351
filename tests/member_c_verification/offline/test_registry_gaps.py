"""Registry acceptance probes; failures require classified investigation.

Synthetic inputs reuse the C engine/context fixtures. No live model is used.
"""
from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from conftest import GOOD_STATE, confirmed_context, make_engine

from tradingagents.runapi.checks import DISCLAIMER
from tradingagents.runapi.execution import run_analysis_api
from tradingagents.runapi.input_service import PortfolioInputService, freeze_no_portfolio
from tradingagents.runapi.result import Finding, RunResult

pytestmark = pytest.mark.unit
DATE = "2026-11-12"


def _run(context, directory, state=None, runner=None):
    factory, default_runner = make_engine(GOOD_STATE if state is None else state)
    return run_analysis_api(context, config={"results_dir": str(directory)},
                            selected_analysts=["market"], graph_factory=factory,
                            engine_runner=runner or default_runner)


@pytest.mark.parametrize("positions", [[], [{"ticker": "MSFT", "quantity": 7}],
                                       [{"ticker": "AAPL", "quantity": 3}, {"ticker": "MSFT", "quantity": 7}]])
@pytest.mark.parametrize("change", ["overwrite", "replace"])
def test_inv014_confirmed_snapshot_survives_source_and_consumer_mutation(tmp_path, positions, change):
    source = tmp_path / "a.json"
    source.write_text(json.dumps({"positions": positions, "cash": 100}), encoding="utf-8")
    service = PortfolioInputService(tmp_path)
    context = service.freeze_path("AAPL", DATE, source, portfolio_as_of=DATE).confirm()
    metadata = context.safe_input_metadata()
    frozen_rows = context.snapshot.positions
    assert len(metadata["fingerprint_sha256"]) == 64
    replacement = json.dumps({"positions": [{"ticker": "AAPL", "quantity": 999}], "cash": 999})
    if change == "replace":
        other = tmp_path / "replacement.json"
        other.write_text(replacement, encoding="utf-8")
        other.replace(source)
    else:
        source.write_text(replacement, encoding="utf-8")
    derived = context.portfolio_context()
    derived.cash = 777
    with pytest.raises((FrozenInstanceError, AttributeError)):
        context.snapshot.fingerprint_sha256 = "forged"
    captured = []

    def runner(graph, selected):
        captured.append(selected.safe_input_metadata())
        assert selected.portfolio_context().cash == 100
        assert selected.snapshot.positions == frozen_rows
        return dict(GOOD_STATE, fingerprint_sha256="forged", portfolio_context=derived)

    result = _run(context, tmp_path / "results", runner=runner)
    assert result.run_outcome == "COMPLETED"
    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    report = Path(result.report_path).read_text(encoding="utf-8")
    assert captured == [metadata]
    assert context.safe_input_metadata() == metadata
    assert manifest["fingerprint_sha256"] == metadata["fingerprint_sha256"]
    assert f"- Portfolio fingerprint (SHA-256): {metadata['fingerprint_sha256']}" in report
    assert source.read_text(encoding="utf-8") == replacement
    selected_b = service.freeze_path("AAPL", DATE, source, portfolio_as_of=DATE).confirm()
    other_result = _run(selected_b, tmp_path / "results")
    other_manifest = json.loads(Path(other_result.manifest_path).read_text(encoding="utf-8"))
    assert other_manifest["fingerprint_sha256"] != manifest["fingerprint_sha256"]


def test_inv014_no_snapshot_and_explicit_empty_publish_distinct_provenance(tmp_path):
    source = tmp_path / "empty.json"
    source.write_text('{"positions": []}', encoding="utf-8")
    empty = PortfolioInputService(tmp_path).freeze_path("AAPL", DATE, source, portfolio_as_of=DATE).confirm()
    none = freeze_no_portfolio("AAPL", DATE).confirm()
    records = []
    for context in (none, empty):
        result = _run(context, tmp_path / "results")
        assert result.run_outcome == "COMPLETED"
        records.append(json.loads(Path(result.manifest_path).read_text(encoding="utf-8")))
    assert records[0]["input_mode"] == "NO_PORTFOLIO"
    assert records[0]["fingerprint_sha256"] is None
    assert records[1]["input_mode"] == "PORTFOLIO_PROVIDED"
    assert len(records[1]["fingerprint_sha256"]) == 64


@pytest.mark.parametrize("reason", ["MODEL_FAILURE", "DATA_FAILURE", "BUDGET", "INTERNAL_ERROR", "PERSISTENCE_ERROR", "INTERRUPTED"])
def test_run001_incomplete_result_serializes_conditional_fields(reason):
    result = RunResult("fixture", "AAPL", DATE, "NO_PORTFOLIO", "INCOMPLETE", reason, None, "NOT_RUN")
    data = result.as_dict()
    assert data["stop_reason"] == reason
    assert data["final_rating"] is None
    assert data["findings"] == []


@pytest.mark.parametrize("rating", ["Buy", "Overweight", "Hold", "Underweight", "Sell"])
def test_run001_completed_rating_can_pass_without_findings(rating):
    result = RunResult("fixture", "AAPL", DATE, "NO_PORTFOLIO", "COMPLETED", None, rating, "PASSED")
    assert result.as_dict()["stop_reason"] is None


def test_inv001_review_cannot_claim_passed_in_public_result():
    with pytest.raises(ValueError):
        RunResult("fixture", "AAPL", DATE, "NO_PORTFOLIO", "COMPLETED", None, "REVIEW", "PASSED")


def test_arch002_corrected_finding_survives_public_result():
    result = RunResult("fixture", "AAPL", DATE, "NO_PORTFOLIO", "COMPLETED", None,
                       "Hold", "PASSED", (Finding("R5", status="CORRECTED"),))
    assert result.as_dict()["findings"][0]["status"] == "CORRECTED"


@pytest.mark.parametrize("case", range(20))
def test_sec003_rendered_report_starts_with_disclaimer(tmp_path, case):
    """Twenty deterministic renders; no claim of live semantic diversity."""
    state = dict(GOOD_STATE, final_trade_decision=f"Rating: Hold\nSynthetic case {case}.")
    result = _run(confirmed_context(), tmp_path, state)
    assert result.run_outcome == "COMPLETED"
    report = Path(result.report_path).read_text(encoding="utf-8")
    assert report.startswith(DISCLAIMER)
