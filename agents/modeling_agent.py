import os

from uagents import Agent, Context

from agents.bridge.events import push_event
from agents.mocks.modeling import mock_model_response
from agents.models.requests import RunModel
from agents.models.responses import ModelResponse

MOCK_DATA = os.getenv("MOCK_DATA", "true").lower() == "true"

modeling_agent = Agent(
    name="modeling",
    seed="modeling-agent-seed-investiswarm",
    port=8003,
)


@modeling_agent.on_message(model=RunModel, replies={ModelResponse})
async def handle_run_model(ctx: Context, sender: str, msg: RunModel) -> None:
    agent_id = str(ctx.agent.address)

    push_event(agent_id, "status", {"status": "working"})
    push_event(agent_id, "thought", {"text": "Running regression and computing risk metrics..."})
    push_event(agent_id, "message_received", {"from": "orchestrator", "title": "RunModel request"})

    if MOCK_DATA or msg.mock:
        response = mock_model_response()
    else:
        # Live implementation in Phase 2
        response = mock_model_response()

    push_event(agent_id, "thought", {"text": "Analysis complete."})
    push_event(agent_id, "message_sent", {"to": "orchestrator", "title": "ModelResponse"})
    push_event(agent_id, "status", {"status": "done"})

    await ctx.send(sender, response)
