import { describe, it, expect } from "vitest";

// Replicate the pure derivation logic from AgentGraph.tsx
type AgentId = "orchestrator" | "portfolio" | "news" | "modeling" | "alternatives";

interface Thought {
    agent_id: AgentId;
    text: string;
    timestamp: string;
}

function deriveLatestThoughts(thoughts: Thought[]): Partial<Record<AgentId, string>> {
    const map: Partial<Record<AgentId, string>> = {};
    for (const t of thoughts) {
        if (!map[t.agent_id]) map[t.agent_id] = t.text;
    }
    return map;
}

describe("deriveLatestThoughts", () => {
    it("returns most recent thought per agent (thoughts are newest-first)", () => {
        const thoughts: Thought[] = [
            { agent_id: "portfolio", text: "Analyzing sector weights", timestamp: "2" },
            { agent_id: "portfolio", text: "Loading data", timestamp: "1" },
        ];
        const result = deriveLatestThoughts(thoughts);
        expect(result.portfolio).toBe("Analyzing sector weights");
    });

    it("returns empty map for no thoughts", () => {
        expect(deriveLatestThoughts([])).toEqual({});
    });

    it("handles multiple agents", () => {
        const thoughts: Thought[] = [
            { agent_id: "news", text: "Scoring sentiment", timestamp: "3" },
            { agent_id: "portfolio", text: "Computing beta", timestamp: "2" },
            { agent_id: "news", text: "Fetching headlines", timestamp: "1" },
        ];
        const result = deriveLatestThoughts(thoughts);
        expect(result.news).toBe("Scoring sentiment");
        expect(result.portfolio).toBe("Computing beta");
    });
});
