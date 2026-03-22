# Phase 3: Frontend and Visualization - Research

**Researched:** 2026-03-22
**Domain:** React frontend integration, SVG graph animation, react-markdown rendering, CSS transitions
**Confidence:** HIGH

## Summary

This phase transforms the existing mockup UI into a fully live, data-driven experience. The codebase already contains working building blocks: a draggable SVG agent graph in `SwarmActivity.tsx`, markdown rendering with chart token resolution in `ExecutiveSummary.tsx`, and full SSE state management in `SwarmContext.tsx`. The work is primarily integration and refactoring, not greenfield development.

The most critical technical finding is that **react-markdown 10.x's `defaultUrlTransform` blocks `data:` URIs** — the scheme is not in the allowed protocol list (`https?|ircs?|mailto|xmpp`). The existing `resolveChartRefs()` pattern inlines base64 PNGs as `![title](data:image/png;base64,...)` markdown, which will be silently stripped to empty `src` attributes unless a custom `urlTransform` prop is passed to the `<Markdown>` component. This must be fixed for charts to render.

The phase has five distinct work areas: (1) rebuilding `DailyReport.tsx` as the unified page with the graph-then-report layout, (2) adapting the graph component from `SwarmActivity.tsx` with thought bubbles on nodes, (3) implementing the collapse/fade transition triggered by `executive_summary` arrival, (4) building the full-page markdown report renderer with working chart embedding, and (5) wiring the empty-state CTA and sidebar re-trigger.

**Primary recommendation:** Extract graph logic from SwarmActivity into a `AgentGraph` component, fix `urlTransform` in the markdown renderer, delete the 5 card components, remove the `/swarm` route, and drive all UI phase transitions from `state.executiveSummary !== null`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Full agent graph (SVG canvas with nodes + animated edges) displayed on the daily report page while agents are working
- Static layout — fixed node positions with animated edge pulses, no dragging
- Agent thoughts integrated directly into the nodes (each node shows its latest thought inline, like a speech bubble)
- No separate thought stream panel — thoughts live on the nodes themselves
- Remove the standalone `/swarm` route and `SwarmActivity.tsx` page entirely
- Smooth collapse + fade in: graph collapses upward (height animates to 0), then report fades in below (~500ms)
- Transition triggers automatically when the `executive_summary` report_section event arrives from the orchestrator
- No user interaction required — seamless automatic transition
- All 5 card components removed (ExecutiveSummary, PortfolioHealth, MarketSentiment, QuantSignals, IntelligenceFeed)
- Full markdown report is the entire page content after transition
- Date header: simple left-aligned date ("March 22, 2026"), nothing else — then the report below
- Generate report trigger: empty state CTA when no report exists (centered "Generate Report" button). After report loads, just date + report. Re-trigger available from sidebar
- Charts are base64 PNGs embedded in markdown via `[chart:UUID]` token resolution (existing pattern in ExecutiveSummary.tsx)
- Constrained max-width (~500px), centered within the report column
- Raw image only — no borders, backgrounds, or captions. Markdown text around the chart provides context
- Default matplotlib style (white background) is acceptable
- Charts must render inline properly within react-markdown and be correctly sized

### Claude's Discretion
- Exact animation timing and easing for the collapse/fade transition
- Agent node layout positions within the SVG canvas
- Thought bubble styling on nodes (font size, truncation, positioning)
- Empty state CTA design and copy
- How to handle the "Generate Report" re-trigger from sidebar
- Loading/shimmer state styling
- Whether to keep or remove the Sidebar agent status indicators during generation

### Deferred Ideas (OUT OF SCOPE)
- None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REPT-01 | Renders report as formatted markdown with embedded charts | react-markdown 10.x + custom `urlTransform` to allow `data:` URIs; `resolveChartRefs()` already exists in ExecutiveSummary.tsx |
| REPT-02 | User can trigger on-demand report generation | `triggerReport()` already wired in SwarmContext; empty-state CTA calls it; Sidebar already has "Generate Report" button |
| REPT-03 | Report displays as unified narrative (not sectioned per-agent) | Single `<Markdown>` render of `state.executiveSummary` replaces all 5 card components |
| GRPH-01 | Node per agent displayed as card with name and status | SVG+HTML node structure already exists in SwarmActivity.tsx; adapt for static layout with thought bubble |
| GRPH-02 | Real-time streaming thought feed in each agent card | `state.thoughts` array tracks per-agent thoughts; latest thought per agent drives node bubble text |
| GRPH-03 | Animated message pulses traveling along edge connections | dashFlow CSS animation + SVG animateMotion already implemented in SwarmActivity.tsx |
| GRPH-04 | Hover on connections shows message title and description | New: SVG edge hit area with `<title>` tooltip or onMouseEnter handler showing latest inter-agent message |
</phase_requirements>

## Standard Stack

### Core (already installed — no new installs needed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| react-markdown | 10.1.0 | Render markdown string to React elements | Already used; v10 exports `Markdown` as default |
| remark-gfm | 4.0.1 | GitHub Flavored Markdown (tables, strikethrough) | Already used with react-markdown |
| lucide-react | 0.577.0 | Icons for agent nodes | Already used throughout app |
| react-router-dom | 7.13.1 | Route management; `/swarm` route to be removed | Already used |

### No New Dependencies Required

All visualization work uses native SVG, CSS animations, and existing libraries. No additional charting or animation libraries are needed.

**Installation:**
```bash
# No new packages required
```

**Version verification (confirmed from node_modules):**
- react-markdown: 10.1.0 (installed)
- remark-gfm: 4.0.1 (installed)

## Architecture Patterns

### Recommended Project Structure After Phase 3

```
frontend/src/
├── pages/
│   ├── DailyReport.tsx          # Rebuilt — unified graph+report page
│   ├── Chat.tsx                 # Unchanged
│   └── Portfolio.tsx            # Unchanged
│   # SwarmActivity.tsx — DELETED
├── components/
│   ├── layout/
│   │   ├── AppShell.tsx         # Unchanged
│   │   ├── TopNav.tsx           # Unchanged
│   │   └── Sidebar.tsx          # Minor: update "Generate Report" nav item behavior
│   └── report/
│       ├── AgentGraph.tsx       # NEW — extracted+adapted from SwarmActivity.tsx
│       └── ReportView.tsx       # NEW — markdown renderer with chart support
│       # All 5 old card components DELETED
├── context/
│   └── SwarmContext.tsx         # Unchanged (already has all state)
└── schemas/
    └── events.ts                # Unchanged
```

### Pattern 1: Phase State from SSE

Drive all three UI phases (`empty`, `generating`, `complete`) from a single derived value based on SwarmContext state — no additional state required.

**What:** `state.executiveSummary !== null` signals completion. `Object.values(state.agentStatuses).some(s => s === 'working' || s === 'done')` signals generation in progress.

**When to use:** On every render in DailyReport.tsx to select which UI to show.

**Example:**
```typescript
// Source: SwarmContext.tsx state shape — derived, not stored
type PagePhase = "empty" | "generating" | "complete";

function getPagePhase(state: SwarmState): PagePhase {
    if (state.executiveSummary !== null) return "complete";
    const anyActive = Object.values(state.agentStatuses).some(
        (s) => s === "working" || s === "done"
    );
    return anyActive ? "generating" : "empty";
}
```

### Pattern 2: Collapse Transition via CSS Height Animation

**What:** The graph container height animates from its natural height to 0, then the report fades in. Triggered by setting a boolean flag when `state.executiveSummary` first becomes non-null.

**When to use:** One-shot transition — once triggered it does not reverse.

**Example:**
```typescript
// Source: CSS transitions pattern, standard browser behavior
// In component:
const isCollapsing = phase === "complete";

// JSX:
<div
    style={{
        height: isCollapsing ? 0 : 500,
        overflow: "hidden",
        transition: "height 500ms ease-in-out",
    }}
>
    <AgentGraph />
</div>

{/* Report fades in after graph collapses */}
<div
    style={{
        opacity: phase === "complete" ? 1 : 0,
        transition: "opacity 300ms ease 500ms", /* 500ms delay = after collapse */
    }}
>
    <ReportView />
</div>
```

### Pattern 3: Per-Agent Latest Thought Derivation

**What:** Derive each agent's latest thought from `state.thoughts` (which is sorted newest-first by the reducer). Display truncated in node speech bubble.

**When to use:** In `AgentGraph` component when rendering each node.

**Example:**
```typescript
// Source: SwarmContext.tsx — thoughts are prepended newest-first (slice 0,50)
const latestThoughtPerAgent = useMemo(() => {
    const map: Partial<Record<AgentId, string>> = {};
    for (const thought of state.thoughts) {
        if (!map[thought.agent_id]) {
            map[thought.agent_id] = thought.text;
        }
    }
    return map;
}, [state.thoughts]);
```

### Pattern 4: SVG animateMotion with Percentage Coordinates

The existing SVG animation in SwarmActivity uses `animateMotion` with `<mpath>` referencing a `<path>` element by ID. However, the path `d` attribute uses the raw percentage numbers (e.g. `M50,50 L20,22`) rather than pixel values — this is a bug in the existing code since SVG coordinates are not percentages. For a static layout, compute pixel positions from the percentage values relative to the container's rendered size.

**What:** With a static layout, hardcode pixel positions in the SVG that correspond to the fixed percentage positions in the HTML. Use `useRef` + `getBoundingClientRect` or simply define consistent px values for a known container width.

**Simpler alternative:** Use the container dimensions from a `ResizeObserver` or set a fixed-height container so positions can be computed as: `px = (pct / 100) * containerSize`.

**Example (static layout):**
```typescript
// Source: MDN SVG animateMotion specification
// Fixed positions for 960px max-width container, 500px height:
const NODE_POSITIONS: Record<AgentId, { x: number; y: number }> = {
    orchestrator: { x: 480, y: 250 },
    portfolio:    { x: 192, y: 110 },
    news:         { x: 749, y: 100 },
    modeling:     { x: 768, y: 390 },
    alternatives: { x: 211, y: 400 },
};
// SVG width/height = "100%" with viewBox="0 0 960 500"
// Then animateMotion path uses actual coordinate values
```

### Pattern 5: react-markdown Custom urlTransform for data: URIs (CRITICAL FIX)

**What:** react-markdown 10.x's `defaultUrlTransform` allows only `https?|ircs?|mailto|xmpp` protocols. Base64 image data URIs (`data:image/png;base64,...`) are stripped to empty strings, producing broken `<img src="">` elements.

**Required fix:** Pass a custom `urlTransform` prop that passes `data:` URIs through unchanged.

**Example:**
```typescript
// Source: react-markdown lib/index.js line 421-438, verified in node_modules
function allowDataUrls(url: string): string {
    // Allow data: URIs (used for embedded base64 chart images)
    if (url.startsWith("data:")) return url;
    // Fall back to default safe-URL behavior for everything else
    return defaultUrlTransform(url);
}

// Usage:
import { defaultUrlTransform } from "react-markdown";

<Markdown
    remarkPlugins={[remarkGfm]}
    urlTransform={allowDataUrls}
>
    {resolvedMarkdown}
</Markdown>
```

### Pattern 6: Chart Image Sizing via Markdown components Prop

**What:** Constrain chart images to max-width 500px centered. Use the `components` prop to override `img` rendering.

**Example:**
```typescript
// Source: react-markdown Components API
<Markdown
    remarkPlugins={[remarkGfm]}
    urlTransform={allowDataUrls}
    components={{
        img: ({ src, alt }) => (
            <img
                src={src}
                alt={alt ?? ""}
                style={{
                    maxWidth: 500,
                    display: "block",
                    margin: "16px auto",
                }}
            />
        ),
    }}
>
    {resolvedMarkdown}
</Markdown>
```

### Anti-Patterns to Avoid

- **Dragging in AgentGraph:** SwarmActivity has full drag-and-drop support. Remove all drag state, pointer capture, and handlers — static layout only. `cursor: grab` should become `cursor: default`.
- **Storing phase as state:** Derive `pagePhase` from `state.executiveSummary` — no `useState` for this.
- **Multiple SSE reconnects in triggerReport:** The existing `triggerReport()` in SwarmContext leaks the second SSE connection (the returned cleanup is lost in the setTimeout). This is a pre-existing issue — note it but do not fix it in this phase unless it causes visible problems.
- **Keeping all 5 card component files:** They should be deleted, not just unused, to avoid dead code and build bloat.
- **Using `xlinkHref` for mpath:** `xlinkHref` is deprecated in SVG 2. Prefer `href` attribute for `<mpath>`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Markdown rendering | Custom markdown parser/renderer | `react-markdown` with `remark-gfm` (already installed) |
| CSS height collapse animation | JS-driven height measurement and animation | CSS `transition: height` — works reliably for fixed heights |
| SVG edge pulse animation | requestAnimationFrame loop | CSS `@keyframes dashFlow` (already defined in index.css) + SVG `animateMotion` |
| URL sanitization override | Custom regex URL replace | `urlTransform` prop on `<Markdown>` |
| Per-agent thought tracking | Separate reducer state per agent | Derive from existing `state.thoughts` array via `useMemo` |

**Key insight:** The CSS design system and animation keyframes are already defined in `index.css`. Adding new animations should extend that file, not add inline `<style>` tags.

## Common Pitfalls

### Pitfall 1: react-markdown strips base64 data URIs silently
**What goes wrong:** `![chart](data:image/png;base64,...)` renders as a broken image with empty `src`. No error is thrown.
**Why it happens:** `defaultUrlTransform` only allows `https?|ircs?|mailto|xmpp` protocols. `data:` is blocked as a security measure.
**How to avoid:** Always pass `urlTransform={allowDataUrls}` to `<Markdown>` when rendering content with embedded images.
**Warning signs:** Images render but with broken icon; browser shows `GET ` (empty URL) in network tab.

### Pitfall 2: SVG animateMotion path coordinates are not CSS percentages
**What goes wrong:** The existing `SwarmActivity.tsx` defines paths as `M50,50 L20,22` using percentage numbers, but SVG coordinate space is pixels. This causes the travelling dot to animate in the wrong location.
**Why it happens:** The HTML nodes use `left: 50%; top: 50%` CSS but the SVG `<path>` uses the same numbers as raw SVG coordinates (in a 100×100 coordinate space, not matching the actual SVG width/height).
**How to avoid:** Use SVG `viewBox` with explicit dimensions matching the node position numbers, OR compute pixel positions from percentage values given the actual container dimensions. Using `viewBox="0 0 100 100"` with percentage-based positions is the simplest approach.
**Warning signs:** The pulse dot jumps to the wrong part of the SVG canvas.

### Pitfall 3: CSS height transition requires explicit height values
**What goes wrong:** `transition: height 500ms` does not animate if `height` changes from `auto` to `0` — the browser cannot interpolate from `auto`.
**Why it happens:** CSS cannot tween to/from `auto` because it's not a numeric value.
**How to avoid:** Use a fixed pixel height (e.g. `height: 500px`) for the expanded state, not `height: auto`. The agent graph container is already `height: 500px` in `.agent-graph-container`.
**Warning signs:** Graph snaps to hidden instantly instead of collapsing smoothly.

### Pitfall 4: Thought bubble overflow on small nodes
**What goes wrong:** Long thought strings overflow the node area or push other nodes' labels out of position.
**Why it happens:** Thoughts are arbitrary-length strings from the LLM.
**How to avoid:** Truncate thoughts to ~60 characters with ellipsis. Use `maxWidth` matching or slightly wider than the node circle.
**Warning signs:** Node text visually overlaps adjacent nodes.

### Pitfall 5: react-markdown 10.x named vs default export
**What goes wrong:** `import { Markdown } from "react-markdown"` and `import ReactMarkdown from "react-markdown"` both work, but some IDE autocomplete suggests `MarkdownAsync` or `MarkdownHooks` which are different components.
**Why it happens:** v10 exports multiple components; `Markdown` is the default export, `MarkdownAsync` is for async plugins, `MarkdownHooks` is experimental.
**How to avoid:** Use `import Markdown from "react-markdown"` (default import). Existing code already uses this pattern correctly.

## Code Examples

Verified patterns from official sources and installed node_modules:

### Correct react-markdown import (v10.x)
```typescript
// Source: node_modules/react-markdown/index.js — exports Markdown as default
import Markdown from "react-markdown";
import { defaultUrlTransform } from "react-markdown";
import remarkGfm from "remark-gfm";
```

### Full chart-safe markdown renderer
```typescript
// Source: react-markdown lib/index.js lines 421-438 (urlTransform API)
import Markdown, { defaultUrlTransform } from "react-markdown";
import remarkGfm from "remark-gfm";

function allowDataUrls(url: string): string {
    if (url.startsWith("data:")) return url;
    return defaultUrlTransform(url);
}

export function ReportView({ markdown, chartMap }: { markdown: string; chartMap: Record<string, ChartOutput> }) {
    const resolved = useMemo(
        () => resolveChartRefs(markdown, chartMap),
        [markdown, chartMap]
    );
    return (
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
    );
}
```

### SVG graph with correct viewBox for percentage-based positions
```typescript
// Source: MDN SVG specification — viewBox establishes coordinate system
// Positions map 0-100 range to SVG coordinate space
<svg
    viewBox="0 0 100 100"
    preserveAspectRatio="none"
    width="100%"
    height="100%"
    style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
>
    {/* Animated travelling dot on an edge */}
    <path
        id="path-portfolio"
        d="M50,50 L20,22"
        fill="none"
        stroke="none"
    />
    <circle r="0.8" fill={agent.color} opacity="0.8">
        <animateMotion dur="2s" repeatCount="indefinite">
            <mpath href="#path-portfolio" />
        </animateMotion>
    </circle>
</svg>
```

### Graph collapse transition
```typescript
// Source: CSS transitions specification — height must be explicit for transition
const graphHeight = phase === "complete" ? 0 : 500;

<div
    style={{
        height: graphHeight,
        overflow: "hidden",
        transition: "height 500ms ease-in-out",
    }}
>
    <AgentGraph />
</div>
```

### Derive per-agent latest thought
```typescript
// Source: SwarmContext.tsx — thoughts prepended newest-first (line 96-100)
const latestThought = useMemo(() => {
    const map: Partial<Record<AgentId, string>> = {};
    for (const t of state.thoughts) {
        if (!map[t.agent_id]) map[t.agent_id] = t.text;
    }
    return map;
}, [state.thoughts]);

// Truncate for display:
const MAX_THOUGHT_LENGTH = 60;
const display = (text: string) =>
    text.length > MAX_THOUGHT_LENGTH ? text.slice(0, MAX_THOUGHT_LENGTH) + "…" : text;
```

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| `transformImageUri` prop (react-markdown v8) | `urlTransform` prop (react-markdown v9+) | Old prop is deprecated; causes warning; `urlTransform` is the correct API |
| `xlinkHref` on SVG `<mpath>` | `href` on SVG `<mpath>` | `xlinkHref` is SVG 1.1; `href` is SVG 2 and works in all modern browsers |
| Separate `/swarm` route for agent visualization | Agent graph embedded inline in DailyReport | Per CONTEXT.md decisions — graph lives on the report page |

**Deprecated/outdated in this codebase:**
- `transformImageUri` / `transformLinkUri` props: replaced by `urlTransform` in react-markdown v9+
- `xlinkHref`: the existing SwarmActivity.tsx uses this on `<mpath>`; should be replaced with `href`
- The 5 card components (ExecutiveSummary, PortfolioHealth, MarketSentiment, QuantSignals, IntelligenceFeed): all deleted this phase

## Open Questions

1. **GRPH-04: What inter-agent message data is available for edge hover tooltips?**
   - What we know: `state.thoughts` contains per-agent thought strings. There is no explicit inter-agent message log in `SwarmState`.
   - What's unclear: Whether the backend emits any event that captures the content of a specific orchestrator-to-agent message (as opposed to agent thoughts). The `ThoughtEvent` has `text` but does not distinguish "message sent" from "internal thought".
   - Recommendation: For GRPH-04, use the latest thought of the target agent as the hover content — it is the closest available proxy. If backend emits distinct message events later, update accordingly.

2. **Sidebar cleanup: remove "Agent Views" nav links?**
   - What we know: The Sidebar currently has per-agent nav links (`/?agent=portfolio`, etc.) and a "Generate Report" button. These agent-view links route to the home page with query params but no component actually reads those params.
   - What's unclear: Whether the per-agent nav links should be removed along with the `/swarm` route, or left as dead UI.
   - Recommendation: Remove the `Agent Views` section from Sidebar in this phase. The sidebar should only show "Generate Report" (CTA button) and the bottom links (Settings, Support). This is within Claude's Discretion scope.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None currently installed in frontend |
| Config file | none — Wave 0 setup needed |
| Quick run command | `cd frontend && npx vitest run --reporter=verbose` (after install) |
| Full suite command | `cd frontend && npx vitest run` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REPT-01 | `resolveChartRefs()` replaces `[chart:UUID]` tokens with base64 data URIs | unit | `npx vitest run src/__tests__/resolveChartRefs.test.ts` | Wave 0 |
| REPT-01 | base64 `data:` URIs survive `allowDataUrls` transform and are not stripped | unit | `npx vitest run src/__tests__/urlTransform.test.ts` | Wave 0 |
| REPT-01 | Unknown chart IDs are left as `[chart:UUID]` literal text | unit | `npx vitest run src/__tests__/resolveChartRefs.test.ts` | Wave 0 |
| REPT-02 | `triggerReport()` dispatches RESET action and POSTs to `/trigger` | unit | `npx vitest run src/__tests__/SwarmContext.test.ts` | Wave 0 |
| REPT-03 | `getPagePhase()` returns correct phase based on state | unit | `npx vitest run src/__tests__/pagePhase.test.ts` | Wave 0 |
| GRPH-02 | Latest-thought-per-agent derivation returns most recent thought for each agent | unit | `npx vitest run src/__tests__/latestThought.test.ts` | Wave 0 |
| GRPH-03 | animateMotion path is present for agents in "working" status | smoke | manual / browser visual check | manual-only |
| GRPH-04 | Edge hover shows latest thought text | smoke | manual / browser visual check | manual-only |

### Sampling Rate
- **Per task commit:** `cd frontend && npx vitest run --reporter=verbose`
- **Per wave merge:** `cd frontend && npx vitest run`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `frontend/src/__tests__/resolveChartRefs.test.ts` — covers REPT-01 chart token replacement
- [ ] `frontend/src/__tests__/urlTransform.test.ts` — covers REPT-01 data URI passthrough
- [ ] `frontend/src/__tests__/pagePhase.test.ts` — covers REPT-03 phase derivation logic
- [ ] `frontend/src/__tests__/latestThought.test.ts` — covers GRPH-02 thought derivation
- [ ] `frontend/src/__tests__/SwarmContext.test.ts` — covers REPT-02 triggerReport behavior
- [ ] `frontend/vitest.config.ts` — vitest configuration (jsdom environment, React plugin)
- [ ] Install: `cd frontend && npm install -D vitest @vitest/ui jsdom @testing-library/react @testing-library/jest-dom`

## Sources

### Primary (HIGH confidence)
- `node_modules/react-markdown/index.js` + `lib/index.js` — verified `defaultUrlTransform` allows only `https?|ircs?|mailto|xmpp`; `data:` is blocked; `urlTransform` prop API confirmed
- `node_modules/react-markdown/package.json` — version 10.1.0 confirmed; `Markdown` exported as default
- `node_modules/remark-gfm/package.json` — version 4.0.1 confirmed
- `frontend/src/pages/SwarmActivity.tsx` — graph implementation, animation patterns, drag state to remove
- `frontend/src/context/SwarmContext.tsx` — full state shape, thoughts array ordering, triggerReport implementation
- `frontend/src/schemas/events.ts` — all event types, AgentId enum, AGENTS metadata array
- `frontend/src/index.css` — existing CSS classes: `.agent-graph-container`, `.agent-node`, `.node-floater`, `@keyframes dashFlow`, `@keyframes fadeInUp`, `@keyframes nodeFloat`
- `frontend/src/components/report/ExecutiveSummary.tsx` — `resolveChartRefs()` function, existing ReactMarkdown usage
- `frontend/package.json` — complete dependency inventory

### Secondary (MEDIUM confidence)
- MDN SVG animateMotion spec — `href` attribute on `<mpath>` preferred over deprecated `xlinkHref`
- CSS Transitions spec — `height: auto` cannot be transitioned; requires explicit numeric height

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified from installed node_modules
- Architecture: HIGH — all patterns derived from reading the actual codebase
- react-markdown urlTransform pitfall: HIGH — verified by reading lib/index.js source
- Pitfalls: HIGH — derived from code inspection, not speculation
- Validation architecture: MEDIUM — vitest not yet installed; test commands assume it will be

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable libraries; react-markdown and remark-gfm versions pinned)
