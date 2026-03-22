import asyncio
import json
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from google import genai

from agents.ports import BUREAU_PORT

app = FastAPI(title="Wealth Council Bridge")

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


_gemini: genai.Client | None = None


def get_gemini() -> genai.Client:
    """Lazy-initialize the Gemini client so module import doesn't fail without the key."""
    global _gemini
    if _gemini is None:
        _gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _gemini


class ChatPart(BaseModel):
    text: str


class ChatHistoryItem(BaseModel):
    role: str
    parts: list[ChatPart]


class ChatRequest(BaseModel):
    message: str
    history: list[ChatHistoryItem] = []
    report_context: str = ""


async def _chat_stream_generator(request: Request, chat_request: ChatRequest):
    system_instruction = (
        "You are a financial analyst assistant. The user has just read the following "
        "investment report. Answer questions about it concisely and accurately. "
        "Reference specific data from the report when relevant.\n\n"
        + chat_request.report_context
    )

    contents = [
        {"role": item.role, "parts": [{"text": p.text} for p in item.parts]}
        for item in chat_request.history
    ]
    contents.append({"role": "user", "parts": [{"text": chat_request.message}]})

    config = genai.types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.3,
        max_output_tokens=2000,
    )

    async for chunk in await get_gemini().aio.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=contents,
        config=config,
    ):
        if await request.is_disconnected():
            break
        text = chunk.text if chunk.text else ""
        if text:
            yield {"data": json.dumps({"token": text, "done": False})}

    yield {"data": json.dumps({"token": "", "done": True})}


@app.post("/chat")
async def chat(request: Request, body: ChatRequest) -> EventSourceResponse:
    """Stream a Gemini chat response as SSE tokens."""
    return EventSourceResponse(_chat_stream_generator(request, body))


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
            json={
                "holdings": EQUITY_TICKERS,
                "mock": False,
                "knowledge_level": knowledge_level,
            },
            timeout=60.0,  # orchestrator needs time for fan-out + LLM
        )
    return {"status": "triggered", "orchestrator_status": resp.status_code}
