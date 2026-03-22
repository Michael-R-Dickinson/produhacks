import { useMemo, useRef, useState, type JSX } from "react"
import {
  Brain,
  PieChart,
  Newspaper,
  TrendingUp,
  Bitcoin,
  FileText,
} from "lucide-react"
import { useSwarm } from "../../context/SwarmContext"
import { AGENTS } from "../../schemas/events"
import type { AgentId, AgentMeta } from "../../schemas/events"
import type { AgentMessage } from "../../context/SwarmContext"
import AgentDetailModal from "./AgentDetailModal"

const iconMap: Record<string, React.ReactNode> = {
  brain: <Brain size={18} />,
  "pie-chart": <PieChart size={18} />,
  newspaper: <Newspaper size={18} />,
  "trending-up": <TrendingUp size={18} />,
  bitcoin: <Bitcoin size={18} />,
}

const cardPositions: Record<AgentId, { x: number; y: number }> = {
  orchestrator: { x: 50, y: 50 },
  portfolio: { x: 15, y: 18 },
  news: { x: 85, y: 18 },
  modeling: { x: 85, y: 82 },
  alternatives: { x: 15, y: 82 },
}

interface EdgeHover {
  from: AgentId
  to: AgentId
  message: AgentMessage
  x: number
  y: number
}

interface AgentGraphProps {
  reportReady?: boolean
  onViewReport?: () => void
}

export default function AgentGraph({
  reportReady,
  onViewReport,
}: AgentGraphProps): JSX.Element {
  const { state } = useSwarm()
  const containerRef = useRef<HTMLDivElement>(null)
  const [edgeHover, setEdgeHover] = useState<EdgeHover | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<AgentMeta | null>(null)

  const agentList = AGENTS.filter((a) => a.id !== "orchestrator")

  // Latest thought per agent (most recent first in state.thoughts)
  const latestThoughts = useMemo(() => {
    const map: Partial<Record<AgentId, string[]>> = {}
    for (const t of state.thoughts) {
      if (!map[t.agent_id]) map[t.agent_id] = []
      if (map[t.agent_id]!.length < 3) {
        map[t.agent_id]!.push(t.text)
      }
    }
    return map
  }, [state.thoughts])

  // Active connections: find the most recent message for each agent pair
  const activeConnections = useMemo(() => {
    const connections = new Map<string, AgentMessage>()
    for (const msg of state.agentMessages) {
      const key = [msg.from, msg.to].sort().join("-")
      if (!connections.has(key)) {
        connections.set(key, msg)
      }
    }
    return connections
  }, [state.agentMessages])

  const handleEdgeEnter = (
    from: AgentId,
    to: AgentId,
    msg: AgentMessage,
    e: React.MouseEvent,
  ) => {
    if (!containerRef.current) return
    const rect = containerRef.current.getBoundingClientRect()
    setEdgeHover({
      from,
      to,
      message: msg,
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    })
  }

  const handleEdgeLeave = () => {
    setEdgeHover(null)
  }

  return (
    <div
      className="agent-graph-container"
      ref={containerRef}
      style={{
        padding: 0,
        background:
          "radial-gradient(var(--border-default) 1px, transparent 1px), radial-gradient(circle at 50% 50%, #f0f4ff 0%, var(--bg-card) 70%)",
        backgroundSize: "24px 24px, 100% 100%",
        backgroundPosition: "0 0, 0 0",
        position: "relative",
      }}
    >
      {/* SVG connection lines */}
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
      >
        {agentList.map((agent) => {
          const from = cardPositions.orchestrator
          const to = cardPositions[agent.id]
          const key = ["orchestrator", agent.id].sort().join("-")
          const msg = activeConnections.get(key)
          const isActive = state.agentStatuses[agent.id] === "working"
          const isDone = state.agentStatuses[agent.id] === "done"
          const hasMessage = !!msg

          return (
            <g key={agent.id}>
              <path
                id={`path-${agent.id}`}
                d={`M${from.x},${from.y} L${to.x},${to.y}`}
                fill="none"
                stroke="none"
              />

              <line
                x1={from.x}
                y1={from.y}
                x2={to.x}
                y2={to.y}
                stroke={
                  hasMessage || isActive
                    ? agent.color
                    : isDone
                      ? agent.color
                      : "#d1d5db"
                }
                strokeWidth={hasMessage || isActive ? 2 : 1.5}
                strokeOpacity={
                  hasMessage || isActive ? 0.9 : isDone ? 0.5 : 0.25
                }
                strokeDasharray={isActive ? "8 4" : "6 6"}
                strokeLinecap="round"
                style={
                  isActive
                    ? { animation: "dashFlow 0.8s linear infinite" }
                    : undefined
                }
              />

              {/* Invisible wider hit area for hover */}
              {msg && (
                <line
                  x1={from.x}
                  y1={from.y}
                  x2={to.x}
                  y2={to.y}
                  stroke="transparent"
                  strokeWidth={12}
                  style={{ pointerEvents: "stroke", cursor: "default" }}
                  onMouseEnter={(e) =>
                    handleEdgeEnter(msg.from, msg.to, msg, e)
                  }
                  onMouseLeave={handleEdgeLeave}
                />
              )}

              {/* Animated travelling dot */}
              {isActive && (
                <circle r="1.5" fill={agent.color} opacity="0.8">
                  <animateMotion dur="2s" repeatCount="indefinite">
                    <mpath href={`#path-${agent.id}`} />
                  </animateMotion>
                </circle>
              )}
            </g>
          )
        })}
      </svg>

      {/* Agent Cards */}
      {AGENTS.map((agent, idx) => {
        const pos = cardPositions[agent.id]
        const status = state.agentStatuses[agent.id]
        const isOrch = agent.id === "orchestrator"
        const thoughts = latestThoughts[agent.id]

        return (
          <div
            key={agent.id}
            className={`agent-card ${status === "working" ? "agent-card--active" : ""} ${status === "done" ? "agent-card--done" : ""} ${isOrch ? "agent-card--orchestrator" : ""}`}
            style={{
              left: `${pos.x}%`,
              top: `${pos.y}%`,
              transform: "translate(-50%, -50%)",
              zIndex: isOrch ? 5 : 2,
              borderColor:
                status === "working" || status === "done"
                  ? agent.color
                  : undefined,
              cursor: "pointer",
            }}
            onClick={() => setSelectedAgent(agent)}
          >
            <div
              className="agent-card__floater"
              style={{ animationDelay: `${idx * -0.8}s` }}
            >
              {/* Header */}
              <div className="agent-card__header">
                <div
                  className="agent-card__icon"
                  style={{
                    color:
                      status === "working" || status === "done"
                        ? agent.color
                        : undefined,
                    borderColor: status === "working" ? agent.color : undefined,
                    boxShadow:
                      status === "working"
                        ? `0 0 12px ${agent.color}30`
                        : undefined,
                  }}
                >
                  {isOrch ? <Brain size={20} /> : iconMap[agent.icon]}
                </div>
                <div className="agent-card__title-group">
                  <span className="agent-card__name">{agent.name}</span>
                  {status === "working" && (
                    <span
                      className="card-badge badge-amber"
                      style={{ fontSize: 9 }}
                    >
                      Processing
                    </span>
                  )}
                  {status === "done" && (
                    <span
                      className="card-badge badge-green"
                      style={{ fontSize: 9 }}
                    >
                      Complete
                    </span>
                  )}
                </div>
              </div>

              {/* Thought output - codeblock style */}
              {thoughts && thoughts.length > 0 && (
                <div className="agent-card__output">
                  {thoughts.map((text, i) => (
                    <div key={i} className="agent-card__output-line">
                      <span className="agent-card__output-prefix">{">"}</span>
                      {text}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )
      })}

      {/* Report ready button - below orchestrator */}
      {reportReady && (
        <button
          onClick={onViewReport}
          style={{
            position: "absolute",
            left: `${cardPositions.orchestrator.x}%`,
            top: `${cardPositions.orchestrator.y + 14}%`,
            transform: "translateX(-50%)",
            zIndex: 10,
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            padding: "6px 14px",
            fontSize: 13,
            fontWeight: 500,
            color: "var(--text-secondary)",
            background: "var(--bg-secondary)",
            border: "1px solid var(--border)",
            borderRadius: 6,
            cursor: "pointer",
            transition: "background 150ms ease, color 150ms ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "var(--bg-tertiary)"
            e.currentTarget.style.color = "var(--text-primary)"
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "var(--bg-secondary)"
            e.currentTarget.style.color = "var(--text-secondary)"
          }}
        >
          <FileText size={14} />
          Report ready
        </button>
      )}

      {/* Agent detail modal */}
      {selectedAgent && (
        <AgentDetailModal
          agent={selectedAgent}
          state={state}
          agents={AGENTS}
          onClose={() => setSelectedAgent(null)}
        />
      )}

      {/* Edge hover tooltip - shows message info */}
      {edgeHover &&
        (() => {
          const fromAgent = AGENTS.find((a) => a.id === edgeHover.from)
          const toAgent = AGENTS.find((a) => a.id === edgeHover.to)
          const msg = edgeHover.message
          return (
            <div
              className="agent-edge-tooltip"
              style={{
                left: edgeHover.x + 12,
                top: edgeHover.y - 12,
              }}
            >
              <div className="agent-edge-tooltip__route">
                <span style={{ color: fromAgent?.color }}>
                  {fromAgent?.name}
                </span>
                <span className="agent-edge-tooltip__arrow">
                  {msg.direction === "request" ? "->" : "<-"}
                </span>
                <span style={{ color: toAgent?.color }}>{toAgent?.name}</span>
              </div>
              <div className="agent-edge-tooltip__title">{msg.title}</div>
              {msg.description && (
                <div className="agent-edge-tooltip__desc">
                  {msg.description}
                </div>
              )}
            </div>
          )
        })()}
    </div>
  )
}
