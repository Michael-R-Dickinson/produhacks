import asyncio
import json

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

app = FastAPI(title="InvestiSwarm Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_private_network=True,
)

event_queue: asyncio.Queue = asyncio.Queue()


@app.on_event("startup")
async def on_startup() -> None:
    """Capture the FastAPI event loop so Bureau thread can push events into it."""
    import agents.bridge.events as ev
    ev._fastapi_loop = asyncio.get_running_loop()
    ev._event_queue = event_queue


@app.get("/events")
async def sse_events(request: Request) -> EventSourceResponse:
    async def generate():
        # Send a comment ping immediately so ASGI headers are flushed to the client.
        # Without this, EventSourceResponse delays headers until the first real event.
        yield {"comment": "connected"}
        while True:
            if await request.is_disconnected():
                break
            event = await event_queue.get()
            yield {"data": json.dumps(event)}

    return EventSourceResponse(generate())


@app.post("/trigger")
async def trigger_report_legacy() -> dict:
    """Deprecated: use /report instead. Phase 1 stub that pushes SSE events directly."""
    from agents.bridge.events import push_sse_event
    from agents.models.events import AgentStatus, SSEEvent

    push_sse_event(SSEEvent.agent_status("orchestrator", AgentStatus.WORKING))
    push_sse_event(SSEEvent.agent_thought("orchestrator", "Dispatching analysis requests to domain agents..."))
    push_sse_event(SSEEvent.agent_thought("orchestrator", "Stub: full agent dispatch implemented in Phase 2"))
    push_sse_event(SSEEvent.agent_status("orchestrator", AgentStatus.DONE))
    return {"status": "triggered"}


@app.post("/report")
async def trigger_report() -> dict:
    """Trigger full report pipeline via orchestrator's REST endpoint."""
    from agents.data.portfolio import EQUITY_TICKERS
    import httpx

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:8005/submit/report",
            json={"holdings": EQUITY_TICKERS, "mock": False},
            timeout=60.0,  # orchestrator needs time for fan-out + LLM
        )
    return {"status": "triggered", "orchestrator_status": resp.status_code}
