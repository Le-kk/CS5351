"""R1 — structured-binding/invocation warnings must pass through the Redactor.

The review found that ``tradingagents/agents/structured.py`` interpolated the raw
exception into the logger, so a credential-bearing provider error reached normal
logging consumers (stderr handlers) before any report/event redaction. These
tests capture the *actual* ``structured`` logger, not just direct calls to
``Redactor.diagnostic``. Synthetic canaries only; no provider is contacted.
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage

from tradingagents.agents import structured

pytestmark = pytest.mark.unit

LOGGER_NAME = structured.logger.name


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records: list[str] = []

    def emit(self, record):
        self.records.append(record.getMessage())


@pytest.fixture
def captured():
    handler = _Capture()
    logger = logging.getLogger(LOGGER_NAME)
    previous = logger.level
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    try:
        yield handler.records
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)


def _assert_clean(records, planted):
    joined = "\n".join(records)
    for value in planted:
        assert value not in joined, f"synthetic credential survived into logging: {value}"


def test_r1_01_binding_failure_warning_is_redacted(captured, monkeypatch):
    """A provider-prefixed assignment and a configured value in the bind error are scrubbed."""
    configured = "configured-synthetic-canary-556677"
    monkeypatch.setenv("OPENAI_API_KEY", configured)

    class _Unsupported:
        def with_structured_output(self, _schema):
            raise NotImplementedError(
                f"provider refused; OPENAI_API_KEY={configured} bearer {configured}"
            )

    assert structured.bind_structured(_Unsupported(), object, "Research Manager") is None

    # Useful context survives, the planted values do not.
    assert captured, "the binding warning must still be emitted"
    joined = "\n".join(captured)
    assert "Research Manager" in joined and "free-text" in joined
    _assert_clean(captured, {configured})


@pytest.mark.parametrize("error", [
    NotImplementedError("boom OPENAI_API_KEY=synthetic-bind-canary-123456"),
    AttributeError("no binding API_KEY=synthetic-bind-canary-123456"),
])
def test_r1_03_bind_variants_share_the_warning_path(captured, error):
    class _Unsupported:
        def with_structured_output(self, _schema):
            raise error

    assert structured.bind_structured(_Unsupported(), object, "Portfolio Manager") is None
    _assert_clean(captured, {"synthetic-bind-canary-123456"})


def test_r1_02_invocation_failure_is_redacted_and_fallback_preserved(captured):
    canary = "sk-syntheticinvocationcanary1234567890"

    structured_llm = MagicMock()
    structured_llm.invoke.side_effect = RuntimeError(
        f"structured call failed; Authorization: Bearer {canary}"
    )
    plain = MagicMock()
    plain.invoke.return_value = AIMessage(content="**Recommendation**: Hold\n\nUsable fallback.")

    result = structured.invoke_structured_or_freetext(
        structured_llm, plain, "prompt", render=lambda value: value.recommendation,
        agent_name="Research Manager",
    )

    # The usable free-text fallback is preserved.
    assert result == "**Recommendation**: Hold\n\nUsable fallback."
    assert captured, "the invocation warning must still be emitted"
    assert "Research Manager" in "\n".join(captured)
    _assert_clean(captured, {canary})


@pytest.mark.parametrize("secret_text,canaries", [
    ('CLIENT_SECRET="synthetic-multiline-123456\nsecond-line"',
     ["synthetic-multiline-123456", "second-line"]),
    ("Authorization: Basic c3ludGhldGljLWJhc2ljLTEyMzQ1Ng==",
     ["c3ludGhldGljLWJhc2ljLTEyMzQ1Ng=="]),
    ("DEEPSEEK_API_KEY=synthetic-deepseek-123456",
     ["synthetic-deepseek-123456"]),
])
def test_r1_03_invocation_variants_are_redacted(captured, secret_text, canaries):
    structured_llm = MagicMock()
    structured_llm.invoke.side_effect = ValueError(f"provider error: {secret_text}")
    plain = MagicMock()
    plain.invoke.return_value = AIMessage(content="FALLBACK")

    assert structured.invoke_structured(structured_llm, "p", "Trader") is None
    joined = "\n".join(captured)
    for marker in canaries:
        assert marker not in joined, f"planted value survived: {marker}"

    # Benign warning context is not over-scrubbed.
    assert "Trader" in joined and "free text" in joined


def test_r1_04_redactor_construction_failure_falls_back_safely(captured, monkeypatch):
    """If the environment-snapshot redactor cannot be built, no raw error is logged."""
    canary = "synthetic-redactor-fail-canary-24680"

    def boom(*_a, **_k):
        raise RuntimeError("redactor unavailable")

    monkeypatch.setattr(structured, "Redactor", boom)
    assert structured.bind_structured(
        type("U", (), {"with_structured_output": lambda self, s: (_ for _ in ()).throw(
            NotImplementedError(f"OPENAI_API_KEY={canary}"))})(), object, "Trader") is None
    joined = "\n".join(captured)
    assert canary not in joined
    assert "redaction unavailable" in joined
    # The warning still carries useful context.
    assert "Trader" in joined


def test_r1_04_context_identity_debug_is_redacted(captured, monkeypatch):
    """The identity-resolution debug sink is redacted like the structured warnings."""
    from tradingagents.agents import context

    # ``context`` uses its own logger name; capture it directly.
    handler = _Capture()
    logger = logging.getLogger(context.logger.name)
    previous = logger.level
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    canary = "sk-syntheticidentitycanary1234567890"
    try:
        def boom(_ticker):
            raise ValueError(f"provider auth failed: Authorization: Bearer {canary}")

        monkeypatch.setattr(context, "_identity", boom)
        assert context.resolve_instrument_identity("AAPL") == {}
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)

    joined = "\n".join(handler.records)
    assert canary not in joined
    assert "AAPL" in joined
