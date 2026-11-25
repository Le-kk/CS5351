"""Developer regressions for the user-authorized H1-H5 repair, not C acceptance."""

import pytest

from tradingagents.runapi.result import CheckResult, Finding, RunRecord, summarize_records


@pytest.mark.parametrize("verdict,findings", [
    ("PASSED", (Finding("R3"),)),
    ("PASSED", (Finding("R5", "CORRECTED"), Finding("R3"))),
    ("NEEDS_REVIEW", (Finding("R5", "CORRECTED"),)),
    ("NOT_RUN", (Finding("R5", "CORRECTED"),)),
    ("UNKNOWN", ()),
])
def test_invalid_check_combinations_fail_closed(verdict, findings):
    with pytest.raises(ValueError):
        CheckResult(verdict, findings)


def test_corrected_details_are_retained_and_mixed_findings_block():
    corrected = Finding("R5", "CORRECTED", "Confidence reduced to low.")
    assert CheckResult("PASSED", (corrected,)).as_dict()["findings"] == [corrected.as_dict()]
    assert CheckResult("NEEDS_REVIEW", (corrected, Finding("R3"))).output_check == "NEEDS_REVIEW"


def test_unknown_finding_severity_is_rejected():
    with pytest.raises(ValueError):
        Finding("R5", "UNKNOWN")


def test_missing_case_identity_is_unknown_not_inferred_from_attempt_name():
    result = summarize_records([RunRecord("case-1-trial-1", "STARTED")])
    assert result["distinct_case_count"] is None
    assert result["completion_fraction"] == 0
    assert result["status"] == "INSUFFICIENT_EVIDENCE"


def test_explicit_case_identity_keeps_unresolved_attempt_in_denominator():
    result = summarize_records([
        RunRecord("a", "STARTED", "COMPLETED", "PASSED", case_id="same"),
        RunRecord("b", "STARTED", case_id="same"),
        RunRecord("c", "PRE_RUN_CANCELLED", case_id="other"),
    ])
    assert result["distinct_case_count"] == 1
    assert result["population_result_count"] is None  # no frozen population controls
    assert result["started_count"] == 2
    assert result["completion_fraction"] == 0.5
    assert result["pre_run_cancelled"] == 1


def test_html_notice_precedes_title_and_trusted_metadata():
    from tradingagents.report_html import render_report
    from tradingagents.runapi.checks import DISCLAIMER

    report = render_report("AAPL", {}, {}, [], body_markdown="Synthetic body", run_metadata={
        "run_id": "fixture", "run_outcome": "INCOMPLETE", "output_check": "NOT_RUN",
    })
    assert report.index(DISCLAIMER) < report.index('<header class="masthead">')
    assert "fixture" in report
