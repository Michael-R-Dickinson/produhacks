import type { SSEEvent } from "../schemas/events"
import { startMockSSE } from "./mockSSE"

const SSE_URL = import.meta.env.VITE_SSE_URL as string | undefined

/**
 * Connect to the SSE stream from the backend bridge.
 * Falls back to mock SSE when no backend URL is configured.
 *
 * Your friend just needs to set VITE_SSE_URL=http://localhost:8000/events
 * in .env and the real agent events will flow in.
 */
export function connectSSE(onEvent: (event: SSEEvent) => void): () => void {
  // If no backend URL configured, use mock data
  if (!SSE_URL) {
    console.log("[SSE] No VITE_SSE_URL configured — using mock SSE")
    return startMockSSE(onEvent)
  }

  console.log(`[SSE] Connecting to ${SSE_URL}`)
  const source = new EventSource(SSE_URL)

  source.onmessage = (e) => {
    try {
      console.log("[SSE] Received event:", e.data)
      const data = JSON.parse(e.data) as SSEEvent
      onEvent(data)
    } catch (err) {
      console.warn("[SSE] Failed to parse event:", err)
    }
  }

  source.onerror = () => {
    console.warn("[SSE] Connection error — will auto-reconnect")
  }

  return () => source.close()
}
