import { NavLink } from "react-router-dom";
import { Search, Bell, User } from "lucide-react";

export default function TopNav() {
    return (
        <header className="topnav">
            <nav className="topnav-tabs">
                <NavLink to="/" className={({ isActive }) => `topnav-tab ${isActive ? "active" : ""}`} end>
                    Daily Report
                </NavLink>
                <NavLink to="/swarm" className={({ isActive }) => `topnav-tab ${isActive ? "active" : ""}`}>
                    Swarm Activity
                </NavLink>
                <NavLink to="/portfolio" className={({ isActive }) => `topnav-tab ${isActive ? "active" : ""}`}>
                    Portfolio
                </NavLink>
                <NavLink to="/chat" className={({ isActive }) => `topnav-tab ${isActive ? "active" : ""}`}>
                    Chat
                </NavLink>
            </nav>

            <div className="topnav-search">
                <Search size={14} />
                <input type="text" placeholder="Search markets..." />
            </div>

            <div className="topnav-actions">
                <button className="topnav-icon-btn">
                    <Bell size={18} />
                </button>
                <div className="topnav-avatar">
                    <User size={16} />
                </div>
            </div>
        </header>
    );
}
