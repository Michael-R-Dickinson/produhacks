import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SwarmProvider } from "./context/SwarmContext";
import AppShell from "./components/layout/AppShell";
import DailyReport from "./pages/DailyReport";
import Chat from "./pages/Chat";
import Portfolio from "./pages/Portfolio";

export default function App() {
    return (
        <SwarmProvider>
            <BrowserRouter>
                <Routes>
                    <Route element={<AppShell />}>
                        <Route index element={<DailyReport />} />
                        <Route path="chat" element={<Chat />} />
                        <Route path="portfolio" element={<Portfolio />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </SwarmProvider>
    );
}
