import { useSwarm } from "../../context/SwarmContext";
import { AGENTS } from "../../schemas/events";
import { ArrowRight, AlertTriangle, TrendingUp, Shield } from "lucide-react";

interface IntelCard {
    agent: string;
    title: string;
    text: string;
    priority: "high" | "medium" | "low";
    icon: React.ReactNode;
}

export default function IntelligenceFeed() {
    const { state } = useSwarm();

    // Build intel cards from available data
    const cards: IntelCard[] = [];

    if (state.news) {
        const bullish = Object.entries(state.news.aggregate_sentiment).filter(([, v]) => v > 0.7);
        const bearish = Object.entries(state.news.aggregate_sentiment).filter(([, v]) => v < -0.3);

        if (bullish.length > 0) {
            cards.push({
                agent: "Sentiment Engine",
                title: `Bullish Signal: ${bullish.map(([t]) => t).join(", ")}`,
                text: `Strong positive sentiment detected across ${bullish.length} ticker${bullish.length > 1 ? "s" : ""}. Market narrative is driven by earnings beats and product announcements.`,
                priority: "high",
                icon: <TrendingUp size={14} />,
            });
        }

        if (bearish.length > 0) {
            cards.push({
                agent: "Sentiment Engine",
                title: `Risk Alert: ${bearish.map(([t]) => t).join(", ")}`,
                text: `Negative sentiment readings suggest caution. Monitor for potential downside exposure in affected positions.`,
                priority: "medium",
                icon: <AlertTriangle size={14} />,
            });
        }
    }

    if (state.modeling) {
        cards.push({
            agent: "Quant Modeler",
            title: "Momentum Analysis Complete",
            text: `Sharpe ratio at ${state.modeling.sharpe_ratio.toFixed(2)} with ${(state.modeling.volatility * 100).toFixed(1)}% annualized volatility. Trend slope is ${state.modeling.trend_slope > 0 ? "positive" : "negative"}.`,
            priority: "low",
            icon: <Shield size={14} />,
        });
    }

    if (state.alternatives) {
        cards.push({
            agent: "Alt Assets",
            title: "Crypto Market Update",
            text: `BTC trading at $${state.alternatives.crypto_prices.BTC?.toLocaleString() ?? "—"}. Portfolio correlation remains low at ${state.alternatives.cross_correlations.BTC?.toFixed(2) ?? "—"}, providing diversification benefit.`,
            priority: "low",
            icon: <TrendingUp size={14} />,
        });
    }

    if (cards.length === 0) {
        return null;
    }

    const agentColor = (name: string) => AGENTS.find((a) => a.name === name)?.color ?? "var(--accent)";

    const priorityBadge = (p: string) => {
        switch (p) {
            case "high": return { class: "badge-red", label: "HIGH PRIORITY" };
            case "medium": return { class: "badge-amber", label: "MONITOR" };
            default: return { class: "badge-green", label: "INFO" };
        }
    };

    return (
        <div className="section-gap fade-in-up">
            <div style={{ fontSize: 13, fontWeight: 600, textTransform: "uppercase", letterSpacing: 0.5, color: "var(--text-secondary)", marginBottom: 12 }}>
                Live Agent Insights
            </div>
            <div className="grid-3">
                {cards.map((card, i) => {
                    const badge = priorityBadge(card.priority);
                    return (
                        <div className="intel-card" key={i}>
                            <div className="intel-card-agent" style={{ color: agentColor(card.agent) }}>
                                {card.icon}
                                {card.agent}
                            </div>
                            <div className="intel-card-title">{card.title}</div>
                            <div className="intel-card-text">{card.text}</div>
                            <div className="intel-card-footer">
                                <span className={`intel-priority ${badge.class}`}>{badge.label}</span>
                                <span className="insight-action" style={{ marginTop: 0, fontSize: 12 }}>
                                    Explore <ArrowRight size={12} />
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
