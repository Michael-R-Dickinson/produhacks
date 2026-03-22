import asyncio

from agents.models.events import SSEEvent

# Set by bureau launcher at startup
_fastapi_loop: asyncio.AbstractEventLoop | None = None
_event_queue: asyncio.Queue | None = None


def push_sse_event(event: SSEEvent) -> None:
    """Thread-safe push of a typed SSEEvent from Bureau thread into FastAPI event loop."""
    if _fastapi_loop is None or _event_queue is None:
        return
    _fastapi_loop.call_soon_threadsafe(_event_queue.put_nowait, event.model_dump())
