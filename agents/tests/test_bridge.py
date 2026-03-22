"""Integration tests for the FastAPI bridge.

NOTE on SSE testing: httpx.AsyncClient with ASGITransport cannot test infinite
SSE streams because it awaits the full ASGI app lifecycle before returning a
Response. We test SSE connectivity via a finite generator proxy that shares the
same EventSourceResponse class and middleware, verifying headers and status.
"""
import asyncio
import json
import pytest
import httpx
from httpx import ASGITransport
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from agents.bridge.app import app
import agents.bridge.events as ev


def _make_finite_sse_app() -> FastAPI:
    """A test-only app with the same CORS config and a finite SSE endpoint.

    Used to verify SSE headers and status without hanging on an infinite stream.
    """
    test_app = FastAPI()
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_private_network=True,
    )

    @test_app.get("/events")
    async def finite_sse(request: Request) -> EventSourceResponse:
        async def generate():
            yield {"data": json.dumps({"agent_id": "test", "type": "ping"})}

        return EventSourceResponse(generate())

    return test_app


_finite_app = _make_finite_sse_app()


@pytest.mark.asyncio
async def test_sse_connects():
    """SSE endpoint responds with 200 and text/event-stream content-type."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=_finite_app), base_url="http://test"
    ) as client:
        response = await client.get("/events")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")


@pytest.mark.asyncio
async def test_pna_header():
    """CORS preflight includes access-control-allow-private-network: true."""
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.options(
            "/events",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Private-Network": "true",
            },
        )
    assert "access-control-allow-private-network" in response.headers
    assert response.headers["access-control-allow-private-network"] == "true"


@pytest.mark.asyncio
async def test_trigger_returns_200():
    """POST /trigger returns 200 with triggered status."""
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/trigger")
    assert response.status_code == 200
    assert response.json() == {"status": "triggered"}


@pytest.mark.asyncio
async def test_api_report_generate_returns_200():
    """POST /api/report/generate matches ARCHITECTURE.md naming."""
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/report/generate")
    assert response.status_code == 200
    assert response.json() == {"status": "triggered"}


@pytest.mark.asyncio
async def test_api_report_stream_options_pna():
    """CORS preflight for /api/report/stream."""
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.options(
            "/api/report/stream",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Private-Network": "true",
            },
        )
    assert response.headers.get("access-control-allow-private-network") == "true"


@pytest.mark.asyncio
async def test_event_delivered():
    """push_sse_event() enqueues a typed SSEEvent retrievable from the queue."""
    from agents.models.events import SSEEvent

    q: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    prev_loop, prev_q = ev._fastapi_loop, ev._event_queue
    try:
        ev._fastapi_loop = loop
        ev._event_queue = q
        ev.push_sse_event(SSEEvent.agent_thought("test", "hello"))
        event = await asyncio.wait_for(q.get(), timeout=2.0)
    finally:
        ev._fastapi_loop = prev_loop
        ev._event_queue = prev_q
    assert event["agent_id"] == "test"
    assert event["event_type"] == "agent.thought"
    assert event["payload"]["text"] == "hello"


@pytest.mark.asyncio
async def test_push_ui_event_delivers_frontend_shaped_dict():
    from agents.bridge.events import push_ui_event

    q: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    prev_loop, prev_q = ev._fastapi_loop, ev._event_queue
    try:
        ev._fastapi_loop = loop
        ev._event_queue = q
        payload = {
            "agent_id": "modeling",
            "type": "report_section",
            "section": "modeling",
            "data": {"sharpe_ratio": 1.0, "volatility": 0.1, "trend_slope": 0.0, "charts": []},
        }
        push_ui_event(payload)
        event = await asyncio.wait_for(q.get(), timeout=2.0)
    finally:
        ev._fastapi_loop = prev_loop
        ev._event_queue = prev_q
    assert event == payload


def test_modeling_ui_payload_matches_frontend_contract():
    import json

    from agents.bridge.modeling_payload import modeling_ui_payload
    from agents.mocks.modeling import mock_model_response

    r = mock_model_response()
    data = modeling_ui_payload(r)
    json.dumps(data)
    assert "charts" in data
    assert len(data["charts"]) == len(r.charts)
    assert data["chart_base64"] == (r.charts[0].image_base64 if r.charts else None)
    assert all("image_base64" in c for c in data["charts"])
