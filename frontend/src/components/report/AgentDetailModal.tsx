import { useEffect } from "react";
import {
    Brain,
    PieChart,
    Newspaper,
    TrendingUp,
    Bitcoin,
    X,
    ArrowRight,
    ArrowLeft,
} from "lucide-react";
import type { AgentMeta, AgentId } from "../../schemas/events";
import type { AgentMessage, Thought, SwarmState } from "../../context/SwarmContext";

const iconMap: Record<string, React.ReactNode> = {
    brain: <Brain size={22} />,
    "pie-chart": <PieChart size={22} />,
    newspaper: <Newspaper size={22} />,
    "trending-up": <TrendingUp size={22} />,
    bitcoin: <Bitcoin size={22} />,
};

/* ── Brand logos as inline SVGs ──────────────────── */
const s = 18; // logo size

function WealthsimpleLogo() {
    return (
        <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="12" fill="#222" />
            <path
                d="M6 15.5L9.2 8.5L12 14L14.8 8.5L18 15.5"
                stroke="#FFF"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
                fill="none"
            />
        </svg>
    );
}

function YfinanceLogo() {
    return (
        <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="12" fill="#6001D2" />
            <text
                x="12" y="17"
                textAnchor="middle"
                fontFamily="Arial, sans-serif"
                fontWeight="700"
                fontSize="14"
                fill="#FFF"
            >
                Y
            </text>
        </svg>
    );
}

function FinnhubLogo() {
    return (
        <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="12" fill="#2962FF" />
            <path
                d="M7 16V8h7M7 12h5"
                stroke="#FFF"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
        </svg>
    );
}

function CoinGeckoLogo() {
    return (
        <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="12" fill="#8BC53F" />
            <circle cx="12" cy="12" r="7" fill="#FFF" />
            <circle cx="14" cy="10" r="1.5" fill="#8BC53F" />
            <path
                d="M9 14c1 1.5 4 1.5 5.5 0"
                stroke="#8BC53F"
                strokeWidth="1.2"
                strokeLinecap="round"
                fill="none"
            />
        </svg>
    );
}

function GeminiLogo() {
    return (
        <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="12" fill="#1A73E8" />
            <path
                d="M12 4C12 4 8 9 8 12s4 8 4 8c0 0 4-5 4-8s-4-8-4-8z"
                fill="#FFF"
                fillOpacity="0.9"
            />
            <path
                d="M4 12c0 0 5-4 8-4s8 4 8 4c0 0-5 4-8 4s-8-4-8-4z"
                fill="#FFF"
                fillOpacity="0.5"
            />
        </svg>
    );
}

const API_LOGOS: Record<string, () => JSX.Element> = {
    Wealthsimple: WealthsimpleLogo,
    yfinance: YfinanceLogo,
    Finnhub: FinnhubLogo,
    CoinGecko: CoinGeckoLogo,
    Gemini: GeminiLogo,
};

const AGENT_DESCRIPTIONS: Record<AgentId, string> = {
    orchestrator: "Coordinates all agents and synthesizes their outputs into a unified report.",
    portfolio: "Breaks down portfolio holdings, sector allocation, beta, and concentration risk.",
    news: "Scrapes and scores financial headlines using sentiment analysis across tickers.",
    modeling: "Generates regression, volatility, and correlation charts from historical price data.",
    alternatives: "Tracks commodity prices, crypto markets, and cross-asset correlations.",
};

interface ExternalAPI {
    name: string;
    description: string;
    direction: "outgoing";
}

const EXTERNAL_APIS: Partial<Record<AgentId, ExternalAPI[]>> = {
    portfolio: [
        { name: "Wealthsimple", description: "Portfolio holdings & positions", direction: "outgoing" },
        { name: "yfinance", description: "Historical prices, beta & correlation", direction: "outgoing" },
    ],
    news: [
        { name: "Finnhub", description: "Market news & company headlines", direction: "outgoing" },
    ],
    alternatives: [
        { name: "CoinGecko", description: "Crypto prices & BTC dominance", direction: "outgoing" },
        { name: "Finnhub", description: "Commodity quotes (Gold, Oil)", direction: "outgoing" },
        { name: "yfinance", description: "Cross-correlation with equities", direction: "outgoing" },
    ],
    modeling: [
        { name: "yfinance", description: "OHLCV data for chart generation", direction: "outgoing" },
    ],
    orchestrator: [
        { name: "Gemini", description: "LLM synthesis & chart selection", direction: "outgoing" },
    ],
};

interface Props {
    agent: AgentMeta;
    state: SwarmState;
    agents: AgentMeta[];
    onClose: () => void;
}

export default function AgentDetailModal({ agent, state, agents, onClose }: Props): JSX.Element {
    const agentThoughts = state.thoughts.filter((t) => t.agent_id === agent.id);
    const incomingMessages = state.agentMessages.filter((m) => m.to === agent.id);
    const outgoingMessages = state.agentMessages.filter((m) => m.from === agent.id);
    const externalApis = EXTERNAL_APIS[agent.id] ?? [];
    const status = state.agentStatuses[agent.id];

    useEffect(() => {
        const handleKey = (e: KeyboardEvent) => {
            if (e.key === "Escape") onClose();
        };
        document.addEventListener("keydown", handleKey);
        return () => document.removeEventListener("keydown", handleKey);
    }, [onClose]);

    const getAgentName = (id: AgentId) => agents.find((a) => a.id === id)?.name ?? id;
    const getAgentColor = (id: AgentId) => agents.find((a) => a.id === id)?.color ?? "#6b7280";

    const statusLabel =
        status === "working" ? "Processing" :
        status === "done" ? "Complete" :
        status === "error" ? "Error" :
        "Idle";

    const statusClass =
        status === "working" ? "badge-amber" :
        status === "done" ? "badge-green" :
        status === "error" ? "badge-red" :
        "badge-idle";

    return (
        <div className="agent-modal-backdrop" onClick={onClose}>
            <div className="agent-modal" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="agent-modal__header">
                    <div className="agent-modal__header-left">
                        <div
                            className="agent-modal__icon"
                            style={{ color: agent.color, borderColor: agent.color }}
                        >
                            {iconMap[agent.icon]}
                        </div>
                        <div>
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <h2 className="agent-modal__name">{agent.name}</h2>
                                <span className={`card-badge ${statusClass}`} style={{ fontSize: 10 }}>
                                    {statusLabel}
                                </span>
                            </div>
                            <p className="agent-modal__desc">{AGENT_DESCRIPTIONS[agent.id]}</p>
                        </div>
                    </div>
                    <button className="agent-modal__close" onClick={onClose}>
                        <X size={18} />
                    </button>
                </div>

                <div className="agent-modal__body">
                    {/* Thoughts section */}
                    <section className="agent-modal__section">
                        <h3 className="agent-modal__section-title">Thoughts</h3>
                        {agentThoughts.length === 0 ? (
                            <p className="agent-modal__empty">No thoughts recorded yet.</p>
                        ) : (
                            <div className="agent-modal__thoughts">
                                {agentThoughts.map((t: Thought, i: number) => (
                                    <div key={i} className="agent-modal__thought-line">
                                        <span className="agent-modal__thought-prefix">{">"}</span>
                                        <span className="agent-modal__thought-text">{t.text}</span>
                                        <span className="agent-modal__thought-time">
                                            {new Date(t.timestamp).toLocaleTimeString()}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>

                    {/* Incoming queries */}
                    <section className="agent-modal__section">
                        <h3 className="agent-modal__section-title">Incoming Queries</h3>
                        {incomingMessages.length === 0 ? (
                            <p className="agent-modal__empty">No incoming queries.</p>
                        ) : (
                            <div className="agent-modal__messages">
                                {incomingMessages.map((m: AgentMessage, i: number) => (
                                    <div key={i} className="agent-modal__message">
                                        <div className="agent-modal__message-route">
                                            <ArrowRight size={14} className="agent-modal__message-arrow" />
                                            <span style={{ color: getAgentColor(m.from) }}>
                                                {getAgentName(m.from)}
                                            </span>
                                        </div>
                                        <div className="agent-modal__message-title">{m.title}</div>
                                        {m.description && (
                                            <div className="agent-modal__message-desc">{m.description}</div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>

                    {/* Outgoing queries */}
                    <section className="agent-modal__section">
                        <h3 className="agent-modal__section-title">Outgoing Queries</h3>
                        {outgoingMessages.length === 0 && externalApis.length === 0 ? (
                            <p className="agent-modal__empty">No outgoing queries.</p>
                        ) : (
                            <div className="agent-modal__messages">
                                {outgoingMessages.map((m: AgentMessage, i: number) => (
                                    <div key={i} className="agent-modal__message">
                                        <div className="agent-modal__message-route">
                                            <ArrowLeft size={14} className="agent-modal__message-arrow" />
                                            <span style={{ color: getAgentColor(m.to) }}>
                                                {getAgentName(m.to)}
                                            </span>
                                        </div>
                                        <div className="agent-modal__message-title">{m.title}</div>
                                        {m.description && (
                                            <div className="agent-modal__message-desc">{m.description}</div>
                                        )}
                                    </div>
                                ))}

                                {/* External API queries */}
                                {externalApis.map((api, i) => {
                                    const Logo = API_LOGOS[api.name];
                                    return (
                                        <div key={`api-${i}`} className="agent-modal__message agent-modal__message--api">
                                            <div className="agent-modal__message-route">
                                                {Logo && (
                                                    <span className="agent-modal__api-logo">
                                                        <Logo />
                                                    </span>
                                                )}
                                                <span className="agent-modal__api-name">{api.name}</span>
                                                <span className="agent-modal__api-badge">API</span>
                                            </div>
                                            <div className="agent-modal__message-desc">{api.description}</div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </section>
                </div>
            </div>
        </div>
    );
}
