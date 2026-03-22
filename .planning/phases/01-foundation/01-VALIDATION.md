---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (not yet installed — Wave 0 installs) |
| **Config file** | `agents/pyproject.toml` — Wave 0 creates |
| **Quick run command** | `pytest agents/tests/ -x -q --tb=short` |
| **Full suite command** | `pytest agents/tests/ -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest agents/tests/ -x -q --tb=short`
- **After every plan wave:** Run `pytest agents/tests/ -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 0 | INFRA-01 | integration | `pytest agents/tests/test_bureau.py::test_all_agents_registered -x` | Wave 0 | pending |
| 01-01-02 | 01 | 0 | INFRA-01 | integration | `pytest agents/tests/test_bureau.py::test_stub_roundtrip -x` | Wave 0 | pending |
| 01-02-01 | 02 | 0 | INFRA-02 | smoke | `pytest agents/tests/test_bridge.py::test_sse_connects -x` | Wave 0 | pending |
| 01-02-02 | 02 | 0 | INFRA-02 | integration | `pytest agents/tests/test_bridge.py::test_event_delivered -x` | Wave 0 | pending |
| 01-02-03 | 02 | 0 | INFRA-02 | smoke | `pytest agents/tests/test_bridge.py::test_pna_header -x` | Wave 0 | pending |
| 01-03-01 | 03 | 0 | INFRA-03 | unit | `pytest agents/tests/test_models.py::test_imports -x` | Wave 0 | pending |
| 01-03-02 | 03 | 0 | INFRA-03 | unit | `pytest agents/tests/test_models.py::test_roundtrip -x` | Wave 0 | pending |
| 01-04-01 | 04 | 0 | INFRA-04 | unit | `pytest agents/tests/test_mock.py::test_mock_toggle -x` | Wave 0 | pending |
| 01-04-02 | 04 | 0 | INFRA-04 | integration | `pytest agents/tests/test_mock.py::test_all_agents_mock -x` | Wave 0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `agents/pyproject.toml` — pytest config with `[tool.pytest.ini_options]`
- [ ] `agents/tests/__init__.py` — empty init
- [ ] `agents/tests/test_models.py` — stubs for INFRA-03
- [ ] `agents/tests/test_bridge.py` — stubs for INFRA-02
- [ ] `agents/tests/test_bureau.py` — stubs for INFRA-01
- [ ] `agents/tests/test_mock.py` — stubs for INFRA-04
- [ ] Framework install: `uv pip install pytest pytest-asyncio`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SSE works in Chrome without PNA errors | INFRA-02 | Requires actual browser + Chrome PNA enforcement | Open Chrome DevTools, connect EventSource to SSE endpoint, verify no net::ERR_FAILED |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
