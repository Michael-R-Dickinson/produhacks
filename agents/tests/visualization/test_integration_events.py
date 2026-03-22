"""Integration tests: typed SSE events (ARCHITECTURE pattern 3) for the modeling agent."""

import asyncio

import pytest

from agents.bridge.events import push_sse_event
from agents.models.events import AgentStatus, EventType, SSEEvent


@pytest.mark.asyncio
async def test_push_sse_event_delivers_when_fastapi_loop_configured():
    import agents.bridge.events as ev

    q: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    prev_loop, prev_q = ev._fastapi_loop, ev._event_queue
    try:
        ev._fastapi_loop = loop
        ev._event_queue = q
        push_sse_event(SSEEvent.agent_thought("modeling-test", "Rendering charts..."))
        await asyncio.sleep(0.02)
        item = await asyncio.wait_for(q.get(), timeout=2.0)
        assert item["agent_id"] == "modeling-test"
        assert item["event_type"] == EventType.AGENT_THOUGHT.value
        assert item["payload"]["text"] == "Rendering charts..."
    finally:
        ev._fastapi_loop = prev_loop
        ev._event_queue = prev_q


def test_push_sse_event_noops_when_bridge_not_wired():
    import agents.bridge.events as ev

    prev_loop, prev_q = ev._fastapi_loop, ev._event_queue
    try:
        ev._fastapi_loop = None
        ev._event_queue = None
        push_sse_event(SSEEvent.agent_status("x", AgentStatus.WORKING))
    finally:
        ev._fastapi_loop = prev_loop
        ev._event_queue = prev_q
