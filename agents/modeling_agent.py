import os

from uagents import Agent, Context

from agents.bridge.events import push_sse_event
from agents.models.events import AgentStatus, MessageDirection, SSEEvent
from agents.models.requests import RunModel
from agents.models.responses import ModelResponse
from agents.modeling_charts import build_model_response


def mock_data_env() -> bool:
    """Read MOCK_DATA at handler time so tests can patch this without reloading the module."""
    return os.getenv("MOCK_DATA", "true").lower() == "true"


modeling_agent = Agent(
    name="modeling",
    seed="modeling-agent-seed-investiswarm",
    port=8003,
)


@modeling_agent.on_message(model=RunModel, replies={ModelResponse})
async def handle_run_model(ctx: Context, sender: str, msg: RunModel) -> None:
    agent_id = "modeling"

    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.WORKING))
    push_sse_event(
        SSEEvent.agent_message(
            agent_id,
            from_agent="orchestrator",
            to_agent=agent_id,
            title="RunModel",
            description=f"Run {msg.analyses} on {len(msg.holdings)} holdings",
            direction=MessageDirection.REQUEST,
        )
    )
    push_sse_event(
        SSEEvent.agent_thought(
            agent_id,
            f"Running {', '.join(msg.analyses)} and computing risk metrics...",
        )
    )

    use_mock = mock_data_env() or msg.mock
    response = build_model_response(msg, use_mock=use_mock)

    push_sse_event(SSEEvent.agent_thought(agent_id, "Analysis complete."))
    push_sse_event(
        SSEEvent.agent_message(
            agent_id,
            from_agent=agent_id,
            to_agent="orchestrator",
            title="ModelResponse",
            description=f"{len(response.charts)} chart(s); Sharpe {response.sharpe_ratio:.2f}",
            direction=MessageDirection.RESPONSE,
        )
    )
    push_sse_event(SSEEvent.agent_status(agent_id, AgentStatus.DONE))

    await ctx.send(sender, response)
