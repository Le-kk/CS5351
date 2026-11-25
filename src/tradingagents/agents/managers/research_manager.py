"""Research Manager: turns the bull/bear debate into a structured investment plan for the trader."""

from __future__ import annotations

from tradingagents.agents.context import (
    compact_handoff_instruction,
    get_instrument_context_from_state,
    get_language_instruction,
    get_portfolio_context_from_state,
    protect_context,
)
from tradingagents.agents.schemas import ResearchPlan, render_research_plan
from tradingagents.agents.structured import (
    NO_EXTERNAL_TOOLS,
    bind_structured,
    invoke_structured_or_freetext,
)


def create_research_manager(llm):
    structured_llm = bind_structured(llm, ResearchPlan, "Research Manager")

    def research_manager_node(state) -> dict:
        instrument_context = protect_context(get_instrument_context_from_state(state))
        # The same trusted, user-supplied book the Trader and PM receive. Supplying
        # the facts and a corrective instruction reduces the chance of an ownership
        # error in the plan; it does not guarantee the model's wording (R4).
        portfolio_context = protect_context(get_portfolio_context_from_state(state))
        has_portfolio = bool((state.get("portfolio_context") or "").strip())
        hold_meaning = ("maintain only an explicitly supplied nonzero target position; if flat, remain flat" if has_portfolio else
                        "the evidence supports no new directional action; do not interpret Hold as maintaining an assumed position")
        history = state["investment_debate_state"].get("history", "")

        investment_debate_state = state["investment_debate_state"]

        prompt = f"""As the Research Manager and debate facilitator, your role is to critically evaluate this round of debate and deliver a clear, actionable investment plan for the trader.

{instrument_context}

{portfolio_context}

---

**Rating Scale** (use exactly one):
- **Buy**: Strong conviction in the bull thesis; recommend taking or growing the position
- **Overweight**: Constructive view; recommend gradually increasing exposure
- **Hold**: Balanced view; {hold_meaning}
- **Underweight**: Cautious view; trim only an explicitly supplied existing long position, otherwise avoid entry
- **Sell**: Strong conviction in the bear thesis; recommend exiting or avoiding the position

The debate always contains conflicting arguments; deciding which side is stronger is the job, so conflict alone is not a reason to Hold. Commit to the side with the stronger case, sized by how decisively it wins. Choose Hold only when the evidence is still balanced after that weighing, or too thin to support a call; do not manufacture a direction to appear decisive. Weigh the bull and bear cases on their merits, independent of which side spoke first or last.

The supplied portfolio facts above are authoritative over any ownership premise stated in the debate or later stages: do not assume a position the caller does not hold, do not describe trimming or retaining a nonexistent position, and state cash or holdings the caller did not supply as unknown rather than zero.

---

**Debate History:**
{history}

## Output

Write these sections, in this order, starting with the recommendation on its own line:

- **Recommendation**: exactly one of Buy / Overweight / Hold / Underweight / Sell
- **Rationale**: which arguments decided it
- **Strategic Actions**: concrete steps for the trader, sized against a standard allocation

{NO_EXTERNAL_TOOLS}""" + get_language_instruction() + compact_handoff_instruction("research_manager")

        investment_plan = invoke_structured_or_freetext(
            structured_llm,
            llm,
            prompt,
            render_research_plan,
            "Research Manager",
        )

        new_investment_debate_state = {
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": investment_plan,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": investment_plan,
        }

    return research_manager_node
