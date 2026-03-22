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


def push_ui_event(payload: dict) -> None:
    """Thread-safe push of a **frontend-shaped** SSE JSON object (e.g. ``report_section``).

    Use :func:`modeling_ui_payload` with ``mock_model_response()`` / ``build_model_response``
    to attach ``charts[].image_base64`` PNGs without extra frontend work.
    """
    if _fastapi_loop is None or _event_queue is None:
        return
    _fastapi_loop.call_soon_threadsafe(_event_queue.put_nowait, payload)
