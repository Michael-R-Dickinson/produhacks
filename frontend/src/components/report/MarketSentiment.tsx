import { useSwarm } from "../../context/SwarmContext";

export default function MarketSentiment() {
    const { state } = useSwarm();

    if (!state.news) {
        return (
            <div className="card section-gap">
                <div className="card-header">
                    <span className="card-title">Market Sentiment</span>
                    <div className="card-badge badge-blue">Fetching...</div>
                </div>
                <div className="shimmer" style={{ height: 160 }} />
            </div>
        );
    }

    const { aggregate_sentiment, headlines } = state.news;
    const tickers = Object.entries(aggregate_sentiment).sort((a, b) => b[1] - a[1]);

    const getSentimentClass = (score: number) =>
        score > 0.3 ? "positive" : score < -0.2 ? "negative" : "neutral";

    const getSentimentLabel = (score: number) =>
        score > 0.5 ? "BULLISH" : score > 0.2 ? "POSITIVE" : score < -0.3 ? "BEARISH" : score < -0.1 ? "NEGATIVE" : "NEUTRAL";

    const getLabelColor = (score: number) =>
        score > 0.3
            ? { background: "var(--green-bg)", color: "var(--green)" }
            : score < -0.2
                ? { background: "var(--red-bg)", color: "var(--red)" }
                : { background: "var(--amber-bg)", color: "var(--amber)" };

    return (
        <div className="card section-gap fade-in-up">
            <div className="card-header">
                <span className="card-title">Market Sentiment</span>
                <span className="card-badge badge-green">
                    {headlines.length} articles analyzed
                </span>
            </div>

            {/* Sentiment bars */}
            <div>
                {tickers.map(([ticker, score]) => (
                    <div className="sentiment-row" key={ticker}>
                        <span className="sentiment-ticker">{ticker}</span>
                        <div className="sentiment-bar-container">
                            <div
                                className={`sentiment-bar ${getSentimentClass(score)}`}
                                style={{ width: `${Math.abs(score) * 100}%` }}
                            />
                        </div>
                        <span className={`sentiment-score`} style={{ color: score > 0 ? "var(--green)" : "var(--red)" }}>
                            {score > 0 ? "+" : ""}{score.toFixed(2)}
                        </span>
                        <span className="sentiment-label" style={getLabelColor(score)}>
                            {getSentimentLabel(score)}
                        </span>
                    </div>
                ))}
            </div>

            {/* Headlines */}
            <div style={{ marginTop: 16 }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 10 }}>
                    Top Headlines
                </div>
                {headlines.slice(0, 3).map((h, i) => (
                    <div
                        key={i}
                        style={{
                            display: "flex",
                            gap: 10,
                            padding: "8px 0",
                            borderBottom: i < 2 ? "1px solid var(--border-light)" : "none",
                            fontSize: 13,
                            color: "var(--text-secondary)",
                            cursor: "pointer",
                            transition: "color 0.15s ease",
                        }}
                        onMouseEnter={(e) => (e.currentTarget.style.color = "var(--text-primary)")}
                        onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-secondary)")}
                    >
                        <span
                            style={{
                                fontSize: 11,
                                fontWeight: 700,
                                color: h.sentiment > 0 ? "var(--green)" : "var(--red)",
                                width: 40,
                                flexShrink: 0,
                            }}
                        >
                            {h.ticker}
                        </span>
                        <span>{h.title}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
