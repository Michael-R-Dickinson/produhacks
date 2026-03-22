/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useContext,
  useReducer,
  useCallback,
  useRef,
  useEffect,
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
  MessageDirection,
  ReportCompleteEvent,
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

export interface AgentMessage {
  from: AgentId
  to: AgentId
  title: string
  description: string
  direction: MessageDirection
  timestamp: string
}

export interface SwarmState {
  agentStatuses: Record<AgentId, AgentStatus>
  thoughts: Thought[]
  agentMessages: AgentMessage[]
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
  reportTriggered: boolean
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
  agentMessages: [],
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
  reportTriggered: false,
}

/* ── Reducer ─────────────────────────────────────── */
type Action =
  | { type: "SSE_EVENT"; event: SSEEvent }
  | { type: "SET_CONNECTED"; connected: boolean }
  | { type: "ADD_CHAT_MESSAGE"; message: ChatMessage }
  | { type: "TRIGGER_REPORT" }

function reducer(state: SwarmState, action: Action): SwarmState {
  switch (action.type) {
    case "SET_CONNECTED":
      return { ...state, connected: action.connected }

    case "ADD_CHAT_MESSAGE":
      return { ...state, chatMessages: [...state.chatMessages, action.message] }

    case "TRIGGER_REPORT":
      return { ...initialState, reportTriggered: true }

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

        case "report_complete": {
          const rc = evt as ReportCompleteEvent
          const newCharts: Record<string, ChartOutput> = { ...state.chartMap }
          for (const chart of rc.charts) {
            newCharts[chart.chart_id] = chart
          }
          return {
            ...state,
            executiveSummary: rc.markdown,
            chartMap: newCharts,
          }
        }

        case "agent_message":
          return {
            ...state,
            agentMessages: [
              {
                from: evt.from,
                to: evt.to,
                title: evt.title,
                description: evt.description,
                direction: evt.direction,
                timestamp: new Date().toISOString(),
              },
              ...state.agentMessages,
            ].slice(0, 50),
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

const EVENT_BUFFER_INTERVAL_MS = 500

export function SwarmProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState)
  const sseCleanupRef = useRef<(() => void) | null>(null)
  const eventQueueRef = useRef<SSEEvent[]>([])
  const drainTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Start/stop the drain loop
  const startDrain = useCallback(() => {
    if (drainTimerRef.current) return
    drainTimerRef.current = setInterval(() => {
      const next = eventQueueRef.current.shift()
      if (next) {
        dispatch({ type: "SSE_EVENT", event: next })
      }
    }, EVENT_BUFFER_INTERVAL_MS)
  }, [])

  const stopDrain = useCallback(() => {
    if (drainTimerRef.current) {
      clearInterval(drainTimerRef.current)
      drainTimerRef.current = null
    }
  }, [])

  // Flush remaining events and stop on unmount
  useEffect(() => {
    return () => {
      stopDrain()
      for (const evt of eventQueueRef.current) {
        dispatch({ type: "SSE_EVENT", event: evt })
      }
      eventQueueRef.current = []
    }
  }, [stopDrain])

  const enqueueEvent = useCallback(
    (event: SSEEvent) => {
      eventQueueRef.current.push(event)
      startDrain()
    },
    [startDrain],
  )

  const triggerReport = useCallback(() => {
    // Clean up any existing SSE connection and buffer
    sseCleanupRef.current?.()
    sseCleanupRef.current = null
    stopDrain()
    eventQueueRef.current = []

    dispatch({ type: "TRIGGER_REPORT" })

    const backendUrl = import.meta.env.VITE_API_URL as string | undefined
    if (backendUrl) {
      fetch(`${backendUrl}/report`, { method: "POST" })
        .then((response) =>
          console.log("Report triggered successfully", response),
        )
        .catch(console.error)
    }

    // Connect SSE after a brief delay to let backend start streaming
    setTimeout(() => {
      dispatch({ type: "SET_CONNECTED", connected: true })
      sseCleanupRef.current = connectSSE(enqueueEvent)
    }, 100)
  }, [enqueueEvent, stopDrain])

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
          content: `Based on the current swarm intelligence synthesis, here's what I found regarding "${message}":\n\nThe Portfolio Analyzer indicates your current holdings are weighted 42% toward Technology, with a portfolio beta of 1.12. The News Scraper reports mixed signals — NVDA is strongly bullish (0.91) while JPM shows bearish sentiment (-0.48) due to commercial real estate concerns.\n\nWould you like me to run a deeper analysis on any specific holding?`,
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
