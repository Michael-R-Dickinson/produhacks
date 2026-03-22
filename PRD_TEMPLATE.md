# Product Requirements Document (PRD)

## Wealth Council — Multi-Agent Investment Intelligence Platform

**Author:**  Claude's Plan
**Target Delivery Date:** March 22, 2026
**Last Update Date:** March 22, 2026
**Drivers:** PM: Michael Dickinson | PD: Anant Khanna, Anthony Lu | XD: Yash Vasdev

---

**Jump to a key section in this PRD:**
[Introduction & Context Setting](#introduction--context-setting) · [Target Segment & Customer Problem](#target-segment--customer-problem) · [Functional Requirements](#functional-requirements) · [Milestone Release Schedule](#milestone-release-schedule--scope) · [Open Questions](#open-questions) · [Artifacts](#artifacts) · [Appendix](#appendix)

---

## INTRODUCTION & CONTEXT SETTING

Retail investors today face a fragmented research experience. Evaluating a portfolio requires checking 5–8 separate platforms — brokerage dashboards for allocation, Yahoo Finance for charts, CNBC/Reuters for news sentiment, CoinGecko for crypto, and commodity trackers — none of which talk to each other. This takes 30–60 minutes daily, so most investors skip it entirely. Contradictions between signals (e.g., bullish news but bearish technical momentum on the same stock) go unnoticed because no single tool synthesizes across domains.

**Wealth Council** solves this by deploying a **swarm of 5 specialized AI agents** on the Fetch.ai uAgents protocol, each responsible for one analytical domain. A central Orchestrator agent synthesizes their structured outputs using Google Gemini into a single, unified narrative daily investment report — replacing 30–60 minutes of manual multi-source research with a one-click, ~15-second report.

**The key architectural insight:** most of an investment report does not need an LLM. Portfolio math (beta, Sharpe ratio, correlation matrices) is deterministic computation. News sentiment is best scored by a fine-tuned NLP model (FinBERT), not a general-purpose LLM. Charts are rendered by matplotlib. Only the final synthesis step — weaving these numerical outputs into a coherent narrative — requires LLM reasoning. This decomposition makes Wealth Council more accurate, faster, cheaper, and more transparent than monolithic LLM-based financial assistants.

---

## TARGET SEGMENT & CUSTOMER PROBLEM

### TARGET PERSONA(S)

| Persona | Mindset |
|---|---|
| **Self-Directed Retail Investor** ("Alex") | "I manage my own $50K–$500K portfolio as a software engineer by day. I want informed decisions, but I don't have 45 minutes every morning to cross-reference Bloomberg, Yahoo Finance, CoinGecko, and Reuters. I need a single source that sees my whole portfolio and tells me what matters today." |
| **Part-Time Financial Advisor** ("Priya") | "I advise 15 clients as a side practice. Before each quarterly meeting I need a quick portfolio health summary — allocation, risk metrics, sentiment, red flags. I spend 2 hours manually assembling each client's review. I want that done in seconds." |
| **Crypto-Curious Traditional Investor** ("Jordan") | "I have a 70/30 equities/crypto split. My brokerage ignores my crypto. CoinGecko ignores my equities. I want to see how BTC correlates with my AAPL position and whether my overall portfolio is riskier than I think." |

### CUSTOMER PROBLEM & HYPOTHESES

**I am a** self-directed retail investor **trying to** get a comprehensive, cross-domain view of my portfolio's health in under 5 minutes…

| Problem — But… | Because… (Root Cause) | Hypothesis |
|---|---|---|
| I need to check 5–8 different platforms (brokerage, chart tools, news sites, crypto trackers) to form a complete picture | **Root Cause 1:** Investment data is siloed by domain — portfolio analytics, news sentiment, quant models, and crypto trackers are built by different companies with no interoperability | If we **deploy specialized agents per domain and synthesize their outputs through a central orchestrator**, then investors get a single report covering all domains in under 30 seconds |
| No existing tool tells me when my news sentiment is bullish but my quantitative momentum is bearish — contradictions critical for decision quality | **Root Cause 2:** Cross-domain contradiction detection requires structured data from multiple sources to be compared programmatically — something a human scanning separate tabs will miss | If we **implement automated contradiction detection** (comparing news sentiment against quantitative signals), then investors catch critical signal conflicts they would have missed |
| General-purpose LLMs hallucinate financial numbers — asking ChatGPT to "analyze my portfolio" produces plausible but unverifiable output | **Root Cause 3:** General LLMs have no traceable data sources for financial metrics — no audit trail | If we **restrict LLM usage to narrative synthesis only** (all numbers computed by deterministic agents with traceable API sources), then 100% of reported metrics are verifiable and accurate |

### Current State → Target State

| Dimension | Current State (Before Wealth Council) | Target State (With Wealth Council) |
|---|---|---|
| **Research workflow** | Open 5–8 browser tabs, manually cross-reference data, form conclusions in your head | One-click report generation; unified narrative in ~15 seconds |
| **Portfolio risk metrics** | No HHI, no beta, no correlation matrix unless you run your own spreadsheet | Auto-computed: sector allocation, HHI diversification index, portfolio beta vs SPY, 90-day correlation matrix |
| **News sentiment** | Scan headlines manually; subjective judgment | FinBERT-scored sentiment per headline, aggregated per-ticker and portfolio-wide, near-neutral noise filtered |
| **Quantitative analysis** | Manual TradingView; no Sharpe ratio unless self-calculated | Sharpe ratio, annualized volatility, trend regression, 5 chart types generated automatically |
| **Alternative assets** | CoinGecko and brokerage completely separate | Unified cross-asset Pearson correlations showing how BTC/ETH/Gold/Oil move relative to equities |
| **Cross-signal awareness** | Never detected | Automated: "Bearish news on AAPL (−0.4 sentiment) but it's your #1 holding at 18% weight" |
| **Report output** | No report — mental model from scattered tabs | Executive-grade markdown report with embedded charts, synthesized by Gemini from structured agent data |
| **Agent visibility** | N/A | Live swarm activity graph showing each agent's real-time thoughts, status, and inter-agent message flow |

---

## FUNCTIONAL REQUIREMENTS

| Scope | Priority | Requirements |
|---|---|---|
| **Agent Infrastructure** | P0 | Fetch.ai uAgents Bureau running all 5 agents in a single process |
| | P0 | FastAPI bridge with SSE endpoints translating HTTP/browser ↔ agent protocol |
| | P0 | Pydantic message models for all inter-agent communication (type-safe contracts) |
| | P0 | Mock data mode toggle (`MOCK_DATA=true` in `.env`) — entire pipeline runs offline with zero API keys |
| **Portfolio Agent** | P0 | Load portfolio holdings (12 holdings across 6 sectors: Technology, Healthcare, Financials, Energy, Consumer Discretionary, Crypto) |
| | P0 | Compute sector/asset allocation breakdown with weights summing to 1.0 |
| | P0 | Calculate diversification metrics: Herfindahl-Hirschman Index (HHI) and portfolio beta vs SPY |
| | P0 | Run 90-day pairwise correlation matrix across all equities using yfinance + pandas |
| | P0 | Return structured `PortfolioResponse` to orchestrator |
| **News / Sentiment Agent** | P0 | Fetch financial news headlines from Finnhub API (general market + per-ticker company news, 7-day window) |
| | P0 | Filter headlines for relevance to portfolio tickers, cap at 5 per ticker |
| | P0 | Score sentiment per headline using FinBERT (`ProsusAI/finbert`) — lazy-loaded to avoid 500MB download during tests |
| | P0 | Discard near-neutral headlines (\|sentiment\| < 0.1) to reduce noise |
| | P0 | Compute aggregate sentiment per ticker and portfolio-wide overall sentiment |
| **Modeling / Quant Agent** | P0 | Retrieve historical price data via yfinance |
| | P0 | Run analyses from extensible chart registry: `regression`, `correlation_matrix`, `sector_performance`, `volatility_cone`, `price_history` |
| | P0 | Generate matplotlib charts as base64 PNG strings with `ChartOutput` metadata (type, title, summary) |
| | P0 | Compute risk metrics: Sharpe ratio, annualized volatility, trend slope |
| **Alt Assets Agent** | P0 | Fetch crypto prices + 7-day changes (BTC, ETH, SOL, BNB, AVAX) from CoinGecko |
| | P0 | Fetch BTC market cap dominance from CoinGecko global endpoint |
| | P0 | Fetch commodity prices (Gold, Oil) from Finnhub |
| | P0 | Compute trend signals: >3% bullish, <−3% bearish, else neutral |
| | P0 | Compute Pearson cross-correlations between alt assets and equity portfolio |
| **Orchestrator Agent** | P0 | Fan-out to all 4 domain agents concurrently via `asyncio.gather` with `return_exceptions=True` |
| | P0 | `safe_result()` — if an agent times out or errors, fall back to mock data (never crash the pipeline) |
| | P0 | `detect_contradictions()` — flag bearish news on top holdings; flag bullish sentiment contradicting negative momentum |
| | P0 | Use Gemini to plan which charts to generate based on agent data context |
| | P0 | `synthesize_report()` — single Google Gemini call to generate 600–800 word unified narrative |
| **Daily Report Page** | P0 | One-page centric: this IS the app's primary experience |
| | P0 | "Generate Report" CTA button in sidebar triggers full pipeline |
| | P0 | During generation: animated agent swarm graph showing real-time agent thoughts and status |
| | P0 | After completion: graph collapses, full markdown report with inline base64 charts fades in |
| | P0 | Report renders as unified narrative organized by investment theme, NOT by agent/data source |
| **Swarm Activity Graph** | P1 | 5 agent cards in circular layout: Orchestrator center, 4 domain agents at corners |
| | P1 | Animated dashed SVG connection lines from orchestrator to each agent |
| | P1 | Travelling dot animation along active connections |
| | P1 | Each card shows: agent name, icon, status badge (Processing/Complete), latest 3 thoughts in code-block style |
| | P1 | Edge hover tooltips showing message title and description |
| **Chat Interface** | P2 | Text input routed through orchestrator agent |
| | P2 | Responses contextual to current report data |
| | P2 | Agent graph shows which agents are dispatched during chat queries |
| **Portfolio Upload** | P2 | CSV upload UI accepting brokerage export files |
| | P2 | Parsed holdings replace mock portfolio for the session |

---

## MILESTONE RELEASE SCHEDULE & SCOPE

### Milestone 1: Agent Infrastructure
**Target Date:** March 21, 2026 — Evening
uAgents Bureau running 5 stub agents, FastAPI bridge with SSE streaming, Pydantic message contracts, mock data mode. Verified end-to-end via curl.

### Milestone 2: Agent Pipeline
**Target Date:** March 21, 2026 — Night
All 5 agents fully implemented with both mock and live modes. Portfolio agent computing real metrics via yfinance/numpy. News agent scoring sentiment via Finnhub + FinBERT. Alt Assets agent fetching CoinGecko/Finnhub with cross-correlations. Orchestrator with Gemini synthesis, contradiction detection, and 61 unit tests passing.

### Milestone 3: Frontend & Visualization
**Target Date:** March 22, 2026 — Morning
React + Vite frontend with: Daily Report page rendering markdown + charts, swarm activity visualization with animated agent cards, sidebar with real-time status indicators, SSE EventSource integration for live thought streaming.

### Milestone 4: Demo Polish
**Target Date:** March 22, 2026 — Afternoon
Chat interface, edge hover tooltips in swarm graph, UX hardening, and demo dry-run on live API data (MOCK_DATA=false).

---

## OPEN QUESTIONS

| Open Question | Driver | Decision/Response | Status | Date to Close |
|---|---|---|---|---|
| Deploy agents to Agentverse or keep local Bureau? | PM | Local Bureau for hackathon — Agentverse deferred to v2 | Resolved | Mar 21 |
| Which LLM for orchestrator synthesis? | PD | Google Gemini 2.5 Flash (migrated from GPT-4o mini) | Resolved | Mar 22 |
| FinBERT vs LLM-based sentiment scoring? | PD | FinBERT — fine-tuned financial NLP is more accurate and cheaper than general LLM | Resolved | Mar 21 |
| yfinance rate limiting strategy? | PD | No caching for v1 — fresh calls per report. Caching deferred to v2 | Resolved | Mar 22 |
| CSV upload parsing scope? | PM | Deferred to v2 — mock portfolio for hackathon demo | Resolved | Mar 21 |
| Real-time vs on-demand data? | PM | On-demand only — agents fetch on report generation, not continuously | Resolved | Mar 21 |

---

## TEAM / DACE

| Function | Name |
|---|---|
| PM | Michael Dickinson (Driver) |
| PD | Anant Khanna, Anthony Lu |
| XD | Yash Vasdev |
| Exec Sponsor | ProduHacks / Fetch.ai Track |

---

## ARTIFACTS

| Resource | Link |
|---|---|
| GitHub Repository | github.com/Michael-R-Dickinson/produhacks |

---

## APPENDIX

### A. System Architecture

The system has three layers:

1. **Frontend** (React + Vite, port 5173) — sends report requests and subscribes to a real-time SSE event stream
2. **FastAPI Bridge** (port 8000) — translates between HTTP/browser and the agent protocol, hosting the SSE endpoint
3. **Agent Bureau** — the Fetch.ai uAgents Bureau running all 5 agents. The Orchestrator fans out to 4 domain agents concurrently:
   - **Portfolio Agent** — yfinance + numpy for allocation, beta, HHI, correlations
   - **News Agent** — Finnhub API + FinBERT NLP for sentiment-scored headlines
   - **Modeling Agent** — yfinance + matplotlib for Sharpe ratio, volatility, and chart generation
   - **Alt Assets Agent** — CoinGecko + Finnhub for crypto prices, commodity prices, and cross-correlations

The Orchestrator calls Google Gemini 2.5 Flash twice: once to plan which charts to generate, and once to synthesize the final unified narrative from all agent data.

**Process model:** The entire backend runs as a single OS process with two threads — the main thread hosts FastAPI with SSE streaming, and a daemon thread runs the uAgents Bureau with all 5 agent event loops.

**Orchestration flow:**
1. Phase 1 — Fan-out to Portfolio, News, and Alt Assets agents concurrently
2. Phase 2 — Ask Gemini which charts to generate based on Phase 1 data
3. Phase 3 — Send targeted chart request to Modeling agent
4. Phase 4 — Detect contradictions, synthesize unified report via Gemini

### B. Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React 18 + TypeScript + Vite | Interactive SPA |
| Styling | Vanilla CSS with design tokens | Light theme, premium feel, no framework lock-in |
| Icons | Lucide React | Consistent iconography |
| Markdown | react-markdown + remark-gfm | Report rendering with GFM tables and formatting |
| Schema Validation | Zod | SSE event parsing and type safety |
| Real-time | Server-Sent Events (SSE) | Unidirectional agent → browser streaming |
| Agent Framework | Fetch.ai uAgents | Multi-agent protocol and Bureau hosting |
| API Bridge | FastAPI + sse-starlette | HTTP ↔ agent protocol translation |
| LLM | Google Gemini 2.5 Flash (`google.genai`) | Orchestrator narrative synthesis + chart planning |
| NLP | ProsusAI/FinBERT (HuggingFace transformers) | Financial sentiment scoring |
| Financial Data | yfinance, Finnhub API, CoinGecko API | Market data, news, crypto prices |
| Computation | NumPy, Pandas, Matplotlib | Portfolio math, charts |
| Testing | Pytest (61 tests) | Monkeypatched unit tests, zero network dependency |

### C. Environment Variables & Setup

The app ships with **`MOCK_DATA=true` by default**. The entire pipeline runs offline with zero API keys — all agents return realistic hardcoded mock data. This means you can run the full app and see a complete report immediately.

**To use real live market data**, set these environment variables in a `.env` file:

| Variable | Required | Source | Purpose |
|---|---|---|---|
| `MOCK_DATA` | No (defaults to `true`) | — | Set to `false` to enable live API calls |
| `FINNHUB_API_KEY` | Only for live mode | Free tier at finnhub.io | News headlines + commodity prices |
| `GEMINI_API_KEY` | Only for live mode | Free tier at aistudio.google.com | Orchestrator LLM synthesis + chart planning |

**Quick start:** Install backend dependencies and run the FastAPI bridge on port 8000. In a separate terminal, install frontend dependencies and run the Vite dev server on port 5173. With mock mode enabled (default), the full app works immediately with no configuration.

### D. Mock Data (Ships with app — works out of the box)

**Mock Portfolio — 12 holdings, 6 sectors:**

| Ticker | Weight | Sector |
|---|---|---|
| AAPL | 18% | Technology |
| MSFT | 14% | Technology |
| NVDA | 10% | Technology |
| META | 7% | Technology |
| UNH | 9% | Healthcare |
| JNJ | 5% | Healthcare |
| JPM | 7% | Financials |
| GS | 4% | Financials |
| XOM | 6% | Energy |
| TSLA | 6% | Consumer Discretionary |
| BTC | 8% | Crypto |
| ETH | 6% | Crypto |

**Mock Portfolio Agent output:**
- Sector allocation: Technology 49%, Healthcare 14%, Crypto 14%, Financials 11%, Energy 6%, Consumer 6%
- HHI (diversification index): 0.087 — moderate tech concentration
- Portfolio beta vs SPY: 1.12 — slightly above market risk
- 90-day pairwise correlation matrix across all equities

**Mock News Agent output — 5 FinBERT-scored headlines:**
- "Apple Reports Record Q1 Revenue Driven by iPhone Sales" → AAPL **+0.82**
- "Microsoft Azure Growth Slows Amid Cloud Competition" → MSFT **−0.35**
- "NVIDIA Unveils Next-Gen Blackwell Architecture" → NVDA **+0.91**
- "JPMorgan Warns of Commercial Real Estate Risks" → JPM **−0.48**
- "UnitedHealth Expands Medicare Advantage Coverage" → UNH **+0.55**
- Overall portfolio sentiment: **+0.29**

**Mock Modeling Agent output:**
- Sharpe ratio, annualized volatility, trend slope
- 5 matplotlib charts as base64 PNGs: regression, correlation matrix, sector performance, volatility cone, price history

**Mock Alt Assets Agent output:**
- Crypto: BTC $67,450 (bullish), ETH $3,520 (bullish), SOL $142 (neutral), FET $2.35 (bullish)
- Commodities: Gold $2,340.50 (neutral), Oil $78.25 (bearish)
- BTC dominance: 52.3%
- Cross-correlations vs equity portfolio: BTC 0.12, ETH 0.18, Gold −0.05, Oil 0.08

**Mock Contradiction Detection:**
- "JPM: News sentiment is bearish (−0.48) but it is a top holding (7% of portfolio)"

### E. Agent Data Contracts

Each agent returns a structured response to the Orchestrator via Pydantic models over the uAgents protocol:

**Portfolio Agent** returns: sector allocation (% per sector), top holdings (ticker, weight, sector), Herfindahl-Hirschman Index (diversification), portfolio beta vs SPY, and a 90-day pairwise correlation matrix across all equities.

**News / Sentiment Agent** returns: list of headlines (title, sentiment score from −1 to +1, matched tickers), aggregate sentiment per ticker, and overall portfolio-wide sentiment score.

**Modeling / Quant Agent** returns: list of holdings analyzed, Sharpe ratio, annualized volatility, trend slope, a collection of charts (each with a UUID, chart type, title, base64-encoded PNG image, and one-line summary), and an extensible metrics dictionary.

**Alt Assets Agent** returns: crypto prices with 7-day changes, trend signals (bullish/neutral/bearish per asset), BTC market dominance percentage, commodity prices (Gold, Oil), and Pearson cross-correlations of each alt asset against the equity portfolio.

### F. Frontend Specification

#### Design System — LIGHT THEME

This app uses a **clean, light, professional aesthetic**. The theme is strictly LIGHT — no dark mode.

**Color palette:**
- **Backgrounds:** soft off-white (#f8f9fb) page background, pure white (#ffffff) cards and sidebar, light gray (#f3f4f8) inputs and hover states
- **Text:** near-black (#111827) primary, medium gray (#6b7280) secondary, light gray (#9ca3af) tertiary/labels
- **Accent:** blue (#2563eb) for buttons, links, active states — with a light blue (#dbeafe) background tint for active tabs and badges
- **Semantic:** green (#10b981) for positive/bullish/complete, red (#ef4444) for negative/bearish/error, amber (#f59e0b) for warning/in-progress
- **Borders:** subtle gray (#e5e7eb) default, very light (#f0f1f3) for dividers

**Typography:** Inter font family, 14px base size, with font weights 400/500/600/700. Labels use 10–11px uppercase with letter-spacing.

**Shape & depth:** Rounded corners (8px small, 12px medium, 16px large). Very subtle shadows for elevation. A dot-grid pattern (24px spacing) on the page background for texture.

**Overall feel:** Premium fintech dashboard — clean, spacious, professional. Inspired by Linear, Stripe Dashboard, and Bloomberg Terminal (but light).

#### Layout — Single-Page Centric

CSS Grid layout with sidebar + top nav + main content:

```
┌──────────────────────────────────────────────────────┐
│ [Sidebar 240px]  │  [Top Navigation Bar]             │
│                  │  ┌──────────────────────────────┐  │
│  Wealth Council  │  │ Daily Report │ Swarm │ Port. │  │
│  logo + title    │  │ ─────────────────────────────│  │
│  "X agents       │  │ [Search markets...]  [Bell]  │  │
│   active"        │  └──────────────────────────────┘  │
│                  │                                    │
│  ┌────────────┐  │  ┌──────────────────────────────┐  │
│  │  Generate  │  │  │                              │  │
│  │  Report    │  │  │   Main Content Area          │  │
│  └────────────┘  │  │   (max-width: 960px,         │  │
│                  │  │    centered, 24px padding)    │  │
│                  │  │                              │  │
│                  │  │   Phase 1: Empty state        │  │
│                  │  │   → "Ready to Analyze" CTA    │  │
│                  │  │                              │  │
│                  │  │   Phase 2: Generating         │  │
│                  │  │   → Agent swarm graph (500px) │  │
│                  │  │                              │  │
│  ──────────────  │  │   Phase 3: Complete           │  │
│  Settings        │  │   → Graph collapses to 0px   │  │
│  Support         │  │   → Markdown report fades in  │  │
│                  │  │     with inline charts        │  │
│                  │  └──────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

**Sidebar** (240px, white, left border):
- Brand area: logo image + "Wealth Council" title (16px bold) + "X agents active" subtitle (11px gray)
- Blue CTA button: "Generate Report" with Zap icon — triggers report pipeline
- Bottom: Settings and Support links with icons

**Top Nav** (56px, white, bottom border):
- Tab navigation: Daily Report | Swarm Activity | Portfolio | Chat — active tab has light blue background tint and blue text
- Right: pill search bar ("Search markets...") + bell notification icon + blue user avatar circle

**Pages:**
- `/` — **Daily Report** (primary page, one-page centric)
- `/swarm` — Swarm Activity (full-page agent graph)
- `/portfolio` — Portfolio analytics
- `/chat` — Chat interface

#### Agent Swarm Graph Visualization

Displayed during report generation inside a 500px container with rounded corners and a radial dot-grid background. 5 agent cards positioned in a circular layout:

| Agent | Position | Icon | Color |
|---|---|---|---|
| **Orchestrator** | Center (50%, 50%) | Brain | #2563eb (blue) |
| **Portfolio Alpha** | Top-left (15%, 18%) | PieChart | #8b5cf6 (purple) |
| **Sentiment Engine** | Top-right (85%, 18%) | Newspaper | #f59e0b (amber) |
| **Quant Modeler** | Bottom-right (85%, 82%) | TrendingUp | #10b981 (green) |
| **Alt Assets** | Bottom-left (15%, 82%) | Bitcoin | #ef4444 (red) |

**Each agent card contains:**
- Header row with a circular bordered icon, agent name in bold, and a status badge ("Processing" in amber or "Complete" in green)
- Output area with a gray code-block-style background showing the agent's latest 3 "thoughts" in monospace font with a `>` prefix per line, scrollable
- Cards gently float up and down with a slow animation to feel alive

**Connection Lines** (orchestrator ↔ each agent):
- Dashed lines in each agent's signature color when active, gray when idle
- Animated dashing effect when the agent is actively working
- A small travelling dot moves along each active connection to show data flow
- Hovering on a connection line shows a tooltip with the message route (e.g., "Orchestrator → Portfolio Alpha"), message title, and description

**When report completes:** the graph smoothly collapses in height, then the rendered report fades in below with a slide-up animation.

#### Report Rendering

The completed report is rendered as formatted markdown with GitHub Flavored Markdown support (tables, bold, italics, blockquotes, horizontal rules).

- Charts generated by the Modeling Agent are embedded inline within the report as images, placed contextually next to the paragraphs that discuss their data — centered, max 500px wide
- The report appears with a smooth fade-in-up animation after the swarm graph collapses
- A date stamp appears above the report in light gray
- Report text is 14px with generous 1.8 line-height for readability
- The report reads as a unified narrative organized by investment theme (e.g., "Tech Sector Outlook", "Risk Assessment") — NOT sectioned by agent or data source

### G. Real-Time Streaming

The frontend subscribes to a Server-Sent Events (SSE) stream from the FastAPI bridge to receive real-time updates during report generation. Events include:

- **Agent status changes** — each agent transitions through idle → working → done, updating the swarm graph in real time
- **Agent thoughts** — free-text reasoning that each agent emits as it works (e.g., "Analyzing 5 headlines for AAPL sentiment..."), displayed in the agent cards
- **Agent messages** — inter-agent communication events showing what data is being sent between agents, with title and description for tooltip display
- **Report complete** — the final synthesized markdown narrative plus an array of chart objects (each containing a UUID, base64 PNG image, title, and summary)

Frontend state is managed via a React context provider with a reducer, using Zod schemas to validate all incoming events for type safety.
