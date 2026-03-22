# Phase 2: Agent Pipeline - Research

**Researched:** 2026-03-21
**Domain:** Financial multi-agent pipeline — Portfolio metrics, FinBERT sentiment, matplotlib charting, CoinGecko alt assets, GPT-4o mini narrative synthesis
**Confidence:** HIGH for integration patterns (grounded in Phase 1 code); MEDIUM for FinBERT loading specifics

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Report Narrative**
- Professional analyst tone — reads like a morning brief from a financial analyst
- Thematic sections organized by investment theme (e.g., "Tech Sector Outlook", "Risk Assessment", "Market Sentiment"), NOT sectioned per-agent
- Chart/visualization-heavy — the report should lean heavily on embedded visuals
- Full report length: 2-3 screens of scrollable content
- Cross-agent contradictions flagged explicitly as dedicated insights

**Portfolio Agent**
- Mock portfolio: 10-15 stocks across 5-6 sectors, curated to surface interesting demo stories (tech-heavy concentration, bearish news + strong momentum tensions)
- Includes 1-2 crypto positions (BTC, ETH) for cross-agent interplay with Alt Assets agent
- Computes: sector allocation breakdown, Herfindahl diversification index, portfolio beta, correlation matrix
- Returns raw structured data (numbers, metrics, structured objects) — no pre-formatted text

**News Agent**
- Fetches Finnhub headlines, filters for portfolio relevance, scores sentiment with FinBERT (not LLM)
- Computes aggregate sentiment metrics per holding/sector
- Returns structured sentiment data + raw headlines

**Modeling Agent (Mock Only)**
- Teammate handles real implementation — stays mock for Phase 2
- Mock returns: structured metrics (Sharpe ratio, volatility numbers) + a static pre-generated base64 PNG chart image
- Static mock chart proves the chart embedding pipeline works end-to-end
- Must conform to the same Pydantic response contract so teammate's real agent is drop-in

**Alt Assets Agent**
- Crypto coverage: portfolio-relevant coins + BTC and ETH always included
- Commodities: gold and crude oil (available via Finnhub). No real estate
- Cross-asset analysis: portfolio correlations, trend direction (bullish/bearish/neutral), BTC dominance percentage

**Orchestrator**
- Fans out to all domain agents concurrently via asyncio.gather
- Uses GPT-4o mini for narrative synthesis
- Produces thematic sections from raw agent data — NOT a pass-through of agent summaries
- Identifies and flags cross-agent contradictions explicitly
- Response contract enforces summary field caps to prevent context window overflow

**Thought Feed (All Agents)**
- Key milestones only: 3-5 thoughts per agent per report run
- Include data teasers with real numbers
- Each agent has its own personality/voice
- Orchestrator emits synthesis narration during LLM step (not streaming LLM tokens)

### Claude's Discretion
- News agent filtering logic, sentiment thresholds, headline count
- Exact Pydantic field shapes for all request/response models (within the constraints above)
- Mock data realism level and specific mock portfolio holdings selection
- Error handling patterns for agent communication failures
- Static mock chart image selection for Modeling agent

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PORT-01 | Portfolio agent loads mock portfolio data (realistic holdings across sectors) | Mock portfolio design section; curated 12-holding portfolio with BTC/ETH |
| PORT-02 | Computes sector/asset allocation breakdown | numpy/pandas pattern; weight sum per sector |
| PORT-03 | Calculates diversification metrics (Herfindahl index, portfolio beta) | Herfindahl formula documented; beta via market regression |
| PORT-04 | Runs correlation matrix across holdings using numpy/pandas | pandas corr() on price history from yfinance |
| PORT-05 | Returns structured numerical output to orchestrator | Existing PortfolioResponse contract; needs correlation_matrix field added |
| NEWS-01 | Fetches financial news headlines from Finnhub API | Finnhub /news endpoint documented with rate-limit pattern |
| NEWS-02 | Filters headlines for relevance to portfolio holdings | Ticker mention matching strategy documented |
| NEWS-03 | Scores sentiment per article using FinBERT | transformers pipeline("text-classification", "ProsusAI/finbert") pattern |
| NEWS-04 | Computes aggregate sentiment metrics per holding/sector | weighted mean of per-article scores grouped by ticker |
| NEWS-05 | Returns structured sentiment data + raw headlines | NewsResponse contract sufficient; no model changes needed |
| MODL-01 | Retrieves historical price data via yfinance | Mock only in Phase 2; yfinance pattern documented for teammate |
| MODL-02 | Runs specifiable analyses via chart registry | Mock only; registry pattern documented |
| MODL-03 | Generates charts as ChartOutput with type, title, image_base64, summary | Static pre-generated PNG base64 embeds proves pipeline; ChartOutput contract exists |
| MODL-04 | Computes risk metrics (Sharpe ratio, volatility) plus extensible metrics dict | Mock values; ModelResponse contract has sharpe_ratio, volatility, metrics fields |
| MODL-05 | Returns structured metrics + multiple chart outputs | ModelResponse.charts: list[ChartOutput] already defined |
| ALT-01 | Fetches current crypto prices and trends from CoinGecko | CoinGecko /simple/price endpoint; trend from 7d price change |
| ALT-02 | Retrieves commodity market data | Finnhub /quote for gold (GC1!) and crude oil (CL1!) futures |
| ALT-03 | Computes cross-asset correlations with portfolio holdings | Correlation between alt asset returns and portfolio equity returns via numpy |
| ALT-04 | Returns structured market data + correlations | AlternativesResponse needs expansion: trend_signals, btc_dominance, commodities |
| ORCH-01 | Dispatches to appropriate domain agents based on report request | asyncio.gather over ctx.send_and_receive to all 4 domain agents |
| ORCH-02 | Receives structured data from all domain agents | Collect PortfolioResponse, NewsResponse, ModelResponse, AlternativesResponse |
| ORCH-03 | Uses LLM to synthesize agent outputs into unified narrative report | GPT-4o mini via openai client; thematic prompt documented |
| ORCH-04 | Identifies cross-agent contradictions and patterns | Contradiction detection via structured comparison before LLM call |
| ORCH-05 | Generates executive summary with key actionable insights | Summary section in LLM prompt template; narrative wraps with exec summary |
</phase_requirements>

---

## Summary

Phase 2 replaces the stub `else: response = mock_*()` branches in all four domain agents and wires the orchestrator to fan out via `asyncio.gather`. The infrastructure (Bureau thread, cross-loop queue, SSE bridge, Pydantic contracts) is fully in place from Phase 1. Phase 2 is purely domain logic + orchestration glue.

Three agents implement real logic: Portfolio (numpy/pandas computation), News (Finnhub API + FinBERT), and Alt Assets (CoinGecko + Finnhub commodities). The Modeling agent remains mock-only with a static pre-generated base64 PNG to prove the chart embedding pipeline works end-to-end. The orchestrator is fully wired: it sends typed requests concurrently to all four agents, collects responses, detects cross-agent contradictions, and calls GPT-4o mini to produce a thematic narrative markdown document.

**Primary recommendation:** Implement the orchestrator fan-out first with mock data forced on all agents, verify the full report pipeline end-to-end with curl, then incrementally replace each agent's mock branch with real logic one at a time. This keeps the curl verification working throughout development.

---

## Model Contract Gaps (Critical for Planning)

The Phase 1 Pydantic models are the foundation. Phase 2 requires additions to two response models before any agent logic can be written. The planner must treat these model changes as Wave 0 tasks that all agent tasks depend on.

### PortfolioResponse — needs one new field

Current Phase 1 contract:
```python
class PortfolioResponse(Model):
    sector_allocation: dict[str, float]
    top_holdings: list[dict]
    herfindahl_index: float
    portfolio_beta: float
```

Phase 2 addition required (PORT-04):
```python
    correlation_matrix: dict[str, dict[str, float]]  # ticker -> ticker -> correlation coefficient
```

### AlternativesResponse — needs significant expansion

Current Phase 1 contract:
```python
class AlternativesResponse(Model):
    crypto_prices: dict[str, float]
    cross_correlations: dict[str, float]
```

Phase 2 contract required (ALT-01 through ALT-04):
```python
class AlternativesResponse(Model):
    crypto_prices: dict[str, float]           # ticker -> USD price
    cross_correlations: dict[str, float]       # asset -> correlation with portfolio
    trend_signals: dict[str, str]              # asset -> "bullish" | "bearish" | "neutral"
    btc_dominance: float                       # BTC market cap as % of total crypto market cap
    commodities: dict[str, float]              # "GOLD" -> price, "OIL" -> price
```

### AnalyzeAlternatives request — no changes needed

The existing `AnalyzeAlternatives(mock: bool = False)` is sufficient. The agent always fetches BTC/ETH plus any portfolio crypto positions. No additional fields required.

### ReportRequest model — new, needed for bridge /report endpoint

The orchestrator needs a typed request it can receive from the bridge:
```python
class ReportRequest(Model):
    """Bridge -> Orchestrator. Triggers full report pipeline."""
    holdings: list[str]  # ticker list from mock portfolio
    mock: bool = False
```

The bridge's `/report` endpoint will instantiate this and `ctx.send()` to the orchestrator's address.

---

## Standard Stack

### Core (all already installed from Phase 1)

| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| uagents | 0.24.0 | Agent runtime, ctx.send_and_receive | Installed |
| fastapi | >=0.115.0 | Bridge HTTP/SSE | Installed |
| httpx | 0.27.x | Async HTTP calls to Finnhub/CoinGecko | Installed |
| openai | 1.x | GPT-4o mini synthesis call | NOT YET installed |
| python-dotenv | 1.x | API key management | Installed |

### Phase 2 New Dependencies

| Library | Version | Purpose | Install Command |
|---------|---------|---------|----------------|
| openai | >=1.0.0 | Orchestrator GPT-4o mini call | `uv pip install openai` |
| transformers | >=4.40.0 | FinBERT model loading | `uv pip install transformers` |
| torch | >=2.0.0 | FinBERT inference backend | `uv pip install torch` (CPU-only acceptable) |
| pandas | >=2.0.0 | Correlation matrix, sentiment groupby | `uv pip install pandas` |
| numpy | >=1.26.0 | Herfindahl, beta, numerical ops | `uv pip install numpy` |
| yfinance | >=0.2.38 | Historical prices for correlation matrix | `uv pip install yfinance` |
| matplotlib | >=3.9.0 | Static mock chart generation (Modeling agent) | `uv pip install matplotlib` |

**Full install command:**
```bash
cd /Users/big_m/Documents/Code/produhacks/agents
uv pip install openai "transformers>=4.40" torch pandas numpy yfinance matplotlib
```

**pyproject.toml additions** (add to `dependencies`):
```toml
"openai>=1.0.0",
"transformers>=4.40.0",
"torch>=2.0.0",
"pandas>=2.0.0",
"numpy>=1.26.0",
"yfinance>=0.2.38",
"matplotlib>=3.9.0",
```

**Note on torch size:** CPU-only torch is approximately 700MB. For hackathon: acceptable. FinBERT model download (~500MB) happens on first load — pre-download before demo with `python -c "from transformers import pipeline; pipeline('text-classification', model='ProsusAI/finbert')"`.

---

## Architecture Patterns

### Pattern 1: Orchestrator Fan-Out with asyncio.gather and ctx.send_and_receive

The orchestrator's Phase 1 stub had no handlers. Phase 2 wires a `ReportRequest` handler that fans out to all four domain agents concurrently.

**Key constraint from uAgents docs:** `ctx.send_and_receive` is available in uAgents 0.24.0 and suspends the coroutine until the reply arrives. Using `asyncio.gather` over multiple `ctx.send_and_receive` calls achieves true concurrent fan-out.

```python
# agents/orchestrator.py
from uagents import Agent, Context
import asyncio
from agents.models.requests import (
    ReportRequest, AnalyzePortfolio, FetchNews, RunModel, AnalyzeAlternatives
)
from agents.models.responses import (
    PortfolioResponse, NewsResponse, ModelResponse, AlternativesResponse
)

@orchestrator.on_message(model=ReportRequest, replies={ReportResponse})
async def handle_report_request(ctx: Context, sender: str, msg: ReportRequest):
    push_sse_event(SSEEvent.agent_status("orchestrator", AgentStatus.WORKING))
    push_sse_event(SSEEvent.agent_thought("orchestrator", "Dispatching to 4 domain agents concurrently..."))

    portfolio_result, news_result, modeling_result, alt_result = await asyncio.gather(
        ctx.send_and_receive(PORTFOLIO_ADDR, AnalyzePortfolio(holdings=msg.holdings, mock=msg.mock)),
        ctx.send_and_receive(NEWS_ADDR, FetchNews(tickers=msg.holdings, mock=msg.mock)),
        ctx.send_and_receive(MODELING_ADDR, RunModel(holdings=msg.holdings, mock=msg.mock)),
        ctx.send_and_receive(ALT_ADDR, AnalyzeAlternatives(mock=msg.mock)),
        return_exceptions=True,
    )
    # return_exceptions=True prevents one timeout from aborting the gather
```

**Agent addresses:** Deterministic from seeds defined in Phase 1. Import address from each agent module:
```python
from agents.portfolio_agent import portfolio_agent
PORTFOLIO_ADDR = portfolio_agent.address  # "agent1q..."
```

### Pattern 2: Bridge /report Endpoint Triggering the Orchestrator

The `/trigger` endpoint in Phase 1 pushed events directly. Phase 2 needs a `/report` endpoint that sends a `ReportRequest` to the orchestrator agent and waits for the `ReportResponse`.

The challenge: the orchestrator is in the Bureau thread; the bridge is in the FastAPI thread. The bridge cannot use `ctx.send_and_receive` directly (it is not an agent). The pattern is:

**Option A (recommended):** Add a thin bridge agent to the Bureau that the FastAPI bridge can address. The bridge sends to `BRIDGE_AGENT_ADDR`, which relays to orchestrator and captures the response, pushing `report.complete` SSE event.

**Option B (simpler for Phase 2):** The bridge endpoint sends an HTTP request to the orchestrator's REST endpoint (`http://localhost:8005/trigger`) and returns immediately. The orchestrator's `@on_rest_post` handler does the fan-out and pushes `report.complete` via SSE when done. The curl test reads from `/events` SSE for completion.

**Decision:** Use Option B for Phase 2. The `/report` POST to bridge triggers the orchestrator via its local REST endpoint, returns `{"status": "triggered"}` immediately, and the result arrives via SSE. This matches the curl verification pattern: `curl -X POST /report` then read `/events` for `report.complete`.

```python
# bridge/app.py — new /report endpoint
@app.post("/report")
async def trigger_report():
    async with httpx.AsyncClient() as client:
        await client.post("http://localhost:8005/submit/report",
                          json={"holdings": MOCK_PORTFOLIO_TICKERS, "mock": False})
    return {"status": "triggered"}
```

The orchestrator exposes `@orchestrator.on_rest_post("/report", ReportRequest, dict)` handler that runs the full pipeline and pushes `report.complete` SSE event with the markdown.

**Important:** Per uAgents 0.24.0 docs and Phase 1 research, `on_rest_post` must be on the agent directly (not a Protocol). The orchestrator is on port 8005. The handler path is `/submit/report` (the uAgents REST framework prepends `/submit/`).

### Pattern 3: FinBERT Sentiment Scoring

FinBERT (`ProsusAI/finbert`) is a BERT model fine-tuned on financial text. It classifies text as positive/negative/neutral with confidence scores.

**Loading pattern (load once at module level, not per-request):**
```python
# agents/news_agent.py
from transformers import pipeline

# Load at import time — expensive (~3s), acceptable at startup
_finbert = pipeline(
    "text-classification",
    model="ProsusAI/finbert",
    return_all_scores=True,
)

def score_sentiment(text: str) -> float:
    """Returns float in [-1, 1]: -1 = very negative, +1 = very positive."""
    results = _finbert(text[:512])[0]  # truncate to BERT's max input
    scores = {r["label"]: r["score"] for r in results}
    return scores.get("positive", 0.0) - scores.get("negative", 0.0)
```

**Filtering strategy (Claude's discretion):** Filter headlines where the ticker symbol appears in the headline text OR where Finnhub's `related` field lists the ticker. Score only the `headline` field (not full article body — Finnhub free tier returns headlines only, not body text). Discard headlines with absolute sentiment score < 0.1 (near-neutral, not interesting for the report). Cap at 5 headlines per ticker.

**Aggregate sentiment per ticker:** Mean of per-headline scores for that ticker's filtered headlines. Range [-1, 1].

**FinBERT label mapping:**
```
"positive" → +score
"negative" → -score
"neutral"  → 0 (score contributes 0 to net sentiment)
```

### Pattern 4: Herfindahl-Hirschman Index

The Herfindahl index (HHI) measures portfolio concentration. Higher = more concentrated. Range [0, 1].

```python
import numpy as np

def herfindahl_index(weights: list[float]) -> float:
    """weights: list of portfolio weight fractions summing to 1.0"""
    return float(np.sum(np.square(weights)))

# Example: equal-weight 10-stock portfolio -> HHI = 10 * (0.1^2) = 0.10
# Example: 100% single stock -> HHI = 1.0
```

### Pattern 5: Portfolio Beta via Market Regression

Beta = covariance(portfolio returns, market returns) / variance(market returns).

```python
import numpy as np
import pandas as pd
import yfinance as yf

def compute_portfolio_beta(holdings: list[str], weights: list[float],
                           lookback_days: int = 365) -> float:
    """Market proxy: SPY ETF."""
    tickers = holdings + ["SPY"]
    data = yf.download(tickers, period=f"{lookback_days}d", auto_adjust=True)["Close"]
    returns = data.pct_change().dropna()

    # Weighted portfolio returns
    port_returns = (returns[holdings] * weights).sum(axis=1)
    market_returns = returns["SPY"]

    cov = np.cov(port_returns, market_returns)
    return float(cov[0, 1] / cov[1, 1])
```

### Pattern 6: Correlation Matrix

```python
def compute_correlation_matrix(holdings: list[str],
                                lookback_days: int = 90) -> dict[str, dict[str, float]]:
    data = yf.download(holdings, period=f"{lookback_days}d", auto_adjust=True)["Close"]
    corr = data.pct_change().dropna().corr()
    return {
        ticker: {other: round(float(corr.loc[ticker, other]), 4) for other in holdings}
        for ticker in holdings
    }
```

**Note:** yfinance for correlation matrix is acceptable — it's historical data (no rate limit concern), called once per report, and the Modeling agent would use the same data anyway. Use 90-day lookback for correlations (enough signal, less noise than 365 days).

### Pattern 7: CoinGecko Crypto Price + Trend

```python
import httpx

COINGECKO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
    "BNB": "binancecoin", "AVAX": "avalanche-2"
}

async def fetch_crypto_data(coins: list[str]) -> dict:
    """Returns prices and 7d price change for trend signal."""
    ids = ",".join(COINGECKO_IDS[c] for c in coins if c in COINGECKO_IDS)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_7d_change=true"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10.0)
        resp.raise_for_status()
    return resp.json()

def trend_signal(price_change_7d: float) -> str:
    if price_change_7d > 3.0:
        return "bullish"
    elif price_change_7d < -3.0:
        return "bearish"
    return "neutral"
```

**BTC Dominance:** CoinGecko global endpoint:
```python
url = "https://api.coingecko.com/api/v3/global"
# Response: data["data"]["btc_dominance"] -> float (e.g., 52.3)
```

**CoinGecko rate limit:** 30 req/min on demo plan. Two calls per report (prices + global) — well within limit. No auth header needed for demo plan; add `x-cg-demo-api-key: {key}` header if registered.

### Pattern 8: Finnhub Commodities

Finnhub `/quote` endpoint works for commodity futures:
- Gold: symbol `GC1!` (front-month gold futures)
- Crude Oil: symbol `CL1!` (front-month WTI crude)

```python
async def fetch_commodity_price(symbol: str, api_key: str) -> float:
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10.0)
        data = resp.json()
    return float(data["c"])  # "c" = current price
```

**Confidence: MEDIUM** — Finnhub commodity symbols `GC1!` and `CL1!` are standard futures identifiers but verify against Finnhub's supported symbols list before implementing.

### Pattern 9: Static Mock Chart for Modeling Agent

The Modeling agent in Phase 2 must return a `ModelResponse` with a non-empty `image_base64` in at least one `ChartOutput`. Generate a static PNG at development time and embed it:

```python
# scripts/generate_mock_chart.py — run once to create the fixture
import matplotlib.pyplot as plt
import base64
import io

def generate_mock_price_chart() -> str:
    fig, ax = plt.subplots(figsize=(8, 4))
    # Simple upward-trending line to represent portfolio performance
    import numpy as np
    x = np.linspace(0, 365, 365)
    y = 100 * np.exp(0.0003 * x + 0.02 * np.random.randn(365).cumsum())
    ax.plot(x, y, color="#2563EB", linewidth=2)
    ax.set_title("Portfolio Price History (1Y)", fontweight="bold")
    ax.set_xlabel("Days")
    ax.set_ylabel("Portfolio Value (indexed to 100)")
    ax.grid(True, alpha=0.3)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()
```

Store the generated base64 string as a constant in `agents/mocks/modeling.py`. The mock `ModelResponse` uses this constant for `image_base64`. This proves the full path from agent response → bridge → markdown embedding works.

**Markdown embedding pattern:**
```markdown
![Portfolio Price History](data:image/png;base64,{image_base64})
```

### Pattern 10: GPT-4o Mini Narrative Synthesis

```python
from openai import AsyncOpenAI

_openai = AsyncOpenAI()  # reads OPENAI_API_KEY from env

async def synthesize_report(
    portfolio: PortfolioResponse,
    news: NewsResponse,
    modeling: ModelResponse,
    alt: AlternativesResponse,
    contradictions: list[str],
    charts: list[ChartOutput],
) -> str:
    """Returns unified markdown report string."""
    chart_embeds = "\n".join(
        f"![{c.title}](data:image/png;base64,{c.image_base64})"
        for c in charts if c.image_base64
    )

    prompt = build_synthesis_prompt(portfolio, news, modeling, alt, contradictions, chart_embeds)

    response = await _openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,  # cap to prevent runaway cost and context issues
        temperature=0.4,  # analytical tone, low creativity
    )
    return response.choices[0].message.content
```

**Prompt template structure (Claude's discretion on exact wording, but must enforce):**
1. System instruction: "You are a professional financial analyst writing a morning brief."
2. Instruction: Organize into thematic sections by investment theme, NOT by agent.
3. Required sections: executive summary, main themes (2-3 investment-themed sections), risk assessment, market context (alt assets), notable contradictions (if any).
4. Data block: raw structured data from all agents (as JSON, not prose)
5. Chart embed instructions: include the pre-formatted markdown embed strings
6. Constraint: "Do not section by data source. Weave all data into a unified narrative."

**Context window math (important):** Each agent response serialized to JSON:
- PortfolioResponse: ~600 tokens
- NewsResponse (5 headlines, sentiment): ~800 tokens
- ModelResponse (no large base64, just metrics): ~300 tokens
- AlternativesResponse: ~400 tokens
- Contradictions list: ~200 tokens
- Prompt template: ~500 tokens
- **Total input: ~2,800 tokens** — well within GPT-4o mini's 128k context. No truncation needed for this scope.

### Pattern 11: Contradiction Detection

Before the LLM call, the orchestrator performs structured contradiction detection:

```python
def detect_contradictions(
    portfolio: PortfolioResponse,
    news: NewsResponse,
    modeling: ModelResponse,
) -> list[str]:
    contradictions = []
    for ticker, sentiment in news.aggregate_sentiment.items():
        # Bearish news but ticker is a top holding with high weight
        matching = [h for h in portfolio.top_holdings if h["ticker"] == ticker]
        if matching and sentiment < -0.3 and matching[0]["weight"] > 0.05:
            contradictions.append(
                f"{ticker}: News sentiment is bearish ({sentiment:.2f}) but it is a top holding "
                f"({matching[0]['weight']*100:.0f}% of portfolio)"
            )
    return contradictions
```

This list is passed into the synthesis prompt so GPT-4o mini can reference real detected contradictions rather than hallucinate them.

### Pattern 12: ReportResponse — new SSE event, not a uAgents message

The orchestrator does not need to return a `ReportResponse` uAgents message to the bridge. Instead:
1. Orchestrator calls `push_sse_event(SSEEvent.report_complete(markdown=report_markdown, charts=[c.model_dump() for c in charts]))`
2. The FastAPI `/report` endpoint returns `{"status": "triggered"}` immediately
3. The frontend (or curl) reads from `/events` SSE and watches for `report.complete` event

This is simpler than trying to relay a uAgents message back to the bridge process. The `report.complete` SSE event payload already has the `markdown` field per the Phase 1 `ReportCompletePayload` model.

**Curl verification pattern:**
```bash
# Terminal 1: listen for events
curl -N http://localhost:8000/events

# Terminal 2: trigger report
curl -X POST http://localhost:8000/report

# Terminal 1 will receive: data: {"event_type": "report.complete", "payload": {"markdown": "...", "charts": [...]}}
```

---

## Mock Portfolio Design

The mock portfolio is used by PortfolioAgent, NewsAgent, and the orchestrator's fan-out. It must be centrally defined (not hardcoded per agent) and curated to create compelling cross-agent stories.

**Recommended portfolio (12 holdings across 6 sectors):**

```python
MOCK_PORTFOLIO = [
    # Technology — overweight (creates concentration story)
    {"ticker": "AAPL", "weight": 0.18, "sector": "Technology", "shares": 150},
    {"ticker": "MSFT", "weight": 0.14, "sector": "Technology", "shares": 80},
    {"ticker": "NVDA", "weight": 0.10, "sector": "Technology", "shares": 200},
    {"ticker": "META", "weight": 0.07, "sector": "Technology", "shares": 120},
    # Healthcare
    {"ticker": "UNH",  "weight": 0.09, "sector": "Healthcare", "shares": 45},
    {"ticker": "JNJ",  "weight": 0.05, "sector": "Healthcare", "shares": 80},
    # Financials
    {"ticker": "JPM",  "weight": 0.07, "sector": "Financials", "shares": 90},
    {"ticker": "GS",   "weight": 0.04, "sector": "Financials", "shares": 30},
    # Energy
    {"ticker": "XOM",  "weight": 0.06, "sector": "Energy", "shares": 110},
    # Consumer Discretionary
    {"ticker": "TSLA", "weight": 0.06, "sector": "Consumer Discretionary", "shares": 95},
    # Crypto (cross-agent bridge to Alt Assets)
    {"ticker": "BTC",  "weight": 0.08, "type": "crypto"},
    {"ticker": "ETH",  "weight": 0.06, "type": "crypto"},
]
```

**Why this composition creates interesting stories:**
- Tech is 49% of portfolio — Herfindahl will show high concentration, contradiction if any tech news is bearish
- TSLA + bearish news (TSLA has frequent sentiment volatility) creates a clear news/momentum contradiction
- BTC/ETH at 14% combined creates a meaningful crypto risk section
- 6 sectors gives a clean sector allocation breakdown

**Central definition:** Store in `agents/data/portfolio.py` as a module-level constant imported by Portfolio, News, and Orchestrator agents. The `AnalyzePortfolio` request message's `holdings` field is derived from this: `[h["ticker"] for h in MOCK_PORTFOLIO if h.get("type") != "crypto"]`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Sentiment scoring | Custom lexicon-based scorer | FinBERT via transformers | Domain-specific accuracy; BERT handles context, negation, financial jargon |
| Correlation matrix | Nested loop with manual covariance | pandas `DataFrame.corr()` | Numerically stable, tested, one line |
| Portfolio beta | Custom OLS regression | numpy `np.cov()` | Direct formula; no regression library needed for a single factor |
| HTTP retries | Custom retry loop | httpx with `limits=` and timeout | httpx handles timeouts cleanly; add tenacity if 429 retry needed |
| Base64 encoding | Manual byte manipulation | Python stdlib `base64.b64encode(buf.getvalue()).decode()` | Already in stdlib |
| Thematic narrative | String concatenation of agent outputs | GPT-4o mini with structured prompt | Narrative synthesis is exactly what LLMs do well; don't template prose |

---

## Common Pitfalls

### Pitfall 1: FinBERT Loading Blocks Startup

**What goes wrong:** Loading `transformers.pipeline(...)` at module import time adds 3-5 seconds to agent startup. In Bureau threading context, this delays agent registration.

**How to avoid:** Load FinBERT at module level in `news_agent.py` (not lazily per request) — this is correct. The Bureau starts agents sequentially; 3-5 second delay on news_agent is acceptable. Do NOT load inside the message handler — that would add 3-5 seconds to every single request.

**Warning sign:** FinBERT loading inside `handle_fetch_news()`.

### Pitfall 2: asyncio.gather return_exceptions Hides Agent Failures

**What goes wrong:** One domain agent times out or raises. With `return_exceptions=True`, the result for that agent is an `Exception` instance. Orchestrator passes it to the LLM synthesis function, which crashes on `NoneType` attribute access.

**How to avoid:** After gather, check each result:
```python
def safe_result(result, fallback):
    if isinstance(result, Exception):
        return fallback
    return result

portfolio_data = safe_result(portfolio_result, mock_portfolio_response())
```

Always have a typed fallback (the mock response) so the LLM synthesis still runs.

### Pitfall 3: ctx.send_and_receive Agent Address Mismatches

**What goes wrong:** Orchestrator uses a hardcoded string for agent addresses. If the agent seed changes, the address changes silently. Orchestrator sends to a dead address; `send_and_receive` times out after 30 seconds.

**How to avoid:** Import the address constant from each agent module:
```python
from agents.portfolio_agent import portfolio_agent
PORTFOLIO_ADDR = portfolio_agent.address
```
This is derived from the seed at import time and stays in sync. Never hardcode `agent1q...` strings.

### Pitfall 4: Finnhub Rate Limit During Fan-Out

**What goes wrong:** News agent and Alt Assets agent both hit Finnhub simultaneously during `asyncio.gather`. With 5 concurrent requests, Finnhub's 60 req/min free tier is not a concern at this scale — but test runs during development can exhaust daily limits on some endpoints.

**How to avoid:** Keep `MOCK_DATA=true` in `.env` during development. Only flip to live for the final demo run. The mock branch is already wired in all agents.

### Pitfall 5: Large base64 PNG Blowing Up SSE Event

**What goes wrong:** The mock chart PNG base64 string is 50-200KB. Putting it in the `report.complete` SSE event payload creates a large SSE message. Some SSE client implementations have buffer limits.

**How to avoid:** The `report.complete` SSE event carries the full markdown string which embeds `![chart](data:image/png;base64,{...})`. This is how the spec requires it. Test with a small chart (4x3 inches, dpi=72) to keep base64 under 50KB. The curl verification will confirm this works fine.

### Pitfall 6: on_rest_post Path Prefix

**What goes wrong:** uAgents 0.24.0 prefixes REST endpoint paths with `/submit/`. Decorating with `@orchestrator.on_rest_post("/report", ...)` creates the route at `http://localhost:8005/submit/report`, not `/report`. Bridge calls `/report` on port 8005 and gets 404.

**How to avoid:** Document the correct URL in the bridge: `http://localhost:8005/submit/report`. Test with curl before wiring the bridge:
```bash
curl -X POST http://localhost:8005/submit/report \
  -H "Content-Type: application/json" \
  -d '{"holdings": ["AAPL"], "mock": true}'
```

### Pitfall 7: yfinance for Correlation Matrix Returns MultiIndex Columns

**What goes wrong:** `yf.download(multiple_tickers)["Close"]` returns a DataFrame with ticker as column headers when downloading multiple tickers. With a single ticker it returns a Series. This breaks `corr()` when the holdings list has one stock.

**How to avoid:** Always force list input and handle the single-ticker case:
```python
if len(holdings) < 2:
    return {}  # correlation matrix requires at least 2 assets
data = yf.download(holdings, period="90d", auto_adjust=True, progress=False)["Close"]
if isinstance(data, pd.Series):
    data = data.to_frame(holdings[0])
```

---

## Wiring Architecture for /report Endpoint

The bridge's `/report` endpoint and the orchestrator's REST handler form the entry point of the pipeline. This is the most integration-sensitive part of Phase 2.

```
curl POST /report (bridge port 8000)
    |
    v
bridge/app.py @app.post("/report")
    -- httpx POST --> http://localhost:8005/submit/report {holdings, mock}
    <-- 200 {"status": "ok"} --
    returns {"status": "triggered"} to curl

Meanwhile in Bureau thread:
orchestrator @on_rest_post("/report", ...)
    -- asyncio.gather -->
        portfolio_agent.handle_analyze_portfolio (Bureau internal ctx.send)
        news_agent.handle_fetch_news
        modeling_agent.handle_run_model
        alternatives_agent.handle_analyze_alternatives
    <-- all responses arrive --
    detect_contradictions(portfolio, news, modeling)
    synthesize_report(all_data, contradictions) --> GPT-4o mini call
    push_sse_event(SSEEvent.report_complete(markdown=report))

curl -N /events (bridge port 8000)
    receives: data: {"event_type": "report.complete", "payload": {"markdown": "..."}}
```

**Important nuance:** The orchestrator's `on_rest_post` handler runs in the Bureau event loop (background thread). It uses `asyncio.gather` with `ctx.send_and_receive` to dispatch to domain agents. This is all within the Bureau's own event loop — not the FastAPI loop. The `push_sse_event` cross-loop call is used to push the final `report.complete` event into the FastAPI queue.

---

## State of the Art

| Old Pattern | Phase 2 Pattern | Why Changed |
|-------------|-----------------|-------------|
| Stub `else: response = mock_*()` | Real domain logic in `else` branch, mock branch unchanged | Incremental: mock always available as fallback |
| Orchestrator pushes events directly from bridge `/trigger` | Orchestrator agent handles `ReportRequest` via `on_rest_post` | Agents own their domain; bridge is just a gateway |
| No LLM in system | GPT-4o mini in orchestrator only | Domain agents are pure computation; only synthesis needs LLM |
| Static mock `image_base64 = ""` | Static pre-generated PNG base64 constant | Proves chart pipeline works without real Modeling agent |

---

## Open Questions

1. **ctx.send_and_receive inside on_rest_post handler**
   - What we know: `on_rest_post` creates an HTTP handler in the Bureau's ASGI server. The `ctx` object inside this handler should have access to `send_and_receive`.
   - What's unclear: Whether `ctx.send_and_receive` is available in REST handlers vs message handlers. The Phase 1 decision to skip `on_rest_post` was due to uncertainty.
   - Recommendation: Test with a minimal `on_rest_post` handler that does one `ctx.send_and_receive` to a known agent before wiring the full fan-out. If `ctx.send_and_receive` is unavailable in REST context, fall back to: bridge sends a uAgents message to a dedicated bridge agent, which forwards to orchestrator as a message. Orchestrator already has the `@on_message(model=ReportRequest)` handler stub from Phase 1 plan.

2. **CoinGecko demo key requirement**
   - What we know: CoinGecko's demo plan is advertised as free. `/simple/price` and `/global` endpoints work without auth in testing.
   - What's unclear: Whether the demo key (`x-cg-demo-api-key`) is required for rate limits to apply or if unauthed calls hit a stricter limit.
   - Recommendation: Register for a free demo key from coingecko.com and add to `.env` as `COINGECKO_API_KEY`. Send it as a header if set, omit if not. This is a 2-minute registration.

3. **FinBERT inference time per headline**
   - What we know: BERT inference on CPU is ~100-300ms per input.
   - What's unclear: With 15-25 filtered headlines, total FinBERT time is 2-8 seconds on CPU. This may feel slow in a live demo.
   - Recommendation: Accept this latency for Phase 2. The SSE thought feed hides it ("Scoring sentiment on 20 headlines..."). Batch inference can reduce this: `_finbert([h["headline"] for h in headlines])` processes all at once (usually faster than sequential calls).

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest with pytest-asyncio |
| Config | `agents/pyproject.toml` — `asyncio_mode = "auto"`, `testpaths = ["tests"]` |
| Quick run command | `.venv/bin/pytest agents/tests/ -x -q -k "not integration"` |
| Full suite command | `.venv/bin/pytest agents/tests/ -x -q` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| PORT-01 | Mock portfolio loads with 10+ holdings | unit | `pytest tests/test_portfolio_agent.py::test_mock_portfolio_has_holdings -x` |
| PORT-02 | Sector allocation sums to 1.0 | unit | `pytest tests/test_portfolio_agent.py::test_sector_allocation_sums_to_one -x` |
| PORT-03 | Herfindahl index in valid range [0,1] | unit | `pytest tests/test_portfolio_agent.py::test_herfindahl_valid_range -x` |
| PORT-04 | Correlation matrix is symmetric | unit | `pytest tests/test_portfolio_agent.py::test_correlation_matrix_symmetric -x` |
| PORT-05 | PortfolioResponse serializes cleanly | unit | existing `tests/test_models.py::test_response_roundtrip_serialization` |
| NEWS-01 | Finnhub response parsed into headlines | unit (mock httpx) | `pytest tests/test_news_agent.py::test_parse_finnhub_response -x` |
| NEWS-02 | Headline filter returns only relevant tickers | unit | `pytest tests/test_news_agent.py::test_headline_filter -x` |
| NEWS-03 | FinBERT score in [-1, 1] | unit | `pytest tests/test_news_agent.py::test_finbert_score_range -x` |
| NEWS-04 | Aggregate sentiment per ticker is mean of headlines | unit | `pytest tests/test_news_agent.py::test_aggregate_sentiment -x` |
| NEWS-05 | NewsResponse has headlines + aggregate_sentiment | unit | existing `tests/test_models.py` |
| MODL-01..05 | Mock ModelResponse has non-empty image_base64 | unit | `pytest tests/test_modeling_agent.py::test_mock_chart_not_empty -x` |
| ALT-01 | CoinGecko response has BTC and ETH | unit (mock httpx) | `pytest tests/test_alternatives_agent.py::test_btc_eth_always_present -x` |
| ALT-02 | Commodity prices returned for GOLD and OIL | unit (mock httpx) | `pytest tests/test_alternatives_agent.py::test_commodity_prices -x` |
| ALT-03 | Cross-correlations dict has entries for alt assets | unit | `pytest tests/test_alternatives_agent.py::test_cross_correlations -x` |
| ALT-04 | AlternativesResponse has trend_signals and btc_dominance | unit | `pytest tests/test_alternatives_agent.py::test_response_fields -x` |
| ORCH-01 | Orchestrator dispatches to 4 agents (mocked) | integration | `pytest tests/test_orchestrator.py::test_fan_out_dispatches_all_agents -x` |
| ORCH-02 | All 4 response types collected | integration | `pytest tests/test_orchestrator.py::test_collects_all_responses -x` |
| ORCH-03 | Report markdown contains executive summary | integration | `pytest tests/test_orchestrator.py::test_report_has_sections -x` |
| ORCH-04 | Contradiction detected when bearish news + top holding | unit | `pytest tests/test_orchestrator.py::test_contradiction_detection -x` |
| ORCH-05 | Report markdown has embedded base64 image | integration | `pytest tests/test_orchestrator.py::test_report_has_chart_embed -x` |

### Wave 0 Gaps (test files to create before implementation)

- [ ] `agents/tests/test_portfolio_agent.py` — covers PORT-01 through PORT-04
- [ ] `agents/tests/test_news_agent.py` — covers NEWS-01 through NEWS-04
- [ ] `agents/tests/test_modeling_agent.py` — covers MODL-03 (non-empty base64)
- [ ] `agents/tests/test_alternatives_agent.py` — covers ALT-01 through ALT-04
- [ ] `agents/tests/test_orchestrator.py` — covers ORCH-01 through ORCH-05

Existing `tests/test_models.py` and `tests/test_mock.py` cover PORT-05, NEWS-05, MODL-05 already.

---

## Sources

### Primary (HIGH confidence)
- Phase 1 codebase — `agents/models/responses.py`, `agents/bridge/events.py`, `agents/bureau.py`, all agent stubs — direct inspection, grounded truth
- Phase 1 CONTEXT.md, STACK.md, ARCHITECTURE.md, PITFALLS.md — established decisions and patterns
- Python stdlib `base64`, `io`, `asyncio` — standard library, no version concerns

### Secondary (MEDIUM confidence)
- ProsusAI/finbert on Hugging Face — transformers `pipeline("text-classification", model="ProsusAI/finbert")` is the documented usage. Verified via HuggingFace model card.
- CoinGecko `/simple/price` and `/global` API — free public endpoints, documented at docs.coingecko.com
- Finnhub `/quote` for commodity symbols — standard REST; `GC1!` and `CL1!` are CME futures symbols supported by Finnhub (verify against their symbol list)
- GPT-4o mini `max_tokens=2000`, `temperature=0.4` — OpenAI API defaults, reasonable for analytical prose
- numpy HHI formula and beta calculation — standard financial math, no library-specific concerns

### Tertiary (LOW confidence — verify before implementing)
- `ctx.send_and_receive` availability inside `on_rest_post` handlers — not confirmed in uAgents 0.24.0 docs. Open Question #1 above. Test in Wave 1 before full orchestrator wiring.
- Finnhub commodity symbols `GC1!` and `CL1!` — common symbols but should be tested against actual API response.

---

## Metadata

**Confidence breakdown:**
- Model contract gaps: HIGH — derived directly from Phase 1 code inspection
- Standard stack additions: HIGH — standard libraries, well-documented
- FinBERT integration pattern: MEDIUM — standard HuggingFace pattern, transformers library well-documented
- Orchestrator on_rest_post + send_and_receive: MEDIUM-LOW — uAgents 0.24.0 REST handler behavior not fully verified; flagged as Open Question
- Mock portfolio design: HIGH — values are choices, not facts; rationale is sound
- Commodity symbols: MEDIUM — standard CME symbols, but Finnhub support requires verification

**Research date:** 2026-03-21
**Valid until:** 2026-04-20 (stable libraries; FinBERT model is static; API endpoints stable)
