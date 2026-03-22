import { z } from "zod";

/* ── Agent identifiers ───────────────────────────── */
export const AgentId = z.enum([
  "orchestrator",
  "portfolio",
  "news",
  "modeling",
  "alternatives",
]);
export type AgentId = z.infer<typeof AgentId>;

export const AgentStatus = z.enum(["idle", "working", "done", "error"]);
export type AgentStatus = z.infer<typeof AgentStatus>;

export const MessageDirection = z.enum(["request", "response"]);
export type MessageDirection = z.infer<typeof MessageDirection>;

/* ── Shared data schemas ─────────────────────────── */

export const HoldingSchema = z.object({
  ticker: z.string(),
  weight: z.number(),
  sector: z.string(),
});
export type Holding = z.infer<typeof HoldingSchema>;

export const PortfolioData = z.object({
  sector_allocation: z.record(z.string(), z.number()),
  top_holdings: z.array(HoldingSchema),
  herfindahl_index: z.number(),
  portfolio_beta: z.number(),
});
export type PortfolioData = z.infer<typeof PortfolioData>;

export const HeadlineSchema = z.object({
  title: z.string(),
  sentiment: z.number(),
  ticker: z.string(),
});
export type Headline = z.infer<typeof HeadlineSchema>;

export const NewsData = z.object({
  headlines: z.array(HeadlineSchema),
  aggregate_sentiment: z.record(z.string(), z.number()),
  overall_sentiment: z.number(),
});
export type NewsData = z.infer<typeof NewsData>;

export const ChartOutput = z.object({
  chart_id: z.string(),
  chart_type: z.string(),
  title: z.string(),
  image_base64: z.string(),
  summary: z.string(),
});
export type ChartOutput = z.infer<typeof ChartOutput>;

export const ModelingData = z.object({
  sharpe_ratio: z.number(),
  volatility: z.number(),
  trend_slope: z.number(),
  chart_base64: z.string().nullable().optional(),
  charts: z.array(ChartOutput).optional(),
  metrics: z.record(z.string(), z.number()).optional(),
});
export type ModelingData = z.infer<typeof ModelingData>;

export const AlternativesData = z.object({
  crypto_prices: z.record(z.string(), z.number()),
  cross_correlations: z.record(z.string(), z.number()),
});
export type AlternativesData = z.infer<typeof AlternativesData>;

/* ── Wire format (matches backend SSEEvent envelope) ── */

export const EventType = z.enum([
  "agent.status",
  "agent.thought",
  "agent.message",
  "report.chunk",
  "report.complete",
  "chat.response",
]);
export type EventType = z.infer<typeof EventType>;

export const AgentStatusPayload = z.object({
  status: AgentStatus,
  message: z.string().optional().default(""),
});

export const AgentThoughtPayload = z.object({
  text: z.string(),
});

export const AgentMessagePayload = z.object({
  from: AgentId,
  to: AgentId,
  title: z.string(),
  description: z.string().optional().default(""),
  direction: MessageDirection,
});

export const ReportChunkPayload = z.object({
  content: z.string(),
  section: z.string(),
  final: z.boolean().optional().default(false),
});

export const ReportCompletePayload = z.object({
  markdown: z.string(),
  charts: z.array(ChartOutput).optional().default([]),
});

export const ChatResponsePayload = z.object({
  text: z.string(),
  final: z.boolean().optional().default(false),
});

/** The envelope the backend actually sends over SSE */
export const SSEWireEvent = z.object({
  event_id: z.string(),
  timestamp: z.number(),
  agent_id: z.string(),
  event_type: EventType,
  payload: z.record(z.string(), z.unknown()),
});
export type SSEWireEvent = z.infer<typeof SSEWireEvent>;

/* ── Internal flat types (used by reducer & mock SSE) ── */

export type StatusEvent = {
  agent_id: AgentId;
  type: "status";
  status: AgentStatus;
};

export type ThoughtEvent = {
  agent_id: AgentId;
  type: "thought";
  text: string;
  timestamp?: string;
};

export type ReportSectionEvent = {
  agent_id: AgentId;
  type: "report_section";
  section: "portfolio" | "news" | "modeling" | "alternatives" | "executive_summary";
  data: PortfolioData | NewsData | ModelingData | AlternativesData | { summary: string };
};

export type ChatTokenEvent = {
  agent_id: AgentId;
  type: "chat_response";
  token: string;
  done: boolean;
};

export type SwarmHealthEvent = {
  agent_id: "orchestrator";
  type: "swarm_health";
  active_agents: number;
  signals_per_min: number;
  processing_power: number;
};

export type AgentMessageEvent = {
  agent_id: AgentId;
  type: "agent_message";
  from: AgentId;
  to: AgentId;
  title: string;
  description: string;
  direction: MessageDirection;
};

export type ReportCompleteEvent = {
  agent_id: AgentId;
  type: "report_complete";
  markdown: string;
  charts: ChartOutput[];
};

export type SSEEvent =
  | StatusEvent
  | ThoughtEvent
  | ReportSectionEvent
  | ChatTokenEvent
  | SwarmHealthEvent
  | AgentMessageEvent
  | ReportCompleteEvent;

/* ── Agent metadata (for UI rendering) ──────────── */
export interface AgentMeta {
  id: AgentId;
  name: string;
  icon: string;
  color: string;
}

export const AGENTS: AgentMeta[] = [
  { id: "orchestrator", name: "Orchestrator", icon: "brain", color: "#2563eb" },
  { id: "portfolio", name: "Portfolio Alpha", icon: "pie-chart", color: "#8b5cf6" },
  { id: "news", name: "Sentiment Engine", icon: "newspaper", color: "#f59e0b" },
  { id: "modeling", name: "Quant Modeler", icon: "trending-up", color: "#10b981" },
  { id: "alternatives", name: "Alt Assets", icon: "bitcoin", color: "#ef4444" },
];
