---
phase: 3
slug: frontend-and-visualization
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-22
---

# Phase 3 -- Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | vitest |
| **Config file** | frontend/vitest.config.ts |
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
| 03-00-01 | 00 | 0 | REPT-01, REPT-02, REPT-03, GRPH-02 | unit | `npx vitest run --reporter=verbose` | Wave 0 creates | pending |
| 03-01-01 | 01 | 1 | GRPH-01, GRPH-02, GRPH-03, GRPH-04 | unit+tsc | `npx tsc --noEmit --strict && npx vitest run src/__tests__/latestThought.test.ts` | Wave 0 | pending |
| 03-01-02 | 01 | 1 | REPT-01, REPT-03 | unit+tsc | `npx tsc --noEmit --strict && npx vitest run src/__tests__/resolveChartRefs.test.ts src/__tests__/urlTransform.test.ts` | Wave 0 | pending |
| 03-02-01 | 02 | 2 | REPT-02 | unit+tsc | `npx tsc --noEmit --strict && npx vitest run src/__tests__/pagePhase.test.ts` | Wave 0 | pending |
| 03-02-02 | 02 | 2 | - | tsc | `npx tsc --noEmit --strict` (file deletion verification) | N/A | pending |
| 03-02-03 | 02 | 2 | - | manual | Browser: full flow visual verification | N/A | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

Wave 0 plan (03-00-PLAN.md) installs vitest and creates 4 test files:

- [ ] `frontend/vitest.config.ts` -- vitest configuration (jsdom environment, React plugin)
- [ ] `frontend/src/__tests__/resolveChartRefs.test.ts` -- covers REPT-01 chart token replacement
- [ ] `frontend/src/__tests__/urlTransform.test.ts` -- covers REPT-01 data URI passthrough
- [ ] `frontend/src/__tests__/pagePhase.test.ts` -- covers REPT-03 phase derivation logic
- [ ] `frontend/src/__tests__/latestThought.test.ts` -- covers GRPH-02 thought derivation
- [ ] Install: `cd frontend && npm install -D vitest jsdom`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Agent nodes show name and status | GRPH-01 | Visual element presence | During generation, verify 5 agent nodes with status indicators |
| Streaming thought text in nodes | GRPH-02 | Real-time SSE visual | During generation, verify thought text updates live in each node |
| Animated edge pulses | GRPH-03 | CSS animation visual | During generation, verify animated pulses travel along edges |
| Edge hover tooltips | GRPH-04 | Hover interaction | During generation, hover edges to see message title/description |
| Graph collapse transition | CONTEXT | CSS animation visual | After report completes, verify graph smoothly collapses and report fades in |
| Chart images render inline in markdown | REPT-01 | Visual rendering in browser | Generate report, verify base64 PNG charts appear inline at ~500px centered |
| Generate button triggers agent activity | REPT-02 | User interaction flow | Click generate, verify swarm graph appears with working agents |
| Report is unified narrative | REPT-03 | Content structure assessment | Read generated report, verify thematic sections not per-agent |

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending execution
