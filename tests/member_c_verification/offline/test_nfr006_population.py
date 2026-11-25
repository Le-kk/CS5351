"""REQ-TA-NFR-EVAL-001 — Transparent evaluation population.

Fit: completion fraction counts started fresh runs; pre-run cancels/rejects are
counted separately; zero-completed means insufficient evidence, never passing.

Enforcing design: runapi/result.summarize_records (RunRecord aggregation).
"""

from __future__ import annotations

import pytest

from tradingagents.runapi.result import RunRecord, summarize_records

pytestmark = pytest.mark.unit


# TC-NFR006-a: six completed (two review-needed) + four incomplete + two cancels.
def test_tc_nfr006_a_population_breakdown():
    started = (
        [RunRecord(f"s{i}", "STARTED", "COMPLETED", "PASSED") for i in range(4)]
        + [RunRecord(f"r{i}", "STARTED", "COMPLETED", "NEEDS_REVIEW") for i in range(2)]
        + [RunRecord(f"i{i}", "STARTED", "INCOMPLETE", "NOT_RUN", reason) for i, reason in enumerate(("DATA_FAILURE", "MODEL_FAILURE", "MODEL_FAILURE", "BUDGET"))]
    )
    pre = [RunRecord("c0", "PRE_RUN_CANCELLED"), RunRecord("c1", "PRE_RUN_CANCELLED")]
    summary = summarize_records(started + pre)

    assert summary["started_count"] == 10
    assert summary["completed_count"] == 6
    assert summary["completion_fraction"] == pytest.approx(0.6)
    assert summary["needs_review_count"] == 2
    assert summary["pre_run_cancelled"] == 2
    assert summary["incomplete_reason_counts"] == {"DATA_FAILURE": 1, "MODEL_FAILURE": 2, "BUDGET": 1}


# TC-NFR006-b: zero completed samples is insufficient evidence, not a pass.
def test_tc_nfr006_b_zero_completed_is_insufficient():
    summary = summarize_records([RunRecord("i0", "STARTED", "INCOMPLETE", "NOT_RUN", "DATA_FAILURE")])
    assert summary["completed_count"] == 0
    assert summary["status"] == "INSUFFICIENT_EVIDENCE"


def test_case_identity_is_not_attempt_identity():
    """REQ-TA-NFR-EVAL-001: 20 fixed cases, 40 attempts, one population result."""
    from tradingagents.runapi.result import EvaluationPopulation

    population = EvaluationPopulation("fixture", "git:fixture", "a" * 64, "b" * 64,
                                      tuple(f"case-{i}" for i in range(20)))
    records = [RunRecord(
        attempt_id=f"case-{case}-trial-{trial}", case_id=f"case-{case}",
        category="STARTED", run_outcome="COMPLETED", output_check="PASSED",
        stop_reason=None, controlled_change=None, population_id="fixture",
        source_revision="git:fixture", prompt_hash="a" * 64,
        configuration_fingerprint="b" * 64,
    ) for case in range(20) for trial in range(2)]
    result = summarize_records(records, population=population)
    assert result["started_count"] == 40
    assert result["completed_count"] == 40
    assert result.get("distinct_case_count") == 20
    assert result.get("population_result_count") == 1


def test_pending_start_remains_in_denominator():
    result = summarize_records([RunRecord("done", "STARTED", "COMPLETED", "PASSED"), RunRecord("pending", "STARTED"), RunRecord("reject", "PRE_RUN_REJECTED")])
    assert result["completion_fraction"] == 0.5
    assert result["started_count"] == 2
    assert result["pre_run_rejected"] == 1
