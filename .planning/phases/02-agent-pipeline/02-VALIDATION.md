---
phase: 2
slug: agent-pipeline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x with pytest-asyncio |
| **Config file** | `agents/pyproject.toml` — `asyncio_mode = "auto"`, `testpaths = ["tests"]` |
| **Quick run command** | `.venv/bin/pytest agents/tests/ -x -q -k "not integration"` |
| **Full suite command** | `.venv/bin/pytest agents/tests/ -x -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `.venv/bin/pytest agents/tests/ -x -q -k "not integration"`
- **After every plan wave:** Run `.venv/bin/pytest agents/tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 0 | PORT-01..05 | unit | `pytest tests/test_portfolio_agent.py -x` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 0 | NEWS-01..05 | unit | `pytest tests/test_news_agent.py -x` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 0 | MODL-01..05 | unit | `pytest tests/test_modeling_agent.py -x` | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 0 | ALT-01..04 | unit | `pytest tests/test_alternatives_agent.py -x` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | PORT-01 | unit | `pytest tests/test_portfolio_agent.py::test_mock_portfolio_has_holdings -x` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 1 | PORT-02 | unit | `pytest tests/test_portfolio_agent.py::test_sector_allocation_sums_to_one -x` | ❌ W0 | ⬜ pending |
| 02-02-03 | 02 | 1 | PORT-03 | unit | `pytest tests/test_portfolio_agent.py::test_herfindahl_valid_range -x` | ❌ W0 | ⬜ pending |
| 02-02-04 | 02 | 1 | PORT-04 | unit | `pytest tests/test_portfolio_agent.py::test_correlation_matrix_symmetric -x` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 1 | NEWS-01 | unit (mock httpx) | `pytest tests/test_news_agent.py::test_parse_finnhub_response -x` | ❌ W0 | ⬜ pending |
| 02-03-02 | 03 | 1 | NEWS-02 | unit | `pytest tests/test_news_agent.py::test_headline_filter -x` | ❌ W0 | ⬜ pending |
| 02-03-03 | 03 | 1 | NEWS-03 | unit | `pytest tests/test_news_agent.py::test_finbert_score_range -x` | ❌ W0 | ⬜ pending |
| 02-03-04 | 03 | 1 | NEWS-04 | unit | `pytest tests/test_news_agent.py::test_aggregate_sentiment -x` | ❌ W0 | ⬜ pending |
| 02-04-01 | 04 | 1 | MODL-01..05 | unit | `pytest tests/test_modeling_agent.py::test_mock_chart_not_empty -x` | ❌ W0 | ⬜ pending |
| 02-05-01 | 05 | 1 | ALT-01 | unit (mock httpx) | `pytest tests/test_alternatives_agent.py::test_btc_eth_always_present -x` | ❌ W0 | ⬜ pending |
| 02-05-02 | 05 | 1 | ALT-02 | unit (mock httpx) | `pytest tests/test_alternatives_agent.py::test_commodity_prices -x` | ❌ W0 | ⬜ pending |
| 02-05-03 | 05 | 1 | ALT-03 | unit | `pytest tests/test_alternatives_agent.py::test_cross_correlations -x` | ❌ W0 | ⬜ pending |
| 02-05-04 | 05 | 1 | ALT-04 | unit | `pytest tests/test_alternatives_agent.py::test_response_fields -x` | ❌ W0 | ⬜ pending |
| 02-06-01 | 06 | 2 | ORCH-01 | integration | `pytest tests/test_orchestrator.py::test_fan_out_dispatches_all_agents -x` | ❌ W0 | ⬜ pending |
| 02-06-02 | 06 | 2 | ORCH-02 | integration | `pytest tests/test_orchestrator.py::test_collects_all_responses -x` | ❌ W0 | ⬜ pending |
| 02-06-03 | 06 | 2 | ORCH-03 | integration | `pytest tests/test_orchestrator.py::test_report_has_sections -x` | ❌ W0 | ⬜ pending |
| 02-06-04 | 06 | 2 | ORCH-04 | unit | `pytest tests/test_orchestrator.py::test_contradiction_detection -x` | ❌ W0 | ⬜ pending |
| 02-06-05 | 06 | 2 | ORCH-05 | integration | `pytest tests/test_orchestrator.py::test_report_has_chart_embed -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `agents/tests/test_portfolio_agent.py` — stubs for PORT-01 through PORT-04
- [ ] `agents/tests/test_news_agent.py` — stubs for NEWS-01 through NEWS-04
- [ ] `agents/tests/test_modeling_agent.py` — stubs for MODL-03 (non-empty base64)
- [ ] `agents/tests/test_alternatives_agent.py` — stubs for ALT-01 through ALT-04
- [ ] `agents/tests/test_orchestrator.py` — stubs for ORCH-01 through ORCH-05

Existing `tests/test_models.py` and `tests/test_mock.py` cover PORT-05, NEWS-05, MODL-05 already.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| curl POST returns full report | ORCH-05 | End-to-end with live agents | `curl -X POST http://localhost:8000/report -H 'Content-Type: application/json' -d '{"user_id":"test"}'` and verify markdown output |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
