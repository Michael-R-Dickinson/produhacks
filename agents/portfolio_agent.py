import os

from uagents import Agent, Context

from agents.bridge.events import push_event
from agents.mocks.portfolio import mock_portfolio_response
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
    agent_id = str(ctx.agent.address)

    push_event(agent_id, "status", {"status": "working"})
    push_event(agent_id, "thought", {"text": "Computing sector allocation and diversification metrics..."})
    push_event(agent_id, "message_received", {"from": "orchestrator", "title": "AnalyzePortfolio request"})

    if MOCK_DATA or msg.mock:
        response = mock_portfolio_response()
    else:
        # Live implementation in Phase 2
        response = mock_portfolio_response()

    push_event(agent_id, "thought", {"text": "Analysis complete."})
    push_event(agent_id, "message_sent", {"to": "orchestrator", "title": "PortfolioResponse"})
    push_event(agent_id, "status", {"status": "done"})

    await ctx.send(sender, response)
