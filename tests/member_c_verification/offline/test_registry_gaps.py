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


def _first_markdown_visible_line(document: str) -> str:
    """Markdown 'first rendered visible content' = first non-blank line."""
    return next(line for line in document.splitlines() if line.strip())


def _first_html_visible_element(document: str) -> str:
    """HTML 'first rendered visible content' = first element inside <body>,
    structure markup (doctype, html/head, styles, wrapper divs) excluded."""
    body = document[document.index("<body"):]
    body = body[body.index(">") + 1:]
    for raw in body.split("<"):
        element = "<" + raw
        if element.startswith(("<div", "</div", "<header", "<nav", "<main", "<footer")):
            continue
        return element
    raise AssertionError("no visible element inside <body>")


# TC-SEC003-c: disclaimer present but not first is a blocking violation, not a pass.
@pytest.mark.parametrize("exporter", ["markdown", "html"])
def test_inv008_disclaimer_only_later_is_a_violation(exporter):
    """REQ-TA-INV-008 / REQ-TA-SEC-003: 'first visible content', not 'contains'.

    A disclaimer that is present but placed after a title, banner or header is a
    blocking violation. The positive probes prove the exporters lead with it; this
    negative probe proves the position contract actually rejects the failure mode
    Member C warned about ('starts with' != 'contains').
    """
    if exporter == "markdown":
        document = f"# AAPL report\n\n## Analysis\n\nHold the line.\n\n## Disclaimer\n\n{DISCLAIMER}"
        first_visible = _first_markdown_visible_line(document)
    else:
        document = (
            "<!doctype html><html><head><title>Report</title></head><body>"
            f'<header class="masthead"><h1>AAPL</h1></header>'
            f'<p class="disclaimer">{DISCLAIMER}</p></body></html>'
        )
        first_visible = _first_html_visible_element(document)
    assert DISCLAIMER in document  # satisfied 'contains'
    assert DISCLAIMER not in first_visible  # violates 'first visible content'
    # Presence-only checking (OutputChecker rule Q3) cannot catch this; the
    # invariant is upheld at the exporter layout that the positive probes assert.
    from tradingagents.runapi.checks import OutputChecker, render_provenance

    trusted = {
        "run_id": "2026-11-12T09:00:00Z-abcdef", "ticker": "AAPL",
        "analysis_date": DATE, "input_mode": "NO_PORTFOLIO", "basename": None,
        "fingerprint_sha256": None, "portfolio_as_of": None, "as_of_basis": None,
    }
    body = document if exporter == "markdown" else f"## Analysis\n\nHold.\n\n## Disclaimer\n\n{DISCLAIMER}"
    result = OutputChecker().evaluate(trusted, render_provenance(trusted), "Hold", body)
    assert "Q3" not in [finding.rule for finding in result.findings]
