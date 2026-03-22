/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useContext,
  useReducer,
  useEffect,
  useCallback,
  type ReactNode,
} from "react"
import { connectSSE } from "../services/sse"
import type {
  AgentId,
  AgentStatus,
  SSEEvent,
  PortfolioData,
  NewsData,
  ModelingData,
  AlternativesData,
  ChartOutput,
} from "../schemas/events"

/* ── State shape ─────────────────────────────────── */
export interface Thought {
  agent_id: AgentId
  text: string
  timestamp: string
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  agents?: AgentId[]
}

export interface SwarmState {
  agentStatuses: Record<AgentId, AgentStatus>
  thoughts: Thought[]
  portfolio: PortfolioData | null
  news: NewsData | null
  modeling: ModelingData | null
  alternatives: AlternativesData | null
  executiveSummary: string | null
  chartMap: Record<string, ChartOutput>
  chatMessages: ChatMessage[]
  chatStreaming: string
  swarmHealth: {
    active_agents: number
    signals_per_min: number
    processing_power: number
  } | null
  connected: boolean
}

const initialState: SwarmState = {
  agentStatuses: {
    orchestrator: "idle",
    portfolio: "idle",
    news: "idle",
    modeling: "idle",
    alternatives: "idle",
  },
  thoughts: [],
  portfolio: null,
  news: null,
  modeling: null,
  alternatives: null,
  executiveSummary: null,
  chartMap: {},
  chatMessages: [],
  chatStreaming: "",
  swarmHealth: null,
  connected: false,
}

/* ── Reducer ─────────────────────────────────────── */
type Action =
  | { type: "SSE_EVENT"; event: SSEEvent }
  | { type: "SET_CONNECTED"; connected: boolean }
  | { type: "ADD_CHAT_MESSAGE"; message: ChatMessage }
  | { type: "RESET" }

function reducer(state: SwarmState, action: Action): SwarmState {
  switch (action.type) {
    case "SET_CONNECTED":
      return { ...state, connected: action.connected }

    case "ADD_CHAT_MESSAGE":
      return { ...state, chatMessages: [...state.chatMessages, action.message] }

    case "RESET":
      return { ...initialState }

    case "SSE_EVENT": {
      const evt = action.event

      switch (evt.type) {
        case "status":
          return {
            ...state,
            agentStatuses: {
              ...state.agentStatuses,
              [evt.agent_id]: evt.status,
            },
          }

        case "thought":
          return {
            ...state,
            thoughts: [
              {
                agent_id: evt.agent_id,
                text: evt.text,
                timestamp: evt.timestamp || new Date().toISOString(),
              },
              ...state.thoughts,
            ].slice(0, 50),
          }

        case "report_section":
          switch (evt.section) {
            case "portfolio":
              return { ...state, portfolio: evt.data as PortfolioData }
            case "news":
              return { ...state, news: evt.data as NewsData }
            case "modeling": {
              const modelingData = evt.data as ModelingData
              const newCharts: Record<string, ChartOutput> = {
                ...state.chartMap,
              }
              for (const chart of modelingData.charts ?? []) {
                newCharts[chart.chart_id] = chart
              }
              return { ...state, modeling: modelingData, chartMap: newCharts }
            }
            case "alternatives":
              return { ...state, alternatives: evt.data as AlternativesData }
            case "executive_summary":
              return {
                ...state,
                executiveSummary: (evt.data as { summary: string }).summary,
              }
            default:
              return state
          }

        case "chat_response":
          if (evt.done) {
            const msg: ChatMessage = {
              id: Date.now().toString(),
              role: "assistant",
              content: state.chatStreaming + evt.token,
              agents: ["orchestrator"],
            }
            return {
              ...state,
              chatMessages: [...state.chatMessages, msg],
              chatStreaming: "",
            }
          }
          return { ...state, chatStreaming: state.chatStreaming + evt.token }

        case "swarm_health":
          return {
            ...state,
            swarmHealth: {
              active_agents: evt.active_agents,
              signals_per_min: evt.signals_per_min,
              processing_power: evt.processing_power,
            },
          }

        default:
          return state
      }
    }

    default:
      return state
  }
}

/* ── Context ─────────────────────────────────────── */
interface SwarmContextValue {
  state: SwarmState
  dispatch: React.Dispatch<Action>
  triggerReport: () => void
  sendChat: (message: string) => void
}

const SwarmContext = createContext<SwarmContextValue | null>(null)

export function SwarmProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState)

  useEffect(() => {
    dispatch({ type: "SET_CONNECTED", connected: true })

    const cleanup = connectSSE((event) => {
      dispatch({ type: "SSE_EVENT", event })
    })

    return () => {
      cleanup()
      dispatch({ type: "SET_CONNECTED", connected: false })
    }
  }, [])

  const triggerReport = useCallback(() => {
    dispatch({ type: "RESET" })
    const backendUrl = import.meta.env.VITE_API_URL as string | undefined
    if (backendUrl) {
      fetch(`${backendUrl}/report`, { method: "POST" })
        .then((response) =>
          console.log("Report triggered successfully", response),
        )
        .catch(console.error)
    }
    setTimeout(() => {
      const cleanup = connectSSE((event) => {
        dispatch({ type: "SSE_EVENT", event })
      })
      return cleanup
    }, 100)
  }, [])

  const sendChat = useCallback((message: string) => {
    dispatch({
      type: "ADD_CHAT_MESSAGE",
      message: { id: Date.now().toString(), role: "user", content: message },
    })
    // In real app, this would POST to backend which then streams response via SSE
    // For now, simulate a response
    setTimeout(() => {
      dispatch({
        type: "ADD_CHAT_MESSAGE",
        message: {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Based on the current swarm intelligence synthesis, here's what I found regarding "${message}":\n\nThe Portfolio Alpha engine indicates your current holdings are weighted 42% toward Technology, with a portfolio beta of 1.12. The Sentiment Engine reports mixed signals — NVDA is strongly bullish (0.91) while JPM shows bearish sentiment (-0.48) due to commercial real estate concerns.\n\nWould you like me to run a deeper analysis on any specific holding?`,
          agents: ["orchestrator", "portfolio", "news"],
        },
      })
    }, 1500)
  }, [])

  return (
    <SwarmContext.Provider value={{ state, dispatch, triggerReport, sendChat }}>
      {children}
    </SwarmContext.Provider>
  )
}

export function useSwarm() {
  const ctx = useContext(SwarmContext)
  if (!ctx) throw new Error("useSwarm must be used within SwarmProvider")
  return ctx
}
