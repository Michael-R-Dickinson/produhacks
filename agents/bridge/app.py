import asyncio
import json

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from agents.ports import BUREAU_PORT

app = FastAPI(title="InvestiSwarm Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.get("/events")
async def sse_events(request: Request) -> EventSourceResponse:
    """SSE stream of agent / report events."""
    return EventSourceResponse(_sse_event_generator(request))


@app.post("/report")
async def trigger_report(request: Request) -> dict:
    """Trigger full report pipeline via orchestrator's REST endpoint."""
    from agents.data.portfolio import EQUITY_TICKERS
    import httpx

    # Parse optional JSON body for knowledge_level
    knowledge_level = 2  # default
    try:
        body = await request.json()
        knowledge_level = body.get("knowledge_level", 2)
    except Exception:
        pass

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"http://localhost:{BUREAU_PORT}/report",
            json={"holdings": EQUITY_TICKERS, "mock": False, "knowledge_level": knowledge_level},
            timeout=60.0,  # orchestrator needs time for fan-out + LLM
        )
    return {"status": "triggered", "orchestrator_status": resp.status_code}
