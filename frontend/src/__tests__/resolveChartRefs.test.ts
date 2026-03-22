import { describe, it, expect } from "vitest";
import { resolveChartRefs } from "../components/report/ReportView";

describe("resolveChartRefs", () => {
    const mockChartMap = {
        abc123: {
            chart_id: "abc123",
            chart_type: "line",
            title: "Portfolio Returns",
            image_base64: "iVBORw0KGgoAAAANS",
            summary: "Shows returns over time",
        },
    };

    it("replaces [chart:UUID] token with markdown image using base64 data URI", () => {
        const input = "Here is the chart: [chart:abc123]";
        const result = resolveChartRefs(input, mockChartMap);
        expect(result).toContain("![Portfolio Returns](data:image/png;base64,iVBORw0KGgoAAAANS)");
    });

    it("leaves unknown chart IDs as literal text", () => {
        const input = "Missing: [chart:unknown999]";
        const result = resolveChartRefs(input, mockChartMap);
        expect(result).toBe("Missing: [chart:unknown999]");
    });

    it("handles multiple chart tokens in one string", () => {
        const multiMap = {
            ...mockChartMap,
            def456: {
                chart_id: "def456",
                chart_type: "bar",
                title: "Sector Allocation",
                image_base64: "AAABBBCCC",
                summary: "Sector breakdown",
            },
        };
        const input = "First: [chart:abc123] Second: [chart:def456]";
        const result = resolveChartRefs(input, multiMap);
        expect(result).toContain("![Portfolio Returns]");
        expect(result).toContain("![Sector Allocation]");
    });

    it("returns original string when no chart tokens present", () => {
        const input = "No charts here, just text.";
        const result = resolveChartRefs(input, mockChartMap);
        expect(result).toBe(input);
    });
});
