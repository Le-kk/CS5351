"""Live pytest fixture must not contaminate credentials/redaction (feedback-8).

``tests/conftest.py::_dummy_api_keys`` injects ``"placeholder"`` for missing keys.
For an opted-in live run that fake value enters the Redactor inventory, redacting
benign words ("a placeholder") and giving unconfigured providers fake keys. The
fixture must skip injection ONLY for a ``live``-marked test when ``GOV004_LIVE``
is exactly enabled. Synthetic env only; no .env read, no model calls.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test.offline import conftest as root_conftest  # tests/conftest.py


class _FakeRequest:
    def __init__(self, live: bool):
        self._live = live
        self.node = self

    def get_closest_marker(self, name):
        return object() if (name == "live" and self._live) else None


class _SubEnv:
    """A minimal environ-like object recording what the fixture would set."""

    def __init__(self):
        self.set = {}

    def setenv(self, key, value):
        self.set[key] = value


def _run_fixture(live: bool):
    import inspect

    stub = _SubEnv()
    # Invoke the real fixture body without pytest's direct-call guard.
    body = getattr(root_conftest._dummy_api_keys, "__wrapped__", root_conftest._dummy_api_keys)
    params = list(inspect.signature(body).parameters)
    if "request" in params:
        body(_FakeRequest(live), stub)
    else:  # pre-fix signature: no request guard exists yet
        body(stub)
    return stub.set


def test_opted_in_live_leaves_missing_keys_absent(monkeypatch):
    monkeypatch.setenv("GOV004_LIVE", "1")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    applied = _run_fixture(live=True)
    # No placeholder injected on the live path.
    assert "OPENAI_API_KEY" not in applied
    assert "ANTHROPIC_API_KEY" not in applied


def test_opted_in_live_preserves_real_synthetic_keys(monkeypatch):
    monkeypatch.setenv("GOV004_LIVE", "1")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-real-key-123")
    applied = _run_fixture(live=True)
    # Real (synthetic) provided value untouched; no fake for the others.
    assert applied.get("OPENAI_API_KEY") in (None, "synthetic-real-key-123")
    assert "DEEPSEEK_API_KEY" not in applied


def test_live_marker_without_opt_in_still_gets_placeholders(monkeypatch):
    monkeypatch.setenv("GOV004_LIVE", "0")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    applied = _run_fixture(live=True)
    assert applied.get("OPENAI_API_KEY") == "placeholder"


def test_non_live_test_gets_placeholders(monkeypatch):
    monkeypatch.setenv("GOV004_LIVE", "1")  # even enabled, a non-live test is offline
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    applied = _run_fixture(live=False)
    assert applied.get("OPENAI_API_KEY") == "placeholder"


def test_offline_preserves_configured_value(monkeypatch):
    monkeypatch.setenv("GOV004_LIVE", "0")
    monkeypatch.setenv("OPENAI_API_KEY", "configured-offline-key")
    applied = _run_fixture(live=False)
    # `or` semantics: a real configured value is preserved.
    assert applied.get("OPENAI_API_KEY") == "configured-offline-key"


def test_benign_word_survives_redactor_without_fake_credential(monkeypatch):
    """When no fake credential exists, 'placeholder' is not treated as a secret."""
    monkeypatch.setenv("GOV004_LIVE", "1")
    for name in root_conftest._API_KEY_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    # Do not run the fixture (no injection), mirroring the live path.
    from tradingagents.runapi.redact import Redactor

    text = "the feed returned a placeholder value"
    assert Redactor().scrub(text) == text


def test_fixture_uses_real_gov004_live_semantics(monkeypatch):
    """Guard matches the live conftest's exact 'enabled' test (== '1')."""
    for value, expect_inject in (("1", False), ("0", True), ("", True), ("true", True)):
        monkeypatch.setenv("GOV004_LIVE", value)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        applied = _run_fixture(live=True)
        injected = applied.get("OPENAI_API_KEY") == "placeholder"
        assert injected is expect_inject, (value, applied)
