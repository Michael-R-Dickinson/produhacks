# Phase 3: Frontend and Visualization - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

React app displays a live agent graph with streaming thoughts during report generation, then transitions to the completed markdown report with embedded charts. The existing mockup UI is replaced with real data integration. CSV upload triggers report generation. The standalone swarm activity page is removed -- its visualization moves into the daily report page.

</domain>

<decisions>
## Implementation Decisions

### Agent Graph on Report Page
- Full agent graph (SVG canvas with nodes + animated edges) displayed on the daily report page while agents are working
- Static layout -- fixed node positions with animated edge pulses, no dragging
- Agent thoughts integrated directly into the nodes (each node shows its latest thought inline, like a speech bubble)
- No separate thought stream panel -- thoughts live on the nodes themselves
- Remove the standalone `/swarm` route and `SwarmActivity.tsx` page entirely

### Swarm-to-Report Transition
- Smooth collapse + fade in: graph collapses upward (height animates to 0), then report fades in below (~500ms)
- Transition triggers automatically when the `executive_summary` report_section event arrives from the orchestrator
- No user interaction required -- seamless automatic transition

### Report Layout
- All 5 card components removed (ExecutiveSummary, PortfolioHealth, MarketSentiment, QuantSignals, IntelligenceFeed)
- Full markdown report is the entire page content after transition
- Date header: simple left-aligned date ("March 22, 2026"), nothing else -- then the report below
- Generate report trigger: empty state CTA when no report exists (centered "Generate Report" button). After report loads, just date + report. Re-trigger available from sidebar

### Chart Rendering
- Charts are base64 PNGs embedded in markdown via `[chart:UUID]` token resolution (existing pattern in ExecutiveSummary.tsx)
- Constrained max-width (~500px), centered within the report column
- Raw image only -- no borders, backgrounds, or captions. Markdown text around the chart provides context
- Default matplotlib style (white background) is acceptable -- no need for dark-themed charts
- Charts must render inline properly within react-markdown and be correctly sized (not overflowing or tiny)

### Claude's Discretion
- Exact animation timing and easing for the collapse/fade transition
- Agent node layout positions within the SVG canvas
- Thought bubble styling on nodes (font size, truncation, positioning)
- Empty state CTA design and copy
- How to handle the "Generate Report" re-trigger from sidebar
- Loading/shimmer state styling
- Whether to keep or remove the Sidebar agent status indicators during generation (graph already shows status)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 1 & 2 Context
- `.planning/phases/01-foundation/01-CONTEXT.md` -- SSE event contract (3 event types: thoughts, messages, status), typed message models, process architecture
- `.planning/phases/02-agent-pipeline/02-CONTEXT.md` -- Report narrative decisions (unified, professional analyst tone, chart-heavy), thought feed personality per agent, orchestrator synthesis approach

### Requirements
- `.planning/REQUIREMENTS.md` -- REPT-01 through REPT-03 (report display), GRPH-01 through GRPH-04 (agent graph visualization)

### Project Context
- `.planning/PROJECT.md` -- Core value, hackathon constraints (24h), tech stack (Vite + React)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/components/report/ExecutiveSummary.tsx` -- Already has `react-markdown` + `remark-gfm` rendering with `[chart:UUID]` token resolution via `resolveChartRefs()`. Core of the new report view
- `frontend/src/pages/SwarmActivity.tsx` -- SVG agent graph with animated edges, node positioning, status-based styling. Visualization logic to extract and adapt for the report page
- `frontend/src/context/SwarmContext.tsx` -- Full state management with reducer, SSE integration, `triggerReport()` method, chartMap for base64 images
- `frontend/src/schemas/events.ts` -- Zod-validated event types, agent metadata (names, colors, icons), all data models (PortfolioData, NewsData, etc.)
- `frontend/src/services/sse.ts` + `mockSSE.ts` -- SSE connection and mock simulation already working

### Established Patterns
- Custom CSS design system in `index.css` (no UI framework) -- cards, badges, shimmer loading, grid layouts, CSS animations (dashFlow, fadeInUp, nodeFloat)
- Zod schema validation on all incoming SSE events
- Inline styles heavily used alongside global CSS classes
- `recharts` library available for any additional charting needs

### Integration Points
- `SwarmContext.triggerReport()` -- resets state, POSTs to `/trigger`, reconnects SSE. Already wired up
- `report_section` event with `section: "executive_summary"` delivers the markdown report string
- `chartMap` state (Record<string, ChartOutput>) populated by `report_section` events with modeling data
- Agent status tracked in `agentStatuses` state -- drives node highlighting
- `thoughts` array in state -- source for node-integrated thought display

</code_context>

<specifics>
## Specific Ideas

- The swarm graph should feel like watching agents collaborate in real time -- nodes light up, edges pulse, thoughts appear on each node as they work
- The transition to the report should feel like "the agents just finished and here's what they produced" -- seamless, not jarring
- The report itself should feel like reading a professional analyst brief -- clean typography, properly sized charts inline, no clutter
- Date at top should be understated -- the report content is the star

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 03-frontend-and-visualization*
*Context gathered: 2026-03-22*
