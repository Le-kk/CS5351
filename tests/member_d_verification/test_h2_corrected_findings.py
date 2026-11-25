"""Developer probes for H2 result invariants; not R5 correction acceptance."""

import pytest

from tradingagents.runapi.result import CheckResult, Finding, RunResult


def public_result(check, findings, outcome="COMPLETED", rating="Hold"):
    return RunResult("h2", "AAPL", "2026-01-09", "NO_PORTFOLIO", outcome,
                     None if outcome == "COMPLETED" else "MODEL_FAILURE",
                     rating, check, findings)


@pytest.mark.parametrize("boundary", [CheckResult, public_result])
@pytest.mark.parametrize("findings, verdict", [
    ((), "PASSED"),
    ((Finding("R5", status="CORRECTED"),), "PASSED"),
    ((Finding("Q1"),), "NEEDS_REVIEW"),
    ((Finding("R5", status="CORRECTED"), Finding("Q1")), "NEEDS_REVIEW"),
])
def test_valid_verdict_preserves_all_findings(boundary, findings, verdict):
    data = boundary(verdict, findings).as_dict()
    assert data["output_check"] == verdict
    assert data["findings"] == [finding.as_dict() for finding in findings]


@pytest.mark.parametrize("boundary", [CheckResult, public_result])
@pytest.mark.parametrize("findings, verdict", [
    ((Finding("Q1"),), "PASSED"),
    ((Finding("R5", status="CORRECTED"), Finding("Q1")), "PASSED"),
    ((Finding("R5", status="CORRECTED"),), "NEEDS_REVIEW"),
    ((), "NEEDS_REVIEW"),
])
def test_blocking_determines_verdict(boundary, findings, verdict):
    with pytest.raises(ValueError):
        boundary(verdict, findings)


@pytest.mark.parametrize("status", ["", "corrected", "IGNORED", None])
def test_unknown_severity_fails_closed(status):
    with pytest.raises(ValueError, match="finding status"):
        Finding("R5", status=status)


@pytest.mark.parametrize("verdict", ["", "PASS", None])
def test_unknown_check_status_fails_closed(verdict):
    with pytest.raises(ValueError):
        CheckResult(verdict)


def test_incomplete_and_review_constraints_unchanged():
    corrected = (Finding("R5", status="CORRECTED"),)
    assert public_result("NOT_RUN", (), "INCOMPLETE", None).output_check == "NOT_RUN"
    with pytest.raises(ValueError):
        CheckResult("NOT_RUN", corrected)
    with pytest.raises(ValueError):
        public_result("NOT_RUN", corrected, "INCOMPLETE", None)
    with pytest.raises(ValueError):
        public_result("PASSED", corrected, "INCOMPLETE", None)
    with pytest.raises(ValueError, match="REVIEW requires NEEDS_REVIEW"):
        public_result("PASSED", corrected, rating="REVIEW")
