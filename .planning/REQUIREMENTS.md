# Requirements: InvestiSwarm

**Defined:** 2026-03-21
**Core Value:** A single cohesive investment report that synthesizes multiple specialized analysis domains into one actionable narrative

## v1 Requirements

Requirements for hackathon demo. Each maps to roadmap phases.

### Infrastructure

- [x] **INFRA-01**: uAgents Bureau running all 5 agents in one process
- [x] **INFRA-02**: FastAPI bridge with SSE endpoints for web-to-agent communication
- [x] **INFRA-03**: Pydantic message models for all inter-agent communication
- [x] **INFRA-04**: Mock data mode for all agents (toggle for demo vs development)

### Portfolio Agent (No LLM -- Pure Computation)

- [x] **PORT-01**: Portfolio agent loads mock portfolio data (realistic holdings across sectors)
- [x] **PORT-02**: Computes sector/asset allocation breakdown
- [x] **PORT-03**: Calculates diversification metrics (Herfindahl index, portfolio beta)
- [x] **PORT-04**: Runs correlation matrix across holdings using numpy/pandas
- [x] **PORT-05**: Returns structured numerical output to orchestrator

### News Agent (Partial LLM -- FinBERT for Sentiment)

- [x] **NEWS-01**: Fetches financial news headlines from Finnhub API
- [x] **NEWS-02**: Filters headlines for relevance to portfolio holdings
- [x] **NEWS-03**: Scores sentiment per article using FinBERT (not LLM)
- [x] **NEWS-04**: Computes aggregate sentiment metrics per holding/sector
- [x] **NEWS-05**: Returns structured sentiment data + raw headlines to orchestrator

### Modeling Agent (No LLM -- Pure Computation)

- [ ] **MODL-01**: Retrieves historical price data via yfinance
- [ ] **MODL-02**: Runs specifiable analyses via chart registry (regression, correlation_matrix, sector_performance, volatility_cone, price_history)
- [x] **MODL-03**: Generates charts (matplotlib/plotly) per requested analysis type, returned as ChartOutput with type, title, image_base64, and summary
- [ ] **MODL-04**: Computes risk metrics (Sharpe ratio, volatility) plus extensible metrics dict
- [ ] **MODL-05**: Returns structured metrics + multiple chart outputs to orchestrator

### Alternative Assets Agent (No LLM -- Pure Computation)

- [ ] **ALT-01**: Fetches current crypto prices and trends from CoinGecko
- [ ] **ALT-02**: Retrieves commodity/real estate market data
- [ ] **ALT-03**: Computes cross-asset correlations with portfolio holdings
- [ ] **ALT-04**: Returns structured market data + correlations to orchestrator

### Orchestrator (LLM-Powered Synthesis)

- [ ] **ORCH-01**: Dispatches to appropriate domain agents based on report request or chat query
- [ ] **ORCH-02**: Receives structured data from all domain agents
- [ ] **ORCH-03**: Uses LLM to synthesize agent outputs into unified narrative report
- [ ] **ORCH-04**: Identifies cross-agent contradictions and patterns (e.g., bullish sentiment but weakening momentum)
- [ ] **ORCH-05**: Generates executive summary with key actionable insights

### Report Display

- [ ] **REPT-01**: Renders report as formatted markdown with embedded charts
- [ ] **REPT-02**: User can trigger on-demand report generation
- [ ] **REPT-03**: Report displays as unified narrative (not sectioned per-agent)

### Chat Interface

- [ ] **CHAT-01**: Text input routed through orchestrator agent
- [ ] **CHAT-02**: Responses are contextual to the current report
- [ ] **CHAT-03**: Agent graph shows which agents are dispatched during chat

### Agent Graph Visualization

- [ ] **GRPH-01**: Node per agent displayed as card with name and status
- [ ] **GRPH-02**: Real-time streaming thought feed in each agent card
- [ ] **GRPH-03**: Animated message pulses traveling along edge connections
- [ ] **GRPH-04**: Hover on connections shows message title and description

## v2 Requirements

Deferred to post-hackathon.

### Portfolio Enhancement

- **PORT-V2-01**: CSV upload and parsing of real brokerage exports
- **PORT-V2-02**: Impact analysis for hypothetical stock additions
- **PORT-V2-03**: Brokerage API auto-sync (Alpaca, Schwab)

### News Enhancement

- **NEWS-V2-01**: Source credibility weighting
- **NEWS-V2-02**: Historical sentiment trend tracking

### Modeling Enhancement

- **MODL-V2-01**: Strategy backtesting with returns comparison
- **MODL-V2-02**: Monte Carlo simulation
- **MODL-V2-03**: Multiple model comparison

### Alternative Assets Enhancement

- **ALT-V2-01**: DeFi yield analysis
- **ALT-V2-02**: Whale movement tracking

### Platform

- **PLAT-V2-01**: User authentication
- **PLAT-V2-02**: Scheduled daily report generation (cron)
- **PLAT-V2-03**: Agentverse deployment (not just local Bureau)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time market data streaming | Agents fetch on report generation, not continuous |
| Mobile app | Web-first for hackathon |
| Direct agent chat (@mentioning specific agents) | All chat routes through orchestrator |
| OAuth/social login | No auth needed for hackathon demo |
| Backtesting strategy builder UI | Too complex for 24h; modeling agent just runs preset analyses |
| LLM in domain agents | Portfolio, Modeling, Alt Assets are pure computation; News uses FinBERT not LLM |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 1 | Complete |
| INFRA-02 | Phase 1 | Complete |
| INFRA-03 | Phase 1 | Pending |
| INFRA-04 | Phase 1 | Pending |
| PORT-01 | Phase 2 | Complete |
| PORT-02 | Phase 2 | Complete |
| PORT-03 | Phase 2 | Complete |
| PORT-04 | Phase 2 | Complete |
| PORT-05 | Phase 2 | Complete |
| NEWS-01 | Phase 2 | Complete |
| NEWS-02 | Phase 2 | Complete |
| NEWS-03 | Phase 2 | Complete |
| NEWS-04 | Phase 2 | Complete |
| NEWS-05 | Phase 2 | Complete |
| MODL-01 | Phase 2 | Pending |
| MODL-02 | Phase 2 | Pending |
| MODL-03 | Phase 2 | Complete |
| MODL-04 | Phase 2 | Pending |
| MODL-05 | Phase 2 | Pending |
| ALT-01 | Phase 2 | Pending |
| ALT-02 | Phase 2 | Pending |
| ALT-03 | Phase 2 | Pending |
| ALT-04 | Phase 2 | Pending |
| ORCH-01 | Phase 2 | Pending |
| ORCH-02 | Phase 2 | Pending |
| ORCH-03 | Phase 2 | Pending |
| ORCH-04 | Phase 2 | Pending |
| ORCH-05 | Phase 2 | Pending |
| REPT-01 | Phase 3 | Pending |
| REPT-02 | Phase 3 | Pending |
| REPT-03 | Phase 3 | Pending |
| GRPH-01 | Phase 3 | Pending |
| GRPH-02 | Phase 3 | Pending |
| GRPH-03 | Phase 3 | Pending |
| GRPH-04 | Phase 3 | Pending |
| CHAT-01 | Phase 4 | Pending |
| CHAT-02 | Phase 4 | Pending |
| CHAT-03 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 38 total
- Mapped to phases: 38
- Unmapped: 0

---
*Requirements defined: 2026-03-21*
*Last updated: 2026-03-21 after roadmap creation*
