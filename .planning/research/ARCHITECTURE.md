# Architecture Research

**Domain:** Multi-agent investment analysis platform (fetch.ai uAgents + React frontend)
**Researched:** 2026-03-21
**Confidence:** MEDIUM — uAgents framework patterns verified via official docs; real-time streaming pattern is a recommended adaptation not natively provided by uAgents

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        React Frontend (Vite)                         │
│                                                                       │
│  ┌────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  Report View   │  │   Agent Graph    │  │   Chat Interface     │  │
│  │ (markdown+charts) │  │  (D3/ReactFlow) │  │  (user → orchestrator) │ │
│  └───────┬────────┘  └────────┬─────────┘  └──────────┬───────────┘  │
│          │                   │                         │              │
│          └───────────────────┴─────────────────────────┘              │
│                              │ HTTP + SSE                             │
└──────────────────────────────┼─────────────────────────────────────── ┘
                               │
┌──────────────────────────────┼─────────────────────────────────────── ┐
│                  FastAPI Bridge (Python)                               │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  /api/report/generate   POST — triggers report pipeline      │    │
│  │  /api/report/stream     GET  — SSE stream of agent events    │    │
│  │  /api/chat              POST — relay chat to orchestrator    │    │
│  │  /api/upload/portfolio  POST — ingest CSV                    │    │
│  └──────────────┬────────────────────────────────────────────── ┘    │
│                 │  ctx.send / ctx.send_and_receive                    │
└─────────────────┼─────────────────────────────────────────────────── ┘
                  │
┌─────────────────┼─────────────────────────────────────────────────── ┐
│           uAgents Layer (Python Bureau — all local)                   │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                    Orchestrator Agent                          │   │
│  │  - Receives report trigger from bridge                        │   │
│  │  - Dispatches to domain agents via ctx.send_and_receive       │   │
│  │  - Synthesizes unified narrative (LLM call)                   │   │
│  │  - Streams thought events back through shared event queue     │   │
│  └───────┬──────────┬──────────────┬──────────────┬─────────────┘   │
│          │          │              │              │                   │
│  ┌───────┴───┐ ┌────┴──────┐ ┌────┴──────┐ ┌────┴──────┐           │
│  │ Portfolio │ │  News     │ │ Modeling  │ │  Crypto/  │           │
│  │  Agent   │ │  Agent    │ │  Agent    │ │  Commod.  │           │
│  │          │ │           │ │           │ │  Agent    │           │
│  │ CSV parse │ │ API fetch │ │ regression│ │ price data│           │
│  │ sector   │ │ sentiment │ │ backtest  │ │ sentiment │           │
│  │ analysis │ │ relevance │ │ charting  │ │           │           │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘           │
│                                                                       │
│  All agents run in one Bureau process. Communication via agent        │
│  addresses using ctx.send / ctx.send_and_receive.                     │
└─────────────────────────────────────────────────────────────────────── ┘
```

### Component Responsibilities

| Component                | Responsibility                                                                    | Implementation                     |
| ------------------------ | --------------------------------------------------------------------------------- | ---------------------------------- |
| React Frontend           | Report display, agent graph visualization, chat UI, CSV upload                    | Vite + React + ReactFlow or D3     |
| FastAPI Bridge           | HTTP/SSE gateway between frontend and agent layer; event queue management         | FastAPI + asyncio.Queue            |
| Orchestrator Agent       | Receives triggers, dispatches to domain agents, synthesizes final report with LLM | uAgents + LLM call (OpenAI/Gemini) |
| Portfolio Agent          | Parses uploaded CSV, computes diversification, sector exposure, stock impact      | uAgents + pandas/numpy             |
| News Agent               | Fetches financial news from APIs, scores sentiment, filters relevance             | uAgents + newsapi/alphavantage     |
| Modeling Agent           | Runs regression/backtesting, generates charts as base64 PNG                       | uAgents + matplotlib/scipy         |
| Crypto/Commodities Agent | Fetches crypto/commodity prices, headlines, and sentiment                         | uAgents + CoinGecko API            |
| Shared Event Queue       | Thread-safe queue where all agents push thought/status events                     | asyncio.Queue in FastAPI process   |

## Recommended Project Structure

```
Wealth Council/
├── frontend/                    # Vite + React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── AgentGraph/      # ReactFlow graph, agent cards, animated edges
│   │   │   ├── ReportView/      # Markdown renderer with chart embedding
│   │   │   └── ChatPanel/       # Chat input and message thread
│   │   ├── hooks/
│   │   │   ├── useAgentStream.ts  # SSE subscription hook
│   │   │   └── useReport.ts       # Report state management
│   │   ├── api/                 # Typed fetch wrappers for bridge endpoints
│   │   └── types/               # Shared TypeScript types
│   └── vite.config.ts
│
├── agents/                      # Python uAgents layer
│   ├── orchestrator.py          # Orchestrator agent definition
│   ├── portfolio_agent.py       # Portfolio analysis agent
│   ├── news_agent.py            # News and sentiment agent
│   ├── modeling_agent.py        # Quantitative modeling agent
│   ├── crypto_agent.py          # Crypto/commodities agent
│   ├── bureau.py                # Bureau runner — starts all agents
│   ├── models/                  # Shared Pydantic message models
│   │   ├── report.py
│   │   ├── portfolio.py
│   │   ├── news.py
│   │   ├── modeling.py
│   │   └── crypto.py
│   └── protocols/               # Reusable protocol definitions
│       └── analysis_protocol.py
│
├── bridge/                      # FastAPI bridge server
│   ├── main.py                  # FastAPI app, SSE endpoint, event queue
│   ├── routes/
│   │   ├── report.py            # /api/report/* routes
│   │   ├── chat.py              # /api/chat route
│   │   └── upload.py            # /api/upload/portfolio route
│   └── agent_client.py          # Wrapper for ctx.send to orchestrator
│
└── start.sh                     # Starts bureau + bridge in parallel
```

### Structure Rationale

- **agents/ vs bridge/:** The uAgents Bureau and the FastAPI bridge are separate Python processes. This is necessary because the Bureau's event loop is managed by uAgents; FastAPI needs its own async loop for SSE. They communicate through a shared event queue or HTTP to localhost.
- **models/:** Pydantic message models must be identical on both sides of every agent-to-agent message. Centralizing them prevents drift.
- **frontend/hooks/:** Separating SSE subscription and report state into hooks keeps components clean and makes the streaming logic reusable.

## Architectural Patterns

### Pattern 1: FastAPI Bridge as SSE Gateway

**What:** A FastAPI server sits between the React frontend and the uAgents Bureau. It exposes REST endpoints for triggering reports and a GET endpoint that streams Server-Sent Events back to the browser as agents emit thought events.

**When to use:** uAgents do not natively push to HTTP clients. The bridge solves the impedance mismatch: uAgents emit events to an in-process queue; FastAPI drains the queue and forwards events over SSE.

**Trade-offs:** Adds one process to run, but is the simplest real-time streaming pattern. Avoids WebSockets complexity while still delivering live updates. SSE is unidirectional (server to client), which is exactly what the agent thought stream requires.

**Example:**
```python
# bridge/main.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio, json

app = FastAPI()
event_queue: asyncio.Queue = asyncio.Queue()

@app.get("/api/report/stream")
async def stream_events():
    async def generate():
        while True:
            event = await event_queue.get()
            yield f"data: {json.dumps(event)}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")

# Agents call push_event() to emit into the queue
async def push_event(agent_name: str, event_type: str, payload: dict):
    await event_queue.put({"agent": agent_name, "type": event_type, **payload})
```

```typescript
// frontend/hooks/useAgentStream.ts
export function useAgentStream(onEvent: (e: AgentEvent) => void) {
  useEffect(() => {
    const es = new EventSource("/api/report/stream")
    es.onmessage = (e) => onEvent(JSON.parse(e.data))
    return () => es.close()
  }, [onEvent])
}
```

### Pattern 2: Orchestrator Fan-Out with ctx.send_and_receive

**What:** The orchestrator receives a single trigger message and sends requests to each domain agent concurrently using `asyncio.gather` over `ctx.send_and_receive`. It collects all domain results before synthesizing.

**When to use:** All domain agents can run in parallel — their analyses are independent. Waiting for each sequentially would be slow. Fan-out-then-collect is the right pattern.

**Trade-offs:** All domain agents must respond within a timeout. If one fails, the orchestrator must decide whether to proceed with partial results or abort. For a 24-hour hackathon, a simple timeout + fallback empty result is sufficient.

**Example:**
```python
# agents/orchestrator.py
@orchestrator.on_message(model=ReportRequest)
async def handle_report_request(ctx: Context, sender: str, msg: ReportRequest):
    await push_event("orchestrator", "thinking", {"text": "Dispatching to domain agents..."})

    # Concurrent requests to all domain agents
    portfolio_result, news_result, modeling_result, crypto_result = await asyncio.gather(
        ctx.send_and_receive(PORTFOLIO_AGENT_ADDR, PortfolioRequest(csv_path=msg.csv_path)),
        ctx.send_and_receive(NEWS_AGENT_ADDR, NewsRequest(topics=msg.topics)),
        ctx.send_and_receive(MODELING_AGENT_ADDR, ModelingRequest(holdings=msg.holdings)),
        ctx.send_and_receive(CRYPTO_AGENT_ADDR, CryptoRequest()),
    )

    await push_event("orchestrator", "thinking", {"text": "Synthesizing unified narrative..."})
    report = await synthesize_report(portfolio_result, news_result, modeling_result, crypto_result)
    await ctx.send(sender, ReportResponse(markdown=report))
```

### Pattern 3: Agent Thought Emission via Shared Queue

**What:** Each agent calls a shared `push_event()` function before and after significant actions. These events are typed (e.g., `thinking`, `fetching`, `complete`, `message_sent`, `message_received`) and carry the agent name plus a human-readable description.

**When to use:** This is how the agent graph visualization gets its live feed. Without a thought stream, the graph would be static.

**Trade-offs:** The shared queue is an in-process coupling between agents and the bridge. For a hackathon this is fine. A production system would use Redis pub/sub or a message broker.

**Example event schema:**
```typescript
type AgentEvent =
  | { agent: AgentName; type: "thinking"; text: string }
  | { agent: AgentName; type: "message_sent"; to: AgentName; title: string; description: string }
  | { agent: AgentName; type: "message_received"; from: AgentName; title: string }
  | { agent: AgentName; type: "complete"; summary: string }
```

## Data Flow

### Report Generation Flow

```
User clicks "Generate Report"
    ↓
React → POST /api/report/generate  { csv_path, topics }
    ↓
FastAPI bridge → ctx.send(ORCHESTRATOR_ADDR, ReportRequest)
    ↓
Orchestrator emits: { type: "thinking", text: "Starting analysis..." }
    ↓ (concurrent fan-out)
Portfolio Agent ──────────────────────────┐
News Agent ───────────────────────────────┤ each emits thought events
Modeling Agent ───────────────────────────┤ as they work
Crypto Agent ─────────────────────────────┘
    ↓ (all respond via ctx.send_and_receive)
Orchestrator collects results
Orchestrator emits: { type: "thinking", text: "Synthesizing narrative..." }
Orchestrator calls LLM to produce unified markdown report
Orchestrator emits: { type: "complete", summary: "Report ready" }
Orchestrator → ctx.send(bridge_agent_addr, ReportResponse)
    ↓
FastAPI stores report, emits final SSE event { type: "report_ready" }
    ↓
React: useAgentStream fires, report state updates
React renders ReportView with markdown + embedded charts
```

### Agent Thought Stream Flow (SSE)

```
React mounts AgentGraph
    ↓
useAgentStream opens EventSource to GET /api/report/stream
    ↓
Any agent calls push_event(name, type, payload)
    ↓
asyncio.Queue receives event
    ↓
FastAPI SSE generator yields  "data: {...}\n\n"
    ↓
Browser EventSource.onmessage fires
    ↓
AgentGraph updates node state (thought text, pulse animation)
Animated edge pulses when type = "message_sent"
```

### Chat Flow

```
User submits chat message
    ↓
React → POST /api/chat  { message: string }
    ↓
FastAPI → ctx.send_and_receive(ORCHESTRATOR_ADDR, ChatRequest)
    ↓
Orchestrator classifies intent, dispatches to relevant domain agent(s)
Domain agents emit thought events (visible in graph)
Orchestrator assembles response
    ↓
FastAPI returns { response: string }
    ↓
React appends to chat thread
```

### State Management

```
AgentEventStream (SSE)
    ↓ onEvent dispatch
agentGraphStore (Zustand or useReducer)
    ├── nodes[agentName].thoughts[]   — append each "thinking" event
    ├── nodes[agentName].status       — idle | active | complete
    └── edges[src→dst].pulseQueue[]   — message_sent events drive animations

reportStore
    ├── status: idle | generating | ready | error
    └── content: string (markdown)
```

## Scaling Considerations

This is a 24-hour hackathon demo — scaling is not a concern. The architecture below is intentionally minimal.

| Scale                       | Architecture                                                                         |
| --------------------------- | ------------------------------------------------------------------------------------ |
| Single demo user            | Bureau (all agents in one process) + FastAPI bridge on localhost                     |
| Multi-user (post-hackathon) | Move agents to Agentverse hosted; use Redis queue per session; auth layer            |
| Production                  | Separate agent pods, message broker (RabbitMQ/Redis Streams), user session isolation |

### Hackathon Scaling Priorities

1. **First bottleneck:** The LLM synthesis call in the orchestrator. If it times out, the report never completes. Mitigation: set a generous timeout (60s) and stream partial content if possible.
2. **Second bottleneck:** Concurrent financial API calls in domain agents. Free tier rate limits will bite. Mitigation: sequential fallback with cached stub data for demo purposes.

## Anti-Patterns

### Anti-Pattern 1: Putting REST endpoints on protocols instead of the agent

**What people do:** Decorate a Protocol method with `@protocol.on_rest_post()`.

**Why it's wrong:** The uAgents documentation explicitly states REST endpoints are "only available at the agent level" — the decorator will fail or be silently ignored on a Protocol.

**Do this instead:** Put `@agent.on_rest_post()` on the agent itself. Use Protocols only for inter-agent message definitions.

### Anti-Pattern 2: Running the Bureau inside the FastAPI process

**What people do:** Import Bureau from uagents and call `bureau.run()` inside a FastAPI lifespan handler.

**Why it's wrong:** `bureau.run()` blocks the calling thread. FastAPI's async event loop will starve. The SSE endpoint will never yield events.

**Do this instead:** Run the Bureau as a separate Python process. The bridge communicates with agents via HTTP to their REST endpoints, or via a shared queue if colocated as separate threads with care. The simplest hackathon approach: `start.sh` launches both as separate `python` processes.

### Anti-Pattern 3: Polling for agent results instead of SSE

**What people do:** React frontend polls `GET /api/report/status` every second.

**Why it's wrong:** Creates latency, unnecessary HTTP traffic, and the agent graph cannot show live thought streams — only coarse status.

**Do this instead:** SSE from the bridge. One persistent connection, push-based, no polling.

### Anti-Pattern 4: Hosting all agents on Agentverse for a hackathon

**What people do:** Deploy each agent to Agentverse cloud hosting expecting easy frontend connectivity.

**Why it's wrong:** Hosted agents on Agentverse "reset global variables after each call" — they cannot hold in-flight state across the multi-step report pipeline. The shared event queue pattern requires agents to be in the same process context as the bridge (or at minimum on the same machine). Remote hosted agents also add latency and require Agentverse API authentication.

**Do this instead:** Run all agents locally using Bureau. Register with agentverse via Mailbox or Proxy for discoverability (satisfies hackathon track requirement) but execute locally.

## Integration Points

### External Services

| Service                                      | Integration Pattern                                | Notes                                                                     |
| -------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------- |
| Financial news API (NewsAPI / Alpha Vantage) | HTTP GET in News Agent on report trigger           | Free tier: 100 req/day on NewsAPI. Cache results.                         |
| CoinGecko API                                | HTTP GET in Crypto Agent                           | Free, no auth. 10-30 calls/min.                                           |
| LLM (OpenAI / Gemini)                        | HTTP POST in Orchestrator for synthesis            | Required for narrative generation. Use streaming completions if possible. |
| Agentverse Almanac                           | Auto-registration on agent startup via uAgents SDK | Required to satisfy fetch.ai track requirement. Needs FET tokens for gas. |

### Internal Boundaries

| Boundary                            | Communication                                                                                         | Notes                                                                    |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| React ↔ FastAPI Bridge              | HTTP REST + SSE                                                                                       | Vite proxy config points `/api/*` to bridge port during dev              |
| FastAPI Bridge ↔ Orchestrator Agent | `ctx.send` to orchestrator's local REST endpoint (`/report`)                                          | Bridge holds orchestrator's address constant                             |
| Orchestrator ↔ Domain Agents        | `ctx.send_and_receive` by agent address                                                               | Addresses are deterministic from seed phrases — hardcode in config       |
| Agents ↔ Event Queue                | In-process `asyncio.Queue` (if bridge and bureau share process via threads) OR HTTP callback endpoint | Shared queue is simplest; see anti-pattern 2 for process boundary caveat |

## Build Order Implications

Dependencies flow bottom-up. Build in this order:

1. **Shared message models** (`agents/models/`) — Everything else depends on these. No models = no typed communication.
2. **Individual domain agents** — Each is independent. Portfolio, News, Crypto, Modeling can be built in parallel. Test each with a standalone `agent.run()` and a curl to its REST endpoint.
3. **Bureau runner** — Wire domain agents into `Bureau`. Verify inter-agent address resolution.
4. **Orchestrator agent** — Depends on domain agents existing and responding. Build fan-out dispatch + LLM synthesis here.
5. **FastAPI bridge** — Depends on orchestrator having a stable address and REST endpoint. Add the SSE event queue here.
6. **React frontend** — Build against the bridge API. Start with report display, then add SSE-driven graph, then chat.

## Sources

- [uAgents Framework Docs](https://uagents.fetch.ai/docs) — Official docs, HIGH confidence
- [REST Endpoints Guide](https://uagents.fetch.ai/docs/guides/rest_endpoints) — Agent-level REST, HIGH confidence
- [Agent Types: Hosted/Local/Mailbox/Proxy](https://uagents.fetch.ai/docs/guides/types) — Deployment options, HIGH confidence
- [uAgent-to-uAgent Communication](https://innovationlab.fetch.ai/resources/docs/agent-communication/uagent-uagent-communication) — Message passing patterns, HIGH confidence
- [Frontend Integration Example](https://innovationlab.fetch.ai/resources/docs/1.0.4/examples/integrations/frontend-integration) — Flask bridge pattern, MEDIUM confidence (Flask, not FastAPI — pattern is transferable)
- [Node.js Client Integration](https://innovationlab.fetch.ai/resources/docs/examples/integrations/nodejs-client-integration) — Bridge architecture rationale, MEDIUM confidence
- [Fetch.ai Architecture Paper](https://arxiv.org/html/2510.18699v1) — System overview, MEDIUM confidence
- [Agent Handlers Docs](https://uagents.fetch.ai/docs/guides/handlers) — on_interval/on_message/on_query/on_event, HIGH confidence
- SSE streaming pattern for agent thoughts: industry standard (FastAPI + asyncio.Queue + EventSource) — MEDIUM confidence for this specific combination, HIGH confidence for SSE as the right transport choice

---
*Architecture research for: Wealth Council — fetch.ai uAgents investment analysis platform*
*Researched: 2026-03-21*
