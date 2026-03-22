# InvestiSwarm -- Full Architecture

## Overview

InvestiSwarm is a multi-agent investment analysis platform. Five specialized uAgents collaborate through a central orchestrator to produce a unified narrative investment report. A FastAPI bridge translates between the browser (HTTP/SSE) and the agent protocol.

```mermaid
graph TB
    subgraph "Browser [Phase 3]"
        UI[React/Vite :5173]
    end

    subgraph "Bridge Layer [Phase 1]"
        FA[FastAPI :8000]
    end

    subgraph "Agent Layer -- uAgents Bureau :8006 [Phase 1 stubs / Phase 2 real]"
        ORCH[Orchestrator :8005]
        PORT[Portfolio Agent :8001]
        NEWS[News Agent :8002]
        MODL[Modeling Agent :8003]
        ALT[Alternatives Agent :8004]
    end

    UI -- "POST /trigger | GET /events (SSE)" --> FA
    FA -- "asyncio.Queue (thread-safe)" --> ORCH
    ORCH -- "ctx.send(AnalyzePortfolio)" --> PORT
    ORCH -- "ctx.send(FetchNews)" --> NEWS
    ORCH -- "ctx.send(RunModel)" --> MODL
    ORCH -- "ctx.send(AnalyzeAlternatives)" --> ALT
    PORT -- "PortfolioResponse" --> ORCH
    NEWS -- "NewsResponse" --> ORCH
    MODL -- "ModelResponse" --> ORCH
    ALT -- "AlternativesResponse" --> ORCH
```

---

## Process Model

The system runs in a **single OS process** with two event loops isolated by thread:

```mermaid
graph LR
    subgraph "Main Thread"
        UV[uvicorn] --> FALOOP["FastAPI asyncio loop"]
        FALOOP --> SSE["/events SSE stream"]
        FALOOP --> TRIG["/trigger endpoint"]
        FALOOP --> EQ["event_queue (asyncio.Queue)"]
    end

    subgraph "Daemon Thread"
        BL["Bureau asyncio loop"] --> B["Bureau :8006"]
        B --> A1[orchestrator :8005]
        B --> A2[portfolio :8001]
        B --> A3[news :8002]
        B --> A4[modeling :8003]
        B --> A5[alternatives :8004]
    end

    A2 -- "push_sse_event() via call_soon_threadsafe" --> EQ
    A3 -- "push_sse_event()" --> EQ
    A4 -- "push_sse_event()" --> EQ
    A5 -- "push_sse_event()" --> EQ
    A1 -- "push_sse_event()" --> EQ
    EQ -- "SSE JSON stream" --> SSE
```

**Key detail:** `push_sse_event()` in `agents/bridge/events.py` bridges the two loops via `loop.call_soon_threadsafe()`. This is the only cross-thread communication point. *[Phase 1]*

---

## Data Types

All inter-agent messages are `uagents.Model` (Pydantic). All SSE events are `pydantic.BaseModel`.

### Request Models *[Phase 1 defined / Phase 2 consumed]*

Defined in `agents/models/requests.py`. Sent **Orchestrator --> Domain Agent**.

```mermaid
classDiagram
    class AnalyzePortfolio {
        holdings: list~str~
        mock: bool = False
    }
    class FetchNews {
        tickers: list~str~
        mock: bool = False
    }
    class RunModel {
        holdings: list~str~
        analyses: list~str~ = ["regression"]
        lookback_days: int = 365
        mock: bool = False
    }
    class AnalyzeAlternatives {
        mock: bool = False
    }

    AnalyzePortfolio --> PortfolioAgent : dispatched to
    FetchNews --> NewsAgent : dispatched to
    RunModel --> ModelingAgent : dispatched to
    AnalyzeAlternatives --> AlternativesAgent : dispatched to
```

| Model | Target Agent | Key Fields | Notes |
|-------|-------------|------------|-------|
| `AnalyzePortfolio` | Portfolio `:8001` | `holdings` (ticker list) | Mock flag bypasses API calls |
| `FetchNews` | News `:8002` | `tickers` (ticker list) | |
| `RunModel` | Modeling `:8003` | `holdings`, `analyses`, `lookback_days` | `analyses` selects from chart registry |
| `AnalyzeAlternatives` | Alternatives `:8004` | (none beyond mock) | Fetches crypto + commodities |

---

### Response Models *[Phase 1 defined / Phase 2 consumed]*

Defined in `agents/models/responses.py`. Sent **Domain Agent --> Orchestrator**.

```mermaid
classDiagram
    class PortfolioResponse {
        sector_allocation: dict~str, float~
        top_holdings: list~dict~
        herfindahl_index: float
        portfolio_beta: float
    }
    class NewsResponse {
        headlines: list~dict~
        aggregate_sentiment: dict~str, float~
        overall_sentiment: float
    }
    class ModelResponse {
        holdings_analyzed: list~str~
        sharpe_ratio: float
        volatility: float
        trend_slope: float
        charts: list~ChartOutput~
        metrics: dict~str, float~
    }
    class ChartOutput {
        chart_type: str
        title: str
        image_base64: str
        summary: str
    }
    class AlternativesResponse {
        crypto_prices: dict~str, float~
        cross_correlations: dict~str, float~
    }

    ModelResponse *-- ChartOutput
```

#### Field Reference

**PortfolioResponse**
| Field | Type | Example |
|-------|------|---------|
| `sector_allocation` | `dict[str, float]` | `{"Technology": 0.42, "Healthcare": 0.18}` |
| `top_holdings` | `list[dict]` | `[{"ticker": "AAPL", "weight": 0.18, "sector": "Technology"}]` |
| `herfindahl_index` | `float` | `0.087` (lower = more diversified) |
| `portfolio_beta` | `float` | `1.12` |

**NewsResponse**
| Field | Type | Example |
|-------|------|---------|
| `headlines` | `list[dict]` | `[{"title": "...", "sentiment": 0.82, "ticker": "AAPL"}]` |
| `aggregate_sentiment` | `dict[str, float]` | `{"AAPL": 0.82, "MSFT": -0.35}` -- range [-1, 1] |
| `overall_sentiment` | `float` | `0.29` |

**ModelResponse**
| Field | Type | Example |
|-------|------|---------|
| `holdings_analyzed` | `list[str]` | `["AAPL", "MSFT", "NVDA"]` |
| `sharpe_ratio` | `float` | `1.34` |
| `volatility` | `float` | `0.187` (annualized) |
| `trend_slope` | `float` | `0.0023` (regression coefficient) |
| `charts` | `list[ChartOutput]` | One per analysis type |
| `metrics` | `dict[str, float]` | Known keys: `r_squared`, `max_drawdown`, `beta` |

**ChartOutput** (embedded in `ModelResponse.charts`)
| Field | Type | Example |
|-------|------|---------|
| `chart_type` | `str` | `"regression"` |
| `title` | `str` | `"Portfolio Linear Regression (1Y)"` |
| `image_base64` | `str` | Base64-encoded PNG |
| `summary` | `str` | One-line description for narrative weaving |

**AlternativesResponse**
| Field | Type | Example |
|-------|------|---------|
| `crypto_prices` | `dict[str, float]` | `{"BTC": 67450.0, "ETH": 3520.0}` |
| `cross_correlations` | `dict[str, float]` | `{"BTC": 0.12, "GOLD": -0.05}` |

---

### SSE Event Models *[Phase 1]*

Defined in `agents/models/events.py`. Sent **Agent Layer --> Browser** via FastAPI SSE.

```mermaid
classDiagram
    class SSEEvent {
        event_id: str
        timestamp: float
        agent_id: str
        event_type: EventType
        payload: dict
    }

    class EventType {
        <<enumeration>>
        AGENT_STATUS = "agent.status"
        AGENT_THOUGHT = "agent.thought"
        AGENT_MESSAGE = "agent.message"
        REPORT_CHUNK = "report.chunk"
        REPORT_COMPLETE = "report.complete"
        CHAT_RESPONSE = "chat.response"
    }

    class AgentStatus {
        <<enumeration>>
        IDLE
        WORKING
        DONE
        ERROR
    }

    class MessageDirection {
        <<enumeration>>
        REQUEST
        RESPONSE
    }

    SSEEvent --> EventType
    AgentStatusPayload --> AgentStatus
    AgentMessagePayload --> MessageDirection

    class AgentStatusPayload {
        status: AgentStatus
        message: str
    }
    class AgentThoughtPayload {
        text: str
    }
    class AgentMessagePayload {
        from_agent: str
        to_agent: str
        title: str
        description: str
        direction: MessageDirection
    }
    class ReportChunkPayload {
        content: str
        section: str
        final: bool
    }
    class ReportCompletePayload {
        markdown: str
        charts: list~dict~
    }
    class ChatResponsePayload {
        text: str
        final: bool
    }
```

Every SSE event is an `SSEEvent` envelope. The `event_type` discriminates the `payload` shape:

| `event_type` | Payload Model | Used By | Phase |
|---|---|---|---|
| `agent.status` | `AgentStatusPayload` | All agents -- lifecycle transitions | 1 (stubs), 2+ (real) |
| `agent.thought` | `AgentThoughtPayload` | All agents -- reasoning steps | 1 (stubs), 2+ (real) |
| `agent.message` | `AgentMessagePayload` | Inter-agent comms visualization | 3 (graph edges) |
| `report.chunk` | `ReportChunkPayload` | Orchestrator -- streaming report | 2 |
| `report.complete` | `ReportCompletePayload` | Orchestrator -- final report | 2 |
| `chat.response` | `ChatResponsePayload` | Orchestrator -- chat replies | 4 |

---

## End-to-End Message Flow *[Phase 2]*

```mermaid
sequenceDiagram
    participant B as Browser
    participant F as FastAPI Bridge
    participant O as Orchestrator
    participant P as Portfolio Agent
    participant N as News Agent
    participant M as Modeling Agent
    participant A as Alternatives Agent

    B->>F: POST /trigger
    F->>O: Enqueue trigger

    par Fan-out (concurrent)
        O->>P: AnalyzePortfolio(holdings, mock)
        O->>N: FetchNews(tickers, mock)
        O->>M: RunModel(holdings, analyses, lookback_days, mock)
        O->>A: AnalyzeAlternatives(mock)
    end

    Note over P,A: Each agent emits SSE events<br/>via push_sse_event() as it works

    P-->>O: PortfolioResponse
    N-->>O: NewsResponse
    M-->>O: ModelResponse (with ChartOutput[])
    A-->>O: AlternativesResponse

    O->>O: GPT-4o mini synthesizes unified narrative
    O-->>F: report.chunk (streamed)
    O-->>F: report.complete (final markdown + charts)
    F-->>B: SSE stream
```

---

## Module Map

```
agents/
  main.py                     Entry point -- uvicorn + Bureau startup       [Phase 1]
  bureau.py                   Bureau launcher (daemon thread)               [Phase 1]
  orchestrator.py             Orchestrator agent (stub -> LLM dispatch)     [Phase 1 stub / Phase 2 real]
  portfolio_agent.py          Portfolio analysis agent                      [Phase 1 stub / Phase 2 real]
  news_agent.py               News + sentiment agent                        [Phase 1 stub / Phase 2 real]
  modeling_agent.py           Quantitative modeling agent (no LLM)          [Phase 1 stub / Phase 2 real]
  alternatives_agent.py       Crypto/commodities agent                      [Phase 1 stub / Phase 2 real]
  models/
    requests.py               Request models (Orchestrator -> Agents)       [Phase 1]
    responses.py              Response models (Agents -> Orchestrator)      [Phase 1]
    events.py                 SSE event envelope + payloads                 [Phase 1]
  bridge/
    app.py                    FastAPI app, /events SSE, /trigger POST       [Phase 1]
    events.py                 push_sse_event() cross-thread bridge          [Phase 1]
  mocks/
    portfolio.py              Mock PortfolioResponse                        [Phase 1]
    news.py                   Mock NewsResponse                             [Phase 1]
    modeling.py               Mock ModelResponse + ChartOutput              [Phase 1]
    alternatives.py           Mock AlternativesResponse                     [Phase 1]
  tests/
    test_models.py            Model serialization round-trips               [Phase 1]
    test_bureau.py            Agent registration + address stability        [Phase 1]
    test_bridge.py            SSE, CORS, PNA headers, event delivery        [Phase 1]
    test_mock.py              Mock data structure validation                [Phase 1]
```

**Frontend** *(Phase 3+, not yet scaffolded)*
```
src/                          React/Vite app                                [Phase 3]
  - Agent graph (React Flow)  Node-per-agent with streaming thoughts       [Phase 3]
  - Report viewer             Markdown + inline base64 charts              [Phase 3]
  - Chat interface            Text input routed through orchestrator        [Phase 4]
```

---

## Phase Roadmap Summary

| Phase | Name | Goal | Status |
|-------|------|------|--------|
| **1** | Foundation | Scaffold, models, bridge, mock data, Bureau -- verified E2E by curl | In Progress (2/3 plans done) |
| **2** | Agent Pipeline | Real agent logic produces complete markdown report via curl (no frontend) | Not Started |
| **3** | Frontend + Visualization | React app with live agent graph, streaming thoughts, report rendering | Not Started |
| **4** | Chat + Demo Polish | Follow-up chat, graph animation, clean demo flow | Not Started |

---

## Configuration

| Variable | Default | Purpose | Phase |
|----------|---------|---------|-------|
| `MOCK_DATA` | `"true"` | Enables mock data mode for all agents | 1 |
| Finnhub API key | -- | Financial news + commodity data (60 req/min) | 2 |
| CoinGecko API | -- | Crypto prices (30 req/min, no key needed) | 2 |
| OpenAI API key | -- | GPT-4o mini for orchestrator narrative synthesis | 2 |

---

## Key Design Decisions

- **Single process, two threads** -- Bureau and FastAPI share a process but have isolated event loops, bridged by `call_soon_threadsafe` *[Phase 1]*
- **Bureau on port 8006** -- avoids ASGI conflict with uvicorn on 8000 *[Phase 1]*
- **Mock-first development** -- every agent has a mock path to preserve API rate limits *[Phase 1]*
- **Curl-verifiable before React** -- Phase 2 must produce a complete report with no frontend *[Phase 2]*
- **GPT-4o mini for orchestrator** -- cost efficiency at hackathon scale *[Phase 2]*
- **Unified narrative, not sectioned** -- orchestrator synthesizes thematic report, not agent-per-section *[Phase 2]*
- **SSE (not WebSocket)** -- simpler unidirectional streaming from server to browser *[Phase 1]*
- **No backwards compatibility concerns** -- single-dev unreleased app
