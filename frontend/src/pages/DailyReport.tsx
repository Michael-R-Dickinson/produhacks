import { useSwarm } from "../context/SwarmContext";
import ExecutiveSummary from "../components/report/ExecutiveSummary";
import PortfolioHealth from "../components/report/PortfolioHealth";
import MarketSentiment from "../components/report/MarketSentiment";
import QuantSignals from "../components/report/QuantSignals";
import IntelligenceFeed from "../components/report/IntelligenceFeed";
import { Calendar, Download } from "lucide-react";

export default function DailyReport() {
    const { state } = useSwarm();

    const activeCount = Object.values(state.agentStatuses).filter((s) => s === "working").length;
    const doneCount = Object.values(state.agentStatuses).filter((s) => s === "done").length;
    const today = new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });

    return (
        <div style={{ maxWidth: 960, margin: "0 auto" }}>
            {/* Page header */}
            <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                    <div className="page-label">Market Intel · {today}</div>
                    <h2>The Daily <em style={{ fontStyle: "italic", fontWeight: 700 }}>Intelligence</em> Report.</h2>
                    <div className="page-header-meta">
                        <span style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "var(--text-tertiary)" }}>
                            <Calendar size={12} />
                            {today}
                        </span>
                        {activeCount > 0 && (
                            <span className="card-badge badge-amber" style={{ fontSize: 10 }}>
                                {activeCount} agent{activeCount > 1 ? "s" : ""} processing
                            </span>
                        )}
                        {doneCount === 5 && (
                            <span className="card-badge badge-green" style={{ fontSize: 10 }}>
                                All agents complete
                            </span>
                        )}
                    </div>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                    <button
                        style={{
                            padding: "8px 16px",
                            fontSize: 12,
                            fontWeight: 600,
                            border: "1px solid var(--border-default)",
                            borderRadius: "var(--radius-sm)",
                            background: "var(--bg-card)",
                            color: "var(--text-secondary)",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            gap: 6,
                        }}
                    >
                        <Calendar size={12} /> Archive
                    </button>
                    <button
                        style={{
                            padding: "8px 16px",
                            fontSize: 12,
                            fontWeight: 600,
                            border: "none",
                            borderRadius: "var(--radius-sm)",
                            background: "var(--accent)",
                            color: "white",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            gap: 6,
                        }}
                    >
                        <Download size={12} /> Download PDF
                    </button>
                </div>
            </div>

            {/* Report sections — each renders from SSE data */}
            <ExecutiveSummary />

            <div className="grid-2 section-gap">
                <PortfolioHealth />
                <MarketSentiment />
            </div>

            <QuantSignals />
            <IntelligenceFeed />
        </div>
    );
}
