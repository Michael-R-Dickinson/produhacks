"""Light integration: FastAPI bridge app loads (report pipeline lands here in later phases)."""

from fastapi.testclient import TestClient

from agents.bridge.app import app


def test_openapi_available():
    import agents.bridge.events as ev

    with TestClient(app) as client:
        r = client.get("/openapi.json")
        assert r.status_code == 200
        assert "paths" in r.json()
    # Startup wires the bridge loop for push_sse_event; clear so other tests do not use a closed loop.
    ev._fastapi_loop = None
    ev._event_queue = None
