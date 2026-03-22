import { describe, it, expect } from "vitest";

// Replicate the pure function as it will be defined in DailyReport.tsx
type PagePhase = "empty" | "generating" | "complete";

function getPagePhase(state: {
    executiveSummary: string | null;
    agentStatuses: Record<string, string>;
}): PagePhase {
    if (state.executiveSummary !== null) return "complete";
    const anyActive = Object.values(state.agentStatuses).some(
        (s) => s === "working" || s === "done"
    );
    return anyActive ? "generating" : "empty";
}

describe("getPagePhase", () => {
    it("returns 'empty' when no summary and all agents idle", () => {
        expect(getPagePhase({
            executiveSummary: null,
            agentStatuses: { orchestrator: "idle", portfolio: "idle" },
        })).toBe("empty");
    });

    it("returns 'generating' when agents are working", () => {
        expect(getPagePhase({
            executiveSummary: null,
            agentStatuses: { orchestrator: "working", portfolio: "idle" },
        })).toBe("generating");
    });

    it("returns 'generating' when agents are done but no summary yet", () => {
        expect(getPagePhase({
            executiveSummary: null,
            agentStatuses: { orchestrator: "done", portfolio: "done" },
        })).toBe("generating");
    });

    it("returns 'complete' when executiveSummary is present", () => {
        expect(getPagePhase({
            executiveSummary: "# Report\nContent here",
            agentStatuses: { orchestrator: "done", portfolio: "done" },
        })).toBe("complete");
    });

    it("returns 'complete' even if agents are still working (summary takes priority)", () => {
        expect(getPagePhase({
            executiveSummary: "# Report",
            agentStatuses: { orchestrator: "working" },
        })).toBe("complete");
    });
});
