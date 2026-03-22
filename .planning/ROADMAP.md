# Roadmap: InvestiSwarm

## Overview

InvestiSwarm ships in four phases ordered by hard dependencies: infrastructure first (the FastAPI bridge and Pydantic models that everything else plugs into), then the full agent pipeline end-to-end (all domain agents plus orchestrator synthesis, verifiable via curl before any frontend exists), then the frontend with live agent graph visualization (built against a working pipeline, not mocks), then chat interaction and demo polish. The agent graph visualization is the primary differentiator for the fetch.ai track and is deliberately last — it is an observability layer on top of the pipeline, not a prerequisite for it.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Foundation** - Scaffold, Pydantic message models, FastAPI SSE bridge, mock data mode, and API client wrappers verified end-to-end
- [ ] **Phase 2: Agent Pipeline** - All five agents (Portfolio, News, Modeling, Alt Assets, Orchestrator) producing a complete verifiable report with no frontend (gap closure in progress)
- [ ] **Phase 3: Frontend and Visualization** - React app with report rendering, CSV upload, and live agent graph with streaming thought feeds and animated edges
- [ ] **Phase 4: Chat and Demo Polish** - Chat interface routed through orchestrator, edge hover tooltips, UX hardening, and demo dry-run

## Phase Details

### Phase 1: Foundation
**Goal**: The three-process architecture is running, agents can communicate through the bridge, and no demo-killing infrastructure risk remains
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04
**Success Criteria** (what must be TRUE):
  1. A dummy uAgents Bureau with one stub agent is running locally and the FastAPI bridge successfully relays a round-trip message to it — verified by a curl call to the bridge endpoint returning a response
  2. All Pydantic message models for agent-to-agent communication are defined and importable from a shared module
  3. Mock data mode is toggled via environment variable and each agent returns realistic mock output instead of calling live APIs
  4. The FastAPI bridge exposes an SSE endpoint that a browser EventSource can connect to without Chrome Private Network Access errors
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Project scaffold, Pydantic message models, mock fixtures, event bridge module
- [x] 01-02-PLAN.md — Five stub agents, Bureau runner, FastAPI bridge with SSE, main.py entrypoint
- [x] 01-03-PLAN.md — Integration tests and end-to-end curl verification

### Phase 2: Agent Pipeline
**Goal**: Triggering a report request produces a complete unified narrative markdown document synthesized from all five agents — verifiable via curl with no frontend running
**Depends on**: Phase 1
**Requirements**: PORT-01, PORT-02, PORT-03, PORT-04, PORT-05, NEWS-01, NEWS-02, NEWS-03, NEWS-04, NEWS-05, MODL-01, MODL-02, MODL-03, MODL-04, MODL-05, ALT-01, ALT-02, ALT-03, ALT-04, ORCH-01, ORCH-02, ORCH-03, ORCH-04, ORCH-05
**Success Criteria** (what must be TRUE):
  1. A curl POST to the bridge /report endpoint returns a complete markdown document containing portfolio metrics, news sentiment, at least one embedded base64 chart, crypto/commodity data, and a synthesized executive summary
  2. The Portfolio agent computes and returns sector allocation, Herfindahl diversification index, portfolio beta, and correlation matrix
  3. The News agent fetches Finnhub headlines, filters them for portfolio relevance, scores sentiment with FinBERT, and returns aggregate per-holding sentiment
  4. The Modeling agent retrieves historical price data, runs requested analyses from its chart registry, generates matplotlib charts as base64 PNGs with ChartOutput metadata (type, title, summary), and returns Sharpe ratio, volatility, and extensible metrics
  5. The Orchestrator fans out to all domain agents concurrently, receives all responses, and produces a unified narrative (not sectioned per-agent) using GPT-4o mini
**Plans**: 6 plans

Plans:
- [x] 02-01-PLAN.md — Model contract updates, Phase 2 dependencies, central mock portfolio, mock chart generation
- [x] 02-02-PLAN.md — Portfolio agent live computation (sector allocation, Herfindahl, beta, correlation matrix)
- [x] 02-03-PLAN.md — News agent live logic (Finnhub fetch, relevance filtering, FinBERT sentiment scoring)
- [x] 02-04-PLAN.md — Alt Assets agent live logic (CoinGecko crypto, Finnhub commodities, correlations) + Modeling agent mock enhancement
- [x] 02-05-PLAN.md — Orchestrator fan-out, contradiction detection, GPT-4o mini synthesis, bridge /report endpoint, E2E verification
- [ ] 02-06-PLAN.md — Gap closure: fix asyncio.gather unpack bug in alternatives agent, create .env.example

### Phase 3: Frontend and Visualization
**Goal**: The React app displays the live agent graph with streaming thought feeds and animated edges during report generation, and renders the completed report with embedded charts
**Depends on**: Phase 2
**Requirements**: REPT-01, REPT-02, REPT-03, GRPH-01, GRPH-02, GRPH-03, GRPH-04
**Success Criteria** (what must be TRUE):
  1. Clicking the report generation button triggers agent activity visible in the graph — each agent node shows streaming thought text updating in real time via SSE
  2. Animated message pulses travel along edges between agent nodes as inter-agent messages are sent
  3. The completed report renders as formatted markdown with embedded chart images visible inline
  4. The CSV upload UI accepts a portfolio file and the report reflects the uploaded holdings
**Plans**: TBD

### Phase 4: Chat and Demo Polish
**Goal**: Judges can ask follow-up questions in the chat interface and see the agent graph respond, and the demo runs cleanly on the presentation machine with no last-minute failures
**Depends on**: Phase 3
**Requirements**: CHAT-01, CHAT-02, CHAT-03
**Success Criteria** (what must be TRUE):
  1. Typing a question in the chat input and submitting it produces a contextual response from the orchestrator visible in the chat thread
  2. The agent graph shows which domain agents are dispatched in response to a chat query — nodes activate and edges animate in real time
  3. Hovering on an animated edge connection shows a tooltip with the message title and brief description
  4. The full demo flow (CSV upload, report generation, chat question) completes without errors on live API data with mock mode disabled
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 3/3 | Complete | 2026-03-22 |
| 2. Agent Pipeline | 5/6 | Gap closure | - |
| 3. Frontend and Visualization | 0/TBD | Not started | - |
| 4. Chat and Demo Polish | 0/TBD | Not started | - |
