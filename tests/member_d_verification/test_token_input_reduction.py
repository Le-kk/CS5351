"""Regression checks: reduce repetition without removing evidence or tool structure."""
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tradingagents.agents.analysts.turn import WRAP_UP, take_turn
from tradingagents.agents.context import concise_analysis_instruction, opponent_argument_or_opening
from tradingagents.dataflows.config import run_config


@pytest.mark.parametrize('enabled', [True, False])
def test_evidence_occurs_once_only_when_full_argument_is_in_history(enabled):
    evidence = 'Bear Analyst: FY2025 revenue USD 12.5m; source unavailable for Q4.'
    with run_config({'concise_intermediate_reports': enabled}):
        result = opponent_argument_or_opening(evidence, 'bear analyst', evidence)
        assert (result == evidence) is (not enabled)
        assert opponent_argument_or_opening(evidence, 'bear analyst', 'FY2025 revenue') == evidence
        assert 'has not spoken yet' in opponent_argument_or_opening('', 'bear analyst', evidence)


@pytest.mark.parametrize('wrap_up', [True, False])
def test_analyst_keeps_tool_evidence_call_ids_and_input_messages(wrap_up):
    evidence = 'As of 2026-01-09: Close 184.86 USD; vendor: cached Yahoo; news unavailable.'
    messages = [HumanMessage(content='Analyze NVDA'),
                AIMessage(content='', tool_calls=[{'name': 'prices', 'args': {}, 'id': 'call-1'}]),
                ToolMessage(content=evidence, tool_call_id='call-1', name='prices')]
    if wrap_up:
        messages.append(HumanMessage(content=WRAP_UP))
    original = [m.model_dump() for m in messages]
    prompt = ChatPromptTemplate.from_messages([('system', 'Trusted instructions {tool_names}'), MessagesPlaceholder('messages')]).partial(tool_names='prices')
    llm = MagicMock()
    llm.invoke.return_value = llm.bind_tools.return_value.invoke.return_value = AIMessage(content='Complete report')
    with run_config({'concise_intermediate_reports': True}):
        _, report = take_turn(prompt, llm, [], messages)
    captured = (llm.invoke if wrap_up else llm.bind_tools.return_value.invoke).call_args.args[0]
    assert 'Evidence-first brevity' in captured[0].content
    assert evidence in '\n'.join(m.content for m in captured)
    assert [m.model_dump() for m in messages] == original
    assert report == 'Complete report'
    if not wrap_up:
        assert captured[2].tool_calls[0]['id'] == 'call-1'
        assert captured[3].tool_call_id == 'call-1'


def test_legacy_mode_has_no_brevity_instruction():
    with run_config({'concise_intermediate_reports': False}):
        assert concise_analysis_instruction() == ''


def test_mode_is_recorded_in_saved_configuration_and_can_be_disabled(monkeypatch):
    from tradingagents.default_config import build_default_config
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.runapi.execution import _effective_config
    monkeypatch.setenv("TRADINGAGENTS_CONCISE_INTERMEDIATE_REPORTS", "false")
    config = build_default_config()
    assert config["concise_intermediate_reports"] is False
    graph = TradingAgentsGraph.__new__(TradingAgentsGraph)
    graph.config = config
    graph.selected_analysts = ["market", "news", "social", "fundamentals"]
    assert graph.run_settings()["concise_intermediate_reports"] is False
    assert _effective_config(config, graph)["concise_intermediate_reports"] is False


@pytest.mark.parametrize("threshold,expected_copies", [(10000, 1), (20, 2)])
def test_deduplication_never_leaves_a_reference_to_compacted_history(monkeypatch, threshold, expected_copies):
    from tradingagents.agents import context
    argument = "Bear Analyst: the latest dated evidence must remain available."
    history = "Older narrative. " * 50 + argument
    with run_config({"concise_intermediate_reports": True, "context_cap_tokens": 10000,
                     "compaction_threshold_tokens": threshold}):
        reference = opponent_argument_or_opening(argument, "bear analyst", history)
        prompt = history + "\nLatest argument: " + reference
        monkeypatch.setattr(context, "bound_agent_prompt", lambda text: text)
        result = context.bound_debate_prompt(prompt, history, [(argument, "bear analyst")])
    assert result.count(argument) == expected_copies
