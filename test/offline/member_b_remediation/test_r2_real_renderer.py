"""R2 — validate scorer against genuinely application-produced artifacts.

Instead of a hand-built manifest/report, this drives the real shared boundary
(``run_analysis_api``) with a scripted engine so the manifest and the report
envelope are produced by the actual renderer, then checks the scorer accepts a
complete population built this way and rejects a mutated one. Fake engine only;
no provider or network.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from tradingagents.runapi.execution import run_analysis_api
from tradingagents.runapi.input_service import freeze_explicit

pytestmark = pytest.mark.unit

LIVE_DIR = Path(__file__).resolve().parents[1] / "member_c_verification" / "live"

STATE = {
    "market_report": "MKT narrative for review.",
    "investment_debate_state": {"bull_history": "BULL", "bear_history": "BEAR"},
    "investment_plan": "**Recommendation**: Underweight\n\nRM stage.",
    "trader_investment_plan": "**Action**: Sell\n\nTrader stage.",
    "risk_debate_state": {"neutral_history": "NEUTRAL"},
    "final_trade_decision": "**Rating**: Underweight\n\nPM stage.",
    "final_rating": "Underweight",
}


def _case_portfolios():
    sys.path.insert(0, str(LIVE_DIR))
    import cases as cases_module

    return {case.case_id: case for case in cases_module.CASES}


def _run_case_real(case_id, run_id, results_dir):
    case = _case_portfolios()[case_id]

    class _Engine:
        memory_log = None

    def factory(*_a, **_k):
        return _Engine()

    def runner(_graph, _context):
        return STATE

    ctx = freeze_explicit("AAPL", "2026-01-09", case.portfolio).confirm()
    from dataclasses import replace

    ctx = replace(ctx, run_id=run_id)
    analysts = ["market", "social", "news", "fundamentals"]
    config = {
        "results_dir": str(results_dir), "selected_analysts": analysts,
        "llm_provider": "deepseek",
        "deep_think_llm": "CS5351/DeepSeek-V4-Flash",
        "quick_think_llm": "CS5351/DeepSeek-V4-Flash",
        "max_debate_rounds": 1, "max_risk_discuss_rounds": 1,
    }
    return run_analysis_api(
        ctx, config=config, selected_analysts=analysts,
        graph_factory=factory, engine_runner=runner,
    )


def _helper():
    spec = importlib.util.spec_from_file_location(
        "r2_real_helper", LIVE_DIR / "test_score_gov004_exitcodes.py")
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    return helper


def test_r2_real_renderer_application_artifacts_score(tmp_path, monkeypatch):
    helper = _helper()
    root = tmp_path / "evidence"
    scorer = helper._fresh_scorer(root, monkeypatch)
    cases = _case_portfolios()
    rows = []
    for case_id in helper.FIXED_CASES:
        case = cases[case_id]
        for trial, label in (("1", "a"), ("2", "b")):
            run_id = f"real-{case_id}-{label}"
            result = _run_case_real(case_id, run_id, root / "results")
            assert result.run_outcome == "COMPLETED"
            manifest_path = Path(result.manifest_path)
            report_path = Path(result.report_path)
            manifest = json.loads(manifest_path.read_text())
            # Reassemble an evidence record from the real artifacts.
            record = {
                "trial": trial,
                "portfolio_kind": case.portfolio_kind,
                "prompt_capture": {"model_calls": 1,
                                   "calls": [{"prompt_sha256": "a" * 64,
                                              "marker_hits": {case.challenge_marker: 1}
                                              if case.challenge_marker else {}}],
                                   "marker_reached_model": {case.challenge_marker: True}
                                   if case.challenge_marker else {}},
                "report_sha256": __import__("hashlib").sha256(report_path.read_bytes()).hexdigest(),
                "manifest_sha256": __import__("hashlib").sha256(manifest_path.read_bytes()).hexdigest(),
                "case_id": case_id, "run_id": run_id,
                "outcome": result.run_outcome, "stop_reason": result.stop_reason,
                "final_rating": result.final_rating, "output_check": result.output_check,
                "challenge_marker": case.challenge_marker,
                "challenge_reached_model": True if case.challenge_marker else None,
                "report_path": str(report_path), "manifest_path": str(manifest_path),
                "run_dir": str(manifest_path.parent), "source_revision": manifest["source_revision"],
                "model_config": dict(helper.FIXED_CONFIG), "findings": [],
                "error": None, "notes": [],
            }
            rows.append(record)
    helper._write_evidence(root, "1", rows)
    # Bind the cohort to the genuine source revision the real manifests recorded.
    cohort_path = root / "cohort.json"
    cohort = json.loads(cohort_path.read_text())
    cohort["source_revision"] = rows[0]["source_revision"]
    cohort["prompt_hash"] = json.loads(Path(rows[0]["manifest_path"]).read_text())["prompt_hash"]
    cohort_path.write_text(json.dumps(cohort), encoding="utf-8")
    scores = root / "gov004_scores.json"
    # Cite the numeric rating the real report states for every applicable cell.
    from score_gov004 import APPLICABILITY
    answers = []
    for record in rows:
        for item in APPLICABILITY[record["case_id"]]:
            answers.append({"case_id": record["case_id"], "run_id": record["run_id"],
                            "trial": record["trial"], "item": item, "score": 1,
                            "citation": "MKT narrative for review."})
    scores.write_text(json.dumps({"reviewer": "synthetic-fixture-reviewer",
                                  "answers": answers}), encoding="utf-8")
    attempts = scorer._load_attempts()
    controls = scorer.cohort_controls()
    for attempt in attempts:
        scorer._check_eligibility(attempt, controls)
        assert attempt.eligible, (attempt.run_id, attempt.reasons)
    selected = scorer._cohort(attempts, controls)
    scorer._score_fraction(scores, [a for a in selected if a.eligible and a.outcome == "COMPLETED"])
    assert scorer.main(["score", str(scores)]) == 0
