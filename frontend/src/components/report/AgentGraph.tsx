import { useMemo, useRef, useState } from "react";
import { Brain, PieChart, Newspaper, TrendingUp, Bitcoin } from "lucide-react";
import { useSwarm } from "../../context/SwarmContext";
import { AGENTS } from "../../schemas/events";
import type { AgentId } from "../../schemas/events";

const iconMap: Record<string, React.ReactNode> = {
    brain: <Brain size={20} />,
    "pie-chart": <PieChart size={20} />,
    newspaper: <Newspaper size={20} />,
    "trending-up": <TrendingUp size={20} />,
    bitcoin: <Bitcoin size={20} />,
};

const defaultPositions: Record<AgentId, { x: number; y: number }> = {
    orchestrator: { x: 50, y: 50 },
    portfolio: { x: 20, y: 22 },
    news: { x: 78, y: 20 },
    modeling: { x: 80, y: 78 },
    alternatives: { x: 22, y: 80 },
};

interface EdgeHover {
    agentId: AgentId;
    x: number;
    y: number;
}

export default function AgentGraph(): JSX.Element {
    const { state } = useSwarm();
    const containerRef = useRef<HTMLDivElement>(null);
    const [edgeHover, setEdgeHover] = useState<EdgeHover | null>(null);

    const agentList = AGENTS.filter((a) => a.id !== "orchestrator");

    const latestThoughts = useMemo(() => {
        const map: Partial<Record<AgentId, string>> = {};
        for (const t of state.thoughts) {
            if (!map[t.agent_id]) map[t.agent_id] = t.text;
        }
        return map;
    }, [state.thoughts]);

    const handleEdgeEnter = (agentId: AgentId, e: React.MouseEvent) => {
        if (!containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        setEdgeHover({
            agentId,
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
        });
    };

    const handleEdgeLeave = () => {
        setEdgeHover(null);
    };

    return (
        <div
            className="agent-graph-container"
            ref={containerRef}
            style={{
                padding: 0,
                background: "radial-gradient(circle at 50% 50%, #f0f4ff 0%, var(--bg-card) 70%)",
                position: "relative",
            }}
        >
            {/* SVG connection lines — viewBox 0 0 100 100 maps directly to % positions */}
            <svg
                width="100%"
                height="100%"
                viewBox="0 0 100 100"
                preserveAspectRatio="none"
                style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
            >
                {agentList.map((agent) => {
                    const from = defaultPositions.orchestrator;
                    const to = defaultPositions[agent.id];
                    const isActive = state.agentStatuses[agent.id] === "working";
                    const isDone = state.agentStatuses[agent.id] === "done";

                    return (
                        <g key={agent.id}>
                            {/* Hidden path for animateMotion reference */}
                            <path
                                id={`path-${agent.id}`}
                                d={`M${from.x},${from.y} L${to.x},${to.y}`}
                                fill="none"
                                stroke="none"
                            />

                            {/* Visible edge line */}
                            <line
                                x1={from.x} y1={from.y}
                                x2={to.x} y2={to.y}
                                stroke={isActive ? agent.color : isDone ? agent.color : "#d1d5db"}
                                strokeWidth={isActive ? 2 : 1.5}
                                strokeOpacity={isActive ? 0.9 : isDone ? 0.5 : 0.35}
                                strokeDasharray={isActive ? "8 4" : "6 6"}
                                strokeLinecap="round"
                                style={isActive ? { animation: "dashFlow 0.8s linear infinite" } : undefined}
                            />

                            {/* Invisible wider hit area for hover */}
                            <line
                                x1={from.x} y1={from.y}
                                x2={to.x} y2={to.y}
                                stroke="transparent"
                                strokeWidth={12}
                                style={{ pointerEvents: "stroke", cursor: "default" }}
                                onMouseEnter={(e) => handleEdgeEnter(agent.id, e)}
                                onMouseLeave={handleEdgeLeave}
                            />

                            {/* Animated travelling dot */}
                            {isActive && (
                                <circle r="1.5" fill={agent.color} opacity="0.8">
                                    <animateMotion dur="2s" repeatCount="indefinite">
                                        <mpath href={`#path-${agent.id}`} />
                                    </animateMotion>
                                </circle>
                            )}
                        </g>
                    );
                })}
            </svg>

            {/* HTML Agent Nodes */}
            {AGENTS.map((agent, idx) => {
                const pos = defaultPositions[agent.id];
                const status = state.agentStatuses[agent.id];
                const isOrch = agent.id === "orchestrator";

                return (
                    <div
                        key={agent.id}
                        className={`agent-node agent-node-${agent.id} ${status === "working" ? "active" : ""} ${isOrch ? "orchestrator" : ""}`}
                        style={{
                            left: `${pos.x}%`,
                            top: `${pos.y}%`,
                            transform: "translate(-50%, -50%)",
                            cursor: "default",
                            zIndex: isOrch ? 5 : 2,
                        }}
                    >
                        <div
                            className="node-floater"
                            style={{ animationDelay: `${idx * -0.8}s` }}
                        >
                            {isOrch ? (
                                <>
                                    <Brain
                                        size={52}
                                        strokeWidth={1.5}
                                        style={{ color: "var(--accent)", filter: "drop-shadow(0 0 18px rgba(37,99,235,0.35))" }}
                                    />
                                    <span className="agent-node-label" style={{ color: "var(--accent)", fontWeight: 700 }}>
                                        Orchestrator
                                    </span>
                                    {status === "done" && (
                                        <span className="card-badge badge-green" style={{ fontSize: 9 }}>Complete</span>
                                    )}
                                </>
                            ) : (
                                <>
                                    <div
                                        className="agent-node-circle"
                                        style={
                                            status === "working"
                                                ? { borderColor: agent.color, boxShadow: `0 0 20px ${agent.color}40`, color: agent.color }
                                                : status === "done"
                                                    ? { borderColor: agent.color, color: agent.color }
                                                    : {}
                                        }
                                    >
                                        {iconMap[agent.icon]}
                                    </div>
                                    <style>{`
                                        .agent-node-${agent.id}:hover .agent-node-circle {
                                            border-color: ${agent.color} !important;
                                            color: ${agent.color} !important;
                                            box-shadow: 0 0 20px ${agent.color}30;
                                        }
                                    `}</style>
                                    <span className="agent-node-label">{agent.name}</span>
                                    {status === "working" && (
                                        <span className="card-badge badge-amber" style={{ fontSize: 9 }}>Processing</span>
                                    )}
                                    {status === "done" && (
                                        <span className="card-badge badge-green" style={{ fontSize: 9 }}>Complete</span>
                                    )}
                                    {latestThoughts[agent.id] && (
                                        <div style={{
                                            fontSize: 10,
                                            color: "var(--text-tertiary)",
                                            maxWidth: 120,
                                            overflow: "hidden",
                                            textOverflow: "ellipsis",
                                            whiteSpace: "nowrap",
                                            marginTop: 4,
                                            fontStyle: "italic",
                                        }}>
                                            {latestThoughts[agent.id]!.length > 60
                                                ? latestThoughts[agent.id]!.slice(0, 60) + "..."
                                                : latestThoughts[agent.id]}
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                );
            })}

            {/* Edge hover tooltip */}
            {edgeHover && (() => {
                const agent = AGENTS.find((a) => a.id === edgeHover.agentId);
                const thought = latestThoughts[edgeHover.agentId];
                return (
                    <div
                        style={{
                            position: "absolute",
                            left: edgeHover.x + 8,
                            top: edgeHover.y - 8,
                            background: "var(--bg-card)",
                            border: "1px solid var(--border-default)",
                            borderRadius: "var(--radius-sm)",
                            padding: "8px 12px",
                            fontSize: 12,
                            maxWidth: 220,
                            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                            zIndex: 30,
                            pointerEvents: "none",
                        }}
                    >
                        <div style={{ fontWeight: 600, marginBottom: 4 }}>{agent?.name}</div>
                        <div style={{ color: "var(--text-secondary)" }}>
                            {thought
                                ? (thought.length > 80 ? thought.slice(0, 80) + "..." : thought)
                                : "Waiting..."}
                        </div>
                    </div>
                );
            })()}
        </div>
    );
}
