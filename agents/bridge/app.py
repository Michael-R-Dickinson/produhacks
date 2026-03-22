import asyncio
import json

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from agents.ports import BUREAU_PORT

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


async def _sse_event_generator(request: Request):
    yield {"comment": "connected"}
    while True:
        if await request.is_disconnected():
            break
        event = await event_queue.get()
        yield {"data": json.dumps(event)}


def _run_trigger_stub() -> None:
    from agents.bridge.events import push_sse_event
    from agents.models.events import AgentStatus, SSEEvent

    push_sse_event(SSEEvent.agent_status("orchestrator", AgentStatus.WORKING))
    push_sse_event(SSEEvent.agent_thought("orchestrator", "Dispatching analysis requests to domain agents..."))
    push_sse_event(SSEEvent.agent_thought("orchestrator", "Stub: full agent dispatch implemented in Phase 2"))
    push_sse_event(SSEEvent.agent_status("orchestrator", AgentStatus.DONE))


@app.get("/events")
async def sse_events_legacy(request: Request) -> EventSourceResponse:
    """Legacy SSE path (Phase 1). Prefer ``/api/report/stream`` for new clients."""
    return EventSourceResponse(_sse_event_generator(request))


@app.get("/api/report/stream")
async def api_report_stream(request: Request) -> EventSourceResponse:
    """ARCHITECTURE.md: GET SSE stream of agent / report events."""
    return EventSourceResponse(_sse_event_generator(request))


@app.post("/trigger")
async def trigger_report_legacy() -> dict:
    """Legacy trigger. Prefer ``POST /api/report/generate``."""
    _run_trigger_stub()
    return {"status": "triggered"}


@app.post("/api/report/generate")
async def api_report_generate() -> dict:
    """ARCHITECTURE.md: POST to start report pipeline (stub until orchestrator wiring)."""
    _run_trigger_stub()
    return {"status": "triggered"}


@app.post("/report")
async def trigger_report() -> dict:
    """Trigger full report pipeline via orchestrator's REST endpoint."""
    from agents.data.portfolio import EQUITY_TICKERS
    import httpx

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"http://localhost:{BUREAU_PORT}/submit/report",
            json={"holdings": EQUITY_TICKERS, "mock": False},
            timeout=60.0,  # orchestrator needs time for fan-out + LLM
        )
    return {"status": "triggered", "orchestrator_status": resp.status_code}
