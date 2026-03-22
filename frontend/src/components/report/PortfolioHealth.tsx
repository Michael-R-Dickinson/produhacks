import { useSwarm } from "../../context/SwarmContext";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = ["#2563eb", "#8b5cf6", "#f59e0b", "#10b981", "#ef4444", "#9ca3af"];

export default function PortfolioHealth() {
    const { state } = useSwarm();

    if (!state.portfolio) {
        return (
            <div className="card section-gap">
                <div className="card-header">
                    <span className="card-title">Portfolio Health</span>
                    <div className="card-badge badge-blue">Analyzing...</div>
                </div>
                <div style={{ height: 200 }} className="shimmer" />
            </div>
        );
    }

    const { sector_allocation, herfindahl_index, portfolio_beta, top_holdings } = state.portfolio;
    const chartData = Object.entries(sector_allocation).map(([name, value]) => ({
        name,
        value: Math.round(value * 100),
    }));

    const diversificationLevel =
        herfindahl_index < 0.1 ? "Well Diversified" : herfindahl_index < 0.18 ? "Moderate" : "Concentrated";
    const diversificationColor =
        herfindahl_index < 0.1 ? "badge-green" : herfindahl_index < 0.18 ? "badge-amber" : "badge-red";

    return (
        <div className="card section-gap fade-in-up">
            <div className="card-header">
                <span className="card-title">Portfolio Health</span>
                <span className={`card-badge ${diversificationColor}`}>{diversificationLevel}</span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "180px 1fr", gap: 24 }}>
                {/* Donut Chart */}
                <div style={{ position: "relative" }}>
                    <ResponsiveContainer width={180} height={180}>
                        <PieChart>
                            <Pie
                                data={chartData}
                                innerRadius={55}
                                outerRadius={80}
                                paddingAngle={3}
                                dataKey="value"
                                stroke="none"
                            >
                                {chartData.map((_entry, i) => (
                                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    background: "white",
                                    border: "1px solid #e5e7eb",
                                    borderRadius: 8,
                                    fontSize: 12,
                                }}
                                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                                formatter={(value: any) => [`${value}%`, "Allocation"]}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                    <div
                        style={{
                            position: "absolute",
                            top: "50%",
                            left: "50%",
                            transform: "translate(-50%, -50%)",
                            textAlign: "center",
                        }}
                    >
                        <div style={{ fontSize: 10, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: 0.5 }}>
                            HHI
                        </div>
                        <div style={{ fontSize: 20, fontWeight: 700 }}>{herfindahl_index.toFixed(3)}</div>
                    </div>
                </div>

                {/* Allocation list */}
                <div>
                    {chartData.map((sector, i) => (
                        <div
                            key={sector.name}
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 10,
                                padding: "6px 0",
                                borderBottom: i < chartData.length - 1 ? "1px solid var(--border-light)" : "none",
                            }}
                        >
                            <div
                                style={{
                                    width: 8,
                                    height: 8,
                                    borderRadius: "50%",
                                    background: COLORS[i % COLORS.length],
                                    flexShrink: 0,
                                }}
                            />
                            <span style={{ flex: 1, fontSize: 13 }}>{sector.name}</span>
                            <span style={{ fontSize: 13, fontWeight: 700 }}>{sector.value}%</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Bottom metrics */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginTop: 16 }}>
                <div className="metric-tile" style={{ padding: "10px 14px" }}>
                    <div className="metric-label">Beta</div>
                    <div className="metric-value" style={{ fontSize: 20 }}>{portfolio_beta.toFixed(2)}</div>
                </div>
                <div className="metric-tile" style={{ padding: "10px 14px" }}>
                    <div className="metric-label">Holdings</div>
                    <div className="metric-value" style={{ fontSize: 20 }}>{top_holdings.length}</div>
                </div>
                <div className="metric-tile" style={{ padding: "10px 14px" }}>
                    <div className="metric-label">Top Weight</div>
                    <div className="metric-value" style={{ fontSize: 20 }}>{(top_holdings.length > 0 ? top_holdings[0].weight * 100 : 0).toFixed(0)}%</div>
                </div>
            </div>
        </div>
    );
}
