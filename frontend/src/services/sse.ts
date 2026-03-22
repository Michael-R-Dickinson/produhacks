import {
  SSEWireEvent,
  AgentStatusPayload,
  AgentThoughtPayload,
  AgentMessagePayload,
  ReportChunkPayload,
  ReportCompletePayload,
  ChatResponsePayload,
  AgentId,
} from "../schemas/events"
import type { SSEEvent } from "../schemas/events"
import { startMockSSE } from "./mockSSE"

const SSE_URL = import.meta.env.VITE_SSE_URL as string | undefined

/**
 * Transform a validated wire event into the flat internal format
 * consumed by the reducer.
 */
function toInternalEvent(wire: SSEWireEvent): SSEEvent | null {
  const agentId = AgentId.safeParse(wire.agent_id)
  if (!agentId.success) {
    console.warn("[SSE] Unknown agent_id:", wire.agent_id)
    return null
  }

  switch (wire.event_type) {
    case "agent.status": {
      const p = AgentStatusPayload.safeParse(wire.payload)
      if (!p.success) return null
      return { agent_id: agentId.data, type: "status", status: p.data.status }
    }
    case "agent.thought": {
      const p = AgentThoughtPayload.safeParse(wire.payload)
      if (!p.success) return null
      return {
        agent_id: agentId.data,
        type: "thought",
        text: p.data.text,
        timestamp: new Date(wire.timestamp * 1000).toISOString(),
      }
    }
    case "agent.message": {
      const p = AgentMessagePayload.safeParse(wire.payload)
      if (!p.success) return null
      return {
        agent_id: agentId.data,
        type: "agent_message",
        from: p.data.from,
        to: p.data.to,
        title: p.data.title,
        description: p.data.description,
        direction: p.data.direction,
      }
    }
    case "report.chunk": {
      const p = ReportChunkPayload.safeParse(wire.payload)
      if (!p.success) return null
      // report.chunk maps to report_section for the reducer
      return {
        agent_id: agentId.data,
        type: "report_section",
        section: p.data.section as "portfolio" | "news" | "modeling" | "alternatives" | "executive_summary",
        data: JSON.parse(p.data.content),
      }
    }
    case "report.complete": {
      const p = ReportCompletePayload.safeParse(wire.payload)
      if (!p.success) return null
      return {
        agent_id: agentId.data,
        type: "report_section",
        section: "executive_summary",
        data: { summary: p.data.markdown },
      }
    }
    case "chat.response": {
      const p = ChatResponsePayload.safeParse(wire.payload)
      if (!p.success) return null
      return {
        agent_id: agentId.data,
        type: "chat_response",
        token: p.data.text,
        done: p.data.final,
      }
    }
    default:
      return null
  }
}

/**
 * Connect to the SSE stream from the backend bridge.
 * Falls back to mock SSE when no backend URL is configured.
 */
export function connectSSE(onEvent: (event: SSEEvent) => void): () => void {
  // If no backend URL configured, use mock data
  if (!SSE_URL) {
    console.log("[SSE] No VITE_SSE_URL configured -- using mock SSE")
    return startMockSSE(onEvent)
  }

  console.log(`[SSE] Connecting to ${SSE_URL}`)
  const source = new EventSource(SSE_URL)

  source.onmessage = (e) => {
    try {
      const parsed = JSON.parse(e.data)
      const wireResult = SSEWireEvent.safeParse(parsed)
      if (!wireResult.success) {
        console.warn("[SSE] Invalid wire event:", wireResult.error.format(), parsed)
        return
      }
      const internal = toInternalEvent(wireResult.data)
      if (!internal) {
        console.warn("[SSE] Could not transform event:", wireResult.data.event_type, wireResult.data.payload)
        return
      }
      console.log("[SSE] Received event:", {
        id: internal.agent_id,
        type: internal.type,
      })
      onEvent(internal)
    } catch (err) {
      console.warn("[SSE] Failed to parse event:", err)
    }
  }

  source.onerror = () => {
    console.warn("[SSE] Connection error -- will auto-reconnect")
  }

  return () => source.close()
}
