import { NavLink, useLocation } from "react-router-dom";
import { useSwarm } from "../../context/SwarmContext";
import { AGENTS } from "../../schemas/events";
import { Brain, PieChart, Newspaper, TrendingUp, Bitcoin, Zap, Settings, HelpCircle } from "lucide-react";
import type { AgentId } from "../../schemas/events";

const iconMap: Record<string, React.ReactNode> = {
    brain: <Brain size={16} />,
    "pie-chart": <PieChart size={16} />,
    newspaper: <Newspaper size={16} />,
    "trending-up": <TrendingUp size={16} />,
    bitcoin: <Bitcoin size={16} />,
};

export default function Sidebar() {
    const { state, triggerReport } = useSwarm();
    const location = useLocation();

    const agentList = AGENTS.filter((a) => a.id !== "orchestrator");

    return (
        <aside className="sidebar">
            <div className="sidebar-brand">
                <div className="sidebar-brand-icon">
                    <Zap size={18} />
                </div>
                <div>
                    <h1>InvestorSwarm</h1>
                    <span>{Object.values(state.agentStatuses).filter((s) => s === "working").length} agents active</span>
                </div>
            </div>

            <div className="sidebar-section-label">Agent Views</div>
            <nav className="sidebar-nav">
                {agentList.map((agent) => (
                    <NavLink
                        key={agent.id}
                        to={`/?agent=${agent.id}`}
                        className={({ isActive }) =>
                            `sidebar-link ${isActive && location.search.includes(agent.id) ? "active" : ""}`
                        }
                    >
                        <span style={{ color: agent.color }}>{iconMap[agent.icon]}</span>
                        {agent.name}
                        <span
                            className={`status-dot ${state.agentStatuses[agent.id as AgentId]}`}
                        />
                    </NavLink>
                ))}
            </nav>

            <button className="sidebar-cta" onClick={triggerReport}>
                <Zap size={14} />
                Generate Report
            </button>

            <div className="sidebar-bottom">
                <NavLink to="/settings" className="sidebar-link">
                    <Settings size={16} />
                    Settings
                </NavLink>
                <NavLink to="/support" className="sidebar-link">
                    <HelpCircle size={16} />
                    Support
                </NavLink>
            </div>
        </aside>
    );
}
