import AgentGraph from "../components/report/AgentGraph";
import { useSwarm } from "../context/SwarmContext";
import { AGENTS } from "../schemas/events";

export default function SwarmActivity() {
    const { state } = useSwarm();

    const activeCount = Object.values(state.agentStatuses).filter(
        (s) => s === "working"
    ).length;
    const doneCount = Object.values(state.agentStatuses).filter(
        (s) => s === "done"
    ).length;

    return (
        <div style={{ maxWidth: 960, margin: "0 auto" }}>
            <div className="page-header">
                <div className="page-label">Real-Time Monitoring</div>
                <h2>Swarm Activity</h2>
                <div className="page-subtitle">
                    Live visualization of the multi-agent intelligence network.
                    {activeCount > 0 && ` ${activeCount} agent${activeCount > 1 ? "s" : ""} processing.`}
                    {doneCount > 0 && activeCount === 0 && ` ${doneCount} agent${doneCount > 1 ? "s" : ""} completed.`}
                </div>
            </div>

            <div style={{ height: 500, marginBottom: 32 }}>
                <AgentGraph />
            </div>

            {/* Agent status cards */}
            <div className="grid-3">
                {AGENTS.filter((a) => a.id !== "orchestrator").map((agent) => {
                    const status = state.agentStatuses[agent.id];
                    const thoughts = state.thoughts.filter(
                        (t) => t.agent_id === agent.id
                    );
                    const latestThought = thoughts[0]?.text;

                    return (
                        <div key={agent.id} className="card">
                            <div className="card-header">
                                <span className="card-title" style={{ color: agent.color }}>
                                    {agent.name}
                                </span>
                                {status === "working" && (
                                    <span className="card-badge badge-amber">Processing</span>
                                )}
                                {status === "done" && (
                                    <span className="card-badge badge-green">Complete</span>
                                )}
                                {status === "idle" && (
                                    <span className="card-badge">Idle</span>
                                )}
                            </div>
                            <div
                                style={{
                                    fontSize: 12,
                                    color: "var(--text-tertiary)",
                                    fontFamily: "monospace",
                                    minHeight: 40,
                                    marginTop: 8,
                                }}
                            >
                                {latestThought
                                    ? `> ${latestThought}`
                                    : "Awaiting dispatch..."}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Message log */}
            {state.agentMessages.length > 0 && (
                <div className="card" style={{ marginTop: 24 }}>
                    <div className="card-header">
                        <span className="card-title">Message Log</span>
                        <span className="card-badge badge-blue">
                            {state.agentMessages.length} messages
                        </span>
                    </div>
                    <div style={{ maxHeight: 300, overflow: "auto" }}>
                        {state.agentMessages.map((msg, i) => {
                            const fromAgent = AGENTS.find(
                                (a) => a.id === msg.from
                            );
                            const toAgent = AGENTS.find((a) => a.id === msg.to);
                            return (
                                <div
                                    key={i}
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 8,
                                        padding: "6px 0",
                                        borderBottom: "1px solid var(--border-light)",
                                        fontSize: 12,
                                    }}
                                >
                                    <span
                                        style={{
                                            fontWeight: 600,
                                            color: fromAgent?.color,
                                        }}
                                    >
                                        {fromAgent?.name}
                                    </span>
                                    <span style={{ color: "var(--text-tertiary)" }}>
                                        {msg.direction === "request" ? "→" : "←"}
                                    </span>
                                    <span
                                        style={{
                                            fontWeight: 600,
                                            color: toAgent?.color,
                                        }}
                                    >
                                        {toAgent?.name}
                                    </span>
                                    <span
                                        style={{
                                            fontWeight: 500,
                                            color: "var(--text-primary)",
                                        }}
                                    >
                                        {msg.title}
                                    </span>
                                    <span
                                        style={{
                                            color: "var(--text-tertiary)",
                                            marginLeft: "auto",
                                            flexShrink: 0,
                                        }}
                                    >
                                        {msg.description.slice(0, 60)}
                                        {msg.description.length > 60 ? "..." : ""}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}
