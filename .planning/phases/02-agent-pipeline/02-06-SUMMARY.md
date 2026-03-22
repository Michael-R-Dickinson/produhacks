---
phase: 02-agent-pipeline
plan: "06"
subsystem: alternatives-agent
tags: [bug-fix, configuration, crypto, asyncio]
dependency_graph:
  requires: []
  provides: [alternatives-agent-non-mock-correctness, env-var-documentation]
  affects: [alternatives_agent.py]
tech_stack:
  added: []
  patterns: [direct-await-over-asyncio.gather-for-single-coroutine]
key_files:
  created:
    - agents/.env.example
  modified:
    - agents/alternatives_agent.py
decisions:
  - "Direct await is cleaner than asyncio.gather for a single coroutine — asyncio.gather returns a list, not the coroutine's return value directly"
metrics:
  duration: "~5 min"
  completed: "2026-03-22"
  tasks_completed: 2
  files_changed: 2
---

# Phase 02 Plan 06: Gap Closure — Asyncio Bug Fix and .env.example Summary

**One-liner:** Fixed asyncio.gather mis-use that broke crypto price unpacking and documented all three required env vars in agents/.env.example.

## What Was Built

Two verification gaps from Phase 02 were closed:

1. **Bug fix in `alternatives_agent.py`:** The `asyncio.gather` call with a single coroutine incorrectly returned a one-element list, causing the `prices, changes = crypto_prices` unpack to fail at runtime in non-mock mode. Replaced with a direct `prices, change_7d = await fetch_crypto_prices(CRYPTO_TICKERS)` call. Updated two downstream references from `changes` to `change_7d` for consistency.

2. **New `agents/.env.example`:** Created developer-facing documentation of the three required environment variables: `MOCK_DATA`, `FINNHUB_API_KEY`, and `GEMINI_API_KEY`. Includes links to where each key is obtained and which agents use each one.

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Fix asyncio.gather unpack bug | aecbbe3 | agents/alternatives_agent.py |
| 2 | Create agents/.env.example | 1db1550 | agents/.env.example |

## Verification

- `python -m pytest agents/tests/test_alternatives.py -x -q` — 13 passed
- `grep -c "asyncio.gather(fetch_crypto_prices" agents/alternatives_agent.py` — returns 0
- `grep "prices, change_7d = await fetch_crypto_prices" agents/alternatives_agent.py` — match found
- `cat agents/.env.example` — shows MOCK_DATA, FINNHUB_API_KEY, GEMINI_API_KEY

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- agents/alternatives_agent.py — FOUND (modified)
- agents/.env.example — FOUND (created)
- Commit aecbbe3 — FOUND
- Commit 1db1550 — FOUND
