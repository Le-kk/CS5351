"""H4: public results must not certify a REVIEW rating as PASSED."""

import pytest

from tradingagents.runapi.result import Finding, RunResult


def test_public_review_passed_is_rejected():
    with pytest.raises(ValueError, match="REVIEW requires NEEDS_REVIEW"):
        RunResult("h4", "AAPL", "2026-01-09", "NO_PORTFOLIO", "COMPLETED",
                  None, "REVIEW", "PASSED")


def test_public_review_with_blocking_finding_remains_serializable():
    result = RunResult("h4", "AAPL", "2026-01-09", "NO_PORTFOLIO", "COMPLETED",
                       None, "REVIEW", "NEEDS_REVIEW", (Finding("Q1"),))
    data = result.as_dict()
    assert data["final_rating"] == "REVIEW"
    assert data["output_check"] == "NEEDS_REVIEW"
    assert data["findings"][0]["rule"] == "Q1"


@pytest.mark.parametrize("rating", ["Buy", "Overweight", "Hold", "Underweight", "Sell"])
def test_actionable_ratings_can_still_pass(rating):
    result = RunResult("h4", "AAPL", "2026-01-09", "NO_PORTFOLIO", "COMPLETED",
                       None, rating, "PASSED")
    assert result.as_dict()["final_rating"] == rating
