import os

from uagents import Agent, Context

from agents.bridge.events import push_sse_event
from agents.mocks.alternatives import mock_alternatives_response
from agents.models.events import AgentStatus, MessageDirection, SSEEvent
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
    agent_id = "alternatives"

    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.WORKING))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent="orchestrator", to_agent=agent_id,
        title="AnalyzeAlternatives", description="Fetch crypto/commodity data",
        direction=MessageDirection.REQUEST,
    ))
    push_sse_event(SSEEvent.agent_thought(agent_id, "Fetching crypto prices and computing cross-asset correlations..."))

    if MOCK_DATA or msg.mock:
        response = mock_alternatives_response()
    else:
        # Live implementation in Phase 2
        response = mock_alternatives_response()

    push_sse_event(SSEEvent.agent_thought(agent_id, "Analysis complete."))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent=agent_id, to_agent="orchestrator",
        title="AlternativesResponse", direction=MessageDirection.RESPONSE,
    ))
    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.DONE))

    await ctx.send(sender, response)
