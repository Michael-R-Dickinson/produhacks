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
    emit(5000, { agent_id: "alternatives", type: "status", status: "done" });

    // ── Phase 6: Orchestrator synthesizes ──
    emit(5800, { agent_id: "orchestrator", type: "thought", text: "All agents reported. Cross-referencing signals for contradictions..." });
    emit(6400, { agent_id: "orchestrator", type: "thought", text: "Divergence detected: NVDA news sentiment bullish (0.91) but portfolio tech concentration already at 42%" });
    emit(7000, {
        agent_id: "orchestrator",
        type: "report_section",
        section: "executive_summary",
        data: {
            summary:
                "Global markets exhibit sustained resilience as the **Portfolio Alpha** engine detects a structural shift in medium-term momentum. Liquidity depth has improved by 14% across tech-heavy indices, while the **Risk Vector** remains within historical norms despite geopolitical volatility. The swarm has identified a **structural breakout** in emerging tech verticals, counter-balanced by defensive shifts in macro liquidity. Sentiment remains asymmetric.",
        },
    });
    emit(7200, { agent_id: "orchestrator", type: "status", status: "done" });

    // ── Swarm health update ──
    emit(7400, {
        agent_id: "orchestrator",
        type: "swarm_health",
        active_agents: 5,
        signals_per_min: 4200,
        processing_power: 94,
    });

    // Cleanup
    return () => timeouts.forEach(clearTimeout);
}
