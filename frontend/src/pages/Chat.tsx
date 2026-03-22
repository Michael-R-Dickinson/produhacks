import { useState } from "react";
import { useSwarm } from "../context/SwarmContext";
import { AGENTS } from "../schemas/events";
import { Send, Zap } from "lucide-react";

const suggestions = [
    "What's my portfolio risk?",
    "Analyze NVDA exposure",
    "Rebalance recommendation",
    "Explain the divergence signal",
];

export default function Chat() {
    const { state, sendChat } = useSwarm();
    const [input, setInput] = useState("");

    const handleSend = () => {
        if (!input.trim()) return;
        sendChat(input.trim());
        setInput("");
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="chat-layout">
            {/* Chat thread */}
            <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
                <div className="page-header" style={{ marginBottom: 16 }}>
                    <div className="page-label">Conversational AI</div>
                    <h2>Chat with Swarm</h2>
                    <div className="page-subtitle">Ask follow-up questions that reference the current report. The orchestrator will dispatch to relevant agents.</div>
                </div>

                <div className="chat-thread" style={{ flex: 1 }}>
                    {state.chatMessages.length === 0 && (
                        <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 16 }}>
                            <div style={{ width: 64, height: 64, borderRadius: "50%", background: "var(--accent-light)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                                <Zap size={28} style={{ color: "var(--accent)" }} />
                            </div>
                            <div style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)" }}>Ask Wealth Council anything</div>
                            <div style={{ fontSize: 13, color: "var(--text-tertiary)", textAlign: "center", maxWidth: 400 }}>
                                Your question will be routed to the relevant specialist agents. Try one of the suggestions below.
                            </div>
                        </div>
                    )}

                    {state.chatMessages.map((msg) => (
                        <div key={msg.id} className={`chat-message ${msg.role}`}>
                            <div className="chat-message-avatar">
                                {msg.role === "assistant" ? <Zap size={14} /> : "U"}
                            </div>
                            <div>
                                <div className="chat-message-bubble">
                                    {msg.content.split("\n").map((line, i) => (
                                        <span key={i}>
                                            {line}
                                            {i < msg.content.split("\n").length - 1 && <br />}
                                        </span>
                                    ))}
                                </div>
                                {msg.agents && msg.agents.length > 0 && (
                                    <div className="chat-agent-pills">
                                        {msg.agents.map((aid) => {
                                            const agent = AGENTS.find((a) => a.id === aid);
                                            return (
                                                <span key={aid} className="chat-agent-pill">
                                                    {agent?.name ?? aid}
                                                </span>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {state.chatStreaming && (
                        <div className="chat-message assistant">
                            <div className="chat-message-avatar"><Zap size={14} /></div>
                            <div className="chat-message-bubble">{state.chatStreaming}▊</div>
                        </div>
                    )}
                </div>

                {/* Input area */}
                <div className="chat-input-container">
                    <div className="chat-suggestions">
                        {suggestions.map((s) => (
                            <button key={s} className="chat-suggestion-chip" onClick={() => sendChat(s)}>
                                {s}
                            </button>
                        ))}
                    </div>
                    <div className="chat-input-bar">
                        <input
                            type="text"
                            placeholder="Ask about market shifts or specific assets..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                        />
                        <button className="chat-send-btn" onClick={handleSend}>
                            <Send size={16} />
                        </button>
                    </div>
                </div>
            </div>

            {/* Active Agents Panel */}
            <div>
                <div className="card" style={{ position: "sticky", top: 16 }}>
                    <div className="card-header">
                        <span className="card-title">Agent Status</span>
                    </div>
                    {AGENTS.filter((a) => a.id !== "orchestrator").map((agent) => (
                        <div
                            key={agent.id}
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 10,
                                padding: "8px 0",
                                borderBottom: "1px solid var(--border-light)",
                                fontSize: 13,
                            }}
                        >
                            <span className={`status-dot ${state.agentStatuses[agent.id]}`} />
                            <span style={{ fontWeight: 500 }}>{agent.name}</span>
                            <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--text-tertiary)", textTransform: "capitalize" }}>
                                {state.agentStatuses[agent.id]}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
