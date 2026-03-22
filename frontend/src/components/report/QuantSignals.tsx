import { useSwarm } from "../../context/SwarmContext";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { ArrowRight } from "lucide-react";

// Generate synthetic momentum data for demo
function generateMomentumData() {
    const data = [];
    let portfolio = 100;
    let benchmark = 100;
    const months = ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"];
    for (let i = 0; i < months.length; i++) {
        portfolio += (Math.random() - 0.35) * 8;
        benchmark += (Math.random() - 0.4) * 5;
        data.push({
            month: months[i],
            portfolio: Math.round(portfolio * 100) / 100,
            benchmark: Math.round(benchmark * 100) / 100,
        });
    }
    return data;
}

const momentumData = generateMomentumData();

export default function QuantSignals() {
    const { state } = useSwarm();

    if (!state.modeling) {
        return (
            <div className="card section-gap">
                <div className="card-header">
                    <span className="card-title">Quantitative Signals</span>
                    <div className="card-badge badge-blue">Computing...</div>
                </div>
                <div className="shimmer" style={{ height: 200 }} />
            </div>
        );
    }

    const { sharpe_ratio, volatility, metrics } = state.modeling;
    const maxDrawdown = metrics?.max_drawdown ?? -0.087;
    const rSquared = metrics?.r_squared ?? 0.74;

    return (
        <div className="card section-gap fade-in-up">
            <div className="card-header">
                <span className="card-title">Quantitative Signals</span>
                <span className="card-badge badge-green">Analysis Complete</span>
            </div>

            {/* Momentum Chart */}
            <div style={{ marginBottom: 20 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                    <div style={{ fontSize: 14, fontWeight: 600 }}>Momentum Backtest</div>
                    <div style={{ display: "flex", gap: 4 }}>
                        {["1M", "6M", "1Y"].map((t, i) => (
                            <button
                                key={t}
                                style={{
                                    padding: "4px 12px",
                                    fontSize: 11,
                                    fontWeight: 600,
                                    border: "1px solid var(--border-default)",
                                    borderRadius: "var(--radius-full)",
                                    background: i === 1 ? "var(--accent)" : "var(--bg-card)",
                                    color: i === 1 ? "white" : "var(--text-secondary)",
                                    cursor: "pointer",
                                }}
                            >
                                {t}
                            </button>
                        ))}
                    </div>
                </div>

                <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={momentumData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f1f3" />
                        <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                        <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                        <Tooltip
                            contentStyle={{
                                background: "white",
                                border: "1px solid #e5e7eb",
                                borderRadius: 8,
                                fontSize: 12,
                            }}
                        />
                        <Line type="monotone" dataKey="portfolio" stroke="#2563eb" strokeWidth={2} dot={false} name="Portfolio" />
                        <Line type="monotone" dataKey="benchmark" stroke="#d1d5db" strokeWidth={2} dot={false} name="S&P 500" strokeDasharray="5 5" />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* Agent-generated PNGs (base64) — shown when backend/mock sends charts[] */}
            {state.modeling.charts && state.modeling.charts.length > 0 && (
                <div style={{ marginBottom: 20 }}>
                    <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>Model charts</div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "flex-start" }}>
                        {state.modeling.charts.slice(0, 6).map((c) => (
                            <figure key={c.chart_type} style={{ margin: 0, maxWidth: 280 }}>
                                <img
                                    src={`data:image/png;base64,${c.image_base64}`}
                                    alt={c.title}
                                    style={{
                                        width: "100%",
                                        height: "auto",
                                        borderRadius: 8,
                                        border: "1px solid var(--border-default)",
                                    }}
                                />
                                <figcaption style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 6 }}>
                                    {c.title}
                                </figcaption>
                            </figure>
                        ))}
                    </div>
                </div>
            )}

            {/* Metric tiles */}
            <div className="metrics-row">
                <div className="metric-tile">
                    <div className="metric-label">Sharpe Ratio</div>
                    <div className="metric-value positive" style={{ fontSize: 22 }}>{sharpe_ratio.toFixed(2)}</div>
                </div>
                <div className="metric-tile">
                    <div className="metric-label">Volatility</div>
                    <div className="metric-value" style={{ fontSize: 22 }}>{(volatility * 100).toFixed(1)}%</div>
                </div>
                <div className="metric-tile">
                    <div className="metric-label">Max Drawdown</div>
                    <div className="metric-value negative" style={{ fontSize: 22 }}>{(maxDrawdown * 100).toFixed(1)}%</div>
                </div>
                <div className="metric-tile">
                    <div className="metric-label">R² Fit</div>
                    <div className="metric-value" style={{ fontSize: 22 }}>{rSquared.toFixed(2)}</div>
                </div>
            </div>

            {/* Cross-agent insight */}
            {state.news && state.news.aggregate_sentiment.NVDA > 0.7 && (
                <div className="insight-callout warning" style={{ marginTop: 16 }}>
                    <div className="insight-title">Divergence Detected</div>
                    <div className="insight-text">
                        News sentiment is bullish on NVDA ({state.news.aggregate_sentiment.NVDA.toFixed(2)}),
                        but portfolio tech concentration is already at {state.portfolio ? (state.portfolio.sector_allocation.Technology * 100).toFixed(0) : "—"}%.
                        The momentum backtest shows mixed signals. Consider the divergence before adding to your position.
                    </div>
                    <span className="insight-action">
                        Ask about this <ArrowRight size={14} />
                    </span>
                </div>
            )}
        </div>
    );
}
