import os

from uagents import Agent, Context

from agents.bridge.events import push_sse_event
from agents.mocks.news import mock_news_response
from agents.models.events import AgentStatus, MessageDirection, SSEEvent
from agents.models.requests import FetchNews
from agents.models.responses import NewsResponse

MOCK_DATA = os.getenv("MOCK_DATA", "true").lower() == "true"

news_agent = Agent(
    name="news",
    seed="news-agent-seed-investiswarm",
    port=8002,
)


@news_agent.on_message(model=FetchNews, replies={NewsResponse})
async def handle_fetch_news(ctx: Context, sender: str, msg: FetchNews) -> None:
    agent_id = "news"

    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.WORKING))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent="orchestrator", to_agent=agent_id,
        title="FetchNews", description=f"Fetch news for {msg.tickers}",
        direction=MessageDirection.REQUEST,
    ))
    push_sse_event(SSEEvent.agent_thought(agent_id, f"Fetching news for {msg.tickers}..."))

    if MOCK_DATA or msg.mock:
        response = mock_news_response()
    else:
        # Live implementation in Phase 2
        response = mock_news_response()

    push_sse_event(SSEEvent.agent_thought(agent_id, "Analysis complete."))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent=agent_id, to_agent="orchestrator",
        title="NewsResponse", direction=MessageDirection.RESPONSE,
    ))
    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.DONE))

    await ctx.send(sender, response)
