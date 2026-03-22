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

## UI Design Language (V0)

The V0 frontend should look polished and production-ready, not like a prototype.

**Aesthetic:** Clean, minimal, light-mode data dashboard. No glass effects or gradients -- depth comes from subtle shadows and borders.

**Foundation:**
- Font: Inter (400, 500, 600, 700 weights)
- Base font size: 14px
- Background: `#f8f9fb` with a subtle radial dot grid pattern (24x24px spacing)
- Cards: white (`#ffffff`), 1px border (`#e5e7eb`), 12px border-radius, 24px padding
- Shadows: light and layered (1-2px blur at 4-6% opacity)

**Colors:**
- Accent: `#2563eb` (interactive elements, CTAs, active states)
- Accent light: `#dbeafe` (highlights, active tab backgrounds)
- Text primary: `#111827`, secondary: `#6b7280`, tertiary: `#9ca3af`
- Status: green `#10b981` (success/idle), amber `#f59e0b` (working), red `#ef4444` (error)

**Agent Graph (initial landing state):**
- Agent nodes are white cards with subtle shadow, positioned in a connected layout
- Each node shows agent name, a 32px circular icon, and a short purpose description
- Nodes have a gentle floating animation (4s cycle, +/-6px vertical)
- Connection lines between agents are SVG with animated dashed strokes
- Hover on a node: shadow deepens, card lifts 2px, border shifts to accent blue

**Report View (post-generation):**
- Rendered using `react-markdown` (^10.1.0) with `remark-gfm` (^4.0.1) for full GFM support (tables, strikethrough, task lists)
- 1.8 line-height for readability
- Charts display inline, max-width 500px, centered
- Fade-in-up entrance animation (0.5s ease)
- The V0 report template should not be plain -- it should emulate a polished, professionally written report using bold, italics, headings, horizontal rules, tables, and bullet points to create visual hierarchy and readability

**Interactive Elements:**
- Primary button: solid accent blue, white text, subtle lift on hover
- Cards lift on hover with enhanced shadow
- All transitions: 0.15s ease

**Nice-to-Have Polish:**
- Hover on connection lines shows a tooltip with the message type being passed between agents (semi-transparent white background, subtle shadow)
- Status dots on agent nodes pulse with opacity animation (1.5s cycle) when the agent is working
- Agent nodes show a monospace output area below the description for streaming "thought" text during generation
- Modal on agent card click: 560px wide, slide-up entrance, showing agent details and external API logos if applicable

ultrathink