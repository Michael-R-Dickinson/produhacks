---
phase: 01-foundation
plan: 02
subsystem: infra
tags: [uagents, bureau, fastapi, sse, asyncio, threading, cors, pna]

requires:
  - phase: 01-01
    provides: Pydantic message models (requests/responses), mock fixtures, bridge/events.py with push_event()

provides:
  - Five uAgent instances (orchestrator, portfolio, news, modeling, alternatives) with deterministic seeds and mock message handlers
  - Bureau runner in isolated daemon thread with its own asyncio event loop
  - FastAPI bridge with /events SSE endpoint (EventSourceResponse) and /trigger POST endpoint
  - CORSMiddleware with allow_private_network=True for Chrome PNA compliance
  - Single python -m agents.main entrypoint that starts Bureau + uvicorn in one process

affects: [02-orchestration, 03-frontend, 04-chat]

tech-stack:
  added: []
  patterns:
    - Bureau runs in daemon thread with bureau_loop=asyncio.new_event_loop(); FastAPI runs on uvicorn's event loop
    - Cross-loop event delivery via fastapi_loop.call_soon_threadsafe(queue.put_nowait, event) in push_event()
    - FastAPI startup event captures asyncio.get_running_loop() and passes it to launch_bureau()
    - Bureau given port=8006 to avoid conflict with uvicorn on port 8000
    - /trigger endpoint pushes SSE events directly (not through orchestrator agent) for Phase 1 simplicity
    - MOCK_DATA env var read at module level per agent; mock functions called if MOCK_DATA or msg.mock

key-files:
  created:
    - agents/portfolio_agent.py
    - agents/news_agent.py
    - agents/modeling_agent.py
    - agents/alternatives_agent.py
    - agents/orchestrator.py
    - agents/bureau.py
    - agents/bridge/app.py
    - agents/main.py
  modified: []

key-decisions:
  - "Bureau given port=8006 to avoid ASGI server conflict with uvicorn on port 8000 (Bureau starts its own ASGI server by default)"
  - "/trigger FastAPI endpoint pushes events directly via push_event() rather than routing through orchestrator on_rest_post; Phase 2 will wire actual agent dispatch"
  - "FastAPI startup event used to capture uvicorn's event loop and launch Bureau thread (loop=none not supported in uvicorn 0.30.x)"
  - "Orchestrator is minimal stub in Phase 1 — no message handlers, just registered with Bureau for addressability"

patterns-established:
  - "Pattern: Bureau thread isolation — Bureau always gets bureau_loop=asyncio.new_event_loop() in a daemon thread"
  - "Pattern: Cross-loop push — push_event() uses fastapi_loop.call_soon_threadsafe(queue.put_nowait, event)"
  - "Pattern: Domain agent handler — status working, thought, message_received, compute, thought complete, message_sent, status done, ctx.send()"

requirements-completed: [INFRA-01, INFRA-02]

duration: 3min
completed: 2026-03-22
---

# Phase 01 Plan 02: Agent Stub + Bureau + SSE Bridge Summary

**Five uAgents with mock handlers wired to a FastAPI SSE bridge via cross-loop asyncio.Queue; single `python -m agents.main` starts Bureau thread + uvicorn**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-22T06:28:40Z
- **Completed:** 2026-03-22T06:31:40Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- Five stub agents (portfolio, news, modeling, alternatives, orchestrator) with deterministic seeds and addressable uAgent addresses
- Bureau running all 5 agents in a daemon thread with its own isolated asyncio event loop on port 8006
- FastAPI bridge with /events SSE endpoint delivering cross-thread events and /trigger POST endpoint
- CORS configured with allow_private_network=True for Chrome Private Network Access compliance
- End-to-end verified: POST /trigger returns `{"status": "triggered"}` and SSE consumer receives 4 events

## Task Commits

Each task was committed atomically:

1. **Task 1: Five stub agents with mock handlers and SSE event emission** - `bc20441` (feat)
2. **Task 2: Bureau runner, FastAPI bridge with SSE, and main.py entrypoint** - `5492cef` (feat)

## Files Created/Modified

- `agents/portfolio_agent.py` - AnalyzePortfolio handler with push_event calls and mock_portfolio_response
- `agents/news_agent.py` - FetchNews handler with ticker-specific thought text
- `agents/modeling_agent.py` - RunModel handler with risk metrics thought
- `agents/alternatives_agent.py` - AnalyzeAlternatives handler with crypto/correlation thought
- `agents/orchestrator.py` - Minimal stub Agent registered with Bureau; dispatch in Phase 2
- `agents/bureau.py` - launch_bureau() starts Bureau in daemon thread, injects fastapi loop and queue into events module
- `agents/bridge/app.py` - FastAPI app, /events SSE, /trigger POST, CORSMiddleware, startup event loop capture
- `agents/main.py` - Entrypoint: load_dotenv, register Bureau startup hook, uvicorn.run on port 8000

## Decisions Made

- Bureau needs `port=8006` — it starts its own ASGI server and defaults to 8000, conflicting with uvicorn. Fixed by specifying Bureau port explicitly.
- `loop="none"` is not a valid uvicorn 0.30.x parameter. Used `@app.on_event("startup")` to capture `asyncio.get_running_loop()` and pass it to `launch_bureau()`. FastAPI's startup event is the correct hook.
- Orchestrator agent is a minimal stub. The plan noted `on_rest_post` decorator behavior is uncertain; the simpler approach of handling /trigger directly in FastAPI was chosen and documented.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Bureau port conflict with uvicorn**
- **Found during:** Task 2 (startup verification)
- **Issue:** Bureau defaults to port 8000 for its internal ASGI server, conflicting with uvicorn also on 8000, causing `[Errno 48] address already in use`
- **Fix:** Added `port=8006` to `Bureau(loop=bureau_loop, port=8006)` in bureau.py
- **Files modified:** agents/bureau.py
- **Verification:** `python -m agents.main` starts cleanly; Bureau logs "Starting server on http://0.0.0.0:8006"
- **Committed in:** `5492cef` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Required fix — Bureau cannot start without a distinct port. No scope creep.

## Issues Encountered

- `loop="none"` parameter not supported in uvicorn 0.30.x (plan noted this as a possible fallback). Used the startup event approach which works cleanly.

## User Setup Required

None - no external service configuration required.

## Self-Check: PASSED

All 8 files exist. Both task commits confirmed in git log: bc20441, 5492cef.

## Next Phase Readiness

- All 5 agents addressable and importable with stable deterministic addresses
- Bureau + uvicorn co-process confirmed working
- /events SSE endpoint ready to receive browser EventSource connections
- /trigger POST endpoint ready for frontend button integration
- Phase 2 can now implement actual ctx.send() dispatch from orchestrator to domain agents
