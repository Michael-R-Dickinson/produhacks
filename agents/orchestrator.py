from uagents import Agent

orchestrator = Agent(
    name="orchestrator",
    seed="orchestrator-agent-seed-investiswarm",
    port=8005,
)

# Phase 1: orchestrator is a stub registered with Bureau for addressability.
# The FastAPI /trigger endpoint handles dispatch directly via push_sse_event().
# Phase 2 will implement ctx.send() dispatch from this agent to domain agents.
