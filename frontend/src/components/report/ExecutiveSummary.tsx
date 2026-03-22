import { useSwarm } from "../../context/SwarmContext";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Sparkles, TrendingUp, ArrowUpRight } from "lucide-react";

export default function ExecutiveSummary() {
    const { state } = useSwarm();

    if (!state.executiveSummary) {
        return (
            <div className="card section-gap">
                <div className="card-header">
                    <div className="card-title">Executive Summary</div>
                    <div className="card-badge badge-blue">Synthesizing...</div>
                </div>
                <div className="shimmer shimmer-line" />
                <div className="shimmer shimmer-line medium" />
                <div className="shimmer shimmer-line short" />
            </div>
        );
    }

    return (
        <div className="card section-gap fade-in-up">
            <div className="card-header">
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <Sparkles size={16} style={{ color: "var(--accent)" }} />
                    <span className="card-title">Executive Summary</span>
                </div>
                <div className="card-badge badge-green">Synthesized</div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 24 }}>
                <div style={{ fontSize: 14, lineHeight: 1.7, color: "var(--text-secondary)" }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{state.executiveSummary}</ReactMarkdown>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 12, minWidth: 140 }}>
                    <div className="metric-tile" style={{ padding: "12px 16px", textAlign: "center" }}>
                        <div className="metric-label">Alpha Signal</div>
                        <div className="metric-value positive" style={{ fontSize: 22 }}>
                            <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 4 }}>
                                +4.2% <ArrowUpRight size={16} />
                            </span>
                        </div>
                        <div className="metric-delta" style={{ color: "var(--green)", justifyContent: "center" }}>
                            <TrendingUp size={12} /> Expected Yield
                        </div>
                    </div>

                    <div className="metric-tile" style={{ padding: "12px 16px", textAlign: "center" }}>
                        <div className="metric-label">Overall Sentiment</div>
                        <div className="metric-value" style={{ fontSize: 22 }}>
                            {state.news ? (state.news.overall_sentiment * 100).toFixed(0) + "%" : "—"}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
