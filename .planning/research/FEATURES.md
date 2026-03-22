# Feature Research

**Domain:** Investment intelligence platform with multi-agent swarm and live agent observability
**Researched:** 2026-03-21
**Confidence:** MEDIUM (ecosystem well-understood; fetch.ai-specific integration patterns are MEDIUM due to limited production examples)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features that users assume exist. Missing these = product feels incomplete or broken in a hackathon demo.

| Feature                                          | Why Expected                                                                                        | Complexity | Notes                                                                                                |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------- |
| Portfolio CSV upload + parsing                   | Every portfolio tool accepts CSV; users expect ticker/quantity/cost at minimum                      | LOW        | Standard format: Symbol, Quantity, Cost. Validate before parsing.                                    |
| Sector/asset allocation breakdown                | Instant expectation from anyone who has used Morningstar, Personal Capital, or Portfolio Visualizer | MEDIUM     | Needs market data lookup to fill sector for each ticker. Can use yfinance or Finnhub /stock/profile2 |
| Investment report generation (on-demand)         | Core product value -- button triggers the full swarm run                                            | HIGH       | Orchestrator must coordinate all agents and produce a unified markdown narrative                     |
| Formatted report display with markdown rendering | Users expect readable, structured output, not raw JSON                                              | LOW        | react-markdown or similar; tables, headers, bold/italic                                              |
| Chart embedding in report                        | Modeling agent output; bar charts, line graphs, scatter plots embedded as images or interactive     | MEDIUM     | Matplotlib/Plotly on Python side; base64 encode or serve as static file                              |
| Financial news integration                       | Any investment tool in 2026 fetches relevant news; absence feels broken                             | MEDIUM     | Finnhub free tier: 60 req/min, news + sentiment endpoints included                                   |
| Sentiment scoring on news                        | NLP-based positive/negative/neutral labeling is expected in modern tools                            | MEDIUM     | Finnhub provides pre-scored sentiment; fallback to LLM-scored on fetch                               |
| Loading/progress state during report generation  | Multi-agent run takes time; dead UI = confused user                                                 | LOW        | Spinner, progress bar, or ideally live agent graph activity                                          |
| Error handling with user feedback                | Agent failures, API timeouts, bad CSV format                                                        | LOW        | Critical for hackathon demo reliability                                                              |

### Differentiators (Competitive Advantage)

Features that no standard investment tool has. These win the hackathon category and validate the fetch.ai track requirement.

| Feature                                                 | Value Proposition                                                                                 | Complexity | Notes                                                                                              |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------- |
| Live agent graph visualization (nodes + edges animated) | No investment tool shows the AI reasoning process in real-time; uniquely compelling for judges    | HIGH       | React Flow nodes as custom agent cards; edges pulse on message send; SSE or WebSocket from backend |
| Agent "thoughts" stream per node                        | Each agent card streams its current reasoning step live; demonstrates swarm coordination visually | HIGH       | Requires backend to emit per-agent events; frontend subscribes per-agent or via multiplexed stream |
| Animated inter-agent message connections                | Visual proof of swarm collaboration -- edges light up when Agent A sends to Agent B               | MEDIUM     | React Flow edge animation on message event; store active edges in state, timeout to return to idle |
| Message hover tooltip (title + description)             | Reveals what the agents are actually sending each other; judges can follow the reasoning          | LOW        | React Flow edge `label` or custom tooltip on edge hover                                            |
| Unified narrative synthesis (not sectioned per agent)   | Demonstrates real orchestrator intelligence; competitors produce section-per-domain dumps         | HIGH       | Orchestrator LLM prompt must weave portfolio context + news + quant models into one coherent text  |
| Chat interface routed through orchestrator              | Ask "should I add NVDA?" and the orchestrator dispatches to portfolio + news + modeling agents    | HIGH       | Requires orchestrator to parse intent and route to correct sub-agents, then re-synthesize          |
| Backtesting results embedded in report                  | Quantitative validation of recommendations with actual historical performance data                | HIGH       | Modeling agent runs in code execution sandbox; generates matplotlib chart, returns as base64       |
| Crypto + commodities domain agent                       | Most portfolio tools cover equities only; BTC/ETH/gold coverage differentiates                    | MEDIUM     | CoinGecko (free, no auth) for crypto; Alpha Vantage for commodities                                |
| "Impact of adding X" portfolio analysis                 | User asks what happens to diversification if they add a stock; portfolio agent responds           | MEDIUM     | Delta calculation: current correlation matrix vs hypothetical; Sharpe ratio comparison             |
| fetch.ai agentverse deployment                          | Agents run on Agentverse not just locally; satisfies the track requirement and is demo-compelling | HIGH       | Critical for the fetch.ai track; uAgents protocol for all inter-agent communication                |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem valuable but are out of scope, risky, or actively harmful to the hackathon build.

| Feature                                             | Why Requested                                     | Why Problematic                                                                                | Alternative                                                                             |
| --------------------------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Brokerage API sync (Plaid, Fidelity, Schwab)        | "Real" portfolio data; no CSV friction            | OAuth flows, API approval, credential security -- days of setup, not hours                     | CSV upload is the correct scope for 24h; note it as "v2 roadmap" in demo                |
| Real-time streaming market prices (WebSocket)       | Live portfolio P&L; "real" feel                   | Constant API cost, requires persistent connections, adds infra complexity with zero demo value | Fetch prices once per report generation; snapshot is fine for analysis                  |
| Scheduled/cron report generation                    | "Get my report every morning"                     | Requires job scheduler, persistent storage, email delivery; out of hackathon scope             | On-demand trigger button achieves the same demo value                                   |
| Direct agent @mention in chat                       | Power-user feature; "ask the news agent directly" | Breaks the swarm narrative; agents become siloed tools                                         | All chat through orchestrator; the graph visualization shows the routing happening live |
| Per-agent streaming chat UX (multiple chat threads) | Granular control                                  | UI complexity explosion; defeats unified narrative value prop                                  | Single chat thread routed by orchestrator                                               |
| User authentication / multi-user                    | "Real app" table stakes                           | Session management, DB schema, JWT -- burns a quarter of the hackathon clock                   | Single-user demo; hardcode or use localStorage for portfolio state                      |
| Mobile responsive design                            | Wide audience reach                               | Adds CSS complexity with no judge value in a 24h hackathon; demo is on a laptop                | Desktop-first; min-width constraint acceptable                                          |
| Persistent report history / database                | Historical comparison                             | Requires persistence layer (PostgreSQL, SQLite) beyond the agent swarm; adds infra             | In-memory for session; if needed, write to a local JSON file                            |
| Trade execution / order routing                     | "Full circle" investment tool                     | Regulatory risk, brokerage API complexity, out of scope for any hackathon                      | Analysis and recommendations only; no execution                                         |
| Social/sharing features                             | "Share your analysis"                             | Auth required, public API exposure, moderation concerns                                        | Screenshot / export to PDF as post-hackathon consideration                              |

---

## Feature Dependencies

```
[CSV Upload + Parsing]
    └──enables──> [Portfolio Agent Analysis]
                      └──feeds──> [Orchestrator Synthesis]
                                      └──produces──> [Report Display]

[Financial News API]
    └──enables──> [News Agent + Sentiment]
                      └──feeds──> [Orchestrator Synthesis]

[Modeling Agent + Code Execution]
    └──produces──> [Charts]
                      └──embeds in──> [Report Display]

[Crypto/Commodities Agent]
    └──feeds──> [Orchestrator Synthesis]

[fetch.ai uAgents Protocol]
    └──required by──> [All agent-to-agent communication]
    └──required by──> [Web app <-> swarm connection]

[Agent Event Stream (SSE/WebSocket)]
    └──required by──> [Live Agent Graph Visualization]
    └──required by──> [Agent Thoughts Streaming]

[Live Agent Graph Visualization]
    └──enhances──> [Report Generation UX]
    └──requires──> [Agent Event Stream]

[React Flow (or equivalent)]
    └──required by──> [Agent Graph Nodes + Edges]
    └──enables──> [Animated Message Connections]
    └──enables──> [Message Hover Tooltips]

[Chat Interface]
    └──requires──> [Orchestrator Agent]
    └──enhances──> [Live Agent Graph] (chat triggers visible routing in graph)
```

### Dependency Notes

- **CSV Upload requires market data lookup:** The CSV gives tickers and quantities but sector metadata (for diversification breakdown) must be fetched from an API (Finnhub /stock/profile2 or yfinance). This must happen before the portfolio agent can produce meaningful analysis.
- **Orchestrator synthesis requires all domain agents:** The unified narrative cannot be written until portfolio, news, modeling, and crypto/commodities agents have all returned results. Parallel agent execution is necessary for acceptable latency.
- **Agent graph visualization requires event stream:** There is no meaningful visualization without a real-time event feed from the backend. This is the hardest integration point -- the web app must receive per-agent events from the agentverse swarm.
- **Modeling agent charts require code execution sandbox:** Backtesting and regression are not prebuilt -- the agent needs an environment (e.g., a subprocess with pandas/numpy/matplotlib) to execute code and return results. This is a non-trivial setup.
- **Chat routing requires orchestrator intent parsing:** The orchestrator must interpret user intent ("add NVDA" → portfolio agent, "what's the news on AAPL?" → news agent) before dispatching. This requires a well-designed system prompt.

---

## MVP Definition

### Launch With (v1 -- the hackathon demo)

Minimum set to demonstrate the value proposition and satisfy the fetch.ai track.

- [ ] **CSV upload** -- without portfolio data, nothing else works
- [ ] **Report generation trigger** -- the core action that drives the swarm
- [ ] **Live agent graph with animated edges** -- this IS the differentiator; without it, this is just a report generator
- [ ] **Agent thoughts streaming per node** -- judges need to see the swarm thinking
- [ ] **Unified narrative report with markdown rendering** -- the output must be readable and synthesized
- [ ] **Financial news + sentiment** -- news agent is the easiest domain agent to make look impressive
- [ ] **Portfolio agent: sector allocation + diversification** -- most tangible output for the portfolio CSV input
- [ ] **fetch.ai agentverse deployment** -- required for the track; do this early or the whole stack may not integrate
- [ ] **Basic chart from modeling agent** -- at least one chart embedded in the report (even a simple allocation pie)

### Add After Validation (v1.x -- if time allows in the 24h window)

- [ ] **Chat interface** -- adds interactivity for judges to probe the system; add only if core graph + report is stable
- [ ] **Message hover tooltips on edges** -- low effort, high polish; add in the last 2 hours
- [ ] **"Impact of adding X" stock analysis** -- impressive portfolio feature if chat is working
- [ ] **Crypto/commodities agent** -- adds breadth to the report; add only if other agents are stable

### Future Consideration (v2+ -- post-hackathon)

- [ ] **Brokerage API sync** -- eliminates CSV friction for real users
- [ ] **Scheduled report generation** -- daily digest delivery
- [ ] **Report history and comparison** -- track analysis over time
- [ ] **Multi-user with authentication** -- productionize the single-user demo
- [ ] **More sophisticated backtesting** -- walk-forward, multi-strategy comparison

---

## Feature Prioritization Matrix

| Feature                                   | User Value               | Implementation Cost | Priority |
| ----------------------------------------- | ------------------------ | ------------------- | -------- |
| CSV upload + portfolio parsing            | HIGH                     | LOW                 | P1       |
| Report generation (orchestrator)          | HIGH                     | HIGH                | P1       |
| Live agent graph (nodes + animated edges) | HIGH                     | HIGH                | P1       |
| Agent thoughts streaming                  | HIGH                     | HIGH                | P1       |
| Unified narrative report + markdown       | HIGH                     | MEDIUM              | P1       |
| fetch.ai agentverse deployment            | HIGH (track requirement) | HIGH                | P1       |
| Financial news + sentiment                | HIGH                     | MEDIUM              | P1       |
| Portfolio sector/diversification analysis | HIGH                     | MEDIUM              | P1       |
| Basic chart in report                     | MEDIUM                   | MEDIUM              | P1       |
| Chat interface (orchestrator-routed)      | MEDIUM                   | HIGH                | P2       |
| Message hover tooltips                    | LOW                      | LOW                 | P2       |
| Crypto/commodities agent                  | MEDIUM                   | MEDIUM              | P2       |
| "Impact of adding X" analysis             | MEDIUM                   | MEDIUM              | P2       |
| Backtesting (multi-period)                | MEDIUM                   | HIGH                | P3       |
| Report export / PDF                       | LOW                      | LOW                 | P3       |

**Priority key:**
- P1: Must have for hackathon demo
- P2: Add if P1 complete before time runs out
- P3: Nice to have, skip in 24h context

---

## Competitor Feature Analysis

| Feature                     | Bloomberg Terminal      | Portfolio Visualizer | Koyfin            | Wealth Council (Our Approach) |
| --------------------------- | ----------------------- | -------------------- | ----------------- | ----------------------------- |
| Portfolio import            | Manual entry / API      | CSV + broker sync    | CSV + broker sync | CSV upload (hackathon scope)  |
| News + sentiment            | YES (proprietary feed)  | NO                   | YES (basic)       | YES (Finnhub free tier)       |
| Charting / backtesting      | YES (institutional)     | YES (deep)           | YES (moderate)    | YES (modeling agent, limited) |
| Unified narrative AI report | NO (data only)          | NO                   | NO                | YES -- core differentiator    |
| Multi-agent architecture    | NO                      | NO                   | NO                | YES -- fetch.ai agentverse    |
| Live agent visualization    | NO                      | NO                   | NO                | YES -- primary UX innovation  |
| Chat with data              | LIMITED (Bloomberg GPT) | NO                   | YES (basic)       | YES (orchestrator-routed)     |
| Crypto / commodities        | YES                     | YES                  | YES               | YES (dedicated agent)         |
| Free / hackathon accessible | NO ($24k/year)          | YES (limited free)   | YES (free tier)   | YES                           |

---

## Sources

- [Alpha Sense: Top Stock and Investment Research Tools 2026](https://www.alpha-sense.com/blog/trends/stock-investment-research-tools/)
- [Paradox Intelligence: What Is a Market Intelligence Platform for Investors 2026](https://www.paradoxintelligence.com/blog/what-is-market-intelligence-platform-investors-2026)
- [Braintrust: 5 Best AI Agent Observability Tools 2026](https://www.braintrust.dev/articles/best-ai-agent-observability-tools-2026)
- [Maxim AI: Top 5 AI Agent Observability Platforms 2026](https://www.getmaxim.ai/articles/top-5-ai-agent-observability-platforms-in-2026/)
- [fetch.ai: uAgents Communication Overview](https://fetch.ai/blog/uagents-communication-overview)
- [fetch.ai: Agentverse Docs](https://docs.agentverse.ai/docs)
- [React Flow: Node-Based UIs in React](https://reactflow.dev)
- [Reagraph: WebGL Graph Visualization for React](https://reagraph.dev/)
- [Finnhub: Free Realtime APIs](https://finnhub.io/finnhub-stock-api-vs-alternatives)
- [Diversiview: Top 5 Portfolio Optimisation Software 2025](https://diversiview.online/blog/top-5-portfolio-optimisation-tools-compared-2025-edition/)
- [Portfolio Visualizer Feature Overview](https://www.findmymoat.com/tools/portfolio-visualizer)
- [Koyfin: Best Model Portfolio Tools 2026](https://www.koyfin.com/blog/best-portfolio-management-software/)
- [Financial Data APIs Compared: Polygon vs IEX vs Alpha Vantage 2026](https://www.ksred.com/the-complete-guide-to-financial-data-apis-building-your-own-stock-market-data-pipeline-in-2025/)
- [OpenBB: Highlights from FinTech AI Hackathon](https://openbb.co/blog/highlights-from-the-openbb-sponsored-fintech-ai-hackathon)
- [Arxiv: Fetch.ai Architecture for Modern Multi-Agent Systems](https://arxiv.org/abs/2510.18699)

---

*Feature research for: Investment intelligence platform with fetch.ai multi-agent swarm*
*Researched: 2026-03-21*
