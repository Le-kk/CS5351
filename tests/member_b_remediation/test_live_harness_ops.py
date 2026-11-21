"""Live-harness operational repairs (feedback-5): isolation, provider override,
truthful preflight and a safe backend identifier.

Synthetic environment/URLs only; no .env read, no model calls, no credentials.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

LIVE_DIR = Path(__file__).resolve().parents[1] / "member_c_verification" / "live"
sys.path.insert(0, str(LIVE_DIR))

import runner  # noqa: E402

pytestmark = pytest.mark.unit


# --- #1 isolated evidence root ----------------------------------------------


def _outcome_with(tmp_root: Path, run_dir: Path, *, has_artifacts=True):
    from runner import CaseOutcome

    report = manifest = None
    if has_artifacts:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "reports").mkdir(exist_ok=True)
        report = run_dir / "reports" / "complete_report.md"
        report.write_text("# report\n", encoding="utf-8")
        manifest = run_dir / "manifest.json"
        manifest.write_text("{}\n", encoding="utf-8")
    return CaseOutcome(
        case_id="GOV004-C1-no-portfolio", description="d", portfolio_kind="none",
        run_id="run-1", source_revision="git:test", model_config={}, outcome="COMPLETED",
        stop_reason=None, final_rating="Hold", output_check="PASSED", findings=[],
        report_path=str(report) if report else None,
        manifest_path=str(manifest) if manifest else None,
        run_dir=str(run_dir) if has_artifacts else None,
        challenge_marker=None, challenge_reached_model=None,
        prompt_capture={"model_calls": 0, "calls": []}, wall_clock_s=0.1,
    )


def test_outcome_to_dict_uses_explicit_evidence_root(tmp_path):
    root = tmp_path / "fresh-evidence"
    run_dir = root / "runs" / "stamp" / "case" / "AAPL" / "run-1"
    outcome = _outcome_with(root, run_dir)
    record = runner.outcome_to_dict(outcome, evidence_root=root)
    assert record["report_path"] == "runs/stamp/case/AAPL/run-1/reports/complete_report.md"
    assert record["manifest_path"] == "runs/stamp/case/AAPL/run-1/manifest.json"
    assert len(record["report_sha256"]) == 64 and len(record["manifest_sha256"]) == 64


def test_outcome_to_dict_default_root_is_adjacent_evidence(tmp_path):
    """The backward-compatible default remains the adjacent evidence/. """
    run_dir = LIVE_DIR / "evidence" / "runs" / "t" / "case" / "AAPL" / "run-x"
    outcome = _outcome_with(LIVE_DIR / "evidence", run_dir)
    try:
        record = runner.outcome_to_dict(outcome)
        assert record["manifest_path"] == "runs/t/case/AAPL/run-x/manifest.json"
    finally:
        import shutil
        shutil.rmtree(LIVE_DIR / "evidence" / "runs" / "t", ignore_errors=True)


def test_outcome_to_dict_rejects_outside_root(tmp_path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside" / "run-1"
    outcome = _outcome_with(outside, outside)
    with pytest.raises(ValueError):
        runner.outcome_to_dict(outcome, evidence_root=allowed)


# --- #4 safe backend identifier ---------------------------------------------


@pytest.mark.parametrize("url,expected", [
    ("https://user:secretpw@host.example:8080/v1/chat?api_key=sk-hidden", "host.example"),
    ("http://user@host.example:9000/path", "host.example"),
    ("https://llm.cs.cityu.edu.hk/v1", "llm.cs.cityu.edu.hk"),
    ("https://[2001:db8::1]:443/v1", "2001:db8::1"),
    ("not a url with user:pass@host", None),
])
def test_backend_host_strips_userinfo_and_query(monkeypatch, url, expected):
    monkeypatch.setenv("TRADINGAGENTS_LLM_BACKEND_URL", url)
    monkeypatch.setenv("TRADINGAGENTS_LLM_PROVIDER", "p")
    monkeypatch.setenv("TRADINGAGENTS_DEEP_THINK_LLM", "m")
    monkeypatch.setenv("TRADINGAGENTS_QUICK_THINK_LLM", "m")
    config = runner._model_config_from_env()
    assert config["backend_host"] == expected
    serialized = str(config)
    for secret in ("secretpw", "sk-hidden", "user:pass", "api_key="):
        assert secret not in serialized


def test_backend_host_absent_is_none(monkeypatch):
    monkeypatch.delenv("TRADINGAGENTS_LLM_BACKEND_URL", raising=False)
    monkeypatch.setenv("TRADINGAGENTS_LLM_PROVIDER", "p")
    monkeypatch.setenv("TRADINGAGENTS_DEEP_THINK_LLM", "m")
    monkeypatch.setenv("TRADINGAGENTS_QUICK_THINK_LLM", "m")
    assert runner._model_config_from_env()["backend_host"] is None


# --- #2 explicit provider override after safe restore -----------------------


def _load_live_conftest():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "live_conftest_ops", LIVE_DIR / "conftest.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_no_override_keeps_saved_settings():
    conftest = _load_live_conftest()
    saved = {
        "TRADINGAGENTS_LLM_PROVIDER": "openai_compatible",
        "TRADINGAGENTS_DEEP_THINK_LLM": "saved-deep",
        "TRADINGAGENTS_QUICK_THINK_LLM": "saved-quick",
        "TRADINGAGENTS_DEEP_THINK_PROVIDER": "other-deep",
    }
    before = dict(saved)
    conftest._apply_llm_provider_override(saved)
    assert saved == before  # untouched


def test_explicit_deepseek_override_selects_provider_only():
    conftest = _load_live_conftest()
    env = {
        "TRADINGAGENTS_LLM_PROVIDER": "openai_compatible",
        "TRADINGAGENTS_DEEP_THINK_LLM": "saved-deep",
        "TRADINGAGENTS_QUICK_THINK_LLM": "saved-quick",
        "GOV004_LLM_PROVIDER": "deepseek",
    }
    conftest._apply_llm_provider_override(env)
    assert env["TRADINGAGENTS_LLM_PROVIDER"] == "deepseek"
    # Model IDs are NOT overwritten: saved/caller model IDs must still reach
    # strict fixed-config validation (bad IDs must not be silently repaired).
    assert env["TRADINGAGENTS_DEEP_THINK_LLM"] == "saved-deep"
    assert env["TRADINGAGENTS_QUICK_THINK_LLM"] == "saved-quick"


def test_override_clears_conflicting_tier_providers():
    conftest = _load_live_conftest()
    env = {
        "TRADINGAGENTS_LLM_PROVIDER": "openai_compatible",
        "TRADINGAGENTS_DEEP_THINK_PROVIDER": "openai_compatible",
        "TRADINGAGENTS_QUICK_THINK_PROVIDER": "anthropic",
        "GOV004_LLM_PROVIDER": "deepseek",
    }
    conftest._apply_llm_provider_override(env)
    # Both tier providers agree with the requested provider (effective adapter).
    assert env["TRADINGAGENTS_DEEP_THINK_PROVIDER"] == "deepseek"
    assert env["TRADINGAGENTS_QUICK_THINK_PROVIDER"] == "deepseek"


def test_provider_override_does_not_touch_credentials():
    conftest = _load_live_conftest()
    env = {"GOV004_LLM_PROVIDER": "deepseek",
           "OPENAI_API_KEY": "caller-supplied-placeholder"}
    conftest._apply_llm_provider_override(env)
    assert env["OPENAI_API_KEY"] == "caller-supplied-placeholder"


def test_wrong_saved_model_with_override_keeps_wrong_id(monkeypatch):
    """A wrong saved model + override retains the wrong model (no silent repair)."""
    conftest = _load_live_conftest()
    env = {
        "TRADINGAGENTS_LLM_PROVIDER": "openai_compatible",
        "TRADINGAGENTS_DEEP_THINK_LLM": "totally-wrong-model",
        "TRADINGAGENTS_QUICK_THINK_LLM": "totally-wrong-model",
        "GOV004_LLM_PROVIDER": "deepseek",
    }
    conftest._apply_llm_provider_override(env)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    model_config = runner._model_config_from_env()
    # The wrong model survives to strict validation (which would reject it).
    assert model_config["deep_think_llm"] == "totally-wrong-model"
    assert model_config["deep_think_llm"] != "CS5351/DeepSeek-V4-Flash"


def test_live_config_sets_effective_tier_providers(monkeypatch, tmp_path):
    """_live_config reflects the effective tier providers so adapter == recorded."""
    env = {
        "TRADINGAGENTS_LLM_PROVIDER": "deepseek",
        "TRADINGAGENTS_DEEP_THINK_PROVIDER": "deepseek",
        "TRADINGAGENTS_QUICK_THINK_PROVIDER": "deepseek",
        "TRADINGAGENTS_DEEP_THINK_LLM": "m",
        "TRADINGAGENTS_QUICK_THINK_LLM": "m",
    }
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    config = runner._live_config(str(tmp_path))
    from tradingagents.llm_clients.factory import tier_provider
    assert tier_provider(config, "deep") == "deepseek"
    assert tier_provider(config, "quick") == "deepseek"


def test_live_config_clears_stale_tier_provider_on_override(monkeypatch, tmp_path):
    """Even if DEFAULT_CONFIG folded a stale tier override at import, the effective
    config for an explicit provider override uses that provider on both tiers."""
    # Simulate an explicit override environment where tier providers are cleared.
    env = {
        "TRADINGAGENTS_LLM_PROVIDER": "deepseek",
        "TRADINGAGENTS_DEEP_THINK_PROVIDER": "",
        "TRADINGAGENTS_QUICK_THINK_PROVIDER": "",
        "TRADINGAGENTS_DEEP_THINK_LLM": "m",
        "TRADINGAGENTS_QUICK_THINK_LLM": "m",
    }
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    config = runner._live_config(str(tmp_path))
    from tradingagents.llm_clients.factory import tier_provider
    assert tier_provider(config, "deep") == "deepseek"
    assert tier_provider(config, "quick") == "deepseek"
