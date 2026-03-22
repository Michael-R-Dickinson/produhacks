# Phase 1: Foundation - Research

**Researched:** 2026-03-21
**Domain:** uAgents Bureau + FastAPI SSE bridge + Pydantic message models + mock data toggle
**Confidence:** MEDIUM-HIGH (Bureau threading: MEDIUM verified via official async_loops docs; SSE/PNA fix: HIGH verified via Starlette release notes; queue cross-loop pattern: HIGH per Python docs)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Process Architecture**
- Single Python process — Bureau runs in a background thread with its own event loop, FastAPI runs on the main asyncio loop
- Communication between Bureau thread and FastAPI via asyncio.Queue
- One `python main.py` entrypoint starts both Bureau and FastAPI
- If Bureau's event loop blocks FastAPI despite threading, escalate — but start with this approach

**SSE Event Contract**
- Single multiplexed SSE endpoint (`/events`) — one EventSource connection from the browser
- Three event types streamed:
  1. Agent thoughts — real-time text of what each agent is doing (explicit `emit_thought()` calls at key computation steps, hand-authored)
  2. Agent-to-agent messages — when one agent sends a message to another (powers edge animations in Phase 3)
  3. Status changes — agent lifecycle events (idle, working, done, error) for node highlighting
- Each SSE event tagged with `agent_id` so the frontend can route to the correct node
- Report delivery mechanism (SSE event vs separate REST) at Claude's discretion

**Message Model Design**
- Typed per-agent for both requests and responses — symmetric contracts
- Request types: `AnalyzePortfolio`, `FetchNews`, `RunModel`, `AnalyzeAlternatives` (orchestrator sends specific typed requests to each agent)
- Response types: `PortfolioResponse`, `NewsResponse`, `ModelResponse`, `AlternativesResponse` (each with domain-specific fields)
- Raw structured data only — no pre-formatted summary strings. Agents return numbers, metrics, and structured objects. The orchestrator's LLM interprets raw data directly
- Typed requests enable selective dispatch (critical for Phase 4 chat where only relevant agents fire)

### Claude's Discretion
- Mock data toggle mechanism (env var, config file, CLI flag)
- Mock data shape and realism level
- Report delivery over SSE vs separate REST endpoint
- Exact asyncio.Queue topology (one queue per agent vs single shared queue)
- Agent seed phrases and addressing strategy
- Error handling patterns for agent communication failures

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFRA-01 | uAgents Bureau running all 5 agents in one process | Bureau `run_async()` pattern confirmed; background thread isolation pattern documented below |
| INFRA-02 | FastAPI bridge with SSE endpoints for web-to-agent communication | `sse-starlette` 3.3.3 + `EventSourceResponse` pattern; cross-loop queue via `call_soon_threadsafe`; Chrome PNA fix via Starlette `allow_private_network=True` |
| INFRA-03 | Pydantic message models for all inter-agent communication | uAgents Model base class pattern documented; typed per-agent contracts specified |
| INFRA-04 | Mock data mode for all agents (toggle for demo vs development) | `MOCK_DATA=true` env var pattern recommended; per-agent mock fixtures in `agents/mocks/` |
</phase_requirements>

---

## Summary

Phase 1 scaffolds the three-layer architecture: five stub uAgents running in a Bureau, a FastAPI bridge exposing a single multiplexed SSE endpoint, and the Pydantic message models defining every inter-agent contract. No domain logic is implemented — the goal is verified infrastructure.

The critical integration challenge is thread isolation. The Bureau runs in a background thread with its own asyncio event loop; FastAPI runs on the main event loop via uvicorn. These two event loops cannot share an `asyncio.Queue` directly — cross-loop writes require `fastapi_loop.call_soon_threadsafe(queue.put_nowait, event)`. This is the only non-obvious pattern in this phase and must be implemented correctly or SSE streaming will silently stall.

The Chrome Private Network Access (PNA) problem is solved at the Starlette CORS middleware level with `allow_private_network=True` (available in Starlette 0.51.0+, released January 2026). No custom middleware workaround needed.

**Primary recommendation:** Build in this order — models, stub agents, Bureau runner, FastAPI bridge with cross-loop queue, SSE endpoint with PNA headers, mock toggle, curl verification. Each step is independently testable before the next.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| uagents | 0.24.0 | Agent runtime, Bureau, inter-agent messaging | fetch.ai hackathon requirement; current stable (2026-03-04) |
| Python | 3.11 | Agent implementation | Supported by uAgents 3.10-3.14; 3.11 widely available |
| fastapi | 0.115.x | FastAPI bridge server | Standard ASGI framework; confirmed compatible with uagents |
| uvicorn | 0.30.x | ASGI server | Standard FastAPI runner |
| sse-starlette | 3.3.3 | SSE streaming from FastAPI | Current stable (2026-03-17); EventSourceResponse handles keep-alive, disconnect |
| pydantic | v2.x | Message model definitions | Bundled with fastapi; uAgents Model base class extends Pydantic |
| python-dotenv | 1.x | Environment variable loading | Standard .env management; used for MOCK_DATA toggle |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| starlette | 0.51.0+ | CORSMiddleware with `allow_private_network` | Pulled in by fastapi; must be 0.51.0+ for PNA header support |
| httpx | 0.27.x | Async HTTP calls from agents | Non-blocking; needed if any stub agent verifies it can call an endpoint |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| sse-starlette | StreamingResponse + manual SSE format | sse-starlette handles keep-alive, disconnect, and proper media type automatically; no benefit to rolling manually |
| Background thread (Bureau) | Two separate processes via start.sh | Two processes avoids event loop isolation entirely but adds startup coordination complexity; threading is simpler for greenfield |
| `call_soon_threadsafe` + `asyncio.Queue` | `janus.Queue` | janus must be created in the consuming loop's context; `call_soon_threadsafe` is standard library and simpler for this one-way event push pattern |

**Installation:**
```bash
uv venv .venv && source .venv/bin/activate
uv pip install "uagents==0.24.0" "fastapi==0.115.*" "uvicorn==0.30.*" "sse-starlette==3.3.3" "python-dotenv==1.*" "httpx==0.27.*"
```

**Version verification (run before coding):**
```bash
uv pip show uagents fastapi sse-starlette starlette
```

---

## Architecture Patterns

### Recommended Project Structure

```
produhacks/
├── agents/
│   ├── main.py                  # Entrypoint: starts Bureau thread + uvicorn
│   ├── bureau.py                # Bureau runner with background thread setup
│   ├── orchestrator.py          # Orchestrator stub agent
│   ├── portfolio_agent.py       # Portfolio stub agent
│   ├── news_agent.py            # News stub agent
│   ├── modeling_agent.py        # Modeling stub agent
│   ├── alternatives_agent.py    # Alternatives stub agent
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py          # AnalyzePortfolio, FetchNews, RunModel, AnalyzeAlternatives
│   │   └── responses.py         # PortfolioResponse, NewsResponse, ModelResponse, AlternativesResponse
│   ├── mocks/
│   │   ├── __init__.py
│   │   ├── portfolio.py         # Mock PortfolioResponse fixture
│   │   ├── news.py              # Mock NewsResponse fixture
│   │   ├── modeling.py          # Mock ModelResponse fixture
│   │   └── alternatives.py      # Mock AlternativesResponse fixture
│   └── bridge/
│       ├── __init__.py
│       ├── app.py               # FastAPI app, SSE endpoint, CORS config
│       └── events.py            # Event queue, push_event(), cross-loop helpers
├── frontend/                    # Phase 3 — not created in this phase
├── .env.example
└── .env
```

### Pattern 1: Bureau in Background Thread with Isolated Event Loop

**What:** Bureau gets its own event loop running in a daemon thread. FastAPI gets the main event loop managed by uvicorn. The two loops never share coroutines — only data passes between them via thread-safe mechanisms.

**When to use:** Always. This is the only safe way to run Bureau + FastAPI in one process.

**Example:**
```python
# agents/bureau.py
import asyncio
import threading
from uagents import Bureau

def start_bureau(agents: list, fastapi_loop: asyncio.AbstractEventLoop, event_queue: asyncio.Queue) -> None:
    """Start Bureau in a background thread with its own event loop."""
    bureau_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bureau_loop)

    bureau = Bureau(loop=bureau_loop)
    for agent in agents:
        bureau.add(agent)

    # Inject push_event into each agent via module-level variable
    # so handlers can call push_event(agent_id, type, payload)
    import agents.bridge.events as ev
    ev._fastapi_loop = fastapi_loop
    ev._event_queue = event_queue

    bureau_loop.run_until_complete(bureau.run_async())

def launch_bureau(agents: list, fastapi_loop: asyncio.AbstractEventLoop, event_queue: asyncio.Queue) -> threading.Thread:
    t = threading.Thread(
        target=start_bureau,
        args=(agents, fastapi_loop, event_queue),
        daemon=True,
    )
    t.start()
    return t
```

```python
# agents/main.py
import asyncio
import uvicorn
from agents.bridge.app import app, event_queue
from agents.bureau import launch_bureau
from agents.orchestrator import orchestrator
from agents.portfolio_agent import portfolio_agent
from agents.news_agent import news_agent
from agents.modeling_agent import modeling_agent
from agents.alternatives_agent import alternatives_agent

if __name__ == "__main__":
    fastapi_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(fastapi_loop)

    all_agents = [orchestrator, portfolio_agent, news_agent, modeling_agent, alternatives_agent]
    launch_bureau(all_agents, fastapi_loop, event_queue)

    uvicorn.run(app, host="0.0.0.0", port=8000, loop="none")
    # "loop=none" tells uvicorn to use the already-running event loop
```

### Pattern 2: Cross-Loop Event Push via `call_soon_threadsafe`

**What:** `asyncio.Queue` is not thread-safe across event loops. Agent handlers in the Bureau thread must push events to the FastAPI event loop's queue using `call_soon_threadsafe`. This is the standard library approach — no additional libraries required.

**When to use:** Whenever a Bureau agent handler needs to emit an SSE event.

**Example:**
```python
# agents/bridge/events.py
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
```

```python
# Usage inside any agent handler
from agents.bridge.events import push_event

@portfolio_agent.on_message(model=AnalyzePortfolio)
async def handle_analyze(ctx: Context, sender: str, msg: AnalyzePortfolio) -> None:
    push_event("portfolio", "status", {"status": "working"})
    push_event("portfolio", "thought", {"text": "Computing sector allocation..."})
    # ... do work ...
    push_event("portfolio", "status", {"status": "done"})
    await ctx.send(sender, mock_portfolio_response() if MOCK_DATA else real_portfolio_response(msg))
```

### Pattern 3: SSE Endpoint with Chrome PNA Fix

**What:** Single `/events` endpoint using `sse-starlette`'s `EventSourceResponse`. CORS middleware configured with `allow_private_network=True` (Starlette 0.51.0+) to prevent Chrome's Private Network Access prompt from blocking the browser's EventSource connection to localhost.

**When to use:** Always for local development where the browser's Vite dev server (public) talks to the FastAPI bridge (localhost/private network).

**Example:**
```python
# agents/bridge/app.py
import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

app = FastAPI()

# allow_private_network=True requires starlette>=0.51.0
# This prevents Chrome PNA prompt when Vite frontend accesses FastAPI on localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server origin
    allow_methods=["*"],
    allow_headers=["*"],
    allow_private_network=True,
)

event_queue: asyncio.Queue = asyncio.Queue()

@app.get("/events")
async def sse_events(request: Request):
    async def generate():
        while True:
            if await request.is_disconnected():
                break
            event = await event_queue.get()
            yield {"data": json.dumps(event)}
    return EventSourceResponse(generate())

@app.post("/trigger")
async def trigger_report():
    """Stub: sends a trigger to the orchestrator agent."""
    # Phase 1: just verify the endpoint is reachable
    return {"status": "triggered"}
```

### Pattern 4: Pydantic Message Models as uAgents Models

**What:** uAgents message types extend `uagents.Model`, which is a Pydantic BaseModel subclass. All request/response types for this project must extend `Model`. Models must be importable from a shared module so orchestrator and domain agents reference the same class.

**When to use:** Every inter-agent message in the system.

**Example:**
```python
# agents/models/requests.py
from uagents import Model

class AnalyzePortfolio(Model):
    """Orchestrator -> Portfolio Agent"""
    holdings: list[str]          # ticker symbols
    mock: bool = False

class FetchNews(Model):
    """Orchestrator -> News Agent"""
    tickers: list[str]
    mock: bool = False

class RunModel(Model):
    """Orchestrator -> Modeling Agent"""
    holdings: list[str]
    mock: bool = False

class AnalyzeAlternatives(Model):
    """Orchestrator -> Alternatives Agent"""
    mock: bool = False
```

```python
# agents/models/responses.py
from uagents import Model

class PortfolioResponse(Model):
    """Portfolio Agent -> Orchestrator"""
    sector_allocation: dict[str, float]   # {"Technology": 0.45, ...}
    top_holdings: list[dict]              # [{"ticker": "AAPL", "weight": 0.18}]
    herfindahl_index: float               # 0.0-1.0 concentration measure
    portfolio_beta: float

class NewsResponse(Model):
    """News Agent -> Orchestrator"""
    headlines: list[dict]                 # [{"title": str, "sentiment": float, "ticker": str}]
    aggregate_sentiment: dict[str, float] # {"AAPL": 0.72, ...}
    overall_sentiment: float              # -1.0 to 1.0

class ModelResponse(Model):
    """Modeling Agent -> Orchestrator"""
    sharpe_ratio: float
    volatility: float
    trend_slope: float
    chart_base64: str | None = None       # Phase 2 — None in Phase 1 stubs

class AlternativesResponse(Model):
    """Alternatives Agent -> Orchestrator"""
    crypto_prices: dict[str, float]       # {"BTC": 67000.0, ...}
    cross_correlations: dict[str, float]  # {"BTC": 0.12, ...}
```

### Pattern 5: Mock Data Toggle via Environment Variable

**What:** `MOCK_DATA=true` in `.env` enables mock mode for all agents. Each agent checks this at handler time (not import time) so it can be toggled without restart during development. Mock data lives in `agents/mocks/` as functions returning pre-built response objects.

**When to use:** All development and testing. Switch to `MOCK_DATA=false` only for live demo.

**Example:**
```python
# agents/portfolio_agent.py
import os
from uagents import Agent, Context
from agents.models.requests import AnalyzePortfolio
from agents.models.responses import PortfolioResponse
from agents.mocks.portfolio import mock_portfolio_response
from agents.bridge.events import push_event

MOCK_DATA = os.getenv("MOCK_DATA", "true").lower() == "true"

portfolio_agent = Agent(name="portfolio", seed="portfolio-agent-seed-investiswarm", port=8001)

@portfolio_agent.on_message(model=AnalyzePortfolio, replies={PortfolioResponse})
async def handle_analyze(ctx: Context, sender: str, msg: AnalyzePortfolio) -> None:
    push_event("portfolio", "status", {"status": "working"})
    push_event("portfolio", "thought", {"text": "Analyzing portfolio allocation..."})

    if MOCK_DATA or msg.mock:
        response = mock_portfolio_response()
    else:
        response = await compute_portfolio_response(msg)  # Phase 2

    push_event("portfolio", "thought", {"text": "Analysis complete."})
    push_event("portfolio", "status", {"status": "done"})
    await ctx.send(sender, response)
```

### Anti-Patterns to Avoid

- **Sharing an `asyncio.Queue` across event loops without `call_soon_threadsafe`:** Bureau thread uses a different event loop than FastAPI. Direct `queue.put_nowait()` from the Bureau thread will corrupt the queue silently. Always use `fastapi_loop.call_soon_threadsafe(queue.put_nowait, event)`.
- **Calling `bureau.run()` inside FastAPI lifespan:** `bureau.run()` blocks. The SSE endpoint will never yield. Always run Bureau in a separate thread.
- **Putting `@protocol.on_rest_post()` on a Protocol instead of the agent:** uAgents REST endpoints are agent-level only. Protocol-level decorators are silently ignored.
- **Making the frontend call any agent port directly:** The browser cannot speak the uAgents binary protocol, and Chrome will block private network requests. All frontend requests go through the FastAPI bridge at port 8000.
- **Using `asyncio.Queue` without `allow_private_network=True`:** Without this CORS header, the browser's EventSource constructor fails silently on Chrome when the Vite dev server (port 5173) connects to localhost:8000.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SSE formatting and keep-alive | Manual `StreamingResponse` with `text/event-stream` | `sse-starlette` `EventSourceResponse` | Handles keep-alive pings, client disconnect detection, proper headers automatically |
| Thread-safe event loop crossing | Custom locking/queuing schemes | `loop.call_soon_threadsafe(queue.put_nowait, event)` | Python stdlib; correct; one line |
| Chrome PNA CORS header | Custom middleware class | `CORSMiddleware(allow_private_network=True)` | Starlette 0.51.0+ includes this natively; no custom class needed |
| Pydantic model inheritance for agents | Custom serialization | `uagents.Model` subclass | `Model` is already a Pydantic BaseModel; uAgents serializes/deserializes automatically |
| Agent seed phrase management | Random address generation | Deterministic seed strings | Agent addresses are derived from seeds — hardcoded seeds give stable, predictable addresses for hardcoding in config |

**Key insight:** The Bureau/FastAPI threading problem looks tricky but has a one-line stdlib solution. The only custom code needed is `push_event()` — everything else uses existing libraries as designed.

---

## Common Pitfalls

### Pitfall 1: asyncio.Queue Cross-Loop Data Corruption

**What goes wrong:** Agent handler in Bureau thread calls `event_queue.put_nowait(event)` directly. The FastAPI SSE generator either never receives the event or crashes with an obscure asyncio error.

**Why it happens:** `asyncio.Queue` is bound to the event loop it was created in. Calling it from a different loop (the Bureau thread's loop) corrupts internal state.

**How to avoid:** Always use `fastapi_loop.call_soon_threadsafe(event_queue.put_nowait, event)` from Bureau thread code. Capture `fastapi_loop = asyncio.get_event_loop()` before launching the Bureau thread.

**Warning signs:** SSE endpoint connects but no events arrive; no error is logged.

### Pitfall 2: Bureau run_async() vs run() Confusion

**What goes wrong:** Code calls `bureau.run()` in the background thread. This calls `asyncio.run()` internally which creates its own event loop, ignoring the `loop=` parameter passed to Bureau. Agents get wrong addresses.

**Why it happens:** `run()` is the simple convenience method; `run_async()` is the coroutine for external loop integration.

**How to avoid:** In the background thread, set the event loop explicitly, then use `bureau_loop.run_until_complete(bureau.run_async())`.

**Warning signs:** Agent addresses differ between runs; `loop` parameter on Agent constructor appears ignored.

### Pitfall 3: Starlette Version Below 0.51.0 Missing PNA Support

**What goes wrong:** `CORSMiddleware(allow_private_network=True)` raises `TypeError: unexpected keyword argument`.

**Why it happens:** FastAPI pins a specific Starlette version; if the installed Starlette is below 0.51.0 (released Jan 2026), `allow_private_network` doesn't exist.

**How to avoid:** Pin `starlette>=0.51.0` explicitly. Verify with `python -c "import starlette; print(starlette.__version__)"`.

**Warning signs:** `TypeError` on app startup; Chrome shows "blocked by CORS" or PNA prompt on EventSource connect.

### Pitfall 4: SSE Generator Never Yields (Nginx/Proxy Buffering)

**What goes wrong:** SSE events are emitted by agents but the browser receives them in large batches with delays.

**Why it happens:** Any reverse proxy (nginx, caddy) buffers streaming responses until a threshold is hit.

**How to avoid:** For local dev, no proxy is in the path so this won't appear. Add `X-Accel-Buffering: no` header to the SSE response if a proxy is added later.

**Warning signs:** Events arrive in bursts; delays of 5-10 seconds between events.

### Pitfall 5: Agent Addresses Not Stable Across Restarts

**What goes wrong:** Orchestrator tries to `ctx.send()` to a domain agent address but the address changed because no seed was set.

**Why it happens:** Without a `seed=` parameter, uAgents generates a random key pair each startup, producing a different `agent1q...` address.

**How to avoid:** Set deterministic seed strings on every Agent constructor. Store addresses as constants in a `config.py` or derive them at startup with `agent.address` after construction.

**Warning signs:** `ctx.send()` silently fails or times out; orchestrator receives no replies.

---

## Code Examples

Verified patterns from official sources and confirmed libraries:

### Creating a Stub Agent with Mock Handler

```python
# agents/news_agent.py
import os
from uagents import Agent, Context
from agents.models.requests import FetchNews
from agents.models.responses import NewsResponse
from agents.mocks.news import mock_news_response
from agents.bridge.events import push_event

MOCK_DATA = os.getenv("MOCK_DATA", "true").lower() == "true"

news_agent = Agent(
    name="news",
    seed="news-agent-seed-investiswarm-v1",  # deterministic address
    port=8002,
)

@news_agent.on_message(model=FetchNews, replies={NewsResponse})
async def handle_fetch_news(ctx: Context, sender: str, msg: FetchNews) -> None:
    push_event("news", "status", {"status": "working"})
    push_event("news", "thought", {"text": f"Fetching news for {msg.tickers}..."})
    push_event("news", "message_received", {"from": "orchestrator", "title": "FetchNews request"})

    response = mock_news_response() if (MOCK_DATA or msg.mock) else None  # Phase 2 fills real path

    push_event("news", "message_sent", {"to": "orchestrator", "title": "NewsResponse"})
    push_event("news", "status", {"status": "done"})
    await ctx.send(sender, response)
```

### SSE Event Schema (TypeScript reference for Phase 3)

```typescript
// The three event shapes emitted on /events
type AgentThought = {
  agent_id: string;
  type: "thought";
  text: string;
};

type AgentMessage = {
  agent_id: string;
  type: "message_sent" | "message_received";
  to?: string;
  from?: string;
  title: string;
};

type AgentStatus = {
  agent_id: string;
  type: "status";
  status: "idle" | "working" | "done" | "error";
};

type AgentEvent = AgentThought | AgentMessage | AgentStatus;
```

### Curl Verification Commands (Success Criteria)

```bash
# 1. Verify SSE endpoint connects (should see event stream, no error)
curl -N http://localhost:8000/events

# 2. Trigger the orchestrator and watch events appear on the SSE stream
# (in one terminal)
curl -N http://localhost:8000/events
# (in another terminal)
curl -X POST http://localhost:8000/trigger

# Expected SSE output:
# data: {"agent_id": "orchestrator", "type": "status", "status": "working"}
# data: {"agent_id": "orchestrator", "type": "thought", "text": "Dispatching to agents..."}
# data: {"agent_id": "portfolio", "type": "status", "status": "working"}
# ... etc
```

### Mock Data Fixture Structure

```python
# agents/mocks/portfolio.py
from agents.models.responses import PortfolioResponse

def mock_portfolio_response() -> PortfolioResponse:
    return PortfolioResponse(
        sector_allocation={
            "Technology": 0.42,
            "Healthcare": 0.18,
            "Financials": 0.15,
            "Consumer Discretionary": 0.12,
            "Energy": 0.08,
            "Other": 0.05,
        },
        top_holdings=[
            {"ticker": "AAPL", "weight": 0.18, "sector": "Technology"},
            {"ticker": "MSFT", "weight": 0.15, "sector": "Technology"},
            {"ticker": "NVDA", "weight": 0.09, "sector": "Technology"},
            {"ticker": "UNH", "weight": 0.08, "sector": "Healthcare"},
            {"ticker": "JPM", "weight": 0.07, "sector": "Financials"},
        ],
        herfindahl_index=0.087,   # moderately diversified
        portfolio_beta=1.12,
    )
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `bureau.run()` blocking call | `bureau.run_async()` coroutine | uAgents 0.20+ | Bureau can now run alongside other async tasks |
| Custom CORS middleware for PNA | `CORSMiddleware(allow_private_network=True)` | Starlette 0.51.0 (Jan 2026) | No custom class needed; one-liner fix |
| `asyncio.Queue` shared across threads | `call_soon_threadsafe` + per-loop Queue | Always correct — misconception in many tutorials | Prevents silent data loss in multi-loop architectures |
| Two separate processes for Bureau + FastAPI | Single process, background thread | Architecture choice | Simpler startup; same process means easier event loop reference passing |

**Deprecated/outdated approaches to avoid:**
- `loop.run_until_complete(bureau.run())` — `run()` calls `asyncio.run()` internally and creates its own loop
- `bureau.run()` in FastAPI lifespan handlers — blocks the ASGI server
- Custom `CORSMiddleware` subclass to add PNA headers — now unnecessary since Starlette 0.51.0

---

## Open Questions

1. **`ctx.send_and_receive` timeout behavior**
   - What we know: UAgentClient has a default timeout of ~35 seconds; this is the HTTP client timeout, not a uAgents-level timeout
   - What's unclear: Whether `ctx.send_and_receive` in Bureau-local agent communication (same process) has a different timeout, and whether it raises `TimeoutError` or returns `None`
   - Recommendation: In Phase 1, test a stub round-trip call between orchestrator and one domain agent with a deliberate 5-second delay in the responder to observe timeout behavior. Document the result before Phase 2 relies on it.

2. **uvicorn `loop="none"` behavior**
   - What we know: uvicorn accepts a `loop` parameter; `"none"` should use the current event loop
   - What's unclear: Whether `uvicorn.run(app, loop="none")` correctly uses a pre-existing event loop set with `asyncio.set_event_loop()`
   - Recommendation: Verify with a simple startup test before adding Bureau thread. If uvicorn creates a new loop anyway, switch to `asyncio.run(uvicorn_serve())` pattern with an explicit asyncio.run entry point.

3. **Report delivery: SSE event vs separate REST GET**
   - What we know: Three event types are locked (thoughts, messages, status). Report content is Claude's discretion.
   - Recommendation: Use a dedicated `GET /report` REST endpoint that returns the final report JSON. The orchestrator's completion SSE event (`type: "status", status: "done"`) triggers the frontend to fetch from `/report`. This keeps SSE events small and the report retrieval simple/cacheable.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (not yet installed — Wave 0 gap) |
| Config file | `agents/pyproject.toml` — Wave 0 gap |
| Quick run command | `pytest agents/tests/ -x -q` |
| Full suite command | `pytest agents/tests/ -q` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFRA-01 | All 5 agents register with Bureau and are addressable | integration | `pytest agents/tests/test_bureau.py::test_all_agents_registered -x` | Wave 0 |
| INFRA-01 | Round-trip message: orchestrator -> portfolio agent -> orchestrator | integration | `pytest agents/tests/test_bureau.py::test_stub_roundtrip -x` | Wave 0 |
| INFRA-02 | SSE endpoint returns 200 with correct content-type | smoke | `pytest agents/tests/test_bridge.py::test_sse_connects -x` | Wave 0 |
| INFRA-02 | push_event() delivers event to SSE consumer | integration | `pytest agents/tests/test_bridge.py::test_event_delivered -x` | Wave 0 |
| INFRA-02 | CORS Access-Control-Allow-Private-Network header present | smoke | `pytest agents/tests/test_bridge.py::test_pna_header -x` | Wave 0 |
| INFRA-03 | All model classes are importable from shared module | unit | `pytest agents/tests/test_models.py::test_imports -x` | Wave 0 |
| INFRA-03 | Models serialize/deserialize without data loss | unit | `pytest agents/tests/test_models.py::test_roundtrip -x` | Wave 0 |
| INFRA-04 | MOCK_DATA=true returns mock fixture, not None | unit | `pytest agents/tests/test_mock.py::test_mock_toggle -x` | Wave 0 |
| INFRA-04 | All 5 agents return non-None response in mock mode | integration | `pytest agents/tests/test_mock.py::test_all_agents_mock -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest agents/tests/ -x -q --tb=short`
- **Per wave merge:** `pytest agents/tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `agents/pyproject.toml` — pytest config, `[tool.pytest.ini_options]`
- [ ] `agents/tests/__init__.py` — empty init
- [ ] `agents/tests/test_models.py` — covers INFRA-03
- [ ] `agents/tests/test_bridge.py` — covers INFRA-02
- [ ] `agents/tests/test_bureau.py` — covers INFRA-01
- [ ] `agents/tests/test_mock.py` — covers INFRA-04
- [ ] Framework install: `uv pip install pytest pytest-asyncio` — if not already in deps

---

## Sources

### Primary (HIGH confidence)

- [uAgents async_loops docs](https://uagents.fetch.ai/docs/guides/async_loops) — `bureau.run_async()`, external event loop pattern, loop= constructor parameter
- [Starlette release notes](https://starlette.dev/release-notes/) — confirmed `allow_private_network` added in 0.51.0 (Jan 10, 2026)
- [Python asyncio docs — call_soon_threadsafe](https://docs.python.org/3/library/asyncio-eventloop.html) — thread-safe cross-loop scheduling
- [sse-starlette PyPI](https://pypi.org/project/sse-starlette/) — version 3.3.3, March 17, 2026; EventSourceResponse API
- [asyncio.Queue docs](https://docs.python.org/3/library/asyncio-queue.html) — not thread-safe; confirmed single-loop use only
- `.planning/research/STACK.md` — uAgents 0.24.0 confirmed current, FastAPI bridge pattern, sse-starlette recommendation
- `.planning/research/ARCHITECTURE.md` — Bureau pattern, asyncio.Queue bridge, agent structure
- `.planning/research/PITFALLS.md` — Chrome PNA pitfall (Pitfall 6), Bureau/FastAPI anti-pattern (Anti-Pattern 2)

### Secondary (MEDIUM confidence)

- [uAgents on_message replies= requirement](https://uagents.fetch.ai/docs/guides/protocols) — `replies={ResponseType}` must be declared in handler decorator
- [Starlette PR #3065](https://github.com/Kludex/starlette/pull/3065) — allow_private_network merge confirmation
- [janus library](https://pypi.org/project/janus/) — version 2.0.0; alternative for sync-async queue if call_soon_threadsafe proves problematic

### Tertiary (LOW confidence)

- WebSearch result: UAgentClient default timeout ~35 seconds — single source, not in official API docs; treat as estimate until verified in Phase 1 test

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all versions verified against PyPI/official docs
- Architecture (threading pattern): MEDIUM — `bureau.run_async()` confirmed; `loop="none"` in uvicorn is an open question; cross-loop queue pattern is confirmed stdlib
- Pitfalls: HIGH — asyncio cross-loop issue is well-documented Python behavior; PNA fix confirmed in Starlette changelog

**Research date:** 2026-03-21
**Valid until:** 2026-04-20 (stable ecosystem; uAgents 0.24.0 is recent)
