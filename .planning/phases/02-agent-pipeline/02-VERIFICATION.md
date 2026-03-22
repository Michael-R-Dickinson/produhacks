---
phase: 02-agent-pipeline
verified: 2026-03-22T12:00:00Z
status: human_needed
score: 24/24 must-haves verified
re_verification:
  previous_status: gaps_found
  previous_score: 20/24
  gaps_closed:
    - "Alt Assets agent fetches crypto prices from CoinGecko (ALT-01) -- asyncio.gather unpack bug fixed with direct await on line 164"
    - "agents/.env.example created with MOCK_DATA, FINNHUB_API_KEY, GEMINI_API_KEY"
  gaps_remaining: []
  regressions: []
human_verification:
  - test: "Run full pipeline end-to-end with mock data"
    expected: "curl -X POST http://localhost:8000/report triggers orchestrator fan-out; SSE stream at /events shows agent.status, agent.thought, and report.complete events with markdown content"
    why_human: "Requires running uAgents Bureau and FastAPI concurrently; curl output contains thematic markdown report"
  - test: "Verify Gemini synthesis output quality"
    expected: "report.complete SSE event contains thematic sections (Executive Summary, sector outlook, risk assessment, alternative assets), professional analyst tone, and chart references"
    why_human: "LLM output quality cannot be verified programmatically"
---

# Phase 2: Agent Pipeline Verification Report

**Phase Goal:** Triggering a report request produces a complete unified narrative markdown document synthesized from all five agents -- verifiable via curl with no frontend running
**Verified:** 2026-03-22
**Status:** human_needed (all automated checks pass; two items require live-process testing)
**Re-verification:** Yes -- after gap closure plan 02-06

## Re-verification Summary

Previous score was 20/24 (2 gaps). Plan 02-06 closed both gaps:

1. **ALT-01 bug fixed:** `agents/alternatives_agent.py` line 164 now reads `prices, change_7d = await fetch_crypto_prices(CRYPTO_TICKERS)`. The defective `asyncio.gather(fetch_crypto_prices(...), return_exceptions=False)` pattern is gone (grep returns 0 occurrences). The stale `prices, changes = crypto_prices` unpack is also gone. 13/13 tests pass.

2. **agents/.env.example created:** File exists with `MOCK_DATA=true`, `FINNHUB_API_KEY=your_finnhub_api_key_here`, and `GEMINI_API_KEY=your_gemini_api_key_here`. Does not contain `OPENAI_API_KEY`. All three required env vars are documented with comments explaining which agents use them.

No regressions detected in previously-passing items.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | PortfolioResponse includes correlation_matrix field | VERIFIED | `agents/models/portfolio.py` line 16: `correlation_matrix: dict[str, dict[str, float]]` |
| 2 | AlternativesResponse includes trend_signals, btc_dominance, commodities fields | VERIFIED | `agents/models/alternatives.py` lines 11-15: all three fields present |
| 3 | ReportRequest model exists for bridge-to-orchestrator communication | VERIFIED | `agents/models/report.py`: `class ReportRequest(Model)` with `holdings` and `mock` fields |
| 4 | Mock portfolio with 12 holdings across 6 sectors is centrally defined and importable | VERIFIED | `agents/data/portfolio.py`: 12 entries, sectors: Technology, Healthcare, Financials, Energy, Consumer Discretionary, Crypto |
| 5 | Mock modeling response includes a real base64 PNG chart image | VERIFIED | `agents/mocks/modeling.py`: MOCK_CHART_BASE64 constant present |
| 6 | Portfolio agent computes sector allocation from the central mock portfolio | VERIFIED | `agents/portfolio_agent.py`: `compute_sector_allocation()` groups by sector, maps crypto to "Crypto" |
| 7 | Portfolio agent computes Herfindahl diversification index | VERIFIED | `agents/portfolio_agent.py`: `compute_herfindahl()` using `np.sum(np.square(weights))` |
| 8 | Portfolio agent computes portfolio beta using SPY as market proxy | VERIFIED | `agents/portfolio_agent.py`: `compute_portfolio_beta()` downloads SPY via yfinance, uses `np.cov()` |
| 9 | Portfolio agent computes correlation matrix across equity holdings | VERIFIED | `agents/portfolio_agent.py`: `compute_correlation_matrix()` using `returns.corr()` |
| 10 | Portfolio agent returns all data as structured PortfolioResponse | VERIFIED | Handler builds `PortfolioResponse(sector_allocation=..., top_holdings=..., herfindahl_index=..., portfolio_beta=..., correlation_matrix=...)` |
| 11 | News agent fetches headlines from Finnhub API for portfolio tickers | VERIFIED | `agents/news_agent.py`: `fetch_finnhub_headlines()` calls `https://finnhub.io/api/v1/news` and `/company-news` |
| 12 | News agent filters headlines for relevance to portfolio holdings | VERIFIED | `agents/news_agent.py`: `filter_headlines_for_tickers()` with per-ticker cap of 5 |
| 13 | News agent scores sentiment per headline using FinBERT | VERIFIED | `agents/news_agent.py`: lazy-loads `ProsusAI/finbert` via `get_finbert()`, `score_sentiment()` returns positive - negative |
| 14 | News agent computes aggregate sentiment per ticker | VERIFIED | `agents/news_agent.py`: `aggregate_sentiment_by_ticker()` computes mean per ticker |
| 15 | News agent returns structured NewsResponse with headlines and sentiment data | VERIFIED | Handler constructs `NewsResponse(headlines=..., aggregate_sentiment=..., overall_sentiment=...)` |
| 16 | Alt Assets agent fetches crypto prices from CoinGecko | VERIFIED | Line 164: `prices, change_7d = await fetch_crypto_prices(CRYPTO_TICKERS)` -- direct await, no asyncio.gather bug. 13/13 tests pass. |
| 17 | Alt Assets agent fetches gold and oil prices from Finnhub | VERIFIED | `fetch_commodity_prices()` calls `finnhub.io/api/v1/quote?symbol=GC1!` and `CL1!` |
| 18 | Alt Assets agent computes trend signals (bullish/bearish/neutral) per asset | VERIFIED | `trend_signal(price_change_7d)`: > 3.0 = bullish, < -3.0 = bearish, else neutral |
| 19 | Alt Assets agent fetches BTC dominance from CoinGecko global endpoint | VERIFIED | `fetch_btc_dominance()` calls `coingecko.com/api/v3/global` |
| 20 | Alt Assets agent computes cross-asset correlations with portfolio equity returns | VERIFIED | `compute_cross_correlations()` uses pandas `pct_change().corr()` |
| 21 | Orchestrator fans out to all 4 domain agents concurrently via asyncio.gather | VERIFIED | `orchestrator.py`: `asyncio.gather(ctx.send_and_receive(...) x4, return_exceptions=True)` |
| 22 | Orchestrator collects all structured responses with fallbacks | VERIFIED | `safe_result()` + `extract_msg()` pattern applied to all 4 results with mock fallbacks |
| 23 | Orchestrator detects cross-agent contradictions before LLM call | VERIFIED | `detect_contradictions()` checks bearish sentiment on top holdings and bullish news + negative momentum |
| 24 | Orchestrator synthesizes unified thematic narrative via LLM | VERIFIED | `synthesize_report()` calls Gemini 2.5 Flash |
| 25 | Bridge /report endpoint triggers orchestrator and returns report via SSE report.complete event | VERIFIED | `@app.post("/report")` exists and posts to `http://localhost:{BUREAU_PORT}/report`; `agents/.env.example` now exists with all required keys |

**Score:** 24/24 truths fully verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `agents/models/responses.py` | Updated PortfolioResponse and AlternativesResponse contracts | VERIFIED | Re-export barrel; domain models in subdomain files |
| `agents/models/requests.py` | ReportRequest model | VERIFIED | Re-export barrel; `ReportRequest` in `agents/models/report.py` |
| `agents/data/portfolio.py` | Central mock portfolio definition | VERIFIED | 12 holdings, MOCK_PORTFOLIO, EQUITY_TICKERS, CRYPTO_TICKERS, ALL_TICKERS |
| `agents/mocks/modeling.py` | Mock chart with real base64 PNG | VERIFIED | MOCK_CHART_BASE64 constant present |
| `agents/portfolio_agent.py` | Live portfolio computation logic | VERIFIED | All 5 computation functions present, uses numpy/yfinance |
| `agents/tests/test_portfolio.py` | Unit tests for portfolio computations | VERIFIED | 14 test functions covering all computation functions |
| `agents/news_agent.py` | Live news fetching and FinBERT sentiment scoring | VERIFIED | Finnhub + ProsusAI/finbert integration present |
| `agents/tests/test_news.py` | Unit tests for news filtering and sentiment aggregation | VERIFIED | 14 test functions, no FinBERT loading in tests |
| `agents/alternatives_agent.py` | Live CoinGecko + Finnhub commodity fetching, bug fixed | VERIFIED | Direct await replaces defective asyncio.gather; 13/13 tests pass |
| `agents/tests/test_alternatives.py` | Unit tests for trend signal logic and correlation | VERIFIED | 13 tests pass via `uv run python -m pytest` |
| `agents/orchestrator.py` | Full orchestrator with fan-out, contradiction detection, LLM synthesis | VERIFIED | asyncio.gather fan-out, detect_contradictions, build_synthesis_prompt, synthesize_report |
| `agents/bridge/app.py` | Bridge /report endpoint wiring | VERIFIED | `@app.post("/report")` present, calls BUREAU_PORT/report |
| `agents/tests/test_orchestrator.py` | Tests for contradiction detection and synthesis prompt | VERIFIED | 14 test functions in TestSafeResult, TestDetectContradictions, TestBuildSynthesisPrompt |
| `agents/.env.example` | Required env vars documentation | VERIFIED | Contains MOCK_DATA, FINNHUB_API_KEY, GEMINI_API_KEY; no OPENAI_API_KEY |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `agents/data/portfolio.py` | `agents/mocks/portfolio.py` | `from agents.data.portfolio import` | VERIFIED | Line 1: `from agents.data.portfolio import MOCK_PORTFOLIO, EQUITY_TICKERS` |
| `agents/portfolio_agent.py` | `agents/data/portfolio.py` | `from agents.data.portfolio import` | VERIFIED | Line 8: `from agents.data.portfolio import EQUITY_TICKERS, MOCK_PORTFOLIO` |
| `agents/portfolio_agent.py` | `agents/models/responses.py` | returns PortfolioResponse | VERIFIED | Handler: `response = PortfolioResponse(...)` |
| `agents/news_agent.py` | Finnhub API | httpx async GET | VERIFIED | `https://finnhub.io/api/v1/news` and `/company-news` |
| `agents/news_agent.py` | `agents/models/responses.py` | returns NewsResponse | VERIFIED | `response = NewsResponse(...)` |
| `agents/alternatives_agent.py` | `fetch_crypto_prices` | direct await (not asyncio.gather) | VERIFIED | Line 164: `prices, change_7d = await fetch_crypto_prices(CRYPTO_TICKERS)` |
| `agents/alternatives_agent.py` | CoinGecko API | httpx async GET | VERIFIED | `https://api.coingecko.com/api/v3/simple/price` |
| `agents/alternatives_agent.py` | Finnhub API | httpx async GET for commodities | VERIFIED | `https://finnhub.io/api/v1/quote?symbol=GC1!` and `CL1!` |
| `agents/bridge/app.py` | `agents/orchestrator.py` | HTTP POST to Bureau REST endpoint | VERIFIED | `http://localhost:{BUREAU_PORT}/report` |
| `agents/orchestrator.py` | `agents/portfolio_agent.py` | ctx.send_and_receive | VERIFIED | PORTFOLIO_ADDR = portfolio_agent.address; used in gather |
| `agents/orchestrator.py` | `agents/bridge/events.py` | push_sse_event(SSEEvent.report_complete(...)) | VERIFIED | `push_sse_event(SSEEvent.report_complete(markdown=..., charts=...))` |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| PORT-01 | 02-01 | Portfolio agent loads mock portfolio data | SATISFIED | `agents/data/portfolio.py`: MOCK_PORTFOLIO with 12 holdings across 6 sectors |
| PORT-02 | 02-02 | Computes sector/asset allocation breakdown | SATISFIED | `compute_sector_allocation()` in portfolio_agent.py |
| PORT-03 | 02-02 | Calculates diversification metrics (HHI, portfolio beta) | SATISFIED | `compute_herfindahl()` and `compute_portfolio_beta()` |
| PORT-04 | 02-02 | Runs correlation matrix across holdings | SATISFIED | `compute_correlation_matrix()` using numpy/pandas |
| PORT-05 | 02-02 | Returns structured numerical output to orchestrator | SATISFIED | `PortfolioResponse` with all computed fields |
| NEWS-01 | 02-03 | Fetches financial news headlines from Finnhub API | SATISFIED | `fetch_finnhub_headlines()` with market + company news |
| NEWS-02 | 02-03 | Filters headlines for relevance to portfolio holdings | SATISFIED | `filter_headlines_for_tickers()` with ticker matching and per-ticker cap |
| NEWS-03 | 02-03 | Scores sentiment per article using FinBERT | SATISFIED | `score_sentiment()` with `ProsusAI/finbert` lazy loading |
| NEWS-04 | 02-03 | Computes aggregate sentiment metrics per holding/sector | SATISFIED | `aggregate_sentiment_by_ticker()` + `compute_overall_sentiment()` |
| NEWS-05 | 02-03 | Returns structured sentiment data + raw headlines | SATISFIED | `NewsResponse(headlines=..., aggregate_sentiment=..., overall_sentiment=...)` |
| MODL-01 | 02-01 | Retrieves historical price data via yfinance | SATISFIED | `agents/modeling_data.py`: `load_adjusted_close_matrix()` uses yfinance with graceful fallback |
| MODL-02 | 02-04 | Runs specifiable analyses via chart registry | SATISFIED | `agents/modeling_charts.py`: CHART_RENDERERS registry with 5 analysis types |
| MODL-03 | 02-01 | Generates charts (matplotlib) as ChartOutput with image_base64 | SATISFIED | All 5 renderers produce `ChartOutput` with `fig_to_base64_png()` |
| MODL-04 | 02-04 | Computes risk metrics (Sharpe ratio, volatility) plus extensible metrics dict | SATISFIED | `estimate_metrics()` computes sharpe, vol, trend_slope, r_squared, max_drawdown, beta |
| MODL-05 | 02-04 | Returns structured metrics + multiple chart outputs | SATISFIED | `ModelResponse(holdings_analyzed=..., sharpe_ratio=..., charts=[...], metrics={...})` |
| ALT-01 | 02-04 / 02-06 | Fetches current crypto prices and trends from CoinGecko | SATISFIED | Bug fixed: direct await at line 164; no asyncio.gather wrapping single coroutine |
| ALT-02 | 02-04 | Retrieves commodity/real estate market data | SATISFIED | `fetch_commodity_prices()` fetches GOLD (GC1!) and OIL (CL1!) from Finnhub |
| ALT-03 | 02-04 | Computes cross-asset correlations with portfolio holdings | SATISFIED | `compute_cross_correlations()` using pandas pct_change + corr |
| ALT-04 | 02-04 | Returns structured market data + correlations | SATISFIED | `AlternativesResponse(crypto_prices=..., cross_correlations=..., trend_signals=..., btc_dominance=..., commodities=...)` |
| ORCH-01 | 02-05 | Dispatches to appropriate domain agents | SATISFIED | `asyncio.gather(ctx.send_and_receive x4)` in `handle_report` |
| ORCH-02 | 02-05 | Receives structured data from all domain agents | SATISFIED | `safe_result(extract_msg(...), fallback)` for all 4 agents |
| ORCH-03 | 02-05 | Uses LLM to synthesize agent outputs into unified narrative | SATISFIED | `synthesize_report()` calls Gemini 2.5 Flash |
| ORCH-04 | 02-05 | Identifies cross-agent contradictions and patterns | SATISFIED | `detect_contradictions()` covers bearish-sentiment-top-holding and bullish-news-negative-momentum |
| ORCH-05 | 02-05 | Generates executive summary with key actionable insights | SATISFIED | `build_synthesis_prompt()` requires Executive Summary section in LLM instructions |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `agents/bridge/app.py` | 41-48 | `_run_trigger_stub()` still used in `/trigger` and `/api/report/generate` | Warning | Phase 1 stub paths still active; these endpoints emit a "Stub" thought event. Not blocking -- /report is the production path. |

The ALT-01 blocker from the previous report is now resolved. Only the pre-existing stub warning on the legacy trigger endpoints remains, which does not block the phase goal.

### Human Verification Required

#### 1. Full pipeline smoke test (mock mode)

**Test:** Start the server with `cd agents && MOCK_DATA=true python -m agents.main`, open SSE stream at `curl -N http://localhost:8000/events`, then trigger with `curl -X POST http://localhost:8000/report`
**Expected:** SSE stream shows agent.status (working/done) and agent.thought events for all 4 agents plus orchestrator, then a report.complete event containing markdown with Executive Summary, thematic sections, portfolio metrics, crypto/commodity data, and professional analyst tone
**Why human:** Requires running uAgents Bureau and FastAPI concurrently; curl output contains thematic markdown report

#### 2. Gemini API synthesis quality

**Test:** With real GEMINI_API_KEY set, trigger with `MOCK_DATA=false` and verify report content
**Expected:** Thematic sections weave portfolio metrics, news sentiment, and alternative assets into a unified narrative -- not just a data dump by agent
**Why human:** LLM synthesis quality requires human judgment

### Gaps Summary

No automated gaps remain. All 24 truths verified. Both previously-identified gaps are closed:

- **ALT-01 (Blocker -- now resolved):** `prices, change_7d = await fetch_crypto_prices(CRYPTO_TICKERS)` at line 164. The defective `asyncio.gather` call and the subsequent `prices, changes = crypto_prices` double-unpack are both gone. 13/13 alternative agent unit tests pass.

- **Missing .env.example (now resolved):** `agents/.env.example` exists with `MOCK_DATA`, `FINNHUB_API_KEY`, and `GEMINI_API_KEY` documented. Does not contain the stale `OPENAI_API_KEY`.

Phase goal is achievable. Remaining human verification items require a live process to confirm the full SSE stream delivers a complete unified narrative document.

---

_Verified: 2026-03-22_
_Verifier: Claude (gsd-verifier)_
