import { useSwarm } from "../context/SwarmContext";
import { AGENTS } from "../schemas/events";
import type { AgentId } from "../schemas/events";
import { Brain, PieChart, Newspaper, TrendingUp, Bitcoin, Activity } from "lucide-react";

const iconMap: Record<string, React.ReactNode> = {
    brain: <Brain size={20} />,
    "pie-chart": <PieChart size={20} />,
    newspaper: <Newspaper size={20} />,
    "trending-up": <TrendingUp size={20} />,
    bitcoin: <Bitcoin size={20} />,
};

/* ── Agent Positions on the graph ──────────────── */
const positions: Record<AgentId, { x: number; y: number }> = {
    orchestrator: { x: 50, y: 45 },
    portfolio: { x: 20, y: 15 },
    news: { x: 80, y: 15 },
    modeling: { x: 80, y: 75 },
    alternatives: { x: 20, y: 75 },
};

export default function SwarmActivity() {
    const { state } = useSwarm();
    const agentList = AGENTS.filter((a) => a.id !== "orchestrator");

    return (
        <div style={{ maxWidth: 960, margin: "0 auto" }}>
            <div className="page-header">
                <div className="page-label">Real-Time</div>
                <h2>Swarm Activity</h2>
                <div className="page-subtitle">
                    The InvestorSwarm Orchestrator is synthesizing global data streams to refine your portfolio allocation.
                </div>
            </div>

            {/* Agent Graph */}
            <div className="agent-graph-container section-gap" style={{ padding: 32 }}>
                <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet" style={{ position: "absolute", top: 0, left: 0 }}>
                    {/* Connection lines from orchestrator to each agent */}
                    {agentList.map((agent) => {
                        const from = positions.orchestrator;
                        const to = positions[agent.id];
                        const isActive = state.agentStatuses[agent.id] === "working";
                        const isDone = state.agentStatuses[agent.id] === "done";

                        return (
                            <g key={agent.id}>
                                <line
                                    x1={`${from.x}%`} y1={`${from.y}%`}
                                    x2={`${to.x}%`} y2={`${to.y}%`}
                                    stroke={isActive ? agent.color : isDone ? "#10b981" : "#e5e7eb"}
                                    strokeWidth={isActive ? 2 : 1}
                                    strokeDasharray={isActive ? "6 4" : isDone ? "none" : "4 6"}
                                    style={isActive ? { animation: "dashFlow 0.8s linear infinite" } : undefined}
                                />
                                {/* Animated dot for active connections */}
                                {isActive && (
                                    <circle r="3" fill={agent.color}>
                                        <animateMotion
                                            dur="1.5s"
                                            repeatCount="indefinite"
                                            path={`M${from.x},${from.y} L${to.x},${to.y}`}
                                        />
                                    </circle>
                                )}
                            </g>
                        );
                    })}
                </svg>

                {/* Agent nodes */}
                {AGENTS.map((agent) => {
                    const pos = positions[agent.id];
                    const status = state.agentStatuses[agent.id];
                    const isOrch = agent.id === "orchestrator";

                    return (
                        <div
                            key={agent.id}
                            className={`agent-node ${status === "working" ? "active" : ""} ${isOrch ? "orchestrator" : ""}`}
                            style={{
                                left: `${pos.x}%`,
                                top: `${pos.y}%`,
                                transform: "translate(-50%, -50%)",
                            }}
                        >
                            <div className="agent-node-circle" style={
                                status === "working" ? { borderColor: agent.color, boxShadow: `0 0 16px ${agent.color}30` } :
                                    status === "done" ? { borderColor: "#10b981" } : {}
                            }>
                                {iconMap[agent.icon]}
                            </div>
                            <span className="agent-node-label">{agent.name}</span>
                            {status === "working" && (
                                <span className="card-badge badge-amber" style={{ fontSize: 9 }}>Processing</span>
                            )}
                            {status === "done" && (
                                <span className="card-badge badge-green" style={{ fontSize: 9 }}>Complete</span>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Thought Stream + Swarm Health */}
            <div className="grid-2">
                {/* Thought Stream */}
                <div className="card">
                    <div className="card-header">
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                            <Activity size={16} style={{ color: "var(--accent)" }} />
                            <span className="card-title">Thought Stream</span>
                        </div>
                        <span className="text-xs text-muted">{state.thoughts.length} events</span>
                    </div>

                    <div style={{ maxHeight: 320, overflowY: "auto" }}>
                        {state.thoughts.length === 0 ? (
                            <div style={{ padding: 24, textAlign: "center", color: "var(--text-tertiary)", fontSize: 13 }}>
                                Waiting for agent activity...
                            </div>
                        ) : (
                            state.thoughts.map((t, i) => {
                                const agent = AGENTS.find((a) => a.id === t.agent_id);
                                return (
                                    <div className="thought-item" key={i}>
                                        <div className="thought-dot" style={{ background: agent?.color ?? "var(--accent)" }} />
                                        <div className="thought-content">
                                            <div className="thought-agent" style={{ color: agent?.color }}>{agent?.name ?? t.agent_id}</div>
                                            <div className="thought-text">{t.text}</div>
                                        </div>
                                        <div className="thought-time">
                                            {i === 0 ? "Just now" : `${i * 2}s ago`}
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                </div>

                {/* Swarm Health */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Swarm Health</span>
                    </div>

                    {state.swarmHealth ? (
                        <>
                            <div style={{ marginBottom: 16 }}>
                                <div className="flex-between" style={{ marginBottom: 6 }}>
                                    <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>Processing Power</span>
                                    <span style={{ fontSize: 20, fontWeight: 700, color: "var(--accent)" }}>
                                        {state.swarmHealth.processing_power}%
                                    </span>
                                </div>
                                <div className="health-bar">
                                    <div className="health-bar-fill" style={{ width: `${state.swarmHealth.processing_power}%` }} />
                                </div>
                            </div>

                            <div className="metrics-row" style={{ gridTemplateColumns: "1fr 1fr" }}>
                                <div className="metric-tile" style={{ padding: "12px 14px" }}>
                                    <div className="metric-label">Active Agents</div>
                                    <div className="metric-value" style={{ fontSize: 24 }}>{state.swarmHealth.active_agents}</div>
                                </div>
                                <div className="metric-tile" style={{ padding: "12px 14px" }}>
                                    <div className="metric-label">Signals / Min</div>
                                    <div className="metric-value" style={{ fontSize: 24 }}>
                                        {(state.swarmHealth.signals_per_min / 1000).toFixed(1)}k
                                    </div>
                                </div>
                            </div>

                            {/* Top signal gainers */}
                            <div style={{ marginTop: 16 }}>
                                <div className="metric-label" style={{ marginBottom: 8 }}>Top Signal Gainers</div>
                                {[
                                    { ticker: "NVDA", source: "News/Sentiment", change: "+0.91" },
                                    { ticker: "AAPL", source: "News/Portfolio", change: "+0.82" },
                                    { ticker: "BTC", source: "Alt Assets", change: "+2.4%" },
                                ].map((item) => (
                                    <div
                                        key={item.ticker}
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "space-between",
                                            padding: "8px 0",
                                            borderBottom: "1px solid var(--border-light)",
                                            fontSize: 13,
                                        }}
                                    >
                                        <div>
                                            <span style={{ fontWeight: 700 }}>{item.ticker}</span>
                                            <span style={{ fontSize: 11, color: "var(--text-tertiary)", marginLeft: 8 }}>{item.source}</span>
                                        </div>
                                        <span style={{ color: "var(--green)", fontWeight: 600 }}>{item.change}</span>
                                    </div>
                                ))}
                            </div>
                        </>
                    ) : (
                        <div style={{ padding: 24, textAlign: "center", color: "var(--text-tertiary)", fontSize: 13 }}>
                            Awaiting swarm initialization...
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
