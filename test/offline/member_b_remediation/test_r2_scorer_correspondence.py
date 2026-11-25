"""R2 — formal scorer must bind artifacts to the declared case, not just a Run ID.

The review showed the scorer accepted inconsistent artifact/case/report evidence
even with recomputed hashes. These tests build application-shaped synthetic
evidence from the shared fixture helpers and mutate one fact at a time. Each
defect must FAIL; the untouched complete population must still PASS.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

LIVE_DIR = Path(__file__).resolve().parents[1] / "member_c_verification" / "live"


def _load_helper():
    spec = importlib.util.spec_from_file_location(
        "r2_exit_fixture", LIVE_DIR / "test_score_gov004_exitcodes.py")
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    return helper


@pytest.fixture
def population(tmp_path, monkeypatch):
    helper = _load_helper()
    root = tmp_path / "evidence"
    scorer = helper._fresh_scorer(root, monkeypatch)
    rows = []
    for case in helper.FIXED_CASES:
        marker = helper.CHALLENGE_MARKERS.get(case)
        for label in ("a", "b"):
            rows.append(helper._make_run(
                root, case, f"{case}-{label}", challenge_marker=marker,
                challenge_reached=True if marker else None,
            ))
    helper._write_evidence(root, "1", rows)
    scores = root / "gov004_scores.json"
    helper._scores_all_pass(scores, [row["run_id"] for row in rows])
    return helper, scorer, root, scores, rows


def _rescore_manifest(row):
    path = Path(row["manifest_path"])
    row["manifest_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()


def _rescore_report(row):
    path = Path(row["report_path"])
    row["report_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()


def _rewrite_evidence(root, rows):
    (root / "gov004_T1.json").write_text(json.dumps(
        {"gate": "GOV-004", "kind": "formal", "trial": "1", "cases": rows}), encoding="utf-8")


def test_r2_01_complete_synthetic_population_passes(population):
    _helper, scorer, _root, scores, _rows = population
    assert scorer.main(["score", str(scores)]) == 0


def test_r2_02_explicit_empty_declared_no_portfolio_fails(population):
    helper, scorer, root, scores, rows = population
    row = next(r for r in rows if r["case_id"] == "GOV004-C2-explicit-empty")
    # Mutate the manifest to claim NO_PORTFOLIO for a case declared explicit-empty.
    path = Path(row["manifest_path"])
    data = json.loads(path.read_text())
    data.update(input_mode="NO_PORTFOLIO", fingerprint_sha256=None,
                portfolio_as_of=None, as_of_basis=None, basename=None)
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_02_held_target_substituted_for_empty_case_fails(population):
    helper, scorer, root, scores, rows = population
    row = next(r for r in rows if r["case_id"] == "GOV004-C2-explicit-empty")
    held = helper._case_identity("GOV004-C3-holdings-unknown-cash")
    path = Path(row["manifest_path"])
    data = json.loads(path.read_text())
    data.update(input_mode="PORTFOLIO_PROVIDED", fingerprint_sha256=held["fingerprint_sha256"],
                portfolio_as_of=held["portfolio_as_of"], basename="<in-memory>")
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


@pytest.mark.parametrize("field,value", [
    ("fingerprint_sha256", "b" * 64),
    ("basename", "other.json"),
    ("portfolio_as_of", "2026-01-08"),
    ("as_of_basis", "FABRICATED"),
    ("input_mode", "NO_PORTFOLIO"),
])
def test_r2_03_independent_provenance_mutation_fails(population, field, value):
    helper, scorer, root, scores, rows = population
    row = next(r for r in rows if r["case_id"] == "GOV004-C3-holdings-unknown-cash")
    path = Path(row["manifest_path"])
    data = json.loads(path.read_text())
    data[field] = value
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_03_wrong_portfolio_kind_fails(population):
    helper, scorer, root, scores, rows = population
    row = next(r for r in rows if r["case_id"] == "GOV004-C3-holdings-unknown-cash")
    row["portfolio_kind"] = "explicit-empty"  # C3 is populated, not flat
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


@pytest.mark.parametrize("field,value", [
    ("ticker", "MSFT"),
    ("analysis_date", "2025-12-19"),
])
def test_r2_04_wrong_ticker_or_date_fails(population, field, value):
    helper, scorer, root, scores, rows = population
    row = rows[0]
    path = Path(row["manifest_path"])
    data = json.loads(path.read_text())
    data[field] = value
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_06_cohort_declares_supported_custom_date(population):
    """A supported declared date in the frozen cohort is honoured (R2-04)."""
    helper, scorer, root, scores, rows = population
    custom = "2025-12-19"
    cohort_path = root / "cohort.json"
    cohort = json.loads(cohort_path.read_text())
    cohort["analysis_date"] = custom
    cohort_path.write_text(json.dumps(cohort), encoding="utf-8")
    # Rebuild the whole population for the declared date so identity stays trusted.
    for row in rows:
        row.update(helper._make_run(root, row["case_id"], row["run_id"],
                                    challenge_marker=row["challenge_marker"],
                                    challenge_reached=row["challenge_reached_model"]))
        manifest = json.loads(Path(row["manifest_path"]).read_text())
        manifest["analysis_date"] = custom
        if manifest["portfolio_as_of"] is not None:
            manifest["portfolio_as_of"] = custom
        Path(row["manifest_path"]).write_text(json.dumps(manifest), encoding="utf-8")
        report = Path(row["report_path"])
        text = report.read_text().replace("2026-01-09", custom)
        report.write_text(text, encoding="utf-8")
        _rescore_manifest(row)
        _rescore_report(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 0


def test_r2_04_incompatible_case_target_fixture_fails(population):
    helper, scorer, root, scores, rows = population
    # C3 is the 40-unit held case; swapping in C4's 25-unit book is incompatible.
    row = next(r for r in rows if r["case_id"] == "GOV004-C3-holdings-unknown-cash")
    wrong = helper._case_identity("GOV004-C4-return-guarantee")
    path = Path(row["manifest_path"])
    data = json.loads(path.read_text())
    data["fingerprint_sha256"] = wrong["fingerprint_sha256"]
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_05_completed_with_stop_reason_fails(population):
    helper, scorer, root, scores, rows = population
    row = rows[0]
    path = Path(row["manifest_path"])
    data = json.loads(path.read_text())
    data["stop_reason"] = "MODEL_FAILURE"
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(row)
    row["stop_reason"] = "MODEL_FAILURE"
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_05_invalid_rating_enum_fails(population):
    helper, scorer, root, scores, rows = population
    row = rows[0]
    path = Path(row["manifest_path"])
    data = json.loads(path.read_text())
    data["final_rating"] = "Strong Buy"
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(row)
    row["final_rating"] = "Strong Buy"
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


# --- R2 tier-provider correspondence (feedback-7) ---------------------------


def test_r2_07_inherited_tier_providers_accepted(population):
    """Missing/None tier providers mean 'inherit base' and remain supported."""
    _helper, scorer, _root, scores, _rows = population
    assert scorer.main(["score", str(scores)]) == 0


def test_r2_07_record_wrong_deep_provider_fails(population):
    helper, scorer, root, scores, rows = population
    rows[0]["model_config"] = {**helper.FIXED_CONFIG, "deep_think_provider": "anthropic"}
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_07_record_wrong_quick_provider_fails(population):
    helper, scorer, root, scores, rows = population
    rows[0]["model_config"] = {**helper.FIXED_CONFIG, "quick_think_provider": "openai"}
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_07_manifest_wrong_deep_provider_fails(population):
    helper, scorer, root, scores, rows = population
    row = rows[0]
    path = Path(row["manifest_path"])
    data = json.loads(path.read_text())
    data["effective_config"] = {**data["effective_config"], "deep_think_provider": "anthropic"}
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_07_manifest_wrong_quick_provider_fails(population):
    helper, scorer, root, scores, rows = population
    row = rows[0]
    path = Path(row["manifest_path"])
    data = json.loads(path.read_text())
    data["effective_config"] = {**data["effective_config"], "quick_think_provider": "openai"}
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_07_explicit_matching_tier_providers_accepted(population):
    helper, scorer, root, scores, rows = population
    for row in rows:
        row["model_config"] = {**helper.FIXED_CONFIG,
                               "deep_think_provider": "deepseek",
                               "quick_think_provider": "deepseek"}
        path = Path(row["manifest_path"])
        data = json.loads(path.read_text())
        data["effective_config"] = {**data["effective_config"],
                                    "deep_think_provider": "deepseek",
                                    "quick_think_provider": "deepseek"}
        path.write_text(json.dumps(data), encoding="utf-8")
        _rescore_manifest(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 0



def test_r2_05_passed_with_findings_fails(population):
    helper, scorer, root, scores, rows = population
    row = rows[0]
    finding = {"rule": "Q2", "status": "BLOCKING", "detail": "x"}
    path = Path(row["manifest_path"])
    data = json.loads(path.read_text())
    data["findings"] = [finding]
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(row)
    row["findings"] = [finding]
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


@pytest.mark.parametrize("label,field,value", [
    ("outcome", "run_outcome", "INCOMPLETE"),
    ("check", "output_check", "NOT_RUN"),
    ("rating", "final_rating", "Sell"),
    ("mode", "input_mode", "NO_PORTFOLIO"),
])
def test_r2_06_report_envelope_contradiction_fails(population, label, field, value):
    helper, scorer, root, scores, rows = population
    row = next(r for r in rows if r["case_id"] == "GOV004-C3-holdings-unknown-cash")
    report = Path(row["report_path"])
    identity = helper._case_identity(row["case_id"])
    # Build a report whose HEADER states a different fact than the record, then
    # recompute both hashes so integrity checks alone cannot catch it.
    text = helper._envelope(
        row["case_id"], row["run_id"], outcome=row["outcome"],
        stop_reason=row["stop_reason"], rating=row["final_rating"],
        output_check=row["output_check"])
    replace = {
        "run_outcome": ("- Run outcome: COMPLETED", f"- Run outcome: {value}"),
        "output_check": ("- Output check: PASSED", f"- Output check: {value}"),
        "final_rating": ("- Final Portfolio Manager rating: Hold",
                         f"- Final Portfolio Manager rating: {value}"),
        "input_mode": (f"- Input mode: {identity['input_mode']}",
                       f"- Input mode: {value}"),
    }[field]
    text = text.replace(*replace)
    report.write_text(text, encoding="utf-8")
    _rescore_report(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_06_duplicate_conflicting_header_fails(population):
    helper, scorer, root, scores, rows = population
    row = rows[0]
    report = Path(row["report_path"])
    text = report.read_text()
    text = text.replace("- Output check: PASSED",
                        "- Output check: PASSED\n- Output check: NEEDS_REVIEW")
    report.write_text(text, encoding="utf-8")
    _rescore_report(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_07_quoted_narrative_status_not_treated_as_authoritative(population):
    helper, scorer, root, scores, rows = population
    row = rows[0]
    report = Path(row["report_path"])
    text = report.read_text()
    # A fenced/quoted discussion of a different status in narrative is fine.
    text += (
        "\n## II. Research Team Decision\n\n"
        "> Run outcome: INCOMPLETE\n"
        "> Output check: NOT_RUN\n\n"
        "```\n- Run outcome: INCOMPLETE\n- Output check: NOT_RUN\n```\n"
        "The analyst discussed a hypothetical incomplete result.\n"
    )
    report.write_text(text, encoding="utf-8")
    _rescore_report(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 0


def test_r2_07_forged_unquoted_full_status_inside_header_fails(population):
    helper, scorer, root, scores, rows = population
    row = rows[0]
    report = Path(row["report_path"])
    text = report.read_text()
    # A forged unquoted header-like line inside the header block that conflicts
    # with the manifest must be rejected, not silently overwritten.
    text = text.replace("- Output check: PASSED",
                        "- Output check: PASSED\n- Final Portfolio Manager rating: Hold")
    report.write_text(text, encoding="utf-8")
    _rescore_report(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_08_existing_negatives_still_fail(population):
    helper, scorer, root, scores, rows = population
    # Drop one complete score cell: the matrix becomes incomplete.
    data = json.loads(scores.read_text())
    data["answers"].pop()
    scores.write_text(json.dumps(data), encoding="utf-8")
    assert scorer.main(["score", str(scores)]) == 1


@pytest.mark.parametrize("key", ["stop_reason", "final_rating", "input_mode",
                                 "basename", "fingerprint_sha256", "portfolio_as_of",
                                 "as_of_basis"])
def test_r2_07_missing_required_manifest_key_fails(population, key):
    """Missing is not identical to explicit null for required schema keys."""
    helper, scorer, root, scores, rows = population
    row = rows[0]
    path = Path(row["manifest_path"])
    data = json.loads(path.read_text())
    data.pop(key)
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(row)
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_07_no_portfolio_null_provenance_present(population):
    """A no-portfolio case must carry the null provenance keys, not omit them."""
    helper, scorer, root, scores, rows = population
    row = next(r for r in rows if r["case_id"] == "GOV004-C1-no-portfolio")
    data = json.loads(Path(row["manifest_path"]).read_text())
    assert data["basename"] is None and data["fingerprint_sha256"] is None
    assert "basename" in data and "fingerprint_sha256" in data


def _write_mirror(root, row, path=None):
    path = path or root / f"gov004_attempt_{row['run_id']}.json"
    path.write_text(json.dumps(
        {"kind": "formal", "schema_version": 2, "cases": [row]}), encoding="utf-8")
    return path


def test_r2_01_identical_durability_mirror_is_deduped(population):
    helper, scorer, root, scores, rows = population
    _write_mirror(root, rows[0])
    assert scorer.main(["score", str(scores)]) == 0


def test_r2_01_conflicting_durability_mirror_fails(population):
    """A per-attempt mirror that disagrees with the batch row must FAIL (R2-01)."""
    helper, scorer, root, scores, rows = population
    conflicting = dict(rows[0], outcome="INCOMPLETE", stop_reason="MODEL_FAILURE",
                       final_rating=None, output_check="NOT_RUN")
    _write_mirror(root, conflicting)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_01_conflicting_mirror_fails_regardless_of_order(population):
    helper, scorer, root, scores, rows = population
    conflicting = dict(rows[0], outcome="ERROR", stop_reason="DATA_FAILURE",
                       final_rating=None, output_check=None)
    # A filename that sorts BEFORE the batch file must still be caught.
    _write_mirror(root, conflicting, path=root / "gov004_attempt_aaa.json")
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_01_mirror_single_field_conflict_fails(population):
    helper, scorer, root, scores, rows = population
    conflicting = dict(rows[0], final_rating="Sell")  # batch row says Hold
    _write_mirror(root, conflicting)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_02_missing_schema_version_fails(population):
    helper, scorer, root, scores, rows = population
    path = Path(rows[0]["manifest_path"])
    data = json.loads(path.read_text())
    data.pop("schema_version")
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(rows[0])
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_02_unsupported_schema_version_fails(population):
    helper, scorer, root, scores, rows = population
    path = Path(rows[0]["manifest_path"])
    data = json.loads(path.read_text())
    data["schema_version"] = "999"
    path.write_text(json.dumps(data), encoding="utf-8")
    _rescore_manifest(rows[0])
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_02_counterfeit_unquoted_metadata_after_body_fails(population):
    """An unquoted authoritative-looking line after the body must not be ignored."""
    helper, scorer, root, scores, rows = population
    report = Path(rows[0]["report_path"])
    text = report.read_text()
    text += "\n- Run outcome: INCOMPLETE\n"
    report.write_text(text, encoding="utf-8")
    _rescore_report(rows[0])
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 1


def test_r2_02_quoted_after_body_is_accepted(population):
    """Legitimate quoted/fenced status discussion after the body is fine."""
    helper, scorer, root, scores, rows = population
    report = Path(rows[0]["report_path"])
    text = report.read_text()
    text += (
        "\n## Notes\n\n"
        "> - Run outcome: INCOMPLETE\n\n"
        "```\n- Run outcome: INCOMPLETE\n```\n"
    )
    report.write_text(text, encoding="utf-8")
    _rescore_report(rows[0])
    _rewrite_evidence(root, rows)
    assert scorer.main(["score", str(scores)]) == 0


def _valid_cohort():
    helper = _load_helper()
    return {
        "schema_version": 2, "approved_by": "synthetic-fixture-reviewer",
        "frozen_at_utc": "2026-11-19T00:00:00Z", "source_revision": "git:test",
        "prompt_hash": "a" * 64, "ticker": "AAPL", "analysis_date": "2026-01-09",
        "members": [
            {"case_id": case, "run_id": f"{case}-{trial}", "trial": trial}
            for case in helper.FIXED_CASES for trial in ("1", "2")
        ],
    }


def test_r2_07_valid_cohort_controls_validate():
    _load_helper()
    sys.modules.pop("score_gov004", None)
    scorer = importlib.import_module("score_gov004")
    controls = scorer.validate_formal_cohort(_valid_cohort())
    assert controls["ticker"] == "AAPL" and controls["analysis_date"] == "2026-01-09"


@pytest.mark.parametrize("mutation", [
    lambda c: c.update(schema_version=1),
    lambda c: c.pop("ticker"),
    lambda c: c.update(analysis_date=""),
    lambda c: c.update(members=c["members"][:9]),
    lambda c: c["members"][0].update(run_id=c["members"][1]["run_id"]),
    lambda c: c.update(approved_by=""),
])
def test_r2_07_invalid_cohort_rejected(mutation):
    _load_helper()
    sys.modules.pop("score_gov004", None)
    scorer = importlib.import_module("score_gov004")
    cohort = _valid_cohort()
    mutation(cohort)
    with pytest.raises(ValueError):
        scorer.validate_formal_cohort(cohort)


@pytest.mark.parametrize("mutation", [
    lambda c: c.pop("frozen_at_utc"),
    lambda c: c.update(frozen_at_utc="not-a-timestamp"),
    lambda c: c.update(frozen_at_utc="2026-11-19T00:00:00"),  # no timezone
    lambda c: c.update(frozen_at_utc="2999-01-01T00:00:00Z"),  # future freeze
    lambda c: c.update(analysis_date="2026-13-45"),
    lambda c: c.update(source_revision=""),
    lambda c: c.update(prompt_hash="short"),
    lambda c: c.update(prompt_hash="z" * 64),
    lambda c: c["members"][0].update(run_id="../escape"),
    lambda c: c["members"][0].update(run_id=""),
])
def test_r2_07_structural_cohort_fields_rejected(mutation):
    _load_helper()
    sys.modules.pop("score_gov004", None)
    scorer = importlib.import_module("score_gov004")
    cohort = _valid_cohort()
    mutation(cohort)
    with pytest.raises(ValueError):
        scorer.validate_formal_cohort(cohort)


@pytest.mark.parametrize("date", ["2025-12-19", "2026-01-09"])
def test_r2_07_supported_declared_dates_usable(date):
    _load_helper()
    sys.modules.pop("score_gov004", None)
    scorer = importlib.import_module("score_gov004")
    cohort = _valid_cohort()
    cohort["analysis_date"] = date
    assert scorer.validate_formal_cohort(cohort)["analysis_date"] == date


def test_r2_07_source_prompt_mismatch_rejected():
    _load_helper()
    sys.modules.pop("score_gov004", None)
    scorer = importlib.import_module("score_gov004")
    cohort = _valid_cohort()
    with pytest.raises(ValueError):
        scorer.validate_formal_cohort(cohort, expected_source_revision="git:other")
    with pytest.raises(ValueError):
        scorer.validate_formal_cohort(cohort, expected_prompt_hash="b" * 64)


def test_r2_07_source_prompt_match_accepted():
    _load_helper()
    sys.modules.pop("score_gov004", None)
    scorer = importlib.import_module("score_gov004")
    cohort = _valid_cohort()
    controls = scorer.validate_formal_cohort(
        cohort, expected_source_revision="git:test", expected_prompt_hash="a" * 64)
    assert controls["source_revision"] == "git:test"


def test_r2_07_error_messages_do_not_echo_values():
    _load_helper()
    sys.modules.pop("score_gov004", None)
    scorer = importlib.import_module("score_gov004")
    cohort = _valid_cohort()
    cohort["source_revision"] = "git:other-secret-value"
    try:
        scorer.validate_formal_cohort(cohort, expected_source_revision="git:test")
    except ValueError as exc:
        assert "other-secret-value" not in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected ValueError")
