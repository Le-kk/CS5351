"""R4 — every decision stage, including the Research Manager, sees the trusted book.

The review reproduced that the Research Manager prompt was identical for a
supplied explicit-empty portfolio and a supplied 40-unit holding: it consumed
only the boolean "a portfolio string exists", so its investment plan could
instruct a trim of a nonexistent position that Trader/PM later contradicted.
These tests capture the actual RM model prompt and assert the facts and the
no-nonzero-target instruction reach it under the same ``protect_context`` seam
as Trader/PM. Fake models only; no provider contact.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage

from tradingagents.agents.managers.portfolio_manager import create_portfolio_manager
from tradingagents.agents.managers.research_manager import create_research_manager
from tradingagents.agents.schemas import (
    PortfolioDecision,
    PortfolioRating,
    ResearchPlan,
    TraderAction,
    TraderProposal,
)
from tradingagents.agents.trader.trader import create_trader
from tradingagents.dataflows.config import run_config
from tradingagents.portfolio import PortfolioContext

pytestmark = pytest.mark.unit

DEBATE = "Bull says the trend is up. Bear says valuation is stretched."


def _state(book) -> dict:
    portfolio = PortfolioContext.model_validate(book) if book is not None else None
    return {
        "company_of_interest": "AAPL",
        "instrument_context": "",
        "market_report": "",
        "investment_plan": "reduce existing exposure",
        "trader_investment_plan": "trim the held position",
        "portfolio_context": portfolio.render("AAPL") if portfolio else "",
        "investment_debate_state": {
            "history": DEBATE, "bull_history": "BULL", "bear_history": "BEAR",
            "current_response": "", "count": 1,
        },
        "risk_debate_state": dict.fromkeys(
            (
                "history", "aggressive_history", "conservative_history", "neutral_history",
                "current_aggressive_response", "current_conservative_response",
                "current_neutral_response",
            ),
            "risk debate text",
        ) | {"count": 1, "latest_speaker": "Neutral"},
    }


def _capturing_llm(result=None):
    captured: dict = {}
    structured = MagicMock()
    structured.invoke.side_effect = lambda prompt: (
        captured.__setitem__("prompt", prompt) or result
    )
    llm = MagicMock()
    llm.with_structured_output.return_value = structured
    llm.invoke.return_value = AIMessage(content="Fallback text.")
    return llm, captured


_RM_PLAN = ResearchPlan(
    recommendation=PortfolioRating.UNDERWEIGHT,
    rationale="Bear case carried on valuation.",
    strategic_actions="Size against a standard allocation.",
)
_TRADER = TraderProposal(action=TraderAction.SELL, reasoning="Avoid entry.")
_PM = PortfolioDecision(
    rating=PortfolioRating.UNDERWEIGHT,
    executive_summary="Avoid entry.",
    investment_thesis="Valuation stretched.",
)


def _prompt_text(prompt) -> str:
    return prompt if isinstance(prompt, str) else "\n".join(m["content"] for m in prompt)


def _rm_prompt(book) -> str:
    llm, captured = _capturing_llm(_RM_PLAN)
    create_research_manager(llm)(_state(book))
    return _prompt_text(captured["prompt"])


def test_r4_01_rm_prompt_distinguishes_absent_empty_and_held():
    absent = _rm_prompt(None)
    empty = _rm_prompt({"positions": []})
    held = _rm_prompt({"positions": [{"ticker": "AAPL", "quantity": 40, "average_price": 190.0}]})

    # Empty and held prompts are no longer identical.
    assert empty != held
    # The absent case is "unknown", never asserted flat.
    assert "no account ownership is assumed" in absent.lower()
    assert "No current position in AAPL" not in absent
    # The empty case carries the no-nonzero-target instruction; the held case does not.
    assert "no nonzero target position" in empty
    assert "no nonzero target position" not in held
    # The held case carries the supplied quantity; the empty case does not invent it.
    assert "40" in held and "40" not in empty


def test_r4_01_all_three_decision_stages_share_the_trusted_facts():
    book = {"positions": [{"ticker": "AAPL", "quantity": 40, "average_price": 190.0}]}
    state = _state(book)
    for factory, result in (
        (create_research_manager, _RM_PLAN),
        (create_trader, _TRADER),
        (create_portfolio_manager, _PM),
    ):
        llm, captured = _capturing_llm(result)
        factory(llm)(state)
        text = _prompt_text(captured["prompt"])
        assert "<protected_context>" in text
        assert "40" in text, f"{factory.__name__} prompt lacks the supplied quantity"


def test_r4_03_all_stages_label_facts_user_supplied_unverified():
    """RM/Trader/PM must label the shared facts as user-supplied and unverified."""
    book = {"positions": [{"ticker": "AAPL", "quantity": 40, "average_price": 190.0}]}
    state = _state(book)
    for factory, result in (
        (create_research_manager, _RM_PLAN),
        (create_trader, _TRADER),
        (create_portfolio_manager, _PM),
    ):
        llm, captured = _capturing_llm(result)
        factory(llm)(state)
        text = _prompt_text(captured["prompt"])
        assert "user-supplied and unverified" in text, factory.__name__


def test_r4_03_unverified_label_survives_compaction():
    state = _state({"positions": [{"ticker": "AAPL", "quantity": 40}]})
    state["investment_debate_state"]["history"] = "opening " * 3000 + "tail " * 3000
    llm, captured = _capturing_llm(_RM_PLAN)
    with run_config({"context_cap_tokens": 3000, "compaction_threshold_tokens": 2500}):
        create_research_manager(llm)(state)
    assert "user-supplied and unverified" in _prompt_text(captured["prompt"])


@pytest.mark.parametrize("book", [
    {"positions": []},
    {"positions": [{"ticker": "MSFT", "quantity": 5}]},
    {"positions": [{"ticker": "AAPL", "quantity": 0}]},
])
def test_r4_02_no_nonzero_target_instruction(book):
    text = _rm_prompt(book)
    assert "no nonzero target position" in text
    assert "there is nothing to trim" in text or "Do not recommend reducing" in text


def test_r4_02_absent_is_unknown_not_flat():
    text = _rm_prompt(None)
    assert "no account ownership is assumed" in text.lower()
    # Unknown is not escalated to the asserted-flat instruction.
    assert "no nonzero target position" not in text


def test_r4_03_signed_quantities_cash_and_unverified_preserved():
    short = _rm_prompt({
        "cash": 0.0, "currency": "USD",
        "positions": [{"ticker": "AAPL", "quantity": -10, "average_price": 150}],
    })
    assert "-10" in short
    assert "Cash available: 0.00 USD" in short

    unknown_cash = _rm_prompt({"positions": [{"ticker": "AAPL", "quantity": 10}]})
    assert "Available funds were not supplied" in unknown_cash
    assert "0.00" not in unknown_cash


def test_r4_04_protected_facts_survive_compaction():
    state = _state({"positions": [{"ticker": "AAPL", "quantity": 40}]})
    # Bury the facts between a long opening and trailing debate so only compaction
    # could drop them, and add conflicting upstream ownership prose elsewhere.
    state["investment_debate_state"]["history"] = (
        "opening " * 2000 + "CONFLICTING: you hold a large position to trim. " + "tail " * 3000
    )
    llm, captured = _capturing_llm(_RM_PLAN)
    with run_config({"context_cap_tokens": 3000, "compaction_threshold_tokens": 2500}):
        create_research_manager(llm)(state)
    text = _prompt_text(captured["prompt"])
    assert len(text) <= 12000
    assert "40" in text
    assert "supplied signed quantities" in text


def test_r4_06_seven_rating_and_three_action_vocabulary_retained():
    text = _rm_prompt({"positions": []})
    for tier in ("Buy", "Overweight", "Hold", "Underweight", "Sell"):
        assert f"**{tier}**" in text


def test_r4_05_report_retains_rm_trader_pm_sections(tmp_path):
    """The delivered report keeps RM/Trader/PM as separate labelled sections."""
    from tradingagents.runapi.context import ConsentState
    from tradingagents.runapi.execution import run_analysis_api
    from tradingagents.runapi.input_service import freeze_explicit

    state = {
        "market_report": "MKT",
        "investment_debate_state": {"bull_history": "BULL", "bear_history": "BEAR"},
        "investment_plan": "**Recommendation**: Underweight\n\nRM stage text.",
        "trader_investment_plan": "**Action**: Sell\n\nTrader stage text.",
        "final_trade_decision": "**Rating**: Underweight\n\nPM stage text.",
        "final_rating": "Underweight",
    }

    class _Engine:
        pass

    factory = lambda *a, **k: _Engine()  # noqa: E731
    runner = lambda g, c: state  # noqa: E731
    ctx = freeze_explicit("AAPL", "2026-11-12", PortfolioContext.model_validate({"positions": []}))
    assert ctx.consent_state == ConsentState.FROZEN
    result = run_analysis_api(
        ctx.confirm(), config={"results_dir": str(tmp_path), "selected_analysts": ["market"]},
        selected_analysts=["market"], graph_factory=factory, engine_runner=runner,
    )
    report = (tmp_path / "AAPL" / result.run_id / "reports" / "complete_report.md").read_text()
    for heading in ("### Research Manager", "### Trader", "### Portfolio Manager"):
        assert heading in report
