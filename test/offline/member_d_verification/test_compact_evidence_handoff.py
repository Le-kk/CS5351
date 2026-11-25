"""Independent negative probes for the opt-in intermediate writing experiment."""
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tradingagents.agents.analysts.turn import take_turn
from tradingagents.agents.context import compact_handoff_instruction, concise_analysis_instruction
from tradingagents.dataflows.config import run_config


def test_disabled_mode_preserves_previous_prompts():
    with run_config({"compact_evidence_handoff": False, "concise_intermediate_reports": True}):
        assert compact_handoff_instruction("analyst") == ""
        assert "450 words" in concise_analysis_instruction()
        assert "220 words" in concise_analysis_instruction("debate")


@pytest.mark.parametrize("stage,target", [("analyst",300), ("debate",140), ("research_manager",220), ("trader",250)])
def test_format_does_not_authorize_dropping_safety_or_evidence(stage, target):
    with run_config({"compact_evidence_handoff": True}):
        text = compact_handoff_instruction(stage)
    assert f"{target} words" in text
    for term in ["source", "fiscal period", "units/basis", "conflicting evidence",
                 "price anchors", "unknown holdings", "required tables", "exceeds"]:
        assert term in text


def test_no_truncation_extra_call_or_hidden_tool_mutation():
    # Deliberately oversized, numerically distinct, contrary/missing evidence.
    report = "FY2026 Q3 USD 57,006m; SEC 2025-10-26. Contrary evidence: debt rises. News unavailable. " * 200
    llm = MagicMock()
    llm.bind_tools.return_value.invoke.return_value = AIMessage(content=report)
    tool = ToolMessage(content="Close 184.428 adjusted USD; source Yahoo; news UNKNOWN.", tool_call_id="e-1")
    messages = [HumanMessage(content="NVDA"), tool]
    before = [m.model_dump() for m in messages]
    prompt = ChatPromptTemplate.from_messages([("system", "Analyze."), MessagesPlaceholder("messages")])
    with run_config({"compact_evidence_handoff": True, "concise_intermediate_reports": True}):
        result, saved = take_turn(prompt, llm, [], messages)
    assert saved == report == result.content
    llm.bind_tools.return_value.invoke.assert_called_once()
    llm.invoke.assert_not_called()
    sent = llm.bind_tools.return_value.invoke.call_args.args[0]
    assert "Compact evidence handoff" in sent[0].content
    assert sent[-1].content == tool.content
    assert [m.model_dump() for m in messages] == before


def test_config_is_opt_in_and_recorded(monkeypatch):
    from tradingagents.default_config import build_default_config
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.runapi.execution import _effective_config
    monkeypatch.delenv("TRADINGAGENTS_COMPACT_EVIDENCE_HANDOFF", raising=False)
    assert build_default_config()["compact_evidence_handoff"] is False
    monkeypatch.setenv("TRADINGAGENTS_COMPACT_EVIDENCE_HANDOFF", "true")
    cfg = build_default_config()
    assert cfg["compact_evidence_handoff"] is True
    graph = TradingAgentsGraph.__new__(TradingAgentsGraph)
    graph.config = cfg
    graph.selected_analysts = ["market"]
    assert graph.run_settings()["compact_evidence_handoff"] is True
    assert _effective_config(cfg, graph)["compact_evidence_handoff"] is True


def test_legacy_master_switch_also_disables_new_format():
    with run_config({"compact_evidence_handoff": True, "concise_intermediate_reports": False}):
        assert concise_analysis_instruction() == ""
        assert compact_handoff_instruction("research_manager") == ""
        assert compact_handoff_instruction("trader") == ""


@pytest.mark.parametrize('enabled', [True, False])
def test_sentiment_separate_structured_path_keeps_sources_and_schema(monkeypatch, enabled):
    import tradingagents.agents.analysts.sentiment_analyst as sentiment
    evidence = 'DATA_UNAVAILABLE; unknown is not neutral; source Yahoo 2026-11-24.'
    monkeypatch.setattr(sentiment.get_news, 'func', lambda *a, **k: evidence)
    monkeypatch.setattr(sentiment, 'fetch_stocktwits_messages', lambda *a, **k: evidence)
    monkeypatch.setattr(sentiment, 'fetch_reddit_posts', lambda *a, **k: evidence)
    monkeypatch.setattr(sentiment, 'jev_screen', lambda *a: None)
    monkeypatch.setattr(sentiment, 'bind_structured', lambda *a: object())
    captured = []
    def invoke(structured, llm, messages, renderer, stage):
        captured.extend(messages)
        assert stage == 'Sentiment Analyst'
        assert renderer is sentiment.render_sentiment_report
        return 'Full sentiment report with all caveats.'
    monkeypatch.setattr(sentiment, 'invoke_structured_or_freetext', invoke)
    with run_config({'compact_evidence_handoff': enabled}):
        result = sentiment.create_sentiment_analyst(object())({
            'company_of_interest': 'NVDA', 'trade_date': '2026-11-24', 'messages': []})
    text = captured[0].content
    assert ('Compact evidence handoff' in text) is enabled
    assert text.count(evidence) == 3
    assert 'overall_band' in text and 'confidence' in text
    assert result['sentiment_report'] == 'Full sentiment report with all caveats.'
