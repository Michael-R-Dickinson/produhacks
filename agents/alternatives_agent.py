import os

from uagents import Agent, Context

from agents.bridge.events import push_event
from agents.mocks.alternatives import mock_alternatives_response
from agents.models.requests import AnalyzeAlternatives
from agents.models.responses import AlternativesResponse

MOCK_DATA = os.getenv("MOCK_DATA", "true").lower() == "true"

alternatives_agent = Agent(
    name="alternatives",
    seed="alternatives-agent-seed-investiswarm",
    port=8004,
)


@alternatives_agent.on_message(model=AnalyzeAlternatives, replies={AlternativesResponse})
async def handle_analyze_alternatives(ctx: Context, sender: str, msg: AnalyzeAlternatives) -> None:
    agent_id = str(ctx.agent.address)

    push_event(agent_id, "status", {"status": "working"})
    push_event(agent_id, "thought", {"text": "Fetching crypto prices and computing cross-asset correlations..."})
    push_event(agent_id, "message_received", {"from": "orchestrator", "title": "AnalyzeAlternatives request"})

    if MOCK_DATA or msg.mock:
        response = mock_alternatives_response()
    else:
        # Live implementation in Phase 2
        response = mock_alternatives_response()

    push_event(agent_id, "thought", {"text": "Analysis complete."})
    push_event(agent_id, "message_sent", {"to": "orchestrator", "title": "AlternativesResponse"})
    push_event(agent_id, "status", {"status": "done"})

    await ctx.send(sender, response)
