import type { AgentId, AgentStatus, SSEEvent } from "../schemas/events";
import { startMockSSE } from "./mockSSE";

const SSE_URL = import.meta.env.VITE_SSE_URL as string | undefined;

/** Map FastAPI bridge ``SSEEvent.model_dump()`` (``event_type`` + ``payload``) to UI events. */
function adaptBridgeSsePayload(raw: unknown): SSEEvent | null {
    if (!raw || typeof raw !== "object") return null;
    const r = raw as Record<string, unknown>;
    if (typeof r.type === "string") {
        return raw as SSEEvent;
    }
    const et = r.event_type;
    const agent_id = r.agent_id;
    if (typeof et !== "string" || typeof agent_id !== "string") return null;
    const payload =
        r.payload && typeof r.payload === "object" ? (r.payload as Record<string, unknown>) : {};
    if (et === "agent.status") {
        return {
            agent_id: agent_id as AgentId,
            type: "status",
            status: payload.status as AgentStatus,
        };
    }
    if (et === "agent.thought") {
        return {
            agent_id: agent_id as AgentId,
            type: "thought",
            text: String(payload.text ?? ""),
        };
    }
    return null;
}

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
        console.log("[SSE] No VITE_SSE_URL configured — using mock SSE");
        return startMockSSE(onEvent);
    }

    console.log(`[SSE] Connecting to ${SSE_URL}`);
    const source = new EventSource(SSE_URL);

    source.onmessage = (e) => {
        try {
            const raw = JSON.parse(e.data) as unknown;
            const adapted = adaptBridgeSsePayload(raw);
            if (adapted) {
                onEvent(adapted);
                return;
            }
            if (raw && typeof raw === "object" && "type" in (raw as object)) {
                onEvent(raw as SSEEvent);
                return;
            }
            console.warn("[SSE] Unrecognized event shape:", raw);
        } catch (err) {
            console.warn("[SSE] Failed to parse event:", err);
        }
    };

    source.onerror = () => {
        console.warn("[SSE] Connection error — will auto-reconnect");
    };

    return () => source.close();
}
