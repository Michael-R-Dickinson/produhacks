import { useState } from "react";
import AgentGraph from "../components/report/AgentGraph";
import ReportView from "../components/report/ReportView";
import { useSwarm } from "../context/SwarmContext";
import { Zap } from "lucide-react";

type PagePhase = "empty" | "generating" | "complete";

const KNOWLEDGE_LABELS = ["Beginner", "Intermediate", "Advanced", "Professional", "Expert"] as const;

function getPagePhase(state: {
    executiveSummary: string | null;
    agentStatuses: Record<string, string>;
    reportTriggered: boolean;
}): PagePhase {
    if (state.executiveSummary !== null) return "complete";
    const anyActive = Object.values(state.agentStatuses).some(
        (s) => s === "working" || s === "done"
    );
    if (anyActive || state.reportTriggered) return "generating";
    return "empty";
}

export default function DailyReport() {
    const { state, triggerReport } = useSwarm();
    const [knowledgeLevel, setKnowledgeLevel] = useState(2);

    const phase = getPagePhase(state);
    const today = new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });

    return (
        <div style={{ maxWidth: 960, margin: "0 auto" }}>
            {phase === "empty" && (
                <div style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    minHeight: 400,
                    gap: 16,
                }}>
                    <Zap size={48} style={{ color: "var(--accent)", opacity: 0.5 }} />
                    <h2 style={{ fontSize: 20, fontWeight: 600, color: "var(--text-primary)" }}>
                        Ready to Analyze
                    </h2>
                    <p style={{ fontSize: 14, color: "var(--text-tertiary)", maxWidth: 360, textAlign: "center" }}>
                        Trigger the agent swarm to analyze your portfolio, scan market news, and generate a comprehensive report.
                    </p>

                    {/* Knowledge Level Slider */}
                    <div className="knowledge-slider">
                        <label className="knowledge-slider__label">
                            Knowledge Level
                        </label>
                        <div className="knowledge-slider__track-wrapper">
                            <input
                                type="range"
                                min={1}
                                max={5}
                                step={1}
                                value={knowledgeLevel}
                                onChange={(e) => setKnowledgeLevel(Number(e.target.value))}
                                className="knowledge-slider__input"
                            />
                            <div className="knowledge-slider__ticks">
                                {KNOWLEDGE_LABELS.map((label, i) => (
                                    <span
                                        key={label}
                                        className={`knowledge-slider__tick ${i + 1 === knowledgeLevel ? "knowledge-slider__tick--active" : ""}`}
                                    >
                                        {label}
                                    </span>
                                ))}
                            </div>
                        </div>
                        <div className="knowledge-slider__badge">
                            {KNOWLEDGE_LABELS[knowledgeLevel - 1]}
                        </div>
                    </div>

                    <button className="sidebar-cta" onClick={() => triggerReport(knowledgeLevel)} style={{ marginTop: 8 }}>
                        <Zap size={14} />
                        Generate Report
                    </button>
                </div>
            )}

            {phase !== "empty" && (
                <div style={{
                    height: phase === "complete" ? 0 : 500,
                    overflow: "hidden",
                    transition: "height 500ms ease-in-out",
                }}>
                    <AgentGraph />
                </div>
            )}

            {phase !== "empty" && (
                <div style={{
                    opacity: phase === "complete" ? 1 : 0,
                    transition: "opacity 300ms ease 500ms",
                    pointerEvents: phase === "complete" ? "auto" : "none",
                }}>
                    <div style={{
                        fontSize: 13,
                        color: "var(--text-tertiary)",
                        marginBottom: 24,
                    }}>
                        {today}
                    </div>
                    <ReportView />
                </div>
            )}
        </div>
    );
}
