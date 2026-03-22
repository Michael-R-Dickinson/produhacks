# Product Requirements Document: InvestorSwarm

## 1. Problem Statement

### The Problem: Information Overload in Retail Investment

Modern retail investors face a fragmented, overwhelming research process. To evaluate a single portfolio decision, they need to:

1. **Check portfolio analytics tools** (Morningstar, Yahoo Finance) for risk metrics and allocation breakdowns
2. **Scan financial news** (Bloomberg, Reuters, CNBC) and evaluate whether headlines are positive or negative for their specific holdings
3. **Assess quantitative models** (TradingView charts, regression trendlines, Sharpe ratios, volatility)
4. **Monitor alternative assets** (crypto prices, commodities, BTC dominance) and their correlation with traditional equities

This creates three critical pain points:

| Pain Point | Impact |
|---|---|
| **Fragmented data sources** | Investors tab-switch across 5-8 platforms, each with its own interface, account, and data format. Insights are never synthesized across domains. |
| **No cross-signal analysis** | A human checking sentiment on CNBC and charts on TradingView will rarely notice that bullish news sentiment contradicts a bearish quantitative trendline — contradictions that are critical for decision quality. |
| **Time cost** | A comprehensive portfolio review takes 30-60 minutes for a sophisticated amateur investor. Most skip it and rely on gut or a single source. |

### Market Evidence

- **62% of retail investors** spend less than 1 hour per week on investment research despite wanting to do more (Charles Schwab 2024 Investor Survey)
- **$1.4T+ in AUM** is managed through self-directed retail brokerage accounts in North America
- AI financial assistants (Wealthfront, Betterment) have proven demand, but they optimize automation, not investor understanding. Users cede control rather than gaining insight.

### Target Users

**Primary: Self-directed retail investors** who actively manage their own portfolios ($10K-$500K), use multiple research sources, and want a single, unified view of their portfolio health. They are often professionals in other fields (engineering, medicine, law) who invest as a serious hobby but don't have the time for a full Bloomberg terminal workflow.

**Secondary: Financial advisors** managing 10-50 client accounts who need quick portfolio health summaries before client meetings.

---

## 2. Proposed Solution: InvestorSwarm

InvestorSwarm is a **multi-agent investment intelligence platform** powered by the Fetch.ai agent protocol. Instead of asking a single LLM to "analyze my portfolio" (which produces generic, unsourced output), InvestorSwarm decomposes the problem into four specialized computational agents, each running its own domain-specific models and APIs, coordinated by an LLM-powered Orchestrator that synthesizes their findings into a single, unified narrative investment report.

### Why Multi-Agent Architecture Matters

The key insight is that **most of an investment report does NOT need an LLM**:

| Domain | LLM Required? | Why Not? |
|---|---|---|
| Portfolio risk metrics (beta, HHI, correlations) | ❌ No | These are deterministic math — numpy/pandas compute them exactly |
| News sentiment scoring | ❌ No (FinBERT) | A fine-tuned financial NLP model is faster, cheaper, and more accurate than a general LLM |
| Chart generation & volatility modeling | ❌ No | matplotlib/scipy produce precise statistical charts |
| Crypto/commodity price fetching | ❌ No | API calls with simple math |
| **Synthesizing all of the above into a narrative** | ✅ **Yes** | This requires reasoning about cross-domain signals, identifying contradictions, and writing natural language |

By limiting LLM usage to only the synthesis step (Orchestrator), InvestorSwarm is:
- **More accurate** — numerical computations are exact, not hallucinated
- **More transparent** — each metric has a traceable source (yfinance, Finnhub, CoinGecko)
- **Faster** — agents run concurrently; the LLM only processes structured summaries, not raw data
- **Cheaper** — one LLM call per report instead of multiple calls for each domain

### Core Value Proposition

> A single cohesive investment report that synthesizes portfolio analytics, market sentiment, quantitative models, and alternative asset signals into one actionable narrative — replacing the need to check multiple sources manually.

---

## 3. System Architecture

### 3.1 High-Level Architecture

The system has three layers connected via HTTP and Server-Sent Events (SSE):

```
┌──────────────────────────────────────────────────────────────────┐
│  FRONTEND (React + Vite, port 5173)                             │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────────┐   │
│  │ Daily      │  │ Swarm        │  │ Chat                   │   │
│  │ Report     │  │ Activity     │  │ Interface              │   │
│  │ (Markdown) │  │ (Agent Graph)│  │ (Orchestrator-routed)  │   │
│  └────────────┘  └──────────────┘  └────────────────────────┘   │
│         │                │                     │                 │
│         └────────────────┴─────────────────────┘                │
│                          │ SSE EventSource                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────────┐
│  BRIDGE LAYER (FastAPI, port 8000)                              │
│  ┌─────────────┐  ┌──────────┐  ┌─────────────────────────┐    │
│  │ GET /events  │  │POST      │  │ POST /report            │    │
│  │ (SSE stream) │  │/trigger  │  │ (→ orchestrator REST)   │    │
│  └─────────────┘  └──────────┘  └─────────────────────────┘    │
│         ▲                                    │                  │
│         │ push_sse_event()                   │                  │
│         │ (loop.call_soon_threadsafe)         │                  │
└─────────┼────────────────────────────────────┼──────────────────┘
          │                                    │
┌─────────┼────────────────────────────────────┼──────────────────┐
│  AGENT LAYER (uAgents Bureau, port 8006)     │                  │
│         │                                    ▼                  │
│  ┌──────┴──────────────────────────────────────────────┐        │
│  │  ORCHESTRATOR (port 8005)                           │        │
│  │  • asyncio.gather fan-out to all agents             │        │
│  │  • detect_contradictions() cross-signal analysis    │        │
│  │  • build_synthesis_prompt() structured thematic     │        │
│  │  • synthesize_report() via Google Gemini            │        │
│  └──────┬─────────┬──────────┬──────────┬──────────────┘        │
│         │         │          │          │                        │
│    ┌────┴───┐ ┌───┴────┐ ┌──┴─────┐ ┌─┴──────────┐            │
│    │Portfolio│ │ News   │ │Modeling│ │Alt Assets   │            │
│    │ :8001  │ │ :8002  │ │ :8003  │ │   :8004     │            │
│    │numpy   │ │Finnhub │ │yfinance│ │CoinGecko    │            │
│    │yfinance│ │FinBERT │ │matplot │ │Finnhub      │            │
│    │pandas  │ │        │ │        │ │pandas       │            │
│    └────────┘ └────────┘ └────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Process Model

The entire backend runs as a **single OS process** with two threads:

- **Main thread**: uvicorn hosting FastAPI (port 8000) with async SSE streaming
- **Daemon thread**: uAgents Bureau (port 8006) running all 5 agent event loops

The two threads communicate through a single point: `push_sse_event()` in `agents/bridge/events.py`, which uses `loop.call_soon_threadsafe()` to forward agent events (thoughts, status changes, report data) from the Bureau thread to the FastAPI SSE stream.

### 3.3 End-to-End Report Flow

```
1. User clicks "Generate Report" in the frontend
2. Frontend POSTs to /report on the FastAPI bridge
3. Bridge forwards to Orchestrator via REST endpoint at localhost:8005/submit/report
4. Orchestrator dispatches to all 4 agents CONCURRENTLY via asyncio.gather:
   ├── Portfolio Agent: computes sector allocation, HHI, beta, 90-day correlation matrix
   ├── News Agent: fetches Finnhub headlines, filters by ticker, scores with FinBERT
   ├── Modeling Agent: runs analyses, generates charts, computes Sharpe ratio
   └── Alt Assets Agent: fetches CoinGecko crypto, Finnhub commodities, BTC dominance
5. Each agent emits real-time SSE "thought" events as it works (visible in Swarm Activity graph)
6. Orchestrator receives all 4 structured responses
7. Orchestrator runs detect_contradictions() for cross-signal analysis
8. Orchestrator builds structured thematic prompt with all agent data
9. Google Gemini synthesizes the unified narrative investment report
10. Report streams back to frontend via SSE report.complete event
```

---

## 4. Agent Specifications

### 4.1 Portfolio Agent

**Purpose**: Pure mathematical computation of portfolio risk and allocation metrics.

**Data Sources**: `yfinance` (Yahoo Finance historical prices)

**Computation Functions**:

| Function | Input | Output | Algorithm |
|---|---|---|---|
| `compute_sector_allocation()` | Portfolio holdings list | `{sector: weight}` dict | Group by sector, sum weights. Crypto → "Crypto" sector |
| `compute_herfindahl()` | Weight array | HHI float | `sum(w²)` — lower = more diversified |
| `compute_top_holdings()` | Portfolio, n | Top N holdings | Sort by weight descending, take first N |
| `compute_portfolio_beta()` | Tickers, weights, lookback | Beta float | `cov(portfolio_returns, SPY_returns) / var(SPY_returns)` using numpy |
| `compute_correlation_matrix()` | Tickers, lookback | Nested dict | 90-day daily returns → `pandas.DataFrame.corr()`, rounded to 4dp |

**Response Schema**:
```python
class PortfolioResponse(Model):
    sector_allocation: dict[str, float]      # {"Technology": 0.42, "Healthcare": 0.18}
    top_holdings: list[dict]                 # [{"ticker": "AAPL", "weight": 0.18, "sector": "Technology"}]
    herfindahl_index: float                  # 0.087 (lower = more diversified)
    portfolio_beta: float                    # 1.12 (vs SPY benchmark)
    correlation_matrix: dict[str, dict[str, float]]  # Nested {ticker: {ticker: corr}}
```

### 4.2 News / Sentiment Agent

**Purpose**: Fetch financial news and score sentiment using FinBERT (a financial domain NLP model, NOT a general LLM).

**Data Sources**: `Finnhub API` (headlines), `ProsusAI/finbert` HuggingFace model (sentiment)

**Pipeline**:
1. `fetch_finnhub_headlines()` — fetches general market news + per-ticker company news (7-day window), deduplicates by headline text
2. `filter_headlines_for_tickers()` — matches ticker symbols in headline text or "related" field, caps at 5 headlines per ticker to prevent one stock dominating the signal
3. `score_sentiment()` — runs FinBERT (lazy-loaded, 500MB model), returns `positive - negative` score in [-1, 1]
4. `score_headlines()` — scores each headline, discards near-neutral (`|score| < 0.1`) for noise reduction
5. `aggregate_sentiment_by_ticker()` — mean sentiment per ticker
6. `compute_overall_sentiment()` — grand mean across all tickers

**Response Schema**:
```python
class NewsResponse(Model):
    headlines: list[dict]                    # [{"title": "...", "sentiment": 0.82, "matched_tickers": ["AAPL"]}]
    aggregate_sentiment: dict[str, float]    # {"AAPL": 0.82, "MSFT": -0.35} — range [-1, 1]
    overall_sentiment: float                 # 0.29 (portfolio-wide mean)
```

### 4.3 Modeling / Quant Agent

**Purpose**: Generate statistical charts and compute risk-adjusted return metrics. No LLM — pure computation.

**Data Sources**: `yfinance` (historical prices), `matplotlib` (chart generation)

**Chart Registry** (extensible — new types are added by writing one function):

| Chart Type Key | What It Generates |
|---|---|
| `regression` | Linear regression + trend line on portfolio value |
| `correlation_matrix` | Heatmap of inter-holding return correlations |
| `sector_performance` | Bar chart comparing sector returns |
| `volatility_cone` | Forward-looking volatility bands (cone chart) |
| `price_history` | Overlay line chart of all holding price histories |

**Response Schema**:
```python
class ChartOutput(Model):
    chart_type: str          # Matches the analysis key (e.g. "regression")
    title: str               # Human-readable (e.g. "Portfolio Linear Regression (1Y)")
    image_base64: str        # PNG encoded as base64 string
    summary: str             # One-line description for the orchestrator narrative

class ModelResponse(Model):
    holdings_analyzed: list[str]
    sharpe_ratio: float             # Risk-adjusted return metric
    volatility: float               # Annualized portfolio volatility  
    trend_slope: float              # Regression slope coefficient
    charts: list[ChartOutput]       # One per requested analysis type
    metrics: dict[str, float]       # Extensible: r_squared, max_drawdown, beta
```

### 4.4 Alternative Assets Agent

**Purpose**: Crypto and commodity market signals with cross-asset correlation to the equity portfolio.

**Data Sources**: `CoinGecko API` (crypto prices, BTC dominance), `Finnhub API` (commodity prices), `yfinance` (for correlation computation)

**Functions**:

| Function | What It Does |
|---|---|
| `fetch_crypto_prices()` | Gets BTC, ETH, SOL, BNB, AVAX prices + 7-day % change from CoinGecko |
| `fetch_btc_dominance()` | Gets BTC market cap dominance from CoinGecko global endpoint |
| `fetch_commodity_prices()` | Gets Gold (GC1!) and Oil (CL1!) from Finnhub |
| `trend_signal()` | Pure math: >3% → bullish, <-3% → bearish, else neutral |
| `compute_cross_correlations()` | Pearson correlation between alt asset returns and equity portfolio returns |

**Response Schema**:
```python
class AlternativesResponse(Model):
    crypto_prices: dict[str, float]          # {"BTC": 67450.0, "ETH": 3520.0}
    trend_signals: dict[str, str]            # {"BTC": "bullish", "ETH": "neutral"}
    btc_dominance: float                     # 54.3 (percentage)
    commodities: dict[str, float]            # {"GOLD": 2340.5, "OIL": 78.2}
    cross_correlations: dict[str, float]     # {"BTC": 0.12, "GOLD": -0.05}
```

### 4.5 Orchestrator Agent

**Purpose**: The only LLM-powered component. Coordinates all agents, detects cross-domain contradictions, and synthesizes the unified narrative.

**LLM**: Google Gemini via `google.genai` (lazy-initialized — module importable without API key)

**Key Functions**:

| Function | What It Does |
|---|---|
| `safe_result()` | If an agent times out or errors, falls back to mock data instead of crashing the whole pipeline |
| `detect_contradictions()` | Flags: (1) bearish news on top portfolio holdings, (2) bullish sentiment contradicting negative quantitative momentum |
| `build_synthesis_prompt()` | Structures all 4 agent responses + contradiction flags into a thematic prompt with JSON-serialized data |
| `synthesize_report()` | Single Gemini API call to generate the unified narrative |

**Fan-out pattern**: `asyncio.gather(*tasks, return_exceptions=True)` — all 4 agents run concurrently. If one fails, the others still contribute to the report.

---

## 5. Frontend Specification

### 5.1 Tech Stack
- **React 18** + TypeScript + Vite (build tooling)
- **Vanilla CSS** with custom design system (no Tailwind/Bootstrap)
- **Lucide React** for iconography
- **SSE (EventSource)** for real-time agent thought streaming

### 5.2 Pages

| Page | Route | Purpose |
|---|---|---|
| **Daily Report** | `/` | Renders the synthesized markdown report with embedded base64 charts |
| **Swarm Activity** | `/swarm` | Interactive agent graph — draggable nodes, dotted connection lines, real-time status indicators |
| **Portfolio** | `/portfolio` | Quantitative analysis dashboard with performance metrics |
| **Chat** | `/chat` | Chat interface routed through the Orchestrator for follow-up questions |

### 5.3 Real-Time SSE Event System

The frontend connects to `GET /events` on the FastAPI bridge and receives a continuous stream of typed JSON events:

| Event Type | Payload | UI Effect |
|---|---|---|
| `agent.status` | `{status: "working"\|"done"\|"error"}` | Agent node color/animation change in Swarm graph |
| `agent.thought` | `{text: "Computing 90-day correlation..."}` | Streaming thought text in agent cards |
| `agent.message` | `{from: "orchestrator", to: "portfolio", title: "AnalyzePortfolio"}` | Animated pulse along graph edge |
| `report.complete` | `{markdown: "...", charts: [...]}` | Report page renders the final document |
| `chat.response` | `{text: "...", final: true}` | Chat response bubble |

### 5.4 Design System

- **Color palette**: Dark navy sidebar (`#1A1F36`) with light content area, accent colors per agent (purple for Portfolio, orange for Sentiment, red for Alt Assets, teal for Quant, blue for Orchestrator)
- **Typography**: System font stack with premium weight hierarchy
- **Animations**: CSS keyframe animations for floating agent nodes, pulse effects on active connections, smooth status transitions
- **Responsive**: Sidebar collapses below 768px viewport width

---

## 6. Data Contracts (Inter-Agent Communication)

All inter-agent messages inherit from `uagents.Model` (Pydantic). All SSE events use `pydantic.BaseModel`.

### 6.1 Request Models (Orchestrator → Domain Agent)

```python
# agents/models/requests.py

class ReportRequest(Model):
    tickers: list[str]
    mock: bool = True

class AnalyzePortfolio(Model):
    holdings: list[str]
    mock: bool = False

class FetchNews(Model):
    tickers: list[str]
    mock: bool = False

class RunModel(Model):
    holdings: list[str]
    analyses: list[str] = ["regression"]
    lookback_days: int = 365
    mock: bool = False

class AnalyzeAlternatives(Model):
    mock: bool = False
```

### 6.2 SSE Event Envelope

```python
# agents/models/events.py

class SSEEvent(BaseModel):
    event_id: str              # UUID
    timestamp: float           # Unix timestamp
    agent_id: str              # "portfolio" | "news" | "modeling" | "alternatives" | "orchestrator"
    event_type: str            # "agent.status" | "agent.thought" | "agent.message" | "report.complete" | "chat.response"
    payload: dict              # Shape depends on event_type
```

---

## 7. Environment & Configuration

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `MOCK_DATA` | No | `"true"` | When true, all agents return realistic mock data without calling any external APIs |
| `FINNHUB_API_KEY` | Live mode only | — | Financial news headlines + commodity prices (60 req/min free tier) |
| `GEMINI_API_KEY` | Live mode only | — | Google Gemini LLM for orchestrator narrative synthesis |

**CoinGecko** does not require an API key (30 req/min on free tier).

**Critical design decision**: Mock mode is the default. The entire pipeline — all 5 agents, the bridge, and the frontend — runs fully offline with zero API keys. This enables frontend development, testing, and demo rehearsal without burning rate limits.

---

## 8. Testing Strategy

**61 unit tests** across the entire agent pipeline, all strictly isolated from external services:

| Agent | Tests | Isolation Technique |
|---|---|---|
| Portfolio Agent | 17 | `yfinance.download` monkeypatched with DataFrame factory |
| News Agent | 16 | `score_sentiment` monkeypatched to avoid loading 500MB FinBERT model |
| Alt Assets Agent | 13 | Pure function tests — no API calls in computation functions |
| Orchestrator | 15 | No Gemini calls — tests cover `safe_result`, `detect_contradictions`, `build_synthesis_prompt` |

All tests run in under 5 seconds with zero network dependency.

```bash
cd agents && pytest
```

---

## 9. File Structure

```
produhacks/
├── PRD.md                          # This document
├── README.md                       # Setup instructions and project overview
├── .env.example                    # MOCK_DATA, FINNHUB_API_KEY, GEMINI_API_KEY
├── pyproject.toml                  # Python dependencies (uv)
│
├── agents/                         # Python backend — the agent swarm
│   ├── main.py                     # Entry point — starts uvicorn + Bureau
│   ├── bureau.py                   # Bureau launcher (daemon thread)
│   ├── orchestrator.py             # LLM-powered orchestrator (Gemini synthesis)
│   ├── portfolio_agent.py          # Portfolio risk & allocation (numpy/yfinance)
│   ├── news_agent.py               # News sentiment (Finnhub + FinBERT)
│   ├── modeling_agent.py           # Quant modeling (Sharpe, volatility, charts)
│   ├── modeling_charts.py          # Chart registry (matplotlib generators)
│   ├── modeling_data.py            # Data fetching utilities for modeling
│   ├── alternatives_agent.py       # Crypto + commodities (CoinGecko/Finnhub)
│   ├── models/
│   │   ├── requests.py             # Pydantic request models (Orchestrator → Agents)
│   │   ├── responses.py            # Pydantic response models (Agents → Orchestrator)
│   │   └── events.py               # SSE event models (Agents → Browser)
│   ├── bridge/
│   │   ├── app.py                  # FastAPI app: /events SSE, /trigger, /report
│   │   └── events.py               # push_sse_event() cross-thread bridge
│   ├── mocks/                      # Mock response factories for each agent
│   ├── data/
│   │   └── portfolio.py            # Central mock portfolio (12 holdings, 6 sectors)
│   └── tests/                      # 61 unit tests
│
└── frontend/                       # React + Vite frontend
    ├── public/
    │   └── brain-logo.png          # Custom brain icon logo
    ├── src/
    │   ├── App.tsx                  # Root component with routing
    │   ├── main.tsx                 # Vite entry point
    │   ├── index.css               # Global design system (~25KB)
    │   ├── pages/
    │   │   ├── DailyReport.tsx      # Markdown report renderer
    │   │   ├── SwarmActivity.tsx     # Interactive draggable agent graph
    │   │   ├── QuantAnalysis.tsx     # Portfolio analytics dashboard
    │   │   └── Chat.tsx             # Chat interface
    │   ├── components/
    │   │   └── layout/
    │   │       └── Sidebar.tsx      # Navigation sidebar with agent status
    │   ├── context/
    │   │   └── SwarmContext.tsx      # Global SSE state management
    │   └── services/
    │       └── sseService.ts        # EventSource connection manager
    └── package.json
```

---

## 10. Scalability Roadmap (v1 → v2)

### Current State (v1 — Hackathon MVP)
- Mock portfolio with 12 hardcoded holdings  
- On-demand report generation only
- Single-user, no authentication
- Local Bureau deployment

### v2 Roadmap (Post-Hackathon)

| Feature | Description | Complexity |
|---|---|---|
| **CSV Portfolio Upload** | Parse brokerage export CSVs (Schwab, Fidelity, Interactive Brokers) | Medium |
| **Brokerage API Sync** | Alpaca, Schwab APIs for live portfolio syncing | High |
| **Impact Analysis** | "What if I add NVDA?" hypothetical scenario modeling | Medium |
| **Monte Carlo Simulation** | Forward-looking probability distributions for portfolio returns | Medium |
| **Strategy Backtesting** | Compare buy-and-hold vs rebalancing over historical periods | High |
| **Source Credibility Weighting** | Weight news sentiment by publisher reputation (Reuters > blog) | Low |
| **Historical Sentiment Trends** | Track sentiment per ticker over weeks/months for trend analysis | Medium |
| **DeFi Yield Analysis** | Evaluate staking/lending yields across DeFi protocols | High |
| **Scheduled Reports** | Cron-based daily report generation with email delivery | Medium |
| **User Authentication** | OAuth2 login for multi-user support and portfolio persistence | Medium |
| **Agentverse Deployment** | Deploy agents to Fetch.ai Agentverse for decentralized hosting | High |

### Market Positioning

InvestorSwarm sits at the intersection of three trends:

1. **AI-assisted investing** (Wealthfront, Betterment) — but those automate decisions. InvestorSwarm **informs** the investor, keeping them in control.
2. **Multi-agent systems** (CrewAI, AutoGen) — but those are developer toolkits. InvestorSwarm is a **consumer product** with a polished UI.
3. **Financial data aggregation** (Yahoo Finance, TradingView) — but those show raw data. InvestorSwarm delivers **synthesized narrative analysis**.

The moat is the **agent specialization pattern**: as the platform grows, new domain agents (ESG scoring, insider trading signals, macro indicators) plug in without modifying existing agents — the Orchestrator automatically incorporates their data into the synthesis.
