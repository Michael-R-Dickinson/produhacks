# Pitfalls Research

**Domain:** Multi-agent investment intelligence platform (fetch.ai uAgents + financial APIs + React visualization)
**Researched:** 2026-03-21
**Confidence:** MEDIUM — uAgents-specific claims verified against official docs; general multi-agent and hackathon patterns HIGH confidence from multiple sources

---

## Critical Pitfalls

### Pitfall 1: Hosted Agent Statelessness Surprise

**What goes wrong:**
You deploy agents to Agentverse as hosted agents for convenience, then discover that global Python variables reset on every handler invocation. Any state you stored in module-level variables — pending requests, in-progress report data, conversation context — vanishes between calls. The orchestrator "loses" its synthesis context mid-report.

**Why it happens:**
Hosted agents on Agentverse run in a serverless-style model. Developers assume a running Python process with persistent memory, but each handler invocation is effectively stateless. Local agents don't have this problem, which creates confusion when switching deployment modes.

**How to avoid:**
Use `ctx.storage` (the uAgents key-value store) for any state that must persist between handler calls. Design agents to be explicitly stateless — pass all needed context in the message payload itself rather than relying on in-memory state. For the orchestrator, include a `correlation_id` in every message so responses can be matched back to the originating report request without relying on module state.

**Warning signs:**
- Orchestrator receives a sub-agent response but has no record of the corresponding request
- Agent behavior changes between first and second invocations of the same workflow
- "Works on my machine" (local agent) but breaks on Agentverse (hosted)

**Phase to address:** Agent infrastructure setup / Phase 1 (agent scaffolding)

---

### Pitfall 2: No Bridge Between uAgents and the React Frontend

**What goes wrong:**
uAgents use a binary protocol (Almanac + agent-to-agent messaging) that is not natively accessible from a browser or a JavaScript/TypeScript environment. You cannot call an agent's address directly from React like a REST endpoint. Teams discover this late and scramble to build a bridge with hours left.

**Why it happens:**
The uAgents docs focus on Python-to-Python agent communication. The "connect a web app" use case requires a separate backend service (FastAPI or Flask) that speaks HTTP to the frontend and uAgents protocol to the agent network. This intermediary is not obvious from the getting-started examples.

**How to avoid:**
Build a thin FastAPI bridge service as part of the core infrastructure — not an afterthought. The bridge exposes REST/WebSocket endpoints to the frontend and communicates with agents either via `ctx.send()` from a local "gateway" agent co-located with the bridge, or via HTTP REST endpoints exposed by agents using uAgents' built-in REST support. Design this bridge in Phase 1, not Phase 3.

**Warning signs:**
- Frontend code attempting to import or directly call uAgents Python classes
- No backend service in the project architecture diagram
- Confusion about how "the UI triggers a report"

**Phase to address:** Phase 1 (project architecture and bridge scaffolding)

---

### Pitfall 3: Financial API Rate Limits Killing the Demo

**What goes wrong:**
During the demo run (or the test run one hour before), every financial API call fails with 429 or returns stale cached data because the free tier was exhausted. Alpha Vantage's free tier is 25 requests/day. Polygon's free tier is 5 calls/minute. A single report generation that hits 5 agents each making 3 API calls can burn through a day's quota in one test.

**Why it happens:**
Developers sign up for free API keys during coding, run repeated tests throughout the 24 hours, and exhaust limits before the final demo. The limit is per-day or per-minute, not per-session, so it resets unpredictably.

**How to avoid:**
- Use Finnhub free tier (60 calls/minute, real-time US markets) rather than Alpha Vantage for stock data — it's far more generous
- Cache all API responses aggressively: store the raw response with a timestamp in agent storage, return cached data if less than N minutes old
- Build a mock data mode for all agents from day one — a toggle that returns realistic fixture data without hitting external APIs. Use this for all development and testing, switch to live only for demo
- Spread API calls across agents: each agent only calls its specialized API, never duplicates calls the orchestrator or another agent already made

**Warning signs:**
- No caching layer in any agent's data-fetch code
- Multiple agents calling the same financial data endpoint
- Quota exhausted before noon on hackathon day

**Phase to address:** Phase 1 (API client scaffolding) — mock mode is not optional

---

### Pitfall 4: Orchestrator Becomes a Context Window Bottleneck

**What goes wrong:**
The orchestrator collects full raw responses from all five sub-agents (portfolio analysis, news sentiment, modeling output, crypto/commodities, plus chart data) and feeds everything into a single LLM prompt for synthesis. The combined token count exceeds the model's context window, causing truncation or outright failures, and the synthesis output becomes slow (30+ seconds).

**Why it happens:**
Each agent returns its complete analysis as a large blob of text. Nobody defines a maximum response size contract. The orchestrator prompt grows linearly with the number of agents and the verbosity of each response.

**How to avoid:**
Define a strict `AgentResponse` Pydantic model with a `summary: str` field (max 500 tokens) and an optional `detail: str` field. The orchestrator uses `summary` fields for synthesis; the full detail is only included if the orchestrator explicitly requests a follow-up. Set explicit `max_tokens` limits on every sub-agent LLM call. The orchestrator prompt should template in summaries, not raw responses.

**Warning signs:**
- Agent response Pydantic models have `str` fields with no length constraints
- LLM calls in sub-agents have no `max_tokens` parameter
- Report generation regularly takes more than 20 seconds

**Phase to address:** Phase 2 (agent communication protocol design)

---

### Pitfall 5: Live Agent Graph Visualization Blocks Report Generation

**What goes wrong:**
The "streaming agent thoughts" and animated graph are built as a first-class feature alongside the core report pipeline, rather than as a thin observability layer on top. The agent thoughts streaming requires a separate real-time channel (WebSocket) that adds significant complexity. Half the hackathon time gets absorbed by the visualization before any agent produces real data.

**Why it happens:**
The visualization is the most visually impressive feature and the most demo-able. It attracts disproportionate development effort. The mistake is building it coupled to the core pipeline rather than as an optional broadcast layer.

**How to avoid:**
Build the full report generation pipeline first with simple logging. Then add the streaming layer as a "broadcast" side-channel: every agent emits structured events (thought/message) to a shared event queue (asyncio queue or Redis pub/sub), and the FastAPI bridge relays these to the frontend via a single WebSocket connection. The pipeline doesn't depend on the WebSocket — if the frontend is disconnected, events are simply dropped. This decoupling means a broken WebSocket never breaks report generation.

**Warning signs:**
- Agent handler code directly contains WebSocket send calls
- Report generation unit tests require a live WebSocket connection
- Visualization work started before the first end-to-end report is generated

**Phase to address:** Phase 3 (visualization) — explicitly after Phase 2 (core pipeline)

---

### Pitfall 6: uAgents Chrome Local Network Access Prompt Breaks Demo

**What goes wrong:**
When running local agents during the hackathon demo, Chrome 142+ (and Brave) shows a "Local Network Access" permission prompt. If the judge or demo machine has not granted this permission, the browser silently fails to reach locally running agents, producing a broken demo with no clear error.

**Why it happens:**
Chromium introduced Private Network Access (PNA) protections that require explicit user permission before a webpage can make requests to localhost or local network addresses. This is a recent browser-level change that many developers haven't encountered.

**How to avoid:**
Deploy agents to Agentverse as hosted agents (or use a Mailbox agent) so all communication goes through Agentverse's public infrastructure, eliminating localhost requests from the browser context. Alternatively, route all frontend requests through the FastAPI bridge (which runs on a public port), so the browser never directly contacts agent ports. Never rely on the browser directly reaching `localhost:8001` etc.

**Warning signs:**
- Frontend JavaScript making direct fetch/axios calls to `localhost:8xxx`
- No reverse proxy or bridge service in front of agents
- Demo machine is Chrome 142+ or Brave without PNA permissions pre-granted

**Phase to address:** Phase 1 (architecture) and Phase 4 (deployment/demo prep)

---

### Pitfall 7: Modeling Agent Code Execution Without Sandboxing

**What goes wrong:**
The modeling agent executes LLM-generated Python code for regressions, backtesting, and chart generation directly in the agent's Python process. A poorly generated code snippet imports a disallowed library, runs an infinite loop, or attempts file system writes outside the intended scope, crashing the agent process entirely and taking down the swarm.

**Why it happens:**
Using `exec()` or `subprocess` to run generated code is the path of least resistance. The risk isn't immediately obvious in a demo context. The agent crashes at demo time when an edge-case stock ticker triggers unusual model behavior.

**How to avoid:**
Use `RestrictedPython` or run generated code in a subprocess with a timeout and resource limits (`resource.setrlimit`). For a hackathon, the pragmatic minimum is: wrap all `exec()` calls in a `try/except` with a hard 10-second timeout, whitelist allowed imports (numpy, pandas, scipy, matplotlib only), and never allow file writes outside a `/tmp/charts/` directory. E2B is the production answer but is overkill for 24 hours.

**Warning signs:**
- Modeling agent executes strings directly with `exec(code)` with no timeout
- No import whitelist in the code execution path
- Chart generation writes to arbitrary file paths

**Phase to address:** Phase 2 (modeling agent implementation)

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut                                                     | Immediate Benefit                     | Long-term Cost                                                | When Acceptable                                                |
| ------------------------------------------------------------ | ------------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------------- |
| No caching on financial API calls                            | Simpler agent code                    | Rate limit exhaustion, demo failures                          | Never — mock mode is the alternative                           |
| Storing orchestration state in Python globals                | Avoids ctx.storage API learning curve | Silent data loss on Agentverse, hard-to-debug race conditions | Never for hosted agents                                        |
| Inline WebSocket sends inside agent handlers                 | Feels unified                         | Couples pipeline to transport, blocks on slow clients         | Never                                                          |
| Single monolithic orchestrator prompt with all agent outputs | Simple to implement                   | Context window overflow, slow synthesis, brittle output       | Only if all sub-agent summaries are strictly capped            |
| Hardcoded agent addresses in frontend                        | Avoids service discovery              | Breaks when agents are redeployed to new addresses            | Acceptable for 24h hackathon if addresses are in a config file |
| No mock data mode                                            | Saves ~1 hour initial setup           | Tests burn live API quota, demo can fail                      | Never — mock mode is the insurance policy                      |

---

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration                       | Common Mistake                                                  | Correct Approach                                                                 |
| --------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Agentverse hosted agents          | Using module-level global variables for state                   | Use `ctx.storage.get/set` for all persistent state                               |
| uAgents protocol from React       | Calling agent addresses directly from browser JS                | Route all frontend requests through a FastAPI bridge service                     |
| Alpha Vantage / Polygon free tier | Calling API on every request during development                 | Implement response caching from day one; use mock mode for development           |
| Finnhub news/market API           | Not setting `Content-Type: application/json` in request headers | Follow their SDK examples; always specify headers explicitly                     |
| uAgents message protocol          | Defining message models without `replies=` on handlers          | Always declare expected reply types in `@on_message(replies={...})`              |
| Cross-origin requests (CORS)      | Agents and bridge on different ports without CORS headers       | Configure `CORSMiddleware` on the FastAPI bridge explicitly                      |
| Agentverse mailbox agents         | Assuming real-time delivery                                     | Mailbox adds latency; use direct peer communication for synchronous report flows |
| WebSocket from React              | Not handling reconnection on dropped connection                 | Implement exponential backoff reconnect in the frontend WebSocket client         |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap                                                              | Symptoms                              | Prevention                                                                        | When It Breaks                            |
| ----------------------------------------------------------------- | ------------------------------------- | --------------------------------------------------------------------------------- | ----------------------------------------- |
| Orchestrator awaiting sub-agents sequentially                     | Report takes 5x longer than necessary | Use `asyncio.gather()` to fan out to all sub-agents in parallel                   | Immediately — even at 1 user              |
| React re-rendering entire agent graph on every thought event      | UI freezes during active streaming    | Memoize node components; use `useCallback` for handlers; debounce thought updates | At ~10 thought events/second              |
| Streaming thoughts as full text replacement vs. append            | Jumpy UI, excessive DOM updates       | Use append-only thought log per agent; only render last N lines                   | At ~5 agents all streaming simultaneously |
| CSS animated SVG edges in React Flow                              | CPU spike, dropped frames             | Limit animation to active connections only; use CSS `will-change: transform`      | At 5+ simultaneously animated edges       |
| Passing entire report markdown to parent component on every token | Laggy report rendering                | Buffer tokens, update markdown display on a 100ms interval not per-token          | At reports longer than 500 tokens         |

---

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake                                                                                           | Risk                                       | Prevention                                                                     |
| ------------------------------------------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------ |
| Storing financial API keys directly in uAgent source code committed to repo                       | Key exposure in public hackathon repo      | Use `.env` + `python-dotenv`; add `.env` to `.gitignore` before first commit   |
| Running LLM-generated code with `exec()` without sandboxing                                       | Agent process crash or arbitrary execution | Wrap in restricted exec with timeout and import whitelist                      |
| Accepting arbitrary ticker symbols and passing them directly to financial APIs without validation | API injection / unexpected data shapes     | Validate tickers against a basic regex `[A-Z]{1,5}` before use                 |
| Logging full LLM prompts including user portfolio data                                            | Portfolio holdings visible in server logs  | Sanitize logs; never log raw CSV content or portfolio positions                |
| Embedding API keys in frontend React code (even temporarily)                                      | Keys visible in browser devtools           | All API keys live server-side only; frontend communicates only with the bridge |

---

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall                                                               | User Impact                                                 | Better Approach                                                                                 |
| --------------------------------------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| No loading state for report generation (30+ second operation)         | User thinks the app is broken, refreshes and loses progress | Show animated agent graph as the loading state — it IS the progress indicator                   |
| Displaying raw per-agent output sections instead of unified narrative | Looks like a data dump, not an intelligence product         | Enforce narrative synthesis in orchestrator; never display raw agent JSON                       |
| Agent "thoughts" streaming too fast to read                           | Overwhelming, feels noisy                                   | Rate-limit thought display to 2-3 thoughts/second per agent; queue and throttle                 |
| Report appears as a wall of markdown text                             | Poor readability, poor demo impact                          | Style markdown with clear section headers, callout boxes for key insights, chart embeds inline  |
| No error state when report generation fails midway                    | Silent failure — user stares at loading agent graph         | Show per-agent error states in graph nodes; surface failure reason in UI                        |
| Chat interface not clearly showing which "agent" responded            | Confusion about the system's multi-agent nature             | Label each chat response with the orchestrator's routing decision ("Portfolio Agent analysis:") |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Agent graph visualization:** Often has mock/static nodes — verify it responds to actual live agent message events from a real report run
- [ ] **Report generation:** Often works with a single agent but fails silently when one sub-agent times out — verify timeout handling and partial-result synthesis
- [ ] **Chat interface:** Often just calls the orchestrator without routing — verify the orchestrator actually dispatches to the correct sub-agent based on query type
- [ ] **CSV portfolio upload:** Often parses the happy-path CSV but breaks on real exports from Robinhood/Fidelity with non-standard column names — test with a real export
- [ ] **Modeling agent charts:** Often generates matplotlib output as a file but never embeds it in the markdown report — verify the full path from generation to display
- [ ] **API caching:** Often added to one agent but missing from others — verify every external API call has a cache layer
- [ ] **Mock mode:** Often written but not wired to a toggle — verify it can be activated without code changes (env var or config flag)
- [ ] **WebSocket reconnection:** Often works on first connect but not after a brief network interruption — test by disabling and re-enabling wifi

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall                                      | Recovery Cost | Recovery Steps                                                                               |
| -------------------------------------------- | ------------- | -------------------------------------------------------------------------------------------- |
| Hosted agent statelessness discovered late   | MEDIUM        | Switch to local agents + mailbox for the demo; costs 2-3 hours to rewire but is recoverable  |
| Financial API rate limit exhausted           | LOW           | Switch to mock mode immediately; mock data is the fallback, not the failure                  |
| WebSocket bridge not working at demo time    | HIGH          | Fall back to polling (HTTP GET every 3 seconds) — ugly but functional for a demo             |
| Context window overflow in orchestrator      | MEDIUM        | Truncate each sub-agent response to 300 tokens before synthesis; rebuild prompt              |
| Modeling agent crashes on bad code execution | LOW           | Restart agent process; add a hard try/except wrapper around all exec calls                   |
| Chrome PNA blocks local agents at demo       | MEDIUM        | Launch Chrome with `--disable-web-security` flag for demo only, or switch to deployed agents |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall                             | Prevention Phase                             | Verification                                                                      |
| ----------------------------------- | -------------------------------------------- | --------------------------------------------------------------------------------- |
| Hosted agent statelessness          | Phase 1: Agent scaffolding                   | State survives a handler restart when using `ctx.storage`                         |
| No web-to-agent bridge              | Phase 1: Architecture and bridge             | FastAPI bridge can trigger a dummy agent and receive a response                   |
| Financial API rate limits           | Phase 1: API client scaffolding              | Mock mode toggle exists; caching layer in place; tested without hitting live APIs |
| Orchestrator context overflow       | Phase 2: Agent communication contracts       | Each sub-agent response model has an enforced `summary` field                     |
| Visualization built before pipeline | Phase 3: Visualization (after pipeline)      | First end-to-end report is complete before any visualization work begins          |
| Chrome PNA localhost blocking       | Phase 1 (architecture) + Phase 4 (demo prep) | Demo machine test run confirms no localhost browser requests                      |
| Code execution without sandboxing   | Phase 2: Modeling agent                      | All `exec()` calls have timeout + import whitelist + error handling               |

---

## Sources

- [Agentverse Documentation — Hosted vs Local vs Mailbox vs Proxy agents](https://uagents.fetch.ai/docs/guides/types)
- [uAgent Creation and Hosted Agent Limitations](https://innovationlab.fetch.ai/resources/docs/agent-creation/uagent-creation)
- [uAgents Protocols and Message Handler Gotchas](https://uagents.fetch.ai/docs/guides/protocols)
- [Agent Mailbox Documentation](https://uagents.fetch.ai/docs/agentverse/mailbox)
- [Frontend Web App Integration Pattern (Fetch.ai Innovation Lab)](https://innovationlab.fetch.ai/resources/docs/next/examples/integrations/frontend-integration)
- [Agentverse Deployment via Render — dependency and env var gotchas](https://innovationlab.fetch.ai/resources/docs/agentverse/deploy-agent-on-agentverse-via-render)
- [Chrome Local Network Access (PNA) prompt — uAgents communication overview](https://fetch.ai/blog/uagents-communication-overview)
- [React Flow Performance Guide](https://reactflow.dev/learn/advanced-use/performance)
- [React Flow Edge Animation Performance](https://liambx.com/blog/tuning-edge-animations-reactflow-optimal-performance)
- [Financial Data APIs Compared 2026 — Polygon vs Alpha Vantage rate limits](https://www.ksred.com/the-complete-guide-to-financial-data-apis-building-your-own-stock-market-data-pipeline-in-2025/)
- [Multi-agent orchestration bottleneck patterns](https://gurusup.com/blog/agent-orchestration-patterns)
- [LLM Hallucinations in Financial Contexts](https://biztechmagazine.com/article/2025/08/llm-hallucinations-what-are-implications-financial-institutions)
- [Lessons from Building AI Agents for Financial Services](https://www.nicolasbustamante.com/p/lessons-from-building-ai-agents-for)
- [Secure Code Execution for AI Agents](https://saurabh-shukla.medium.com/secure-code-execution-in-ai-agents-d2ad84cbec97)
- [WebSocket reverse proxy timeout / heartbeat gotcha](https://cesium-ml.org/blog/2016/07/13/a-pattern-for-websockets-in-python/)

---
*Pitfalls research for: Wealth Council — multi-agent investment intelligence platform*
*Researched: 2026-03-21*
