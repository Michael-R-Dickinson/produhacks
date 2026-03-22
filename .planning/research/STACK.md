# Stack Research

**Domain:** Multi-agent investment intelligence platform (fetch.ai uAgents + Vite/React)
**Researched:** 2026-03-21
**Confidence:** MEDIUM-HIGH (uAgents core: HIGH | financial APIs: MEDIUM | visualization: HIGH)

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| uAgents (fetch.ai) | 0.24.0 | Agent runtime, inter-agent messaging, agentverse hosting | The required fetch.ai hackathon primitive. Version 0.24.0 released 2026-03-04 is the current stable. Requires Python >=3.10, <4.0 |
| Python | 3.11 | Agent implementation language | 3.11 is the sweet spot: uAgents supports 3.10-3.14, 3.11 is widely available in CI/cloud, stable performance gains over 3.10 |
| FastAPI | 0.115.x | HTTP bridge between Vite/React frontend and agent swarm | uAgents REST endpoints are agent-local only; a FastAPI process bridges the web frontend to the Bureau over HTTP/SSE. This is the standard pattern |
| Vite | 6.x | Frontend build tool | Required by project. Current is v6. Zero config, fast HMR, excellent TS support |
| React | 19.x | Frontend framework | Required by project. Concurrent mode features aid streaming/SSE display |
| TypeScript | 5.x | Frontend type safety | Standard in all 2025 React projects. No reason not to use it |

### Agent Layer Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| openai | 1.x | LLM calls from inside agents | Use for orchestrator synthesis and domain agent analysis. GPT-4o mini is the cheapest capable model at $0.15/1M input tokens — ideal for hackathon budget |
| uagents[llm] | 0.24.0 extras | LLM integrations bundled with uAgents | Install with `pip install "uagents[llm]"` — includes LangChain adapter if you want the LangGraph integration path |
| pandas | 2.x | Portfolio CSV parsing and data manipulation | Portfolio agent reads CSV uploads, computes diversification metrics. Standard data science library |
| numpy | 1.26.x | Numerical operations, regression | Modeling agent statistical work. Pinned to 1.26 for broad compatibility |
| scikit-learn | 1.5.x | Regression models, backtesting primitives | Modeling agent — linear/logistic regression on portfolio holdings |
| matplotlib | 3.9.x | Chart generation as base64 PNG | Modeling agent generates charts, encodes to base64, embeds as `![chart](data:image/png;base64,...)` in report markdown. Simpler than Plotly for server-side static generation |
| httpx | 0.27.x | Async HTTP calls from agents to financial APIs | Prefer over `requests` in async uAgent handlers — non-blocking |
| python-dotenv | 1.x | API key management in agents | Standard env var loading |
| uvicorn | 0.30.x | ASGI server for FastAPI bridge | Runs alongside Bureau in same process or as separate process |

### Financial Data APIs

| API | Free Tier | Purpose | Why Recommended |
|-----|-----------|---------|-----------------|
| **Finnhub** | 60 req/min, US stocks + crypto + news + sentiment | Primary market data + news source | Most generous free tier for hackathons. Covers stocks, forex, crypto, company news with AI sentiment scores. Single key covers all needed domains |
| **CoinGecko** (Demo plan) | 30 req/min, 10,000/month | Crypto price and market data | Free demo key from coingecko.com. Best coverage of crypto assets, commodities-adjacent tokens. More reliable than Finnhub for crypto specifics |
| **Alpha Vantage** | 25 req/day, 5 req/min | Backup for historical OHLCV + news sentiment | 25 req/day is very tight — use only as fallback if Finnhub is insufficient. Their AI news sentiment endpoint is good but the daily cap makes it impractical as primary |
| **yfinance (Python)** | Unlimited (unofficial scraper) | Historical price data for backtesting | Use ONLY inside the Modeling agent for longer historical series needed for regression/backtest. It is a scraper and can break, but is zero-cost and works well for occasional historical pulls. Do NOT use for real-time data |

**API Strategy for hackathon:** Finnhub as primary for everything (news, sentiment, stock quotes, crypto). CoinGecko for dedicated crypto data. yfinance for historical backtesting windows only.

### Frontend Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| React Flow (`@xyflow/react`) | 12.10.x | Agent graph visualization — nodes, edges, animation | The right tool for this specific use case. Designed for node-based UIs with custom node components, animated edges, and interactive layout. Custom nodes ARE the agent cards with streaming thought feeds. Animated edges show message pulses. Excellent DX for hackathon speed |
| Zustand | 5.x | Client-side UI state | Agent graph state (node positions, active connections), chat history, report content. Minimal API, no boilerplate |
| TanStack Query | 5.x | Server state and SSE subscription management | Use for the SSE connection to FastAPI bridge, report fetch polling, API data synchronization |
| react-markdown | 9.x with `remark-gfm` | Render report markdown with tables and embedded charts | Orchestrator produces markdown. react-markdown renders it including `![chart](data:image/png;base64,...)` inline images |
| `eventsource` / native EventSource | browser native | SSE client for agent thought streaming | Use native browser EventSource API for the SSE stream from FastAPI. No library needed |
| Tailwind CSS | 4.x | Styling | Fast utility-first styling — critical for 24h hackathon. No custom CSS architecture needed |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv (Astral) | Python dependency management for agent layer | Faster than pip, handles lockfiles properly, use `uv venv` + `uv pip install` |
| Agentverse Inspector | Local agent debugging UI | Built into uAgents CLI — run `agentverse inspect` to see agent messages locally without deploying |
| pnpm | Node package manager | Faster than npm, good workspace support if monorepo layout needed |

---

## Installation

```bash
# Python agent layer
uv venv .venv && source .venv/bin/activate
uv pip install "uagents[llm]==0.24.0" fastapi uvicorn httpx pandas numpy scikit-learn matplotlib python-dotenv openai

# Frontend
pnpm create vite frontend --template react-ts
cd frontend
pnpm add @xyflow/react zustand @tanstack/react-query react-markdown remark-gfm tailwindcss
pnpm add -D @types/react @types/react-dom typescript
```

---

## Architecture: How Frontend Connects to Agents

uAgents run in a `Bureau` (multiple agents, single Python process). The Bureau has no built-in WebSocket or SSE. The connection bridge pattern is:

```
Vite/React  --HTTP/SSE-->  FastAPI bridge  --uagents protocol-->  Bureau (agents)
```

FastAPI runs alongside the Bureau in the same Python process using `asyncio`. The Bureau uses `bureau.run()` which is async-compatible. FastAPI exposes:
- `POST /report` — triggers orchestrator agent
- `GET /stream/{session_id}` — SSE endpoint streaming agent "thoughts" as JSON events
- `POST /chat` — routes message through orchestrator

Agents write to an in-memory queue; FastAPI SSE endpoint reads from the queue and streams to frontend.

uAgents also support `@agent.on_rest_post()` decorators for direct HTTP POST handlers — use these as an alternative to FastAPI for simpler endpoints. The direct REST handlers run on the agent's own port (e.g., `localhost:8000/rest/post`).

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| React Flow (`@xyflow/react`) | Reagraph | Use Reagraph for large-scale network graphs (100+ nodes). For 5 agent nodes with rich custom card UIs, React Flow's component model is far more flexible |
| React Flow | D3.js force graph | Only if you need physics simulation for organic layout. D3 requires significantly more implementation time |
| Finnhub (primary) | Polygon.io | Use Polygon if you have a paid account — richer data, better reliability. Free tier is too limited |
| FastAPI SSE bridge | WebSocket (raw) | WebSockets add reconnection complexity for a hackathon. SSE is simpler, one-directional, and sufficient for agent thought streaming |
| matplotlib (server-side charts) | Plotly.py | Use Plotly if you need interactive charts in the frontend. For the hackathon, static PNG charts embedded in markdown is simpler and faster to implement |
| GPT-4o mini | Claude Haiku 4.5 | Claude Haiku 4.5 is $1.00/1M input vs $0.15/1M for GPT-4o mini. For a 24h hackathon with many agent calls, cost matters. Use GPT-4o mini unless you specifically need Haiku's capabilities |
| uv | pip/venv | pip works fine but uv is significantly faster for dependency resolution |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| yfinance as real-time data source | Unofficial Yahoo Finance scraper — breaks without warning when Yahoo changes backend. Already documented instability in 2025. Rate limiting / IP blocking on heavy use | Finnhub for real-time quotes |
| NewsAPI.org | Free tier has 24-hour delay on articles and only 100 req/day. Completely breaks the "current news" use case | Finnhub market news endpoint (free, ~real-time) |
| Redux / Redux Toolkit | Heavy boilerplate, overkill for a single-user hackathon app. Zustand + TanStack Query covers all needs with a fraction of code | Zustand + TanStack Query |
| Agentverse-hosted agents only | Agentverse-hosted agents (via the IDE) cannot expose REST endpoints or SSE streams accessible to a locally-running frontend during development. Run agents locally during hackathon, use mailbox/agentverse for the demo deployment step | Local Bureau + FastAPI bridge for dev |
| WebSockets for agent streaming | Adds reconnection logic, server-side connection state, more complex than needed. SSE is sufficient for one-way agent thought streaming | Native EventSource / SSE |
| CrewAI / LangGraph as agent layer | These are alternative agent frameworks. This is a fetch.ai hackathon — the judging criteria favor uAgents and agentverse usage. Do not replace uAgents with another framework | uAgents 0.24.0 |
| Alpha Vantage as primary API | 25 req/day free tier is unusable as a primary data source for a multi-agent system that fires on each report generation | Finnhub (60 req/min) |

---

## Stack Patterns by Variant

**If Bureau REST endpoints are sufficient (no streaming thoughts):**
- Use `@agent.on_rest_post()` decorators on the orchestrator agent
- Frontend calls the agent's local port directly
- No FastAPI bridge needed
- Simpler architecture but loses SSE streaming for the live graph visualization

**If deploying to agentverse for demo (final submission):**
- Register each agent on agentverse and enable Mailbox
- The mailbox handles queuing when agents cycle on/off
- Frontend still connects to your FastAPI bridge (deployed separately or tunneled via ngrok)
- Agent addresses on agentverse take the form `agent1q...` (bech32 encoded)

**If Finnhub rate limits hit during demo (5 agents firing simultaneously):**
- Add a shared rate-limiter middleware in the Python layer
- Use `asyncio.Semaphore` to serialize external API calls across agents
- Cache responses in a simple in-memory dict keyed by symbol + timestamp bucket

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| uagents==0.24.0 | Python 3.10-3.14 | Do NOT use Python 3.9 — explicitly excluded |
| uagents==0.24.0 | fastapi>=0.100 | No known conflicts |
| @xyflow/react==12.x | React 18+ and React 19 | v12 dropped support for React 17 |
| react-markdown==9.x | remark-gfm==4.x | Match major versions — v9 requires remark-gfm v4 |
| TanStack Query v5 | React 18+ | v5 dropped React 17 support and changed the `useQuery` API signature |

---

## Sources

- [uAgents PyPI page](https://pypi.org/project/uagents/) — version 0.24.0, Python >=3.10 confirmed HIGH confidence
- [uAgents official docs](https://uagents.fetch.ai/docs) — Bureau pattern, mailbox, agent concepts HIGH confidence
- [uAgents REST endpoints guide](https://uagents.fetch.ai/docs/guides/rest_endpoints) — `on_rest_get/post` decorators confirmed HIGH confidence
- [uAgents run local guide](https://uagents.fetch.ai/docs/guides/run_local_agents) — Bureau multi-agent pattern confirmed HIGH confidence
- [Agentverse mailbox docs](https://uagents.fetch.ai/docs/agentverse/mailbox) — mailbox as message broker confirmed HIGH confidence
- [React Flow official site](https://reactflow.dev) — version 12.10.1 current, custom nodes/animated edges confirmed HIGH confidence
- [Reagraph GitHub](https://github.com/reaviz/reagraph) — WebGL network graphs, confirmed as alternative MEDIUM confidence
- [Finnhub pricing/docs](https://finnhub.io/docs/api/rate-limit) — 60 req/min free tier, stocks + crypto + news + sentiment MEDIUM confidence (rate limit page visited, pricing page confirmed via search)
- [CoinGecko API pricing](https://www.coingecko.com/en/api/pricing) — 30 req/min, 10,000/month demo plan MEDIUM confidence
- [Alpha Vantage](https://www.alphavantage.co/) — 25 req/day free tier confirmed MEDIUM confidence
- [yfinance reliability concerns](https://medium.com/@trading.dude/why-yfinance-keeps-getting-blocked-and-what-to-use-instead-92d84bb2cc01) — instability documented LOW-MEDIUM confidence (single source, matches known behavior)
- [Zustand + TanStack Query 2025 pattern](https://dev.to/devforgedev/you-dont-need-redux-zustand-tanstack-query-replaced-90-of-my-state-management-2ggi) — community consensus MEDIUM confidence
- [GPT-4o mini pricing](https://openai.com/api/pricing/) — $0.15/1M input tokens MEDIUM confidence
- [FastAPI SSE patterns](https://fastapi.tiangolo.com/tutorial/server-sent-events/) — EventSourceResponse pattern HIGH confidence

---

*Stack research for: InvestiSwarm — fetch.ai multi-agent investment intelligence platform*
*Researched: 2026-03-21*
