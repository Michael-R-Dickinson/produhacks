---
phase: 3
slug: frontend-and-visualization
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | vitest |
| **Config file** | frontend/vite.config.ts |
| **Quick run command** | `cd frontend && npx vitest run --reporter=verbose` |
| **Full suite command** | `cd frontend && npx vitest run --reporter=verbose` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && npx vitest run --reporter=verbose`
- **After every plan wave:** Run `cd frontend && npx vitest run --reporter=verbose`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | REPT-01 | manual | Browser: markdown renders with charts | N/A | pending |
| 03-01-02 | 01 | 1 | REPT-02 | manual | Browser: generate button triggers report | N/A | pending |
| 03-01-03 | 01 | 1 | REPT-03 | manual | Browser: unified narrative, not per-agent | N/A | pending |
| 03-02-01 | 02 | 1 | GRPH-01 | manual | Browser: agent nodes visible with status | N/A | pending |
| 03-02-02 | 02 | 1 | GRPH-02 | manual | Browser: thought text updates in nodes | N/A | pending |
| 03-02-03 | 02 | 1 | GRPH-03 | manual | Browser: animated pulses on edges | N/A | pending |
| 03-02-04 | 02 | 1 | GRPH-04 | manual | Browser: edge hover shows message info | N/A | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. Frontend visualization is primarily manual-verification (browser-based UI behavior).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Chart images render inline in markdown | REPT-01 | Visual rendering in browser | Generate report, verify base64 PNG charts appear inline at ~500px centered |
| Generate button triggers agent activity | REPT-02 | User interaction flow | Click generate, verify swarm graph appears with working agents |
| Report is unified narrative | REPT-03 | Content structure assessment | Read generated report, verify thematic sections not per-agent |
| Agent nodes show name and status | GRPH-01 | Visual element presence | During generation, verify 5 agent nodes with status indicators |
| Streaming thought text in nodes | GRPH-02 | Real-time SSE visual | During generation, verify thought text updates live in each node |
| Animated edge pulses | GRPH-03 | CSS animation visual | During generation, verify animated pulses travel along edges |
| Edge hover tooltips | GRPH-04 | Hover interaction | During generation, hover edges to see message title/description |
| Graph collapse transition | CONTEXT | CSS animation visual | After report completes, verify graph smoothly collapses and report fades in |
| CSV upload and report reflects holdings | SC-4 | End-to-end flow | Upload CSV, generate report, verify holdings appear in report |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
