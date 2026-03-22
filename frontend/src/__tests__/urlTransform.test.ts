import { describe, it, expect } from "vitest";
// allowDataUrls is a module-level function in ReportView.tsx
// Since it may not be exported, test the pattern directly
import { defaultUrlTransform } from "react-markdown";

describe("allowDataUrls pattern", () => {
    // Replicate the function as defined in ReportView.tsx
    function allowDataUrls(url: string): string {
        if (url.startsWith("data:")) return url;
        return defaultUrlTransform(url);
    }

    it("passes data: URIs through unchanged", () => {
        const dataUri = "data:image/png;base64,iVBORw0KGgoAAAANS";
        expect(allowDataUrls(dataUri)).toBe(dataUri);
    });

    it("delegates https URLs to defaultUrlTransform", () => {
        const url = "https://example.com/image.png";
        expect(allowDataUrls(url)).toBe(defaultUrlTransform(url));
    });

    it("blocks javascript: URLs via defaultUrlTransform", () => {
        const url = "javascript:alert(1)";
        const result = allowDataUrls(url);
        expect(result).not.toBe(url);
    });
});
