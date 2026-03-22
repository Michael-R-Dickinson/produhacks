import { NavLink } from "react-router-dom";
import { useSwarm } from "../../context/SwarmContext";
import { Zap, Settings, HelpCircle } from "lucide-react";

export default function Sidebar() {
    const { state, triggerReport } = useSwarm();

    return (
        <aside className="sidebar">
            <div className="sidebar-brand">
                <img
                    src="/brain-logo.png"
                    alt="InvestorSwarm"
                    style={{ width: 36, height: 36, objectFit: 'contain' }}
                />
                <div>
                    <h1>InvestorSwarm</h1>
                    <span>{Object.values(state.agentStatuses).filter((s) => s === "working").length} agents active</span>
                </div>
            </div>

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
