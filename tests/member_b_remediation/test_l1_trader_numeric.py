"""L1 — Trader numerical grounding (bounded prompt correction).

Approved by the live-found Trader arithmetic error (C3 `20261121T093733Z-8c832879`:
stop 255.33 described as ~1.5xATR/6.6 points below a 258.47 close with ATR 4.39,
while the real difference is 3.14 = ~0.715xATR). These tests capture the actual
Trader prompt on both the structured and free-text paths. They assert the
instruction reaches the model; they cannot prove live model compliance.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage

from tradingagents.agents.schemas import TraderAction, TraderProposal
from tradingagents.agents.trader.trader import create_trader

pytestmark = pytest.mark.unit

MARKET_REPORT = (
    "AAPL closed at 258.47. ATR(14) = 4.39. Support 255.33, resistance 262.10. "
    "The research plan claims the stop is roughly 1.5xATR (6.6 points) below the close."
)
INVESTMENT_PLAN = (
    "**Recommendation**: Underweight\n"
    "**Rationale**: momentum faded; the stop at 255.33 sits about 1.5xATR below 258.47.\n"
    "**Strategic Actions**: size against a standard allocation."
)
PORTFOLIO_BLOCK = (
    "Portfolio at the analysis date:\n"
    "These holdings and cash are user-supplied and unverified; treat them as the caller's "
    "stated snapshot, not an authenticated account.\n"
    "- Current position in AAPL: 40 units, average price 190.00\n"
    "Available funds were not supplied; do not invent a balance or affordability."
)


def _state():
    return {
        "company_of_interest": "AAPL",
        "instrument_context": "",
        "market_report": MARKET_REPORT,
        "investment_plan": INVESTMENT_PLAN,
        "portfolio_context": PORTFOLIO_BLOCK,
    }


def _structured_llm(captured):
    proposal = TraderProposal(action=TraderAction.SELL, reasoning="Fade.")
    structured = MagicMock()
    structured.invoke.side_effect = lambda prompt: captured.__setitem__("prompt", prompt) or proposal
    llm = MagicMock()
    llm.with_structured_output.return_value = structured
    return llm


def _fallback_llm(captured):
    llm = MagicMock()
    llm.with_structured_output.side_effect = NotImplementedError("no structured output")
    llm.invoke.side_effect = lambda prompt: (captured.__setitem__("prompt", prompt)
                                             or AIMessage(content="**Action**: Sell\n\nFade."))
    return llm


def _prompt_text(prompt) -> str:
    return prompt if isinstance(prompt, str) else "\n".join(m["content"] for m in prompt)


@pytest.mark.parametrize("builder", [_structured_llm, _fallback_llm], ids=["structured", "fallback"])
def test_l1_01_numeric_grounding_reaches_model(builder):
    captured = {}
    create_trader(builder(captured))(_state())
    text = _prompt_text(captured["prompt"]).lower()

    # General instruction to recompute distances/multiples from explicit anchors.
    assert "recompute" in text or "compute" in text
    assert "atr" in text
    # Absolute distance and multiple guidance with the positive-ATR guard.
    assert "absolute" in text or "abs(" in text
    assert "multiple" in text and ("positive" in text or "nonzero" in text)
    # Correct inconsistent upstream arithmetic rather than repeat it.
    assert "upstream" in text or "research" in text
    assert "do not repeat" in text or "not repeat" in text or "correct" in text
    # Never assert guaranteed/locked gains.
    assert "guarantee" in text or "locked" in text
    # Omit unsupported ratios / say unknown.
    assert "unknown" in text or "omit" in text
    # Source values and portfolio facts are preserved.
    for anchor in ("258.47", "255.33", "4.39"):
        assert anchor in text
    assert "40" in text
    assert "user-supplied and unverified" in text


def test_l1_01_no_hardcoded_observed_values_in_instruction():
    """The prompt must be general, not hardcode the observed 3.14/0.715 numbers."""
    captured = {}
    create_trader(_structured_llm(captured))(_state())
    system = "\n".join(m["content"] for m in captured["prompt"] if m["role"] == "system")
    assert "3.14" not in system and "0.715" not in system
    # Absolute-price/action/vocabulary constraints are unchanged.
    assert "absolute price" in system.lower()
    assert "Buy / Hold / Sell" in _prompt_text(captured["prompt"])


def test_l1_04_missing_atr_is_not_required_to_fabricate():
    captured = {}
    state = _state()
    state["market_report"] = "AAPL closed at 258.47. Support 255.33; resistance 262.10."
    create_trader(_structured_llm(captured))(state)
    text = _prompt_text(captured["prompt"]).lower()
    # The instruction still asks to omit/mark-unknown unsupported ratios.
    assert "unknown" in text or "omit" in text
    # No ATR figure is invented into the prompt by our instruction.
    assert "atr(14) = 4.39" not in text


@pytest.mark.parametrize("builder", [_structured_llm, _fallback_llm], ids=["structured", "fallback"])
def test_l1_07_direction_instruction_reaches_model(builder):
    """Compare level vs anchor before calling it above/below; avoid extra claims."""
    captured = {}
    create_trader(builder(captured))(_state())
    text = _prompt_text(captured["prompt"]).lower()
    # General direction rule: below when level < anchor, above when level > anchor.
    assert "below" in text and "above" in text
    assert "anchor" in text
    # Avoid unnecessary extra derived numeric claims not needed for the proposal.
    assert "unnecessary" in text or "not needed" in text or "only the numbers" in text
    # The anchors are still present and no observed numbers are hardcoded.
    for anchor in ("258.47", "255.33"):
        assert anchor in text
    assert "0.72" not in text and "1.21" not in text
