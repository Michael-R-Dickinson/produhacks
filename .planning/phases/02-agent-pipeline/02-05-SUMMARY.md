---
phase: 02-agent-pipeline
plan: 05
subsystem: api
tags: [python, uagents, gemini, genai, asyncio, orchestrator, sse, tdd]

requires:
  - phase: 02-agent-pipeline
    plan: 02
    provides: portfolio_agent with compute functions and PortfolioResponse
  - phase: 02-agent-pipeline
    plan: 03
    provides: news_agent with FinBERT sentiment and NewsResponse
  - phase: 02-agent-pipeline
    plan: 04
    provides: alternatives_agent with CoinGecko/Finnhub and AlternativesResponse

provides:
  - Full orchestrator fan-out to 4 domain agents via asyncio.gather
  - detect_contradictions: flags bearish news on top holdings and bullish news with negative momentum
  - build_synthesis_prompt: structured thematic prompt with all agent data serialized as JSON
  - synthesize_report: Gemini LLM call with lazy-initialized genai.Client
  - on_rest_post /report handler with fallback mock responses on agent timeout
  - Bridge /report endpoint that POSTs to orchestrator REST endpoint and streams SSE events
  - agents/.env.example documenting required API keys

affects:
  - 03-bridge (frontend consumes report.complete SSE events from this pipeline)

tech-stack:
  added: []
  patterns:
    - Lazy Gemini client initialization: get_gemini() initializes on first call to avoid import-time env key requirement
    - asyncio.gather with return_exceptions=True for fault-tolerant concurrent fan-out
    - safe_result() extracts message from (msg, sender) uAgents tuple, falls back to mock on Exception
    - ReportResponse uAgents Model used instead of dict for on_rest_post compatibility

key-files:
  created:
    - agents/tests/test_orchestrator.py
    - agents/.env.example
  modified:
    - agents/orchestrator.py
    - agents/bridge/app.py

key-decisions:
  - "genai.Client lazy-initialized via get_gemini() so orchestrator.py can be imported without GEMINI_API_KEY set"
  - "on_rest_post response type must be a uAgents Model subclass (not dict) - ReportResponse added"
  - "ctx.send_and_receive returns (message, sender) tuple in uAgents 0.24.0 - extract_msg helper unwraps it"
  - "model_dump(exclude=...) not supported by uAgents Model - pop charts from dict after calling model_dump()"

patterns-established:
  - "Lazy client pattern: module-level None sentinel, getter function initializes on first call"
  - "Fault-tolerant fan-out: asyncio.gather with return_exceptions=True + safe_result() for mock fallbacks"

requirements-completed:
  - ORCH-01
  - ORCH-02
  - ORCH-03
  - ORCH-04
  - ORCH-05

duration: ~4min
completed: 2026-03-22
---

# Phase 02 Plan 05: Orchestrator Fan-Out, Contradiction Detection, and LLM Synthesis Summary

**Complete report pipeline: asyncio.gather fan-out to 4 domain agents, cross-agent contradiction detection, Gemini thematic synthesis, bridge /report endpoint — curl-verifiable via SSE report.complete event**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-03-22T07:31:00Z
- **Completed:** 2026-03-22T07:35:00Z
- **Tasks:** 2 automated + 1 human verify checkpoint
- **Files modified:** 4

## Accomplishments

- Rewrote orchestrator.py with full asyncio.gather fan-out to all 4 domain agents concurrently with return_exceptions=True for fault tolerance
- Implemented detect_contradictions() for cross-agent signal analysis (bearish news on top holdings, bullish news vs negative momentum)
- Implemented build_synthesis_prompt() structuring all agent data as thematic sections for Gemini
- Wired bridge /report endpoint to POST to orchestrator REST handler at localhost:8005/submit/report
- Created 15 passing unit tests for safe_result, detect_contradictions, and build_synthesis_prompt
- Added .env.example documenting MOCK_DATA, FINNHUB_API_KEY, GEMINI_API_KEY

## Task Commits

Each task was committed atomically (TDD: RED then GREEN for Task 1):

1. **RED: Failing tests for orchestrator pure logic** - `dd80a00` (test)
2. **GREEN: Full orchestrator implementation** - `c70fb57` (feat)
3. **Task 2: Bridge /report endpoint and .env.example** - `4b2fb00` (feat)

**Plan metadata:** _(docs commit follows)_

## Files Created/Modified

- `agents/orchestrator.py` - Full implementation: asyncio.gather fan-out, safe_result, detect_contradictions, build_synthesis_prompt, synthesize_report, on_rest_post /report handler
- `agents/tests/test_orchestrator.py` - 15 unit tests for pure logic functions (no OpenAI API calls)
- `agents/bridge/app.py` - Added /report endpoint; /trigger renamed with deprecation note
- `.env.example` - Documents MOCK_DATA, FINNHUB_API_KEY, GEMINI_API_KEY

## Decisions Made

- genai.Client lazy-initialized via `get_gemini()` getter so the module can be imported during tests without GEMINI_API_KEY set — mirrors the FinBERT lazy-loading pattern from Plan 03
- `on_rest_post` response type must be a uAgents Model subclass, not `dict` — added `ReportResponse(Model)` with a single `status: str` field
- `ctx.send_and_receive` returns a `(message, sender)` tuple in uAgents 0.24.0 — `extract_msg()` helper unwraps tuples before passing to `safe_result()`
- `Model.model_dump()` does not accept `exclude` kwarg in uAgents — charts popped from dict after calling `model_dump()` to avoid inflating the prompt

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] AsyncOpenAI module-level init fails import without OPENAI_API_KEY**
- **Found during:** Task 1 GREEN (first test run)
- **Issue:** `_openai = AsyncOpenAI()` at module level raises OpenAIError when OPENAI_API_KEY is not set, breaking all test imports
- **Fix:** Wrapped in `get_openai()` lazy getter with `_openai: AsyncOpenAI | None = None` sentinel
- **Files modified:** agents/orchestrator.py
- **Verification:** All 15 tests pass without OPENAI_API_KEY in environment
- **Committed in:** c70fb57

**2. [Rule 1 - Bug] on_rest_post rejected dict as response_model**
- **Found during:** Task 1 GREEN (second test run)
- **Issue:** uAgents ASGI server ValidationError — response_model must be a uAgents Model or pydantic BaseModel subclass, not `dict`
- **Fix:** Added `class ReportResponse(UAgentModel): status: str` and used it in the decorator
- **Files modified:** agents/orchestrator.py
- **Verification:** Module imports cleanly; tests pass
- **Committed in:** c70fb57

**3. [Rule 1 - Bug] model_dump(exclude=...) not supported by uAgents Model**
- **Found during:** Task 1 GREEN (third test run, TestBuildSynthesisPrompt)
- **Issue:** `modeling.model_dump(exclude={"charts"})` raises TypeError — uAgents Model.model_dump() does not accept keyword args
- **Fix:** Call `model_dump()` then `pop("charts", None)` on the resulting dict
- **Files modified:** agents/orchestrator.py
- **Verification:** All 15 tests pass
- **Committed in:** c70fb57

---

**Total deviations:** 3 auto-fixed (all Rule 1 bugs)
**Impact on plan:** All fixes required for test correctness and runtime compatibility. No scope creep.

## Issues Encountered

None beyond the auto-fixed deviations above.

## User Setup Required

Live mode (MOCK_DATA=false) requires:
- `FINNHUB_API_KEY` — get from https://finnhub.io/dashboard
- `GEMINI_API_KEY` — get from https://aistudio.google.com/app/apikey

Mock mode (`MOCK_DATA=true`) works without any API keys.

## Next Phase Readiness

- Phase 2 complete: all 4 domain agents implemented, orchestrator wired, bridge /report endpoint live
- curl POST to /report (with MOCK_DATA=true) exercises the full pipeline and streams report.complete SSE event
- Phase 3 (React Flow visualization) can now consume real SSE events from the running pipeline
- No blockers for Phase 3

## Self-Check: PASSED

- agents/orchestrator.py: exists, contains asyncio.gather, ctx.send_and_receive, portfolio_agent.address, def detect_contradictions, def build_synthesis_prompt, def safe_result, gpt-4o-mini, AsyncOpenAI, on_rest_post, report_complete, return_exceptions=True
- agents/tests/test_orchestrator.py: exists, contains def test_detect_contradictions, 15 tests all pass
- agents/bridge/app.py: contains @app.post("/report"), localhost:8005/submit/report, EQUITY_TICKERS, timeout=60.0
- agents/.env.example: contains FINNHUB_API_KEY, OPENAI_API_KEY
- Task commits dd80a00, c70fb57, 4b2fb00 verified in git log

---
*Phase: 02-agent-pipeline*
*Completed: 2026-03-22*
