import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import TopNav from "./TopNav";

export default function AppShell() {
    return (
        <div className="app-shell">
            <Sidebar />
            <TopNav />
            <main className="main-content">
                <Outlet />
            </main>
        </div>
    );
}
