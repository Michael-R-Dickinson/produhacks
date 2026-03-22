import asyncio
import threading

from uagents import Bureau


def start_bureau(agents: list, fastapi_loop: asyncio.AbstractEventLoop, event_queue: asyncio.Queue) -> None:
    """Start Bureau in a background thread with its own event loop."""
    bureau_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bureau_loop)

    # Bureau needs its own port for inter-agent ASGI server (separate from uvicorn's 8000).
    bureau = Bureau(loop=bureau_loop, port=8006)
    for agent in agents:
        bureau.add(agent)

    # Inject references so push_sse_event() can cross loops
    import agents.bridge.events as ev
    ev._fastapi_loop = fastapi_loop
    ev._event_queue = event_queue

    bureau_loop.run_until_complete(bureau.run_async())


def launch_bureau(
    agents: list,
    fastapi_loop: asyncio.AbstractEventLoop,
    event_queue: asyncio.Queue,
) -> threading.Thread:
    """Launch Bureau in a daemon thread. Returns the thread."""
    t = threading.Thread(
        target=start_bureau,
        args=(agents, fastapi_loop, event_queue),
        daemon=True,
    )
    t.start()
    return t
