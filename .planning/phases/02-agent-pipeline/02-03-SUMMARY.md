---
phase: 02-agent-pipeline
plan: 03
subsystem: api
tags: [python, uagents, finbert, transformers, httpx, finnhub, sentiment, news, tdd]

requires:
  - phase: 02-agent-pipeline
    provides: agents package structure, NewsResponse/FetchNews Pydantic models, mock news response

provides:
  - Live Finnhub headline fetching (general market + per-ticker company news, deduplicated)
  - filter_headlines_for_tickers: ticker match in headline text or related field, 5-per-ticker cap
  - score_sentiment: lazy-loaded FinBERT pipeline, positive - negative in [-1, 1]
  - score_headlines: scores each headline, discards near-neutral (abs < 0.1)
  - aggregate_sentiment_by_ticker: mean sentiment per ticker
  - compute_overall_sentiment: mean across all tickers
  - handle_fetch_news: live branch with 4 punchy thought events, FINNHUB_API_KEY from env
  - 16 unit tests for pure logic functions (no FinBERT load, no network calls)

affects:
  - 02-05 (orchestrator receives NewsResponse with live aggregate_sentiment and overall_sentiment)
  - 03-bridge (frontend SSE stream receives thought events from news agent)

tech-stack:
  added: []
  patterns:
    - Lazy FinBERT loading pattern (module-level _finbert = None, get_finbert() loads once on first call)
    - TDD with monkeypatching for FinBERT isolation (tests stub score_sentiment via monkeypatch.setattr)

key-files:
  created:
    - agents/tests/test_news.py
  modified:
    - agents/news_agent.py

key-decisions:
  - "FinBERT loaded lazily via get_finbert() so test imports never trigger 500MB model download"
  - "filter_headlines_for_tickers caps at 5 headlines per ticker to prevent any one holding dominating the sentiment signal"
  - "near-neutral threshold of abs < 0.1 matches plan spec — filters headlines with no meaningful sentiment signal"

patterns-established:
  - "Lazy ML model loading: _finbert = None at module level, load inside get_finbert() on first real call"
  - "TDD isolation for ML: monkeypatch.setattr swaps score_sentiment so aggregation tests run without GPU/network"

requirements-completed:
  - NEWS-01
  - NEWS-02
  - NEWS-03
  - NEWS-04
  - NEWS-05

duration: 8min
completed: 2026-03-22
---

# Phase 02 Plan 03: News Agent Live Logic Summary

**Finnhub headline fetching with FinBERT sentiment scoring via lazy-loaded ProsusAI/finbert pipeline, per-ticker aggregation, and 16 unit tests using monkeypatching for ML isolation**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-22T07:19:39Z
- **Completed:** 2026-03-22T07:27:39Z
- **Tasks:** 1 (TDD: test commit + implementation commit)
- **Files modified:** 2

## Accomplishments

- Created 16 unit tests for all pure logic functions — no FinBERT loads, no Finnhub calls, monkeypatch used for sentiment scoring isolation
- Implemented full Finnhub pipeline: general market news + per-ticker company news (7-day window), deduplicated by headline text
- FinBERT lazy-loaded once on first real call — imports stay fast for testing
- Live `handle_fetch_news` branch reads `FINNHUB_API_KEY`, emits 4 punchy thought events with real values (headline counts, top ticker scores, overall sentiment label)

## Task Commits

Each task was committed atomically:

1. **RED: Failing tests for news filtering and sentiment aggregation** - `6bcd915` (test)
2. **GREEN: Implement news fetching, FinBERT scoring, and sentiment aggregation** - `83b50ae` (feat)

**Plan metadata:** _(docs commit follows)_

## Files Created/Modified

- `agents/tests/test_news.py` - 16 unit tests: filter_headlines_for_tickers (7 tests), aggregate_sentiment_by_ticker (4 tests), compute_overall_sentiment (3 tests), score_headlines near-neutral filter (1 test via monkeypatch), mock mode (1 test)
- `agents/news_agent.py` - Added get_finbert(), fetch_finnhub_headlines(), filter_headlines_for_tickers(), score_sentiment(), score_headlines(), aggregate_sentiment_by_ticker(), compute_overall_sentiment(); live branch in handle_fetch_news

## Decisions Made

- FinBERT loaded lazily via `get_finbert()` so test imports never trigger the 500MB model download — critical for fast test runs
- `filter_headlines_for_tickers` caps at 5 per ticker to prevent any single holding dominating the aggregate sentiment signal
- near-neutral threshold of `abs(sentiment) < 0.1` matches plan spec — removes headlines with no actionable sentiment direction

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

Live mode requires `FINNHUB_API_KEY` environment variable. Mock mode (`MOCK_DATA=true`, the default) works without it. No dashboard configuration needed.

## Next Phase Readiness

- `agents/news_agent.py` fully implemented with live Finnhub + FinBERT pipeline
- All 16 tests pass; pure logic functions importable without FinBERT or network
- Ready for orchestrator (02-05) to invoke with real tickers and receive structured `NewsResponse`
- No blockers for remaining Phase 2 plans

## Self-Check: PASSED

Both task commits (6bcd915, 83b50ae) verified in git log. Both files exist: agents/news_agent.py, agents/tests/test_news.py. All 16 tests pass.

---
*Phase: 02-agent-pipeline*
*Completed: 2026-03-22*
