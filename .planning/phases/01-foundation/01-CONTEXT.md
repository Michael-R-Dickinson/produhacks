# Phase 1: Foundation - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Scaffold the three-layer architecture: uAgents Bureau running all 5 agents, FastAPI bridge with SSE streaming, and Pydantic message models defining all inter-agent contracts. Mock data mode for all agents. No domain logic, no frontend -- just the verified infrastructure that everything else plugs into.

</domain>

<decisions>
## Implementation Decisions

### Process Architecture
- Single Python process -- Bureau runs in a background thread with its own event loop, FastAPI runs on the main asyncio loop
- Communication between Bureau thread and FastAPI via asyncio.Queue
- One `python main.py` entrypoint starts both Bureau and FastAPI
- If Bureau's event loop blocks FastAPI despite threading, escalate -- but start with this approach

### SSE Event Contract
- Single multiplexed SSE endpoint (`/events`) -- one EventSource connection from the browser
- Three event types streamed:
  1. **Agent thoughts** -- real-time text of what each agent is doing (explicit `emit_thought()` calls at key computation steps, hand-authored)
  2. **Agent-to-agent messages** -- when one agent sends a message to another (powers edge animations in Phase 3)
  3. **Status changes** -- agent lifecycle events (idle, working, done, error) for node highlighting
- Each SSE event tagged with `agent_id` so the frontend can route to the correct node
- Report delivery mechanism (SSE event vs separate REST) at Claude's discretion

### Message Model Design
- **Typed per-agent** for both requests and responses -- symmetric contracts
- Request types: `AnalyzePortfolio`, `FetchNews`, `RunModel`, `AnalyzeAlternatives` (orchestrator sends specific typed requests to each agent)
- Response types: `PortfolioResponse`, `NewsResponse`, `ModelResponse`, `AlternativesResponse` (each with domain-specific fields)
- **Raw structured data only** -- no pre-formatted summary strings. Agents return numbers, metrics, and structured objects. The orchestrator's LLM interprets raw data directly
- Typed requests enable selective dispatch (critical for Phase 4 chat where only relevant agents fire)

### Mock Data Strategy
- Claude's discretion on toggle mechanism and mock data shape
- Mock agents should be functional enough to verify the full SSE event pipeline (thoughts, messages, status changes)

### Claude's Discretion
- Mock data toggle mechanism (env var, config file, CLI flag)
- Mock data shape and realism level
- Report delivery over SSE vs separate REST endpoint
- Exact asyncio.Queue topology (one queue per agent vs single shared queue)
- Agent seed phrases and addressing strategy
- Error handling patterns for agent communication failures

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### fetch.ai / uAgents
- `.planning/research/STACK.md` -- uAgents 0.24.0 specifics, Bureau pattern, `@agent.on_rest_post()` decorator
- `.planning/research/ARCHITECTURE.md` -- Agent communication patterns, `ctx.send` / `ctx.send_and_receive`, address-based messaging, Bureau process model
- `.planning/research/PITFALLS.md` -- Hosted agent statelessness, Chrome PNA blocking, anti-patterns (don't run Bureau inside FastAPI, don't put REST on Protocols)

### SSE / Bridge
- `.planning/research/ARCHITECTURE.md` -- FastAPI SSE bridge pattern, asyncio.Queue for event streaming
- `.planning/research/STACK.md` -- sse-starlette library recommendation

### Project Context
- `.planning/PROJECT.md` -- Core value, constraints, key decisions
- `.planning/REQUIREMENTS.md` -- INFRA-01 through INFRA-04 requirements

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None -- greenfield project

### Established Patterns
- None -- patterns will be established in this phase

### Integration Points
- Phase 2 agents will implement the typed request/response contracts defined here
- Phase 3 React app will connect to the SSE endpoint defined here
- Phase 4 chat will use the typed request messages for selective agent dispatch

</code_context>

<specifics>
## Specific Ideas

- The agent graph visualization (Phase 3) needs the SSE contract to be rich enough to power node cards with streaming thoughts, animated edge pulses, and status highlighting -- the event types defined here are designed for that
- Typed messages were chosen specifically because Phase 4 chat needs selective dispatch, not broadcast -- build the contracts right from Phase 1

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-03-21*
