import asyncio
from typing import Any

# Set by bureau launcher at startup
_fastapi_loop: asyncio.AbstractEventLoop | None = None
_event_queue: asyncio.Queue | None = None


def push_event(agent_id: str, event_type: str, payload: dict[str, Any]) -> None:
    """Thread-safe event push from Bureau thread into FastAPI event loop."""
    if _fastapi_loop is None or _event_queue is None:
        return
    event = {"agent_id": agent_id, "type": event_type, **payload}
    _fastapi_loop.call_soon_threadsafe(_event_queue.put_nowait, event)
