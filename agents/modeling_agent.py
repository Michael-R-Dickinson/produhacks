import os

from uagents import Agent, Context

from agents.bridge.events import push_sse_event
from agents.mocks.modeling import mock_model_response
from agents.models.events import AgentStatus, MessageDirection, SSEEvent
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
    agent_id = "modeling"

    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.WORKING))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent="orchestrator", to_agent=agent_id,
        title="RunModel", description=f"Run {msg.analyses} on {len(msg.holdings)} holdings",
        direction=MessageDirection.REQUEST,
    ))
    push_sse_event(SSEEvent.agent_thought(
        agent_id,
        f"Loading {msg.lookback_days}-day price history for {len(msg.holdings)} holdings...",
    ))

    if MOCK_DATA or msg.mock:
        response = mock_model_response()
    else:
        # Live implementation in Phase 2
        response = mock_model_response()

    push_sse_event(SSEEvent.agent_thought(agent_id, f"Running {', '.join(msg.analyses)} analysis..."))
    push_sse_event(SSEEvent.agent_thought(agent_id, f"Sharpe ratio: {response.sharpe_ratio:.2f} -- above benchmark threshold"))
    push_sse_event(SSEEvent.agent_thought(agent_id, f"Volatility: {response.volatility * 100:.1f}% annualized -- moderate risk profile"))
    push_sse_event(SSEEvent.agent_thought(
        agent_id,
        f"Chart generated: {response.charts[0].title}" if response.charts else "Chart generated: Portfolio analysis",
    ))
    push_sse_event(SSEEvent.agent_message(
        agent_id, from_agent=agent_id, to_agent="orchestrator",
        title="ModelResponse", direction=MessageDirection.RESPONSE,
    ))
    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.DONE))

    await ctx.send(sender, response)
