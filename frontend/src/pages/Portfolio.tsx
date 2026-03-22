import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Upload, FileText, Zap } from "lucide-react";
import { useSwarm } from "../context/SwarmContext";

export default function Portfolio() {
    const [holdings, setHoldings] = useState<{ ticker: string; quantity: number; cost: number }[]>([]);
    const [dragging, setDragging] = useState(false);
    const { triggerReport } = useSwarm();
    const navigate = useNavigate();

    const parseCSV = useCallback((text: string) => {
        const lines = text.trim().split("\n");
        const parsed: { ticker: string; quantity: number; cost: number }[] = [];
        for (let i = 1; i < lines.length; i++) {
            const parts = lines[i].split(",").map((s) => s.trim());
            if (parts.length >= 3) {
                parsed.push({
                    ticker: parts[0].toUpperCase(),
                    quantity: parseFloat(parts[1]) || 0,
                    cost: parseFloat(parts[2]) || 0,
                });
            }
        }
        setHoldings(parsed);
    }, []);

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            setDragging(false);
            const file = e.dataTransfer.files[0];
            if (file && file.name.endsWith(".csv")) {
                file.text().then(parseCSV);
            }
        },
        [parseCSV]
    );

    const handleFileSelect = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const file = e.target.files?.[0];
            if (file) file.text().then(parseCSV);
        },
        [parseCSV]
    );

    return (
        <div style={{ maxWidth: 960, margin: "0 auto" }}>
            <div className="page-header">
                <div className="page-label">Portfolio</div>
                <h2>Holdings</h2>
                <div className="page-subtitle">Import your portfolio via CSV to get personalized agent analysis.</div>
            </div>

            {/* Upload zone */}
            <div
                className={`upload-zone section-gap ${dragging ? "dragging" : ""}`}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
                onClick={() => document.getElementById("csv-input")?.click()}
            >
                <Upload size={32} style={{ color: "var(--accent)", marginBottom: 12 }} />
                <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>Drop your portfolio CSV here</div>
                <div style={{ fontSize: 13, color: "var(--text-tertiary)" }}>
                    Format: ticker, quantity, cost_basis
                </div>
                <input id="csv-input" type="file" accept=".csv" style={{ display: "none" }} onChange={handleFileSelect} />
            </div>

            {/* Demo button */}
            {holdings.length === 0 && (
                <div style={{ textAlign: "center", marginBottom: 24 }}>
                    <button
                        onClick={() => {
                            setHoldings([
                                { ticker: "AAPL", quantity: 50, cost: 142.50 },
                                { ticker: "MSFT", quantity: 35, cost: 310.20 },
                                { ticker: "NVDA", quantity: 20, cost: 485.00 },
                                { ticker: "UNH", quantity: 15, cost: 520.30 },
                                { ticker: "JPM", quantity: 25, cost: 178.40 },
                                { ticker: "GOOGL", quantity: 30, cost: 138.70 },
                                { ticker: "AMZN", quantity: 18, cost: 175.80 },
                                { ticker: "TSM", quantity: 40, cost: 105.60 },
                            ]);
                        }}
                        style={{
                            padding: "8px 20px",
                            fontSize: 13,
                            fontWeight: 600,
                            border: "1px solid var(--border-default)",
                            borderRadius: "var(--radius-sm)",
                            background: "var(--bg-card)",
                            color: "var(--accent)",
                            cursor: "pointer",
                        }}
                    >
                        <FileText size={14} style={{ marginRight: 6, verticalAlign: "middle" }} />
                        Load Demo Portfolio
                    </button>
                </div>
            )}

            {/* Holdings table */}
            {holdings.length > 0 && (
                <div className="card section-gap fade-in-up">
                    <div className="card-header">
                        <span className="card-title">Current Holdings</span>
                        <span className="card-badge badge-blue">{holdings.length} positions</span>
                    </div>

                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Ticker</th>
                                <th>Quantity</th>
                                <th>Cost Basis</th>
                                <th>Total Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {holdings.map((h) => (
                                <tr key={h.ticker}>
                                    <td style={{ fontWeight: 700 }}>{h.ticker}</td>
                                    <td>{h.quantity}</td>
                                    <td>${h.cost.toFixed(2)}</td>
                                    <td style={{ fontWeight: 600 }}>${(h.quantity * h.cost).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 16, paddingTop: 16, borderTop: "1px solid var(--border-light)" }}>
                        <div>
                            <span className="metric-label">Total Portfolio Value</span>
                            <div className="metric-value" style={{ fontSize: 22 }}>
                                ${holdings.reduce((sum, h) => sum + h.quantity * h.cost, 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </div>
                        </div>
                        <button
                            className="sidebar-cta"
                            style={{ margin: 0 }}
                            onClick={() => {
                                triggerReport();
                                navigate("/");
                            }}
                        >
                            <Zap size={14} /> Analyze with Swarm
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
