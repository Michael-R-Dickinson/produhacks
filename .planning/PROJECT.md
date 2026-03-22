# InvestiSwarm

## What This Is

An investment intelligence platform powered by a fetch.ai agent swarm. Five specialized agents collaborate on the agentverse to produce a unified daily narrative report synthesizing portfolio analysis, financial news, quantitative models, and crypto/commodities insights. Users interact through a Vite+React web app featuring the report, a chat interface, and a live agent graph visualization showing real-time agent collaboration.

## Core Value

A single cohesive investment report that synthesizes multiple specialized analysis domains into one actionable narrative -- replacing the need to check multiple sources manually.

## Requirements

### Validated

- [x] Multi-agent swarm on fetch.ai agentverse using uAgents library -- Validated in Phase 1: Foundation (5 agents running in Bureau, communicating via bridge)
- [x] On-demand report generation trigger mechanism -- Validated in Phase 1: Foundation (POST /trigger endpoint working)
- [x] Orchestrator agent that synthesizes information from domain agents into a unified narrative report -- Validated in Phase 2: Agent Pipeline (Gemini 2.5 Flash synthesis, fan-out to all 4 agents)
- [x] Portfolio agent that analyzes holdings (diversification, sector exposure, beta, correlation matrix) -- Validated in Phase 2: Agent Pipeline
- [x] News agent that fetches and analyzes financial news via APIs (Finnhub headlines, FinBERT sentiment scoring) -- Validated in Phase 2: Agent Pipeline
- [x] Crypto/commodities agent covering blockchain assets and physical commodities -- Validated in Phase 2: Agent Pipeline (CoinGecko crypto, Finnhub gold/oil)
- [x] On-demand report generation (user triggers, not scheduled) -- Validated in Phase 2: Agent Pipeline (POST /report triggers full pipeline)
- [x] Report displayed as formatted markdown with embedded charts from modeling agent -- Validated in Phase 2: Agent Pipeline (base64 PNG charts in ModelResponse)

### Active

- [ ] Modeling agent with code execution environment for regression, backtesting, and chart generation
- [ ] Chat interface routed through orchestrator, which dispatches to appropriate agents
- [ ] Live agent graph visualization: each node is an agent card showing real-time "thoughts" stream
- [ ] Animated message connections between agent nodes showing inter-agent communication
- [ ] Hover on connections shows brief title and description of the message
- [ ] Vite + React web frontend

### Out of Scope

- Brokerage API auto-sync -- CSV upload only for hackathon scope
- Scheduled/cron report generation -- on-demand only
- Direct agent chat (@mentioning specific agents) -- all chat goes through orchestrator
- Mobile app -- web only
- User authentication -- single-user demo for hackathon
- Real-time market data streaming -- agents fetch on report generation

## Context

- **Hackathon:** fetch.ai track at ProduHacks, 24-hour timeline
- **fetch.ai:** Agents will be deployed to agentverse using the uAgents Python library. Team is new to fetch.ai/agentverse -- research phase is critical for understanding the protocol, agent communication patterns, and deployment to agentverse
- **Agent communication:** Agents communicate via the uAgents protocol on agentverse. The web app needs to connect to the agent swarm to trigger reports, stream agent thoughts, and relay chat messages
- **Visualization:** The agent graph is a single unified view -- nodes ARE the agent cards with streaming thought feeds, edges ARE the message connections with animated pulses. Not two separate visualizations
- **Report style:** Orchestrator produces a unified narrative, not sectioned per-agent output. The orchestrator does real synthesis work to weave insights together
- **Modeling agent:** Runs statistical models (regression, backtesting) in a code execution environment, generates charts that get embedded in the report markdown

## Constraints

- **Timeline**: 24-hour hackathon -- every feature must justify its existence
- **Tech stack**: Vite + React (frontend), Python + uAgents (agents), fetch.ai agentverse (agent hosting)
- **fetch.ai track**: Must use uAgents library and ideally deploy to agentverse to be competitive
- **Financial APIs**: Need free/hackathon-friendly APIs for news and market data (research will determine which)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Unified narrative over sectioned report | More valuable synthesis, demonstrates orchestrator intelligence | -- Pending |
| On-demand over scheduled reports | Simpler architecture for 24h hackathon | -- Pending |
| CSV upload over brokerage API | Dramatically reduces scope while still demonstrating portfolio analysis | -- Pending |
| Single agent graph view (nodes = cards) | One cohesive visualization instead of two separate views | -- Pending |
| Chat through orchestrator only | Simpler UX, demonstrates agent routing in the graph view | -- Pending |

---
## Current State

Phase 2 (Agent Pipeline) complete -- all 4 domain agents live (Portfolio, News, Alt Assets with real APIs; Modeling mock with real charts). Orchestrator fans out concurrently, detects contradictions, synthesizes unified narrative via Gemini 2.5 Flash. Full pipeline verifiable via curl POST to /report. 145 tests passing. Ready for Phase 3: Frontend and Visualization.

---
*Last updated: 2026-03-22 after Phase 2 completion*
