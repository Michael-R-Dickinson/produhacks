import type { SSEEvent } from "../schemas/events";

/**
 * Mock SSE emitter — simulates the full agent report generation flow.
 * Each event fires with realistic delays mimicking actual agent processing.
 * Your friend's backend just needs to emit these same event shapes at /events.
 */
export function startMockSSE(onEvent: (event: SSEEvent) => void): () => void {
    const timeouts: ReturnType<typeof setTimeout>[] = [];

    const emit = (delay: number, event: SSEEvent) => {
        timeouts.push(setTimeout(() => onEvent(event), delay));
    };

    // ── Phase 1: Orchestrator wakes up ──
    emit(200, { agent_id: "orchestrator", type: "status", status: "working" });
    emit(400, { agent_id: "orchestrator", type: "thought", text: "Initiating daily intelligence synthesis. Dispatching requests to all domain agents..." });

    // ── Orchestrator dispatches to all agents ──
    emit(500, { agent_id: "orchestrator", type: "agent_message", from: "orchestrator", to: "portfolio", title: "AnalyzePortfolio", description: "Analyze current holdings, sector allocation, and concentration risk", direction: "request" });
    emit(600, { agent_id: "orchestrator", type: "agent_message", from: "orchestrator", to: "news", title: "FetchNews", description: "Fetch recent headlines and run sentiment analysis for portfolio tickers", direction: "request" });
    emit(700, { agent_id: "orchestrator", type: "agent_message", from: "orchestrator", to: "modeling", title: "RunModel", description: "Compute risk metrics, Sharpe ratio, and generate trend analysis", direction: "request" });
    emit(750, { agent_id: "orchestrator", type: "agent_message", from: "orchestrator", to: "alternatives", title: "AnalyzeAlternatives", description: "Fetch crypto prices and compute cross-correlations with portfolio", direction: "request" });

    // ── Phase 2: Portfolio Agent ──
    emit(800, { agent_id: "portfolio", type: "status", status: "working" });
    emit(1000, { agent_id: "portfolio", type: "thought", text: "Loading portfolio holdings — 12 positions across 6 sectors" });
    emit(1800, { agent_id: "portfolio", type: "thought", text: "Computing sector allocation and Herfindahl concentration index..." });
    emit(2600, { agent_id: "portfolio", type: "thought", text: "Portfolio beta calculated at 1.12 against S&P 500 benchmark" });
    emit(3200, {
        agent_id: "portfolio",
        type: "report_section",
        section: "portfolio",
        data: {
            sector_allocation: {
                Technology: 0.42,
                Healthcare: 0.18,
                Financials: 0.15,
                "Consumer Discretionary": 0.12,
                Energy: 0.08,
                Other: 0.05,
            },
            top_holdings: [
                { ticker: "AAPL", weight: 0.18, sector: "Technology" },
                { ticker: "MSFT", weight: 0.15, sector: "Technology" },
                { ticker: "NVDA", weight: 0.09, sector: "Technology" },
                { ticker: "UNH", weight: 0.08, sector: "Healthcare" },
                { ticker: "JPM", weight: 0.07, sector: "Financials" },
            ],
            herfindahl_index: 0.087,
            portfolio_beta: 1.12,
        },
    });
    emit(3300, { agent_id: "portfolio", type: "agent_message", from: "portfolio", to: "orchestrator", title: "PortfolioResponse", description: "Portfolio analysis complete: 12 positions, 42% tech concentration, beta 1.12", direction: "response" });
    emit(3400, { agent_id: "portfolio", type: "status", status: "done" });

    // ── Phase 3: News & Sentiment Agent ──
    emit(1200, { agent_id: "news", type: "status", status: "working" });
    emit(1500, { agent_id: "news", type: "thought", text: "Fetching headlines from Finnhub and NewsAPI for portfolio tickers..." });
    emit(2200, { agent_id: "news", type: "thought", text: "Found 23 relevant articles. Running sentiment analysis pipeline..." });
    emit(3000, { agent_id: "news", type: "thought", text: "NVDA sentiment strongly bullish (0.91) — Blackwell Ultra chip announcement driving positive coverage" });
    emit(3800, { agent_id: "news", type: "thought", text: "JPM sentiment bearish (-0.48) — commercial real estate risk warnings" });
    emit(4400, {
        agent_id: "news",
        type: "report_section",
        section: "news",
        data: {
            headlines: [
                { title: "Apple reports record Q1 revenue driven by iPhone 16 demand", sentiment: 0.82, ticker: "AAPL" },
                { title: "Microsoft Azure growth slows amid enterprise spending pullback", sentiment: -0.35, ticker: "MSFT" },
                { title: "NVIDIA announces next-gen Blackwell Ultra chips for AI data centers", sentiment: 0.91, ticker: "NVDA" },
                { title: "JPMorgan warns of commercial real estate risks in Q2 outlook", sentiment: -0.48, ticker: "JPM" },
                { title: "UnitedHealth Group expands Medicare Advantage network coverage", sentiment: 0.55, ticker: "UNH" },
            ],
            aggregate_sentiment: { AAPL: 0.82, MSFT: -0.35, NVDA: 0.91, JPM: -0.48, UNH: 0.55 },
            overall_sentiment: 0.29,
        },
    });
    emit(4500, { agent_id: "news", type: "agent_message", from: "news", to: "orchestrator", title: "NewsResponse", description: "Sentiment analysis complete: 23 articles processed, overall sentiment +0.29", direction: "response" });
    emit(4600, { agent_id: "news", type: "status", status: "done" });

    // ── Phase 4: Modeling Agent ──
    emit(1600, { agent_id: "modeling", type: "status", status: "working" });
    emit(2000, { agent_id: "modeling", type: "thought", text: "Pulling 1-year historical price data from yfinance for all holdings..." });
    emit(2800, { agent_id: "modeling", type: "thought", text: "Running linear regression on portfolio value trajectory..." });
    emit(3600, { agent_id: "modeling", type: "thought", text: "Computing Sharpe ratio, volatility metrics, and maximum drawdown..." });
    emit(4200, { agent_id: "modeling", type: "thought", text: "Generating correlation matrix heatmap across holdings..." });
    emit(5200, {
        agent_id: "modeling",
        type: "report_section",
        section: "modeling",
        data: {
            sharpe_ratio: 1.34,
            volatility: 0.187,
            trend_slope: 0.0023,
            chart_base64: null,
            metrics: { r_squared: 0.74, max_drawdown: -0.087, beta: 1.12 },
        },
    });
    emit(5300, { agent_id: "modeling", type: "agent_message", from: "modeling", to: "orchestrator", title: "ModelResponse", description: "Risk modeling complete: Sharpe 1.34, volatility 18.7%, max drawdown -8.7%", direction: "response" });
    emit(5400, { agent_id: "modeling", type: "status", status: "done" });

    // ── Phase 5: Alternatives Agent ──
    emit(2000, { agent_id: "alternatives", type: "status", status: "working" });
    emit(2400, { agent_id: "alternatives", type: "thought", text: "Fetching crypto prices from CoinGecko — BTC, ETH, SOL, FET..." });
    emit(3200, { agent_id: "alternatives", type: "thought", text: "Computing cross-correlations between crypto and traditional portfolio..." });
    emit(4000, { agent_id: "alternatives", type: "thought", text: "BTC correlation to portfolio: 0.12 — low, providing diversification benefit" });
    emit(4800, {
        agent_id: "alternatives",
        type: "report_section",
        section: "alternatives",
        data: {
            crypto_prices: { BTC: 67450.0, ETH: 3520.0, SOL: 142.0, FET: 2.35 },
            cross_correlations: { BTC: 0.12, ETH: 0.18, GOLD: -0.05, OIL: 0.08 },
        },
    });
    emit(4900, { agent_id: "alternatives", type: "agent_message", from: "alternatives", to: "orchestrator", title: "AlternativesResponse", description: "Alt analysis complete: BTC correlation 0.12, providing diversification benefit", direction: "response" });
    emit(5000, { agent_id: "alternatives", type: "status", status: "done" });

    // ── Phase 6: Orchestrator synthesizes ──
    emit(5800, { agent_id: "orchestrator", type: "thought", text: "All agents reported. Cross-referencing signals for contradictions..." });
    emit(6400, { agent_id: "orchestrator", type: "thought", text: "Divergence detected: JPM news sentiment bearish (-0.48) but it is a top holding at 7% weight" });
    emit(6800, { agent_id: "orchestrator", type: "thought", text: "Synthesizing unified narrative report via Gemini..." });

    const mockReport = `# Daily Investment Intelligence Report

## Executive Summary

Your portfolio is positioned with a **moderate growth tilt**, carrying a beta of **1.12** against the S\&P 500 and an annualized Sharpe ratio of **1.34**. Technology dominates at **42% allocation**, which is above the recommended 30% threshold for a diversified portfolio. Overall news sentiment is **mildly bullish (+0.29)**, but cross-signal analysis reveals one notable contradiction that warrants attention.

---

## Tech Sector Outlook

The technology sector continues to drive portfolio returns, with your four tech holdings (AAPL, MSFT, NVDA, META) comprising nearly half of total value. **NVIDIA** stands out with the strongest sentiment signal at **+0.91**, fueled by the Blackwell Ultra chip announcement targeting AI data center workloads. Apple also sees bullish coverage (**+0.82**) on the back of record Q1 revenue driven by iPhone demand.

However, **Microsoft shows bearish drift** at **-0.35** as Azure growth decelerates amid enterprise spending pullback. Given MSFT's 15% portfolio weight, this warrants monitoring — a sustained Azure slowdown could drag portfolio returns given the high intra-sector correlation (\`0.82\`) between your tech holdings.

> **Key Takeaway:** Tech concentration at 42% with an HHI of 0.087 indicates moderate concentration risk. Consider whether NVDA's strong momentum justifies adding exposure vs. rebalancing toward underweight sectors.

## Risk Assessment

Quantitative modeling reports an annualized volatility of **18.7%** with a maximum drawdown of **-8.7%** over the lookback period. The portfolio beta of **1.12** means you're carrying roughly 12% more systematic risk than the market benchmark. The trend regression shows a positive slope of **0.0023**, indicating upward momentum, but the R-squared of **0.74** suggests meaningful dispersion around the trendline.

The Herfindahl-Hirschman Index at **0.087** confirms moderate diversification — not dangerously concentrated, but tilted enough that a tech sector rotation would disproportionately impact returns.

## Financials & Healthcare

**JPMorgan** (**-0.48** sentiment) has flagged commercial real estate risks in its Q2 outlook. At 7% portfolio weight, this is your largest financial holding. The bearish sentiment contrasts with the broader portfolio's bullish lean, creating a **cross-signal contradiction**: your overall sentiment reads positive, but one of your significant positions faces sector-specific headwinds.

**UnitedHealth** provides a bullish counterpoint (**+0.55**) with Medicare Advantage network expansion. Healthcare at 18% allocation offers defensive balance against your growth-heavy tech exposure.

> **Contradiction Alert:** JPM carries bearish sentiment (-0.48) despite being a 7% holding. Monitor CRE exposure in upcoming earnings.

## Alternative Assets & Diversification

Bitcoin trades at **$67,450** with bullish momentum, while Ethereum holds at **$3,520**. Critically, BTC's correlation to your equity portfolio is just **0.12** — confirming genuine diversification benefit. Gold shows a **-0.05** correlation, acting as a true hedge. Oil at **$78.25** is slightly bearish with a weak **0.08** correlation to equities.

The crypto allocation (BTC 8%, ETH 6%) is contributing to portfolio diversification without adding correlated risk. BTC market dominance at **52.3%** suggests the broader crypto market is consolidating around major assets.

## Actionable Summary

1. **Monitor MSFT** — Azure deceleration could widen the gap between NVDA's bullish momentum and MSFT's drag
2. **Watch JPM CRE exposure** — bearish sentiment on a 7% holding is a yellow flag
3. **Tech rebalancing** — 42% concentration warrants review; consider trimming into healthcare or financials
4. **Crypto thesis intact** — low correlation confirms diversification value at current allocation levels

*Report generated by Wealth Council multi-agent intelligence platform. All metrics computed from deterministic sources with full data traceability.*`;

    emit(7200, {
        agent_id: "orchestrator",
        type: "report_complete",
        markdown: mockReport,
        charts: [],
    });
    emit(7400, { agent_id: "orchestrator", type: "status", status: "done" });

    // ── Swarm health update ──
    emit(7600, {
        agent_id: "orchestrator",
        type: "swarm_health",
        active_agents: 5,
        signals_per_min: 4200,
        processing_power: 94,
    });

    // Cleanup
    return () => timeouts.forEach(clearTimeout);
}
