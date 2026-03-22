import os

from uagents import Agent, Context

from agents.bridge.events import push_event
from agents.mocks.news import mock_news_response
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
    agent_id = str(ctx.agent.address)

    push_event(agent_id, "status", {"status": "working"})
    push_event(agent_id, "thought", {"text": f"Fetching news for {msg.tickers}..."})
    push_event(agent_id, "message_received", {"from": "orchestrator", "title": "FetchNews request"})

    if MOCK_DATA or msg.mock:
        response = mock_news_response()
    else:
        # Live implementation in Phase 2
        response = mock_news_response()

    push_event(agent_id, "thought", {"text": "Analysis complete."})
    push_event(agent_id, "message_sent", {"to": "orchestrator", "title": "NewsResponse"})
    push_event(agent_id, "status", {"status": "done"})

    await ctx.send(sender, response)
