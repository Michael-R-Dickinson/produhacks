---
phase: 02-agent-pipeline
plan: 01
subsystem: api
tags: [pydantic, uagents, matplotlib, mock-data, portfolio, python]

requires:
  - phase: 01-foundation
    provides: agents package structure, uagents Model base class, test infrastructure

provides:
  - Updated PortfolioResponse with correlation_matrix field
  - Updated AlternativesResponse with trend_signals, btc_dominance, commodities
  - ReportRequest model for Bridge -> Orchestrator communication
  - agents/data/portfolio.py central mock portfolio (12 holdings, 6 sectors)
  - Real base64 PNG chart embedded in agents/mocks/modeling.py
  - Phase 2 Python dependencies installed (openai, transformers, torch, pandas, numpy, yfinance, matplotlib)

affects:
  - 02-02 (portfolio agent uses agents.data.portfolio)
  - 02-03 (alternatives agent uses expanded AlternativesResponse)
  - 02-04 (modeling agent uses real chart mock)
  - 02-05 (orchestrator uses ReportRequest)
  - 03-bridge (bridge uses ReportRequest to trigger pipeline)

tech-stack:
  added:
    - openai>=1.0.0
    - transformers>=4.40.0
    - torch>=2.0.0
    - pandas>=2.0.0
    - numpy>=1.26.0
    - yfinance>=0.2.38
    - matplotlib>=3.9.0
  patterns:
    - Central mock data module (agents/data/) imported by all mock providers
    - Script-generated assets embedded as module constants (MOCK_CHART_BASE64)

key-files:
  created:
    - agents/data/__init__.py
    - agents/data/portfolio.py
    - agents/scripts/__init__.py
    - agents/scripts/generate_mock_chart.py
  modified:
    - agents/pyproject.toml
    - agents/models/responses.py
    - agents/models/requests.py
    - agents/models/__init__.py
    - agents/mocks/portfolio.py
    - agents/mocks/alternatives.py
    - agents/mocks/modeling.py
    - agents/tests/test_models.py

key-decisions:
  - "agents/data/portfolio.py is the single source of truth for mock holdings — all mock providers import from it"
  - "MOCK_CHART_BASE64 embedded as a module constant in modeling.py rather than loaded from disk at runtime"
  - "correlation_matrix uses all 10 equity tickers with realistic within-sector / cross-sector correlation values"

patterns-established:
  - "Central data module pattern: agents/data/ holds shared test/mock fixtures imported by mocks/ and agents"
  - "Script-generated assets pattern: scripts/ generates artifacts that get embedded as constants in mocks/"

requirements-completed:
  - PORT-01
  - MODL-03

duration: 12min
completed: 2026-03-22
---

# Phase 02 Plan 01: Contracts, Dependencies, and Mock Data Foundation Summary

**Pydantic model contracts expanded with correlation_matrix and alternatives fields, 12-holding mock portfolio centralized in agents/data/, and a real 51940-char matplotlib PNG embedded in the modeling mock**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-03-22T07:19:56Z
- **Completed:** 2026-03-22T07:31:56Z
- **Tasks:** 2
- **Files modified:** 11

## Accomplishments

- Added 7 Phase 2 Python libraries to pyproject.toml and installed them via uv pip
- Updated PortfolioResponse (correlation_matrix), AlternativesResponse (trend_signals, btc_dominance, commodities), and added ReportRequest
- Created agents/data/portfolio.py with MOCK_PORTFOLIO (12 holdings across 6 sectors: Technology, Healthcare, Financials, Energy, Consumer Discretionary, plus 2 crypto)
- Generated realistic portfolio performance vs S&P 500 chart via matplotlib; embedded 51940-char base64 PNG as MOCK_CHART_BASE64 in modeling mock
- Updated all 3 mock providers to match expanded contracts; all 6 model tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1: Install Phase 2 dependencies and update model contracts** - `ed75b15` (feat)
2. **Task 2: Create central mock portfolio and update mock responses** - `c5149a6` (feat)

**Plan metadata:** _(docs commit follows)_

## Files Created/Modified

- `agents/pyproject.toml` - Added 7 Phase 2 dependencies
- `agents/models/responses.py` - correlation_matrix on PortfolioResponse; expanded AlternativesResponse
- `agents/models/requests.py` - Added ReportRequest model
- `agents/models/__init__.py` - Export ReportRequest
- `agents/tests/test_models.py` - New fields coverage + ReportRequest test
- `agents/data/__init__.py` - Package marker (empty)
- `agents/data/portfolio.py` - MOCK_PORTFOLIO, EQUITY_TICKERS, CRYPTO_TICKERS, ALL_TICKERS
- `agents/mocks/portfolio.py` - Imports from agents.data.portfolio; adds 10x10 correlation_matrix
- `agents/mocks/alternatives.py` - Added trend_signals, btc_dominance, commodities
- `agents/mocks/modeling.py` - MOCK_CHART_BASE64 constant + updated ChartOutput usage
- `agents/scripts/generate_mock_chart.py` - matplotlib chart generator (8x4in, dpi=72, 1-year trend)

## Decisions Made

- agents/data/portfolio.py is the single source of truth for mock holdings — all mock providers import from it, preventing drift between mocks
- MOCK_CHART_BASE64 embedded as a module constant rather than loaded from disk at runtime, so the mock works in any environment without filesystem access
- correlation_matrix uses all 10 equity tickers with realistic within-sector (0.7-0.9) and cross-sector (0.1-0.35) correlation values, matching real-world portfolio behavior

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `uv run python` from inside the agents/ subdirectory creates a new venv on first run; had to install pytest/pytest-asyncio into that venv separately. Resolved by running `uv pip install pytest pytest-asyncio` before running tests.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All Pydantic contracts are finalized — Plans 02-05 can import without modification
- agents/data/portfolio.py is ready for import by portfolio_agent.py, alternatives_agent.py, and orchestrator
- Mock chart PNG is real and renderable — frontend can test base64 image rendering immediately
- No blockers for Plans 02-05

## Self-Check: PASSED

All 13 claimed files exist. Both task commits (ed75b15, c5149a6) verified in git log.

---
*Phase: 02-agent-pipeline*
*Completed: 2026-03-22*
