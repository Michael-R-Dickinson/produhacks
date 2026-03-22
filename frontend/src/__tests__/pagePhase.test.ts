import { describe, it, expect } from "vitest";

// Replicate the pure function as it will be defined in DailyReport.tsx
type PagePhase = "empty" | "generating" | "complete";

function getPagePhase(state: {
    executiveSummary: string | null;
    agentStatuses: Record<string, string>;
    reportTriggered: boolean;
}): PagePhase {
    if (state.executiveSummary !== null) return "complete";
    const anyActive = Object.values(state.agentStatuses).some(
        (s) => s === "working" || s === "done"
    );
    if (anyActive || state.reportTriggered) return "generating";
    return "empty";
}

describe("getPagePhase", () => {
    it("returns 'empty' when no summary, all agents idle, and not triggered", () => {
        expect(getPagePhase({
            executiveSummary: null,
            agentStatuses: { orchestrator: "idle", portfolio: "idle" },
            reportTriggered: false,
        })).toBe("empty");
    });

    it("returns 'generating' when agents are working", () => {
        expect(getPagePhase({
            executiveSummary: null,
            agentStatuses: { orchestrator: "working", portfolio: "idle" },
            reportTriggered: false,
        })).toBe("generating");
    });

    it("returns 'generating' when agents are done but no summary yet", () => {
        expect(getPagePhase({
            executiveSummary: null,
            agentStatuses: { orchestrator: "done", portfolio: "done" },
            reportTriggered: false,
        })).toBe("generating");
    });

    it("returns 'generating' when reportTriggered but no agents active yet", () => {
        expect(getPagePhase({
            executiveSummary: null,
            agentStatuses: { orchestrator: "idle", portfolio: "idle" },
            reportTriggered: true,
        })).toBe("generating");
    });

    it("returns 'complete' when executiveSummary is present", () => {
        expect(getPagePhase({
            executiveSummary: "# Report\nContent here",
            agentStatuses: { orchestrator: "done", portfolio: "done" },
            reportTriggered: true,
        })).toBe("complete");
    });

    it("returns 'complete' even if agents are still working (summary takes priority)", () => {
        expect(getPagePhase({
            executiveSummary: "# Report",
            agentStatuses: { orchestrator: "working" },
            reportTriggered: true,
        })).toBe("complete");
    });
});
