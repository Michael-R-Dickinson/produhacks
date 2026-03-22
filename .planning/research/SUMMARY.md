# Project Research Summary

**Project:** InvestiSwarm
**Domain:** Multi-agent investment intelligence platform (fetch.ai uAgents + Vite/React)
**Researched:** 2026-03-21
**Confidence:** MEDIUM

## Executive Summary

InvestiSwarm is a fetch.ai hackathon project that must satisfy two simultaneous goals: deliver a genuinely useful investment analysis tool and demonstrate compelling multi-agent coordination using the uAgents framework. The recommended architecture is a three-tier system — a React/Vite frontend, a FastAPI bridge server, and a uAgents Bureau running all domain agents locally. This three-tier split is non-negotiable: uAgents speak a binary protocol inaccessible from the browser, so the FastAPI bridge is a core infrastructure component, not an afterthought. The live agent graph visualization (React Flow nodes animated via SSE) is the primary differentiator that separates this from any ordinary investment report tool, and it is what judges will remember.

The recommended build order flows from dependencies: shared Pydantic message models first, then independent domain agents (Portfolio, News, Modeling, Crypto), then the Bureau wiring and Orchestrator fan-out, then the FastAPI SSE bridge, and finally the React frontend. The visualization layer must be built last as a decoupled broadcast side-channel — building it first is the single most common failure mode for this category of project. Financial API rate limits (Finnhub at 60 req/min is the right primary; Alpha Vantage's 25 req/day free tier is nearly useless as a primary source) and orchestrator context window overflow are the two technical risks most likely to cause demo failures.

The key mitigation strategy across all risks is defensive infrastructure from day one: mock data mode for all agents (so no live API quota is burned during development), strict `summary` field caps on every agent response model (to prevent context window overflow), and all agent communication routed through the FastAPI bridge (so the browser never directly contacts localhost agent ports, avoiding Chrome's Private Network Access permission prompts). If these three safeguards are in place before domain agent logic is written, the project is unlikely to fail on technical grounds.

## Key Findings

### Recommended Stack

The agent layer runs Python 3.11 with uAgents 0.24.0 as the required fetch.ai primitive. FastAPI + uvicorn forms the bridge layer, using `asyncio.Queue` and SSE to relay agent thought events to the frontend in real time. The frontend is Vite 6 + React 19 + TypeScript 5, with React Flow (`@xyflow/react` 12.x) as the agent graph renderer — it is the correct tool for this use case, offering custom node components and animated edges out of the box. Zustand 5 manages UI state (graph node positions, active connections), TanStack Query 5 manages the SSE subscription and report fetching.

For financial data, Finnhub is the clear primary: 60 req/min free, covering stocks, crypto, news, and sentiment in one key. CoinGecko (30 req/min, no auth) handles dedicated crypto data. yfinance is acceptable only inside the Modeling agent for historical backtesting series. Alpha Vantage (25 req/day) should be treated as a last resort. GPT-4o mini ($0.15/1M tokens) is the LLM for orchestrator synthesis — significantly cheaper than alternatives for a 24-hour window with many agent calls.

**Core technologies:**
- uAgents 0.24.0 (Python 3.11): agent runtime and inter-agent messaging — fetch.ai track requirement
- FastAPI + uvicorn: HTTP/SSE bridge between frontend and agent Bureau — the required impedance adapter
- React Flow (`@xyflow/react` 12.x): agent graph visualization — purpose-built for node-based UIs with animated edges
- Finnhub API: primary financial data source — most generous free tier (60 req/min)
- GPT-4o mini: orchestrator synthesis LLM — cheapest capable model for high-volume hackathon usage
- Zustand 5 + TanStack Query 5: frontend state — minimal boilerplate, replaces Redux entirely
- pandas + numpy + scikit-learn + matplotlib: Modeling agent quantitative stack — standard scientific Python

### Expected Features

The core product loop is: CSV upload -> report generation trigger -> multi-agent fan-out -> unified narrative report with embedded charts. The live agent graph with animated edges and streaming thought feeds is the feature that makes this different from any existing investment tool. Without it, the product is just a report generator. With it, judges see multi-agent coordination as a first-class experience.

**Must have (P1 — hackathon demo):**
- CSV upload and portfolio parsing — nothing else works without portfolio data
- Report generation trigger that drives the full agent swarm
- Live agent graph with animated edges and per-node thought streaming — the primary differentiator
- Unified narrative report with markdown rendering and embedded charts
- Financial news and sentiment via Finnhub
- Portfolio sector/diversification analysis
- fetch.ai Agentverse registration — required for the track; do this early
- At least one chart embedded in the report (allocation or backtest)

**Should have (P2 — add if P1 complete):**
- Chat interface routed through orchestrator — adds interactivity for judges
- Message hover tooltips on graph edges — low effort, high polish
- Crypto/commodities agent — adds breadth to report
- "Impact of adding X" portfolio analysis — impressive if chat is working

**Defer (v2+):**
- Brokerage API sync (Plaid, Fidelity) — OAuth complexity, days not hours
- Scheduled report generation — requires job scheduler and persistent storage
- User authentication and multi-user support — burns a quarter of the hackathon clock
- Real-time streaming market prices — zero demo value over snapshot pricing
- Persistent report history with database — in-memory is sufficient for demo

### Architecture Approach

The system uses a strict three-process architecture: the uAgents Bureau (all agents in one Python process), the FastAPI bridge (separate Python process with its own async event loop), and the Vite dev server / React frontend. Agents communicate via `ctx.send_and_receive` using deterministic addresses derived from seed phrases. The Orchestrator fans out to all four domain agents concurrently using `asyncio.gather`, collects results, then calls GPT-4o mini for narrative synthesis. Agents push thought events to a shared `asyncio.Queue`; the FastAPI SSE endpoint drains this queue and forwards events to the browser's native `EventSource`. All frontend requests go through the bridge — the browser never contacts agent ports directly.

**Major components:**
1. React Frontend — report display, agent graph visualization (React Flow), CSV upload, chat input
2. FastAPI Bridge — HTTP/SSE gateway, event queue management, CORS configuration
3. Orchestrator Agent — trigger handler, concurrent fan-out via `asyncio.gather`, LLM synthesis
4. Portfolio Agent — CSV parsing, sector/diversification analysis using pandas/numpy
5. News Agent — Finnhub news/sentiment fetch, relevance filtering
6. Modeling Agent — regression, backtesting, matplotlib chart generation (base64-encoded PNG)
7. Crypto/Commodities Agent — CoinGecko price and sentiment fetch
8. Shared asyncio.Queue — in-process event bus between agents and bridge SSE endpoint

### Critical Pitfalls

1. **Running agents on Agentverse as hosted (serverless) during development** — global Python variables reset per handler invocation, silently losing orchestration state mid-report. Prevention: run all agents locally via Bureau; use `ctx.storage` for any state that must persist; include `correlation_id` in all messages.

2. **No FastAPI bridge built upfront** — teams discover late that the browser cannot speak uAgents protocol. Prevention: the bridge is Phase 1 infrastructure, built before any domain agent logic. Verify with a dummy agent round-trip before writing domain code.

3. **Financial API rate limits exhausted before demo** — Alpha Vantage's 25 req/day is useless as a primary source; even Finnhub at 60 req/min can be exhausted by untamed parallel agent calls. Prevention: mock data mode from day one; aggressive response caching keyed by symbol + timestamp bucket; `asyncio.Semaphore` for shared rate-limiting across agents.

4. **Orchestrator context window overflow** — five sub-agents each returning verbose analysis text overflows LLM context and slows synthesis to 30+ seconds. Prevention: define strict `AgentResponse` Pydantic models with a `summary: str` (max 500 tokens) field; orchestrator uses summaries for synthesis, not raw blobs; set `max_tokens` on all sub-agent LLM calls.

5. **Visualization built before the core pipeline** — the agent graph is visually compelling and attracts disproportionate development time, but it is an observability layer on top of the pipeline, not the pipeline itself. Prevention: first end-to-end report (no visualization) must complete before any React Flow work begins. The SSE event queue decouples them — a broken frontend never breaks report generation.

6. **Chrome Private Network Access blocking localhost agent ports during demo** — Chrome 142+ requires explicit permission for pages to contact localhost. Prevention: all frontend requests go through the FastAPI bridge (public port); no direct browser-to-agent-port calls ever.

## Implications for Roadmap

Based on the dependency graph in ARCHITECTURE.md and the pitfall phase mappings in PITFALLS.md, four phases emerge naturally. The ordering is dictated by hard dependencies (models before agents, bridge before frontend, pipeline before visualization) and by the need to eliminate demo-killing risks in Phase 1.

### Phase 1: Foundation and Infrastructure

**Rationale:** Everything else depends on this. The three most catastrophic demo failures (no bridge, exhausted API quota, Chrome PNA) all trace back to infrastructure decisions. This phase eliminates all of them before a single line of domain logic is written.

**Delivers:**
- Project structure scaffolded (frontend/, agents/, bridge/ directories)
- Shared Pydantic message models defined for all agent-to-agent communication
- FastAPI bridge running with a dummy agent round-trip verified end-to-end
- Mock data mode implemented and toggled via env var for all agents
- Financial API client wrappers with caching and Finnhub as primary
- Agentverse registration and mailbox configured (satisfies track requirement early)
- All frontend requests routed through bridge (no direct localhost calls from browser)

**Addresses:** CSV upload infrastructure, agent scaffolding
**Avoids:** No-bridge pitfall, API rate limit exhaustion, Chrome PNA blocking

### Phase 2: Core Agent Pipeline (No Visualization)

**Rationale:** Build the full report generation pipeline — Portfolio, News, Modeling, Crypto agents plus Orchestrator synthesis — before touching any visualization. A working end-to-end report with static output is the prerequisite for Phase 3. This order also forces the orchestrator response contract (summary fields, max tokens) to be correct before the LLM is wired in.

**Delivers:**
- Portfolio Agent: CSV parsing, sector allocation, diversification metrics
- News Agent: Finnhub news fetch + sentiment scoring
- Modeling Agent: regression, backtesting, matplotlib chart (base64 PNG)
- Crypto Agent: CoinGecko price and sentiment
- Orchestrator: concurrent `asyncio.gather` fan-out, GPT-4o mini synthesis, unified markdown report
- Orchestrator produces a complete readable report (verified via curl, no frontend required)

**Uses:** uAgents 0.24.0, pandas, numpy, scikit-learn, matplotlib, httpx, openai (GPT-4o mini)
**Implements:** Orchestrator fan-out pattern, agent thought event emission, shared asyncio.Queue
**Avoids:** Context window overflow (enforce summary contracts here), code execution sandboxing for Modeling agent

### Phase 3: Frontend and Live Visualization

**Rationale:** The frontend is built against a working pipeline, not a mock. This means the SSE event stream carries real agent thought events, and the agent graph visualization is tested with actual data from the start. React Flow nodes map to real agent names; edge animations reflect real message_sent events.

**Delivers:**
- React Flow agent graph with custom node cards showing agent name and streaming thoughts
- Animated edge pulses on message_sent events from SSE stream
- ReportView: react-markdown rendering with base64 chart embedding
- CSV upload UI wired to bridge endpoint
- Report generation trigger button with loading state (animated graph IS the loading indicator)
- SSE subscription via native EventSource + `useAgentStream` hook

**Uses:** React Flow 12.x, Zustand 5, TanStack Query 5, react-markdown 9 + remark-gfm 4, Tailwind CSS 4
**Implements:** AgentGraph component, ReportView component, useAgentStream hook, agentGraphStore

### Phase 4: Chat, Polish, and Demo Prep

**Rationale:** Chat and polish are P2 features that add significant judge interaction value but must not gate the core demo. Demo prep (including verifying no localhost browser requests, testing on the actual demo machine, confirming mock mode toggle works) is a distinct phase that prevents the most common last-hour failures.

**Delivers:**
- Chat interface routed through orchestrator with intent classification
- Message hover tooltips on graph edges
- Thought stream rate-limited to 2-3 events/second per agent (avoid overwhelming UI)
- Per-agent error states surfaced in graph nodes
- Demo machine dry-run: all APIs on live data, mock mode toggle verified, no Chrome PNA issues
- Agentverse deployment verified (mailbox agents registered, addresses stable)

**Avoids:** UX pitfalls (no loading state, raw agent output displayed, thoughts too fast to read), Chrome PNA on demo day

### Phase Ordering Rationale

- **Models before agents:** Pydantic message models must be stable before any agent-to-agent calls are made. Changing models after the fact breaks both sides of every message.
- **Bridge before frontend:** The FastAPI bridge is infrastructure the frontend depends on. Testing against a real bridge from the start catches CORS and SSE issues early.
- **Pipeline before visualization:** The SSE event queue is a side-channel — the pipeline works with or without a subscriber. Building the pipeline first means visualization failures never block report generation.
- **Agentverse early (Phase 1):** Registration requires FET tokens, can have quota or setup delays, and must be resolved before demo day. Do it in Phase 1, not Phase 4.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (Modeling Agent):** Code execution sandboxing (RestrictedPython vs subprocess + resource limits) needs a concrete implementation decision. The research recommends a timeout + import whitelist wrapper, but the exact mechanism needs a spike.
- **Phase 2 (Orchestrator synthesis):** The LLM system prompt design for unified narrative synthesis across five domains is non-trivial. May benefit from a prompt engineering spike before committing to a prompt structure.
- **Phase 3 (React Flow performance):** Animated SVG edges at 5+ simultaneously active connections can cause CPU spikes. Needs a React Flow performance configuration spike (CSS `will-change`, animation limiting to active edges only) before the full graph is wired.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Infrastructure):** FastAPI + asyncio.Queue + SSE is a well-documented pattern. Bridge scaffold is straightforward.
- **Phase 3 (Report display):** react-markdown + remark-gfm + base64 chart embedding is a standard pattern with high-confidence documentation.
- **Phase 4 (Chat):** Orchestrator intent routing with LLM classification is a standard RAG-adjacent pattern; no novel integration required.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM-HIGH | uAgents core patterns: HIGH (official docs verified). Finnhub free tier limits: MEDIUM (rate limit page confirmed). React Flow 12.x capabilities: HIGH. GPT-4o mini pricing: MEDIUM. |
| Features | MEDIUM | Product domain well understood. fetch.ai-specific integration patterns have limited production examples outside official docs. |
| Architecture | MEDIUM | Three-tier pattern and SSE bridge verified via official uAgents docs and fetch.ai innovation lab examples. The specific asyncio.Queue bridge is a recommended adaptation, not a natively documented pattern. |
| Pitfalls | MEDIUM-HIGH | uAgents-specific pitfalls (hosted statelessness, PNA, REST endpoint restrictions) verified against official docs. General multi-agent and hackathon patterns: HIGH confidence from multiple independent sources. |

**Overall confidence:** MEDIUM

### Gaps to Address

- **Agentverse FET token requirement:** Registration requires FET tokens for gas. The exact amount and acquisition process for a hackathon was not confirmed. Address in Phase 1 before assuming registration is frictionless.
- **ctx.send_and_receive timeout behavior:** The exact timeout mechanism and default value for `ctx.send_and_receive` was not confirmed in docs. The orchestrator fan-out pattern depends on this behaving predictably. Verify with a test call in Phase 1.
- **Bureau + FastAPI process isolation:** The exact IPC mechanism between the Bureau process and FastAPI bridge (shared queue vs HTTP to agent REST endpoints) has trade-offs that depend on whether they run in the same Python process or as siblings. The safest hackathon approach (two separate processes via start.sh) is confirmed, but the queue-sharing approach requires threads and care. This is a Phase 1 implementation decision.
- **react-markdown base64 image rendering:** Base64-encoded PNG images in markdown (`![chart](data:image/png;base64,...)`) should render, but this was not verified against react-markdown 9.x + remark-gfm 4.x specifically. Verify in Phase 3 before the Modeling agent chart pipeline is complete.

## Sources

### Primary (HIGH confidence)
- [uAgents official docs](https://uagents.fetch.ai/docs) — Bureau pattern, agent types, REST endpoints, handlers
- [uAgents REST Endpoints Guide](https://uagents.fetch.ai/docs/guides/rest_endpoints) — agent-level REST decorator behavior
- [Agentverse Mailbox docs](https://uagents.fetch.ai/docs/agentverse/mailbox) — mailbox as message broker
- [React Flow official site](https://reactflow.dev) — custom nodes, animated edges, performance guide
- [FastAPI SSE patterns](https://fastapi.tiangolo.com/tutorial/server-sent-events/) — EventSourceResponse pattern

### Secondary (MEDIUM confidence)
- [Finnhub pricing/docs](https://finnhub.io/docs/api/rate-limit) — 60 req/min free tier confirmed
- [CoinGecko API pricing](https://www.coingecko.com/en/api/pricing) — 30 req/min demo plan confirmed
- [GPT-4o mini pricing](https://openai.com/api/pricing/) — $0.15/1M input tokens
- [Frontend Web App Integration Pattern](https://innovationlab.fetch.ai/resources/docs/next/examples/integrations/frontend-integration) — Flask bridge pattern (transferable to FastAPI)
- [Fetch.ai Architecture Paper](https://arxiv.org/abs/2510.18699) — system overview
- [Chrome PNA / uAgents communication overview](https://fetch.ai/blog/uagents-communication-overview) — localhost browser restriction documented
- [Zustand + TanStack Query 2025 pattern](https://dev.to/devforgedev/you-dont-need-redux-zustand-tanstack-query-replaced-90-of-my-state-management-2ggi) — community consensus

### Tertiary (LOW confidence)
- [yfinance reliability concerns](https://medium.com/@trading.dude/why-yfinance-keeps-getting-blocked-and-what-to-use-instead-92d84bb2cc01) — single source, matches known behavior
- [Alpha Vantage 25 req/day free tier](https://www.alphavantage.co/) — confirmed but relies on current pricing page accuracy

---
*Research completed: 2026-03-21*
*Ready for roadmap: yes*
