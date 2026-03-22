# Phase 2: Agent Pipeline - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

All five agents (Portfolio, News, Modeling, Alt Assets, Orchestrator) producing a complete unified narrative markdown report -- verifiable via curl POST to the bridge /report endpoint with no frontend running. The Modeling agent is mock-only (teammate handles real implementation). All other agents implement real domain logic.

</domain>

<decisions>
## Implementation Decisions

### Report Narrative
- Professional analyst tone -- reads like a morning brief from a financial analyst
- Thematic sections organized by investment theme (e.g., "Tech Sector Outlook", "Risk Assessment", "Market Sentiment"), NOT sectioned per-agent
- Chart/visualization-heavy -- the report should lean heavily on embedded visuals
- Full report length: 2-3 screens of scrollable content
- Cross-agent contradictions flagged explicitly as dedicated insights (e.g., "Note: News sentiment is bullish on TSLA but momentum indicators show weakening trend")

### Portfolio Agent
- Mock portfolio: 10-15 stocks across 5-6 sectors, curated to surface interesting demo stories (tech-heavy concentration, bearish news + strong momentum tensions)
- Includes 1-2 crypto positions (BTC, ETH) for cross-agent interplay with Alt Assets agent
- Computes: sector allocation breakdown, Herfindahl diversification index, portfolio beta, correlation matrix
- Returns raw structured data (numbers, metrics, structured objects) -- no pre-formatted text

### News Agent
- Fetches Finnhub headlines, filters for portfolio relevance, scores sentiment with FinBERT
- Computes aggregate sentiment metrics per holding/sector
- Returns structured sentiment data + raw headlines
- Specific filtering logic, sentiment thresholds, and headline count at Claude's discretion

### Modeling Agent (Mock Only)
- Teammate handles real implementation -- stays mock for Phase 2
- Mock returns: structured metrics (Sharpe ratio, volatility numbers) + a static pre-generated base64 PNG chart image
- Static mock chart proves the chart embedding pipeline works end-to-end
- Must conform to the same Pydantic response contract so teammate's real agent is drop-in

### Alt Assets Agent
- Crypto coverage: portfolio-relevant coins + BTC and ETH always included regardless of portfolio
- Commodities: gold and crude oil (available via Finnhub, already in the stack). No real estate
- Cross-asset analysis:
  - Portfolio correlations: correlation between crypto/commodities and equity holdings
  - Trend direction: bullish/bearish/neutral indicator per alt asset from recent price action
  - BTC dominance percentage and what it signals for altcoin allocation

### Orchestrator
- Fans out to all domain agents concurrently via asyncio.gather
- Uses GPT-4o mini for narrative synthesis
- Produces thematic sections from raw agent data -- NOT a pass-through of agent summaries
- Identifies and flags cross-agent contradictions explicitly
- Response contract enforces summary field caps to prevent context window overflow

### Thought Feed (All Agents)
- Key milestones only: 3-5 thoughts per agent per report run
- Include data teasers with real numbers (e.g., "Sector allocation: 42% Tech, 18% Healthcare...")
- Each agent has its own personality/voice:
  - Portfolio: precise, metrics-focused
  - News: headline-style, punchy
  - Modeling: technical, analytical
  - Alt Assets: market-savvy, crypto-native
  - Orchestrator: synthesis narration ("Identifying cross-domain themes...", "Flagging 2 contradictions")
- Orchestrator emits synthesis narration during LLM step (not streaming LLM tokens)

### Claude's Discretion
- News agent filtering logic, sentiment thresholds, headline count
- Exact Pydantic field shapes for all request/response models (within the constraints above)
- Mock data realism level and specific mock portfolio holdings selection
- Error handling patterns for agent communication failures
- Static mock chart image selection for Modeling agent

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Agent Architecture
- `.planning/research/ARCHITECTURE.md` -- Agent communication patterns, ctx.send/ctx.send_and_receive, Bureau process model, orchestrator fan-out pattern
- `.planning/research/STACK.md` -- uAgents 0.24.0 specifics, financial API details (Finnhub 60 req/min, CoinGecko 30 req/min), GPT-4o mini for synthesis

### Pitfalls
- `.planning/research/PITFALLS.md` -- Context window overflow prevention (summary field caps), API rate limit mitigation, hosted agent statelessness

### Phase 1 Contracts
- `.planning/phases/01-foundation/01-CONTEXT.md` -- SSE event contract (3 event types), typed message models (AnalyzePortfolio, FetchNews, RunModel, AnalyzeAlternatives), process architecture (single process, Bureau in background thread)

### Project Context
- `.planning/PROJECT.md` -- Core value, constraints, key decisions
- `.planning/REQUIREMENTS.md` -- PORT-01 through PORT-05, NEWS-01 through NEWS-05, MODL-01 through MODL-05, ALT-01 through ALT-04, ORCH-01 through ORCH-05

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None -- greenfield project, Phase 1 not yet executed

### Established Patterns
- Pydantic message models pattern established in Phase 1 context (typed per-agent requests and responses)
- SSE event emission pattern (emit_thought() calls at key computation steps)
- asyncio.Queue for event streaming to FastAPI bridge

### Integration Points
- Phase 1 FastAPI bridge: /report endpoint triggers orchestrator, SSE streams agent events
- Phase 1 Pydantic models: agents implement the typed request/response contracts
- Phase 3 React app: consumes SSE events powered by the thought emissions defined here
- Teammate's Modeling agent: must match the ModelResponse Pydantic contract

</code_context>

<specifics>
## Specific Ideas

- The mock portfolio should be curated to create compelling cross-agent stories -- e.g., a tech-heavy portfolio where news sentiment conflicts with momentum indicators
- Including BTC/ETH in the portfolio creates a natural bridge between Portfolio and Alt Assets agents
- The well-featured modeling agent with strong visualizations is a key priority (teammate's domain)
- The report should feel like something a financial professional would actually read, not a hackathon demo artifact

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 02-agent-pipeline*
*Context gathered: 2026-03-21*
