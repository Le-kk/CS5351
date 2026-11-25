"""L2 — Fundamentals Analyst period/source consistency (bounded prompt repair).

Approved by the live-found contradiction (deepseek C1 `20261121T095453Z-2a60842e`,
as of 2026-01-09). These scenarios capture the ACTUAL analyst prompt on both the
regular tool-using path and the existing WRAP_UP path, with synthetic dated tool
evidence, and check that the source/period/cutoff/summary contract is in the
SYSTEM message (not accidentally matched from the tool payload). Prompt capture
only; live compliance is the coordinator's to inspect.
"""

from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from tradingagents.agents.analysts.fundamentals_analyst import TOOLS, create_fundamentals_analyst
from tradingagents.agents.analysts.turn import WRAP_UP

pytestmark = pytest.mark.unit

DATED_PACKET = (
    "income_statement: FY2025 Q1 quarter ending 2024-12-31 filed 2025-02-01; "
    "income_statement: latest quarter ending 2025-06-28; "
    "balance_sheet: 2025-09-27; "
    "note: no income statement ending 2025-12-31 is available"
)
POST_CUTOFF_PACKET = (
    "excluded post-cutoff row: quarter ending 2026-03-31 filed 2026-01-29 "
    "revenue $999 (after the analysis date)"
)


class _Capture:
    def __init__(self):
        self.tools = None
        self.prompt = None
        self.bind_tools_called = False
        self.invoke_called = False


def _capture(*, ticker="AAPL", trade_date="2026-01-09", tool_payloads=(DATED_PACKET,),
             company=None):
    cap = _Capture()

    class _Bound:
        def invoke(self, prompt, *a, **k):
            cap.prompt = prompt
            return AIMessage(content="report", tool_calls=[])

    class _LLM:
        def bind_tools(self, tools, *a, **k):
            cap.bind_tools_called = True
            cap.tools = tools
            return _Bound()

        def invoke(self, prompt, *a, **k):
            cap.invoke_called = True
            cap.prompt = prompt
            return AIMessage(content="report")

    messages = [HumanMessage(content=f"Analyze {ticker} fundamentals.")]
    for i, payload in enumerate(tool_payloads):
        messages.append(ToolMessage(content=payload, tool_call_id=f"call-{i}",
                                    name="get_income_statement"))
    state = {
        "company_of_interest": ticker,
        "trade_date": trade_date,
        "asset_type": "stock",
        "instrument_context": "",
        "messages": messages,
    }
    create_fundamentals_analyst(_LLM())(state)
    return cap


def _capture_called():
    """Capture the WRAP_UP path: the last message is the WRAP_UP instruction."""
    cap = _Capture()

    class _LLM:
        def bind_tools(self, tools, *a, **k):  # must NOT be used on wrap-up
            cap.bind_tools_called = True
            return self

        def invoke(self, prompt, *a, **k):
            cap.invoke_called = True
            cap.prompt = prompt
            return AIMessage(content="final report")

    messages = [
        HumanMessage(content="Analyze AAPL fundamentals."),
        ToolMessage(content=DATED_PACKET, tool_call_id="call-0", name="get_income_statement"),
        HumanMessage(content=WRAP_UP),
    ]
    state = {"company_of_interest": "AAPL", "trade_date": "2026-01-09",
             "asset_type": "stock", "instrument_context": "", "messages": messages}
    create_fundamentals_analyst(_LLM())(state)
    return cap


def _system_text(prompt):
    """The SYSTEM message text only (never the tool payload)."""
    if isinstance(prompt, str):
        return prompt
    for message in prompt:
        if getattr(message, "type", "") == "system" or getattr(message, "role", "") == "system":
            return str(getattr(message, "content", message))
    return ""


def _all_text(prompt):
    if isinstance(prompt, str):
        return prompt
    parts = []
    for message in prompt:
        content = getattr(message, "content", message)
        if isinstance(content, list):
            content = " ".join(str(c) for c in content)
        parts.append(str(content))
    return "\n".join(parts)


def _assert_system_contract(system: str):
    """The essential source/period/cutoff/summary contract, grouped in one check."""
    text = system.lower()
    # Dated-period grounding and fiscal-label handling.
    assert "period end" in text and "fiscal label" in text and "filing date" in text
    assert "fiscal-year label" in text and "calendar year" in text
    # Analysis-date cutoff.
    assert "cutoff" in text and "after the analysis" in text
    # Do not claim missing/unfiled periods reported; do not invent release dates.
    assert "missing" in text and "do not claim" in text
    assert "earnings-release date" in text or "earnings release" in text
    # Summary/table/caveat consistency.
    assert "summary" in text and "caveat" in text and "consistent" in text
    # Post-cutoff metadata cannot schedule/forecast timing.
    assert "post-cutoff" in text and "event timing" in text and "earnings schedule" in text
    assert "on or before the cutoff" in text


# --- L2-01: regular tool-using path ----------------------------------------


def test_l2_01_regular_path_system_contract_and_boundaries():
    cap = _capture()
    assert cap.bind_tools_called and not cap.invoke_called
    assert tuple(cap.tools) == TOOLS  # same tool tuple
    system = _system_text(cap.prompt)
    _assert_system_contract(system)
    # Dynamic instrument/analysis date and delegation live in the SYSTEM prompt.
    assert "2026-01-09" in system
    assert "AAPL" in _all_text(cap.prompt)
    assert "delegat" in system.lower() or "another agent decides" in system.lower()


def test_l2_01_full_dated_packet_passes_through_unchanged():
    cap = _capture(tool_payloads=(DATED_PACKET,))
    text = _all_text(cap.prompt)
    # Every dated source value in the packet reaches the model intact.
    for token in ("FY2025 Q1", "2024-12-31", "2025-02-01", "2025-06-28",
                  "2025-09-27", "2025-12-31"):
        assert token in text, token
    # The instruction embeds none of the fixture's dates/figures.
    system = _system_text(cap.prompt)
    for token in ("2024-12-31", "2025-02-01", "2025-06-28", "2025-09-27",
                  "2025-12-31", "December 2025", "FY2025", "FY2026", "fiscal Q1"):
        assert token not in system, token


# --- L2-01/L2-04: existing WRAP_UP path (used by the real live fixtures) ----


def test_l2_01_wrap_up_path_uses_invoke_and_preserves_contract():
    cap = _capture_called()
    # No tool binding on wrap-up; the actual llm.invoke path is taken.
    assert not cap.bind_tools_called
    assert cap.invoke_called
    system = _system_text(cap.prompt)
    _assert_system_contract(system)
    # Dated ToolMessages are written out via _as_text and reach the model.
    text = _all_text(cap.prompt)
    assert "2025-06-28" in text and "2025-09-27" in text
    assert "get_income_statement returned" in text or "2025-06-28" in text


# --- L2-03: missing-data and post-cutoff packets ---------------------------


def test_l2_03_missing_and_post_cutoff_packets_intact_and_no_invention():
    cap = _capture(tool_payloads=(DATED_PACKET, POST_CUTOFF_PACKET))
    text = _all_text(cap.prompt)
    # Both packets survive intact to the model.
    assert "no income statement ending 2025-12-31 is available" in text
    assert "2026-01-29" in text and "$999" in text
    # The system instruction embeds no fixture dates/figures (no fabrication).
    system = _system_text(cap.prompt)
    for token in ("2026-01-29", "$999", "2025-12-31", "2024-12-31"):
        assert token not in system, token
    # The exclusion/timing constraint is specifically in the SYSTEM message.
    _assert_system_contract(system)


# --- L2-01: generality across inputs (not an Apple/year patch) --------------


@pytest.mark.parametrize("ticker,trade_date", [("MSFT", "2024-03-15"), ("7203.T", "2026-08-14")])
def test_l2_01_contract_is_general_across_ticker_and_date(ticker, trade_date):
    cap = _capture(ticker=ticker, trade_date=trade_date)
    system = _system_text(cap.prompt)
    _assert_system_contract(system)
    assert trade_date in system
    # No hardcoded Apple figures/year in the instruction.
    for token in ("AAPL", "2026-01-09", "258.47", "255.33"):
        assert token not in system, token
