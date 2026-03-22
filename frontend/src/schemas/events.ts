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

/* ── SSE Event Types ────────────────────────────── */

/** Agent status change */
export const StatusEvent = z.object({
  agent_id: AgentId,
  type: z.literal("status"),
  status: AgentStatus,
});
export type StatusEvent = z.infer<typeof StatusEvent>;

/** Agent thought / activity log */
export const ThoughtEvent = z.object({
  agent_id: AgentId,
  type: z.literal("thought"),
  text: z.string(),
  timestamp: z.string().optional(),
});
export type ThoughtEvent = z.infer<typeof ThoughtEvent>;

/* ── Agent Response Payloads ────────────────────── */

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

/** Report section delivered via SSE */
export const ReportSectionEvent = z.object({
  agent_id: AgentId,
  type: z.literal("report_section"),
  section: z.enum(["portfolio", "news", "modeling", "alternatives", "executive_summary"]),
  data: z.union([PortfolioData, NewsData, ModelingData, AlternativesData, z.object({ summary: z.string() })]),
});
export type ReportSectionEvent = z.infer<typeof ReportSectionEvent>;

/** Chat response token (streamed) */
export const ChatTokenEvent = z.object({
  agent_id: AgentId,
  type: z.literal("chat_response"),
  token: z.string(),
  done: z.boolean(),
});
export type ChatTokenEvent = z.infer<typeof ChatTokenEvent>;

/** Swarm-wide health */
export const SwarmHealthEvent = z.object({
  agent_id: z.literal("orchestrator"),
  type: z.literal("swarm_health"),
  active_agents: z.number(),
  signals_per_min: z.number(),
  processing_power: z.number(),
});
export type SwarmHealthEvent = z.infer<typeof SwarmHealthEvent>;

/** Agent-to-agent message */
export const MessageDirection = z.enum(["request", "response"]);
export type MessageDirection = z.infer<typeof MessageDirection>;

export const AgentMessageEvent = z.object({
  agent_id: AgentId,
  type: z.literal("agent_message"),
  from: AgentId,
  to: AgentId,
  title: z.string(),
  description: z.string(),
  direction: MessageDirection,
});
export type AgentMessageEvent = z.infer<typeof AgentMessageEvent>;

/** Union of all SSE events */
export const SSEEvent = z.discriminatedUnion("type", [
  StatusEvent,
  ThoughtEvent,
  ReportSectionEvent,
  ChatTokenEvent,
  SwarmHealthEvent,
  AgentMessageEvent,
]);
export type SSEEvent = z.infer<typeof SSEEvent>;

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
