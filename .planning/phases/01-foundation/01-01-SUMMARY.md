---
phase: 01-foundation
plan: 01
subsystem: infra
tags: [uagents, pydantic, fastapi, sse-starlette, python, asyncio, mock-data]

requires: []
provides:
  - "8 typed Pydantic message models (4 request, 4 response) importable from agents.models"
  - "4 mock data fixtures returning valid typed response instances"
  - "push_event() bridge utility using call_soon_threadsafe for cross-loop event push"
  - "Installable Python package (Wealth Council) with pytest configured"
affects:
  - 01-02
  - 01-03

tech-stack:
  added:
    - uagents==0.24.0
    - fastapi>=0.115.0 (resolved to 0.135.1)
    - sse-starlette==3.3.3
    - uvicorn>=0.30.0 (resolved to 0.42.0)
    - python-dotenv==1.x
    - httpx==0.27.x
    - pytest + pytest-asyncio
  patterns:
    - "uagents.Model subclass pattern for all inter-agent message types"
    - "call_soon_threadsafe cross-loop event push from Bureau thread to FastAPI loop"
    - "MOCK_DATA env var toggle (checked at handler time, not import time)"
    - "Symmetric typed contracts: one request type per agent, one response type per agent"

key-files:
  created:
    - agents/pyproject.toml
    - agents/models/requests.py
    - agents/models/responses.py
    - agents/models/__init__.py
    - agents/bridge/events.py
    - agents/mocks/portfolio.py
    - agents/mocks/news.py
    - agents/mocks/modeling.py
    - agents/mocks/alternatives.py
    - agents/mocks/__init__.py
    - agents/tests/test_models.py
    - agents/tests/test_mock.py
    - .env.example
    - .gitignore
  modified: []

key-decisions:
  - "Relaxed fastapi version constraint from ==0.115.* to >=0.115.0 to resolve sse-starlette==3.3.3 starlette>=0.49.1 conflict; resolved to fastapi 0.135.1 + starlette 0.52.1 (satisfies allow_private_network requirement)"
  - "Added [tool.setuptools.packages.find] with where=['..'] to pyproject.toml so editable install from agents/ correctly discovers the agents package root one level up"

patterns-established:
  - "All inter-agent messages extend uagents.Model (Pydantic BaseModel subclass)"
  - "Mock fixtures are pure functions returning typed response instances — no side effects"
  - "push_event() silently no-ops if bridge not initialized — safe to call from agents before bridge is wired"

requirements-completed: [INFRA-03, INFRA-04]

duration: 3min
completed: 2026-03-22
---

# Phase 1 Plan 01: Foundation Scaffold Summary

**8 typed uAgents/Pydantic message models, 4 mock fixtures, and cross-loop push_event() bridge utility — installable Python package with 10 passing unit tests**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-22T06:22:10Z
- **Completed:** 2026-03-22T06:25:43Z
- **Tasks:** 2
- **Files modified:** 14 created

## Accomplishments

- 4 request models and 4 response models defined as `uagents.Model` subclasses, all importable from `agents.models`
- 4 mock fixtures returning valid typed instances with realistic financial data (sector allocation, news sentiment, Sharpe ratio, crypto prices)
- `push_event()` bridge utility implemented with `call_soon_threadsafe` pattern — thread-safe event push from Bureau thread to FastAPI event loop
- Installable package (`Wealth Council`) with pytest configured; all 10 tests green

## Task Commits

1. **Task 1: Project scaffold, Pydantic message models, and event bridge** - `0ce194e` (feat)
2. **Task 2: Mock data fixtures with unit tests** - `2f30ba0` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `agents/pyproject.toml` - Package config, dependency pinning, pytest configuration
- `agents/models/requests.py` - AnalyzePortfolio, FetchNews, RunModel, AnalyzeAlternatives models
- `agents/models/responses.py` - PortfolioResponse, NewsResponse, ModelResponse, AlternativesResponse models
- `agents/models/__init__.py` - Re-exports all 8 model classes
- `agents/bridge/events.py` - push_event() with call_soon_threadsafe cross-loop pattern
- `agents/mocks/portfolio.py` - mock_portfolio_response() with sector allocation and top holdings
- `agents/mocks/news.py` - mock_news_response() with 5 headlines and aggregate sentiment
- `agents/mocks/modeling.py` - mock_model_response() with Sharpe ratio, volatility, trend slope
- `agents/mocks/alternatives.py` - mock_alternatives_response() with crypto prices and correlations
- `agents/mocks/__init__.py` - Re-exports all 4 mock functions
- `agents/tests/test_models.py` - 5 tests: imports, roundtrip serialization, re-exports
- `agents/tests/test_mock.py` - 5 tests: mock return types, field assertions, init imports
- `.env.example` - Documents MOCK_DATA=true
- `.gitignore` - Standard Python ignores

## Decisions Made

- Relaxed `fastapi==0.115.*` to `fastapi>=0.115.0` because `sse-starlette==3.3.3` requires `starlette>=0.49.1` which is incompatible with fastapi 0.115.x. Resolved to fastapi 0.135.1 + starlette 0.52.1 — this satisfies the `allow_private_network=True` requirement (needs starlette>=0.51.0).
- Added `[tool.setuptools.packages.find]` config pointing `where = [".."]` so the editable install discovers the `agents` package from the repo root rather than treating `models/`, `mocks/`, `bridge/` as top-level packages.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed fastapi/sse-starlette version incompatibility**
- **Found during:** Task 1 (dependency installation)
- **Issue:** `fastapi==0.115.*` requires `starlette<0.47.0`; `sse-starlette==3.3.3` requires `starlette>=0.49.1` — mutually exclusive
- **Fix:** Changed `fastapi==0.115.*` to `fastapi>=0.115.0` allowing resolution to fastapi 0.135.1 + starlette 0.52.1
- **Files modified:** `agents/pyproject.toml`
- **Verification:** `uv pip install` succeeded; all tests pass
- **Committed in:** `0ce194e` (Task 1 commit)

**2. [Rule 3 - Blocking] Fixed setuptools flat-layout package discovery**
- **Found during:** Task 1 (dependency installation)
- **Issue:** `uv pip install -e ".[dev]"` from `agents/` directory failed because setuptools discovered `models/`, `mocks/`, `bridge/` as multiple top-level packages rather than sub-packages of `agents`
- **Fix:** Added `[tool.setuptools.packages.find]` with `where = [".."]` and `include = ["agents*"]` to `pyproject.toml`
- **Files modified:** `agents/pyproject.toml`
- **Verification:** `uv pip install` succeeded; package importable as `agents.*`
- **Committed in:** `0ce194e` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 3 - blocking install issues)
**Impact on plan:** Both fixes were necessary to make the package installable. No scope creep — all planned files created exactly as specified.

## Issues Encountered

- Version conflict between fastapi 0.115.x and sse-starlette 3.3.3 via shared starlette dependency — resolved by relaxing fastapi lower bound. The resulting starlette 0.52.1 is better than the minimum required (0.51.0) for `allow_private_network=True`.

## User Setup Required

None - no external service configuration required. Run `.venv/bin/pytest agents/tests/ -x -q` to verify.

## Next Phase Readiness

- All typed message contracts stable — Plan 02 can implement agents and bridge against these interfaces
- Mock fixtures ready for Plan 02 agent handlers to call in mock mode
- push_event() ready for Plan 02 to wire with FastAPI event loop reference
- Blocker to address: uagents Bureau `run_async()` vs `run()` behavior needs verification in Plan 02 (see RESEARCH.md open questions)

---
*Phase: 01-foundation*
*Completed: 2026-03-22*
