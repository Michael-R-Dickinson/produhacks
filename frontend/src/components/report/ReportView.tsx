import { useMemo, type JSX } from "react";
import Markdown, { defaultUrlTransform } from "react-markdown";
import remarkGfm from "remark-gfm";
import { useSwarm } from "../../context/SwarmContext";
import type { ChartOutput } from "../../schemas/events";

export function resolveChartRefs(markdown: string, chartMap: Record<string, ChartOutput>): string {
    return markdown.replace(/\[chart:([a-f0-9]+)\]/g, (_match, id: string) => {
        const chart = chartMap[id];
        if (!chart) return _match;
        return `![${chart.title}](data:image/png;base64,${chart.image_base64})`;
    });
}

function allowDataUrls(url: string): string {
    if (url.startsWith("data:")) return url;
    return defaultUrlTransform(url);
}

export default function ReportView(): JSX.Element | null {
    const { state } = useSwarm();

    const resolved = useMemo(
        () => state.executiveSummary ? resolveChartRefs(state.executiveSummary, state.chartMap) : "",
        [state.executiveSummary, state.chartMap]
    );

    if (!state.executiveSummary) return null;

    return (
        <div className="fade-in-up" style={{ fontSize: 14, lineHeight: 1.8, color: "var(--text-primary)" }}>
            <Markdown
                remarkPlugins={[remarkGfm]}
                urlTransform={allowDataUrls}
                components={{
                    img: ({ src, alt }) => (
                        <img
                            src={src}
                            alt={alt ?? ""}
                            style={{ maxWidth: 500, display: "block", margin: "16px auto" }}
                        />
                    ),
                }}
            >
                {resolved}
            </Markdown>
        </div>
    );
}
