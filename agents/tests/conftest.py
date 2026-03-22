"""Global test hooks."""

import pytest


@pytest.fixture(autouse=True)
def isolate_bridge_event_wiring():
    """Prevent a closed FastAPI loop from remaining in push_sse_event() wiring between tests."""
    import agents.bridge.events as ev

    ev._fastapi_loop = None
    ev._event_queue = None
    yield
