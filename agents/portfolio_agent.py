import os

from uagents import Agent, Context

from agents.bridge.events import push_sse_event
from agents.mocks.portfolio import mock_portfolio_response
from agents.models.events import AgentStatus, MessageDirection, SSEEvent
from agents.models.requests import AnalyzePortfolio
from agents.models.responses import PortfolioResponse

MOCK_DATA = os.getenv("MOCK_DATA", "true").lower() == "true"

portfolio_agent = Agent(
    name="portfolio",
    seed="portfolio-agent-seed-investiswarm",
    port=8001,
)


@portfolio_agent.on_message(model=AnalyzePortfolio, replies={PortfolioResponse})
async def handle_analyze_portfolio(ctx: Context, sender: str, msg: AnalyzePortfolio) -> None:
    agent_id = "portfolio"

    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.WORKING))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent="orchestrator", to_agent=agent_id,
        title="AnalyzePortfolio", description=f"Analyze {len(msg.holdings)} holdings",
        direction=MessageDirection.REQUEST,
    ))
    push_sse_event(SSEEvent.agent_thought(agent_id, "Computing sector allocation and diversification metrics..."))

    if MOCK_DATA or msg.mock:
        response = mock_portfolio_response()
    else:
        # Live implementation in Phase 2
        response = mock_portfolio_response()

    push_sse_event(SSEEvent.agent_thought(agent_id, "Analysis complete."))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent=agent_id, to_agent="orchestrator",
        title="PortfolioResponse", direction=MessageDirection.RESPONSE,
    ))
    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.DONE))

    await ctx.send(sender, response)
