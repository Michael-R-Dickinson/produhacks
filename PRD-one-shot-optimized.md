## **Product Requirements Document (PRD)**

**Wealth Council**
Author: @big_m
Last Update Date: 2026-03-22

---

# **INTRODUCTION & CONTEXT SETTING**

Over 30 million new brokerage accounts were opened between 2020 and 2022, and retail investors now account for 25% of U.S. equities trading volume. The barrier to opening an account has effectively disappeared -- but the barrier to understanding what's in it has not.

Only 27% of Americans can correctly answer 5 of 7 basic financial literacy questions (FINRA, 2024). The tools that provide institutional-quality analysis -- multi-factor synthesis, correlation modeling, sentiment scoring -- cost $32,000/year (Bloomberg) to $113,000/year (Refinitiv) per seat. Casual investors are left manually cross-referencing fragmented sources with no way to synthesize them.

Wealth Council is a multi-agent investment intelligence platform that synthesizes portfolio analysis, quantitative modeling, and market data into a single unified report -- with plain-language explanations accessible to a college student and useful to an experienced quantitative investor. This PRD defines a clear path from prototype to scalable product.

# **TARGET SEGMENT & CUSTOMER PROBLEM**

## **TARGET PERSONA(S)**

| Persona                                                                                                                                                                                            | Mindset                                                                                                                                                                                                              |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **The Curious Student** -- College student with minimal investment knowledge, possibly holding a small portfolio through a robo-advisor or paper trading account                                   | "I want to understand what's happening in the markets and why, without needing a finance degree to parse the information. I need a single place that explains things in plain language instead of 20 open tabs."     |
| **The Self-Directed Casual Investor** -- Working professional managing their own brokerage account (10-30 holdings), reads financial news but lacks tools to synthesize it against their portfolio | "I check my portfolio daily but I'm connecting dots manually -- reading news here, checking prices there, guessing at correlations. I want a unified view that tells me what matters specifically to *my* holdings." |
| **The Quantitative Enthusiast** -- Technically literate investor (engineer, data scientist) who wants statistical analysis on their portfolio but doesn't want to build the tooling                | "I want Sharpe ratios, correlation matrices, and sector exposure breakdowns alongside the news -- not instead of it. Give me the data and the charts, let me draw my own conclusions."                               |

## **CUSTOMER PROBLEM & HYPOTHESES**

**I am an** investor **trying to** understand how market conditions affect my holdings and make informed decisions...

| **Problem (But...)**                                                                                                | **Why (Because...)**                                                                                                                                               | **Hypothesis**                                                                                                                                                                                                           |
| :------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| New investors are overwhelmed by the volume of metrics, terminology, and tools required to evaluate their portfolio | The learning curve for concepts like beta, Sharpe ratio, sector correlation, and sentiment scoring is steep, and most platforms assume you already understand them | If we pair quantitative breakdowns and modeling with plain-language analysis that explains what the numbers mean, new investors will engage with metrics they would otherwise ignore                                     |
| Casual investors lack access to the kind of multi-factor analysis that institutional tools provide                  | Institutional-grade platforms (Bloomberg, Refinitiv) are prohibitively expensive and complex for non-professionals                                                 | If we surface institutional-quality analysis (correlation matrices, sector exposure, sentiment scoring) in an accessible format, casual investors will make more informed decisions without needing professional tooling |

### **Current State <> Target State**

**From:** New investors are locked out by jargon and complexity. Experienced casual investors manually check 3-5 separate tools and mentally synthesize across them. Neither group has access to analysis tools that can break help interpret investments from multiple perspectives.

**To:** A single report synthesizes portfolio analysis, news sentiment, quantitative modeling, and alternative asset data -- with plain-language explanations that make the analysis accessible regardless of experience level.

## **FUNCTIONAL REQUIREMENTS**

**V0 -- Basic Infrastructure**: Mock data, template-based report, no LLM, no external APIs.
**V1 -- Working Implementation**: Live data, LLM synthesis, additional agents, interactive features.
**V2 -- MVP**: Multi-user platform, brokerage integrations, personalization, and subscription model.

| Scope                          | Priority | Requirements                                                                                                                                                                                                                                                      |
| :----------------------------- | :------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Portfolio Agent (V0)           | P0       | Agent loads a hardcoded mock portfolio (10-15 holdings across sectors). Computes sector allocation breakdown, diversification index, and portfolio beta. Returns structured data to orchestrator.                                                                 |
| Modeling Agent (V0)            | P0       | Agent uses mock historical price data. Generates charts (sector performance, correlation matrix, volatility) via matplotlib, returned as base64-encoded PNGs. Computes Sharpe ratio and volatility metrics. Returns charts and metrics to orchestrator.           |
| Orchestrator (V0)              | P0       | Collects outputs from Portfolio and Modeling agents. Populates a predefined report template with agent data -- portfolio metrics in their section, charts inline, risk metrics summarized. Outputs a complete markdown report. No LLM synthesis in V0.            |
| Report Display (V0)            | P0       | Frontend renders the orchestrator's markdown report with inline chart images. Single "Generate Report" button triggers the pipeline.                                                                                                                              |
| Frontend Shell (V0)            | P0       | Vite + React app with a single page. Initial state displays an agent graph showing all connected agents with their purposes labeled beneath each node. "Generate Report" button triggers the pipeline -- graph view transitions to the report view on completion. |
| News Agent (V1)                | P1       | Fetches financial news headlines, filters for portfolio relevance, scores sentiment. Orchestrator incorporates sentiment into report narrative.                                                                                                                   |
| Alt Assets Agent (V1)          | P1       | Fetches crypto and commodity market data. Computes cross-asset correlations with portfolio holdings.                                                                                                                                                              |
| LLM Synthesis (V1)             | P1       | Orchestrator uses an LLM to synthesize agent outputs into a unified narrative rather than template population. Identifies cross-agent contradictions and patterns.                                                                                                |
| Agent Graph Visualization (V1) | P2       | Live node-per-agent graph with streaming thought feeds, animated message pulses along edges, and hover tooltips on connections.                                                                                                                                   |
| User Authentication (V2)       | P1       | Multi-user support with account creation and login. Users maintain persistent portfolios and report history.                                                                                                                                                      |
| Brokerage API Sync (V2)        | P1       | Direct API integration with brokerages (Alpaca, Schwab, Robinhood) for automatic portfolio sync.                                                                                                                                                                  |
| Personalized Insights (V2)     | P1       | Reports adapt language complexity to user-stated experience level. Beginner users receive inline explanations of metrics; advanced users get raw data and methodology notes.                                                                                      |
| Report History (V2)            | P1       | Persistent storage of generated reports. Users can compare current report against previous reports to track how sentiment, exposure, and risk metrics change over time.                                                                                           |
| Scheduled Reports (V2)         | P2       | Daily or weekly automated report generation delivered via email or in-app notification.                                                                                                                                                                           |

## **USER STORIES**

### V0

- As an investor, I want to press a single button and receive a complete portfolio report with charts and metrics so I can understand my holdings without switching between tools.

### V1

- As a new investor, I want the report to include news sentiment scored against my specific holdings so I can understand how current events affect my portfolio.
- As a casual investor, I want to see crypto and commodity data correlated with my equity holdings so I can evaluate diversification opportunities.
- As an investor, I want the report to read as a unified narrative rather than disconnected data sections so I can follow a coherent analysis without assembling the picture myself.
- As a quantitative enthusiast, I want to watch agents collaborate in real time on a visual graph so I can understand what analysis is being performed and trust the output.

### V2

- As a returning user, I want to log in and see my portfolio already loaded from my brokerage so I don't have to re-enter holdings manually.
- As a new investor, I want the report to explain metrics like Sharpe ratio and beta in plain language so I can learn while I review my portfolio.
- As an experienced investor, I want raw data and methodology notes instead of simplified explanations so I can evaluate the analysis on its own terms.
- As a casual investor, I want to compare this week's report against last week's so I can see how my risk exposure and sentiment have shifted.
- As a busy investor, I want scheduled weekly reports delivered to my email so I stay informed without remembering to check.

## **MILESTONE RELEASE SCHEDULE & SCOPE**

| **V0 -- Basic Infrastructure** Target Date: March 22, 2026                                                                                                                                                                                                           |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 3 agents (Portfolio, Modeling, Orchestrator) running with mock data. Template-based report generation. Vite + React frontend with agent graph landing page and report display. Full pipeline triggerable from a single button. No external API keys or LLM required. |

| **V1 -- Working Implementation** Target Date: March 22, 2026                                                                                                                                               |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| News and Alt Assets agents added with live API data (Finnhub, CoinGecko). LLM-powered orchestrator synthesis replaces template. Agent graph visualization with streaming thought feeds and animated edges. |

| **V2 -- MVP** Target Date: April 5, 2026                                                                                                                                                                                                                                                   |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| User authentication and persistent accounts. Brokerage API integrations (Alpaca, Schwab, Robinhood) for automatic portfolio sync. Reports adapt language to user experience level. Report history with comparison over time. Scheduled report generation via email or in-app notification. |

# **TEAM/DACE**

| Function   | Name             |
| :--------- | :--------------- |
| PM:        | Michael (Driver) |
| Architect: | Anant (Approver) |
| Frontend:  | Yash             |
| Backend:   | Anthony          |

# **APPENDIX**

*Note on implementation:*
When implementing this PRD with Agents, the root agent should never attempt tasks by itself, but instead always dispatch sub-agents to research first, then implementation agent to handle core implementation, the validation agents to write and run unit tests to ensure everything works correctly. This is especially true for interfaces which should be tested frequently on both sides and ensured that they match.
If an agent is attempting to one-shot this project - stick with the V0 implementation strictly, anything more is too much.

## Architecture Sketch (V0)

### Overview

Three components run in a single Python process:

1. **FastAPI server** (uvicorn, port 8000) -- serves the frontend and exposes the report endpoint
2. **uAgents Bureau** (background thread, port 8006) -- runs all agents with its own asyncio event loop
3. **Vite + React frontend** (dev server, port 5173) -- calls FastAPI, never contacts agents directly

### Endpoint

**`POST /report`** -- Triggers the orchestrator agent via the Bureau's REST interface. Returns the completed report synchronously. CORS is set to allow all origins for V0.

### Agent Flow

```
Frontend -> POST /report -> FastAPI -> Orchestrator Agent
                                           |
                            +--------------+--------------+
                            |                             |
                     Portfolio Agent               Modeling Agent
                     (mock holdings,               (mock price data,
                      sector metrics)               matplotlib charts)
                            |                             |
                            +--------------+--------------+
                                           |
                                    Orchestrator
                                (template population)
                                           |
                                   ReportResponse
                                           |
                                    FastAPI -> Frontend
```

The orchestrator dispatches to Portfolio and Modeling agents concurrently, collects their responses, populates a markdown template, and returns the result.

### Response Model

```
ReportResponse {
    markdown: string       -- Complete report as markdown.
                              Chart locations marked with [chart:<id>] placeholders.
    charts: ChartOutput[]  -- Array of chart objects referenced by the markdown.
}

ChartOutput {
    chart_id: string       -- 8-character hex identifier (e.g. "a1b2c3d4")
    chart_type: string     -- "sector_performance" | "correlation_matrix" | "volatility"
    title: string          -- Display title (e.g. "Sector Allocation Breakdown")
    image_base64: string   -- Base64-encoded PNG, no data URI prefix
    summary: string        -- One-line description of what the chart shows
}
```

### Chart Resolution

The frontend resolves chart placeholders before rendering:

`[chart:a1b2c3d4]` becomes `![Sector Allocation Breakdown](data:image/png;base64,<image_base64>)`

This means:
- Charts are generated as **PNG via matplotlib**, encoded as **base64 strings**
- The orchestrator's markdown template references charts by ID, not inline data
- The frontend prepends the `data:image/png;base64,` URI prefix at render time

## V0 Implementation Blueprint

This section contains everything needed to implement V0 from scratch. V0 uses **mock data only**, **no LLM**, **no external API keys**, and **template-based report generation**.

### File Structure

```
project-root/
  pyproject.toml
  agents/
    __init__.py
    main.py                  # Entry point: uvicorn + bureau startup
    bureau.py                # Bureau thread launcher
    ports.py                 # Centralized port constants
    orchestrator.py          # Orchestrator agent + template report builder
    portfolio_agent.py       # Portfolio analysis agent
    modeling_agent.py        # Chart generation agent
    modeling_charts.py       # matplotlib chart renderers + fig_to_base64_png
    bridge/
      __init__.py
      app.py                 # FastAPI app, CORS, /report and /events endpoints
      events.py              # Cross-thread SSE push (Bureau loop -> FastAPI loop)
    data/
      __init__.py
      portfolio.py           # MOCK_PORTFOLIO list + EQUITY_TICKERS
    mocks/
      __init__.py
      portfolio.py           # mock_portfolio_response() -> PortfolioResponse
      modeling.py            # mock_model_response() -> ModelResponse
    models/
      __init__.py
      events.py              # SSEEvent envelope + EventType enum + payload models
      portfolio.py           # AnalyzePortfolio, PortfolioResponse (uagents.Model)
      modeling.py            # RunModel, ChartOutput, ModelResponse (uagents.Model)
      report.py              # ReportRequest (uagents.Model)
  frontend/
    package.json
    vite.config.ts
    index.html
    .env                     # VITE_SSE_URL, VITE_API_URL
    src/
      main.tsx
      App.tsx                # Router + SwarmProvider
      index.css              # CSS variables design system, no Tailwind
      schemas/
        events.ts            # Zod schemas mirroring backend SSEEvent + flat internal types
      services/
        sse.ts               # EventSource -> Zod parse -> dispatch to reducer
      context/
        SwarmContext.tsx      # React Context + useReducer + event buffering (500ms drain)
      components/
        report/
          AgentGraph.tsx      # SVG agent visualization with animated connections
          ReportView.tsx      # react-markdown renderer with chart placeholder resolution
        layout/
          AppShell.tsx        # Sidebar + TopNav + Outlet shell
      pages/
        DailyReport.tsx       # Main page: agent graph + report view
```

### V0 Dependencies

```toml
[project]
requires-python = ">=3.11,<3.14"
dependencies = [
    "uagents==0.24.0",
    "fastapi>=0.115.0",
    "uvicorn>=0.30.0",
    "sse-starlette==3.3.3",
    "python-dotenv==1.*",
    "httpx==0.27.*",
    "numpy>=1.26.0",
    "matplotlib>=3.9.0",
    "pytest",
    "pytest-asyncio",
]
```

Frontend: React 19, React Router DOM 7, Vite 8, TypeScript 5.9, zod 4, react-markdown 10 + remark-gfm 4, lucide-react (icons).

### Dual Event Loop Architecture

This is the hardest part to get right. Two async event loops run in separate threads:

```
Main Thread                          Bureau Thread
-----------                          -------------
uvicorn (FastAPI)                    uAgents Bureau
port 8000                            port 8006
asyncio event loop A                 asyncio event loop B
  |                                    |
  |<--- call_soon_threadsafe() --------|  (SSE events)
  |                                    |
  |---- httpx POST to Bureau --------->|  (trigger report)
```

**Startup sequence** (`agents/main.py`):
1. `dotenv.load_dotenv()` runs first (top of file, before any other imports)
2. FastAPI app starts via `uvicorn.run(app, host="0.0.0.0", port=8000)`
3. FastAPI `@app.on_event("startup")` captures `asyncio.get_running_loop()` as `fastapi_loop`
4. `launch_bureau()` creates a daemon thread that:
   - Creates a new event loop (`asyncio.new_event_loop()`)
   - Instantiates `Bureau(loop=bureau_loop, port=8006)`
   - Adds all agents to Bureau
   - Injects `fastapi_loop` and `event_queue` refs into `bridge.events` module globals
   - Runs `bureau_loop.run_until_complete(bureau.run_async())`

**Cross-loop SSE push** (`agents/bridge/events.py`):
```python
# Module-level refs, set by bureau launcher at startup
_fastapi_loop: asyncio.AbstractEventLoop | None = None
_event_queue: asyncio.Queue | None = None

def push_sse_event(event: SSEEvent) -> None:
    if _fastapi_loop is None or _event_queue is None:
        return
    _fastapi_loop.call_soon_threadsafe(_event_queue.put_nowait, event.model_dump())
```

Agents call `push_sse_event()` from the Bureau thread. The event lands in the FastAPI thread's queue via `call_soon_threadsafe()`. The `/events` SSE endpoint drains this queue.

### Port Configuration

```python
FASTAPI_PORT    = 8000  # HTTP bridge (uvicorn)
PORTFOLIO_PORT  = 8001  # Portfolio agent
MODELING_PORT   = 8003  # Modeling agent
ORCHESTRATOR_PORT = 8005  # Orchestrator agent
BUREAU_PORT     = 8006  # Bureau ASGI server (inter-agent routing)
```

Each agent needs a unique port for the Bureau's internal ASGI routing. Ports are centralized in `agents/ports.py`.

### Agent Creation Pattern

All agents use the uAgents framework. Each agent is created at module level with a deterministic seed:

```python
from uagents import Agent
agent = Agent(name="portfolio", seed="portfolio-agent-seed-Wealth Council", port=PORTFOLIO_PORT)
```

The `seed` determines the agent's address (deterministic). The orchestrator imports other agent modules and reads their `.address` property to know where to send messages:

```python
from agents.portfolio_agent import portfolio_agent
PORTFOLIO_ADDR = portfolio_agent.address
```

### Message Models (uagents.Model subclasses)

All request/response models extend `uagents.Model` (which wraps Pydantic v1). Each lives in its own file under `agents/models/`.

**Portfolio:**
```python
class AnalyzePortfolio(Model):
    holdings: list[str]
    mock: bool = False

class PortfolioResponse(Model):
    sector_allocation: dict[str, float]   # {"Technology": 0.49, "Healthcare": 0.14, ...}
    top_holdings: list[dict]              # [{ticker, weight, sector}, ...]
    herfindahl_index: float               # concentration metric (sum of squared weights)
    portfolio_beta: float                 # vs SPY
    correlation_matrix: dict[str, dict[str, float]]  # 2D nested dict of pairwise correlations
```

**Modeling:**
```python
class RunModel(Model):
    holdings: list[str]
    analyses: list[str] = ["regression"]  # chart types to generate
    lookback_days: int = 365
    mock: bool = False

class ChartOutput(Model):
    chart_id: str       # 8-char hex from uuid4().hex[:8]
    chart_type: str     # "sector_performance" | "correlation_matrix" | "volatility_cone" | "regression" | "price_history"
    title: str
    image_base64: str   # base64-encoded PNG, no data URI prefix
    summary: str        # one-line description

class ModelResponse(Model):
    holdings_analyzed: list[str]
    sharpe_ratio: float
    volatility: float       # annualized
    trend_slope: float
    charts: list[ChartOutput]
    metrics: dict[str, float]  # {r_squared, max_drawdown, beta}
```

**Report (Bridge -> Orchestrator):**
```python
class ReportRequest(Model):
    holdings: list[str]
    mock: bool = False
    knowledge_level: int = 2  # unused in V0 template mode
```

**Important:** `ChartOutput.chart_id` uses `pydantic.v1.Field(default_factory=...)` because uagents wraps Pydantic v1, not v2.

### Agent Handler Pattern

Agents register handlers with `@agent.on_message(model=RequestType, replies={ResponseType})` and respond with `await ctx.send(sender, response)`:

```python
@portfolio_agent.on_message(model=AnalyzePortfolio, replies={PortfolioResponse})
async def handle(ctx: Context, sender: str, msg: AnalyzePortfolio) -> None:
    push_sse_event(SSEEvent.agent_status("portfolio", AgentStatus.WORKING))
    push_sse_event(SSEEvent.agent_thought("portfolio", "Analyzing holdings..."))
    # ... compute or use mock ...
    push_sse_event(SSEEvent.agent_status("portfolio", AgentStatus.DONE))
    await ctx.send(sender, response)
```

Every handler follows this pattern: emit SSE status WORKING, emit thoughts during processing, emit SSE status DONE, then send response.

### Orchestrator (V0 Template Mode)

The orchestrator registers a REST endpoint (not a message handler) via `@orchestrator.on_rest_post("/report", ReportRequest, ReportResponse)`:

```python
@orchestrator.on_rest_post("/report", ReportRequest, ReportResponse)
async def handle_report(ctx: Context, req: ReportRequest) -> ReportResponse:
```

**V0 pipeline:**
1. Fan-out to Portfolio and Modeling agents concurrently using `asyncio.gather` with `ctx.send_and_receive(addr, msg, response_type=Type, timeout=30)`
2. Extract responses (handle tuple returns: `result[0]` is the message), fall back to mocks on failure
3. Populate a **markdown template** with agent data (no LLM)
4. Push `SSEEvent.report_complete(markdown=..., charts=[...])` via SSE
5. Return `ReportResponse(status="complete")`

**Template population** (V0 -- no LLM): Build markdown string directly from portfolio metrics, modeling metrics, and chart references. Embed `[chart:<chart_id>]` placeholders at appropriate positions. The template should include sections for portfolio overview (sector allocation, beta, HHI), risk metrics (Sharpe, volatility, max drawdown), and charts.

**`send_and_receive` return value:** Returns a tuple `(message, metadata)`. Always extract with `result[0]` or a helper:
```python
def extract_msg(result):
    if isinstance(result, Exception): return result
    if isinstance(result, tuple): return result[0]
    return result
```

### Mock Data

**Portfolio** (`agents/data/portfolio.py`):
```python
MOCK_PORTFOLIO = [
    {"ticker": "AAPL", "weight": 0.18, "sector": "Technology", "shares": 150},
    {"ticker": "MSFT", "weight": 0.14, "sector": "Technology", "shares": 80},
    {"ticker": "NVDA", "weight": 0.10, "sector": "Technology", "shares": 200},
    {"ticker": "META", "weight": 0.07, "sector": "Technology", "shares": 120},
    {"ticker": "UNH",  "weight": 0.09, "sector": "Healthcare", "shares": 45},
    {"ticker": "JNJ",  "weight": 0.05, "sector": "Healthcare", "shares": 80},
    {"ticker": "JPM",  "weight": 0.07, "sector": "Financials", "shares": 90},
    {"ticker": "GS",   "weight": 0.04, "sector": "Financials", "shares": 30},
    {"ticker": "XOM",  "weight": 0.06, "sector": "Energy", "shares": 110},
    {"ticker": "TSLA", "weight": 0.06, "sector": "Consumer Discretionary", "shares": 95},
]
EQUITY_TICKERS = [h["ticker"] for h in MOCK_PORTFOLIO]
```

Mock response functions return hardcoded `PortfolioResponse` / `ModelResponse` objects with realistic values. The mock portfolio response includes a hand-coded 10x10 correlation matrix with sector clustering (tech tickers correlate 0.7-0.8 with each other, cross-sector correlations are lower).

### Chart Generation

Charts are rendered with matplotlib using the `Agg` backend (headless). Each chart renderer:
1. Creates a `matplotlib.figure.Figure`
2. Draws the chart (see types below)
3. Calls `fig_to_base64_png(fig)` which saves to `BytesIO`, base64-encodes, and closes the figure
4. Returns a `ChartOutput` with the base64 string

```python
def fig_to_base64_png(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")
```

**V0 chart types** (all use synthetic/mock data):
- `sector_performance`: Bar chart of returns per holding. Green/red bars for gains/losses.
- `correlation_matrix`: Heatmap (RdBu_r colormap) of pairwise correlations from mock data.
- `volatility_cone`: Historical vol percentiles by tenor with filled bands (10-90th, 25-75th percentile).

For V0, generate synthetic price series (random walk with drift) rather than calling yfinance. The mock modeling response builder should produce these charts deterministically from the mock portfolio data.

### SSE Event System

**Backend envelope** (`agents/models/events.py`):
```python
class SSEEvent(BaseModel):            # Pydantic v2 (bridge-side, not uagents)
    event_id: str                     # uuid4
    timestamp: float                  # time.time()
    agent_id: str                     # "orchestrator" | "portfolio" | "modeling"
    event_type: EventType             # "agent.status" | "agent.thought" | "agent.message" | "report.complete"
    payload: dict                     # type-specific payload

class EventType(str, Enum):
    AGENT_STATUS = "agent.status"     # {status: "idle"|"working"|"done"|"error", message: str}
    AGENT_THOUGHT = "agent.thought"   # {text: str}
    AGENT_MESSAGE = "agent.message"   # {from, to, title, description, direction: "request"|"response"}
    REPORT_COMPLETE = "report.complete"  # {markdown: str, charts: [{chart_id, chart_type, title, image_base64, summary}]}
```

Factory methods on `SSEEvent` create typed events: `SSEEvent.agent_status(...)`, `SSEEvent.agent_thought(...)`, `SSEEvent.agent_message(...)`, `SSEEvent.report_complete(...)`.

**FastAPI SSE endpoint** (`GET /events`): Returns `EventSourceResponse` from `sse-starlette`. Reads from `asyncio.Queue`, yields `{"data": json.dumps(event)}`.

**Trigger endpoint** (`POST /report`): Sends an httpx POST to `http://localhost:{BUREAU_PORT}/report` with `ReportRequest` JSON. Returns immediately with `{"status": "triggered"}`. The actual report arrives via SSE.

### Frontend SSE Consumption

**Connection** (`services/sse.ts`): Uses `EventSource` to connect to `VITE_SSE_URL` (default `http://localhost:8000/events`). Parses each message with Zod `SSEWireEvent` schema, transforms the wire format to flat internal `SSEEvent` types, dispatches to the reducer.

**State management** (`context/SwarmContext.tsx`): React Context + `useReducer`. Key state shape:
```typescript
{
  agentStatuses: Record<AgentId, "idle"|"working"|"done"|"error">
  thoughts: {agent_id, text, timestamp}[]   // max 50, newest first
  agentMessages: {from, to, title, description, direction}[]
  chartMap: Record<string, ChartOutput>     // keyed by chart_id
  executiveSummary: string | null           // final markdown
  connected: boolean
  reportTriggered: boolean
}
```

Events are buffered in a ref and drained every 500ms to prevent rapid re-renders during burst SSE events.

**Report trigger flow:**
1. User clicks "Generate Report"
2. Frontend dispatches `TRIGGER_REPORT` action (resets state)
3. Frontend sends `POST /report` to FastAPI
4. SSE events stream in: agent statuses, thoughts, messages (animate the agent graph)
5. `report.complete` event arrives with `{markdown, charts[]}`
6. Reducer populates `chartMap` (keyed by `chart_id`) and `executiveSummary` (the markdown)
7. `ReportView` resolves `[chart:id]` placeholders to `data:image/png;base64,...` URLs and renders with `react-markdown`

### Chart Placeholder Resolution (Frontend)

```typescript
function resolveChartRefs(markdown: string, chartMap: Record<string, ChartOutput>): string {
    return markdown.replace(/\[chart:([a-f0-9]+)\]/g, (match, id) => {
        const chart = chartMap[id];
        if (!chart) return match;
        return `![${chart.title}](data:image/png;base64,${chart.image_base64})`;
    });
}
```

`react-markdown` must be configured with a custom `urlTransform` that allows `data:` URIs (the default blocks them). Custom `img` component constrains width to ~500px.

### Agent Graph Visualization

SVG-based graph with agent cards positioned around a central orchestrator node. Key behaviors:
- Each agent card shows status badge (idle/working/done) and latest thoughts
- Connection lines between orchestrator and agents animate when the agent is in "working" state (dashed stroke animation + circle traveling along path)
- Agent messages (`SSEEvent.agent_message`) trigger visual pulse on the relevant connection
- Cards use a gentle floating CSS animation with staggered delays per agent

The graph requires 3 agents for V0: orchestrator (center), portfolio (one side), modeling (other side).

### Frontend Styling

Pure CSS with CSS variables (no Tailwind). Key design tokens:
```css
--bg-primary: #f8f9fb;   --bg-card: #ffffff;
--text-primary: #111827;  --text-secondary: #6b7280;
--accent: #2563eb;        --green: #10b981;  --red: #ef4444;  --amber: #f59e0b;
--radius-sm: 8px;         --radius-md: 12px;
--sidebar-width: 240px;   --topnav-height: 56px;
```

Layout: CSS Grid with fixed sidebar + top nav. Cards use `--bg-card` with subtle borders and shadows.

### Critical Gotchas

1. **uagents.Model uses Pydantic v1**, not v2. Use `from pydantic.v1 import Field` for `default_factory` on `ChartOutput.chart_id`. The bridge-side `SSEEvent` uses standard Pydantic v2 (`from pydantic import BaseModel`).

2. **`send_and_receive` returns a tuple**, not a bare model. Always extract with `result[0]`. Wrap in `asyncio.gather(..., return_exceptions=True)` and handle exceptions with a fallback to mock responses.

3. **`on_rest_post` is the orchestrator's entry point**, not `on_message`. The Bureau exposes the orchestrator's REST endpoint at `http://localhost:{BUREAU_PORT}/report`. FastAPI bridges to it via httpx.

4. **The SSE queue is an `asyncio.Queue`** shared between threads. Only use `call_soon_threadsafe(queue.put_nowait, ...)` from the Bureau thread. Never await across threads.

5. **matplotlib must use the `Agg` backend** (`matplotlib.use("Agg")`) since there is no display. Set this before importing pyplot.

6. **Frontend `EventSource` auto-reconnects** but the `event_queue` is not persistent -- reconnecting clients miss events that occurred during disconnection. For V0 this is acceptable.

7. **CORS must allow all origins** for V0 local development (`allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]`).

8. **Load dotenv at the very top of `main.py`** before any other imports. Some modules read env vars at import time (e.g., `MOCK_DATA`).