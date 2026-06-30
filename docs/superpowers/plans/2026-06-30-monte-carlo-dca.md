# Monte Carlo DCA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan step-by-step. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add GBM Monte Carlo simulation for DCA growth with P5–P95 bands on brut/net charts and a win-probability result card (issue #7).

**Architecture:** Run immo simulation once via `runSimulation()`, overlay stochastic DCA paths with `runMonteCarloDCA()` using precomputed `monthlyEfforts`. Extend `drawLineChart()` for confidence bands. Fix deterministic DCA to use `exp(ln(1+g)/12)` monthly factor.

**Tech Stack:** Vanilla JS in `index.html`, Python pytest for regression tests.

**Spec:** `docs/superpowers/specs/2026-06-30-monte-carlo-dca-design.md`

---

## File map

| File | Responsibility |
|------|----------------|
| `tests/test_issue_7_monte_carlo.py` | Python mirror of MC engine + assertions |
| `index.html` (JS ~L634) | `gaussianRandom`, `runMonteCarloDCA`, deterministic fix |
| `index.html` (HTML ~L359) | Collapsible advanced section + sliders |
| `index.html` (HTML ~L526) | Win-probability result card |
| `index.html` (CSS ~L100) | `.mc-advanced`, `.result-card.mc-prob` styles |
| `index.html` (JS ~L1403) | `drawLineChart` confidence band rendering |
| `index.html` (JS ~L1085) | `simuler()` wires MC + chart updates |
| `index.html` (JS ~L1773) | Slider bindings + debounce for MC sliders |

---

### Task 1: Monte Carlo engine (Python tests first)

**Files:**
- Create: `tests/test_issue_7_monte_carlo.py`

- [ ] **Step 1: Write the test file** (see spec for full `run_monte_carlo_dca` implementation)

- [ ] **Step 2: Run tests**

Run: `cd /Users/loukas/dca-vs-immo && pytest tests/test_issue_7_monte_carlo.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_issue_7_monte_carlo.py
git commit -m "test: add Monte Carlo DCA regression tests for #7"
```

---

### Task 2: JS engine + deterministic fix

**Files:**
- Modify: `index.html` (~L691, after `annualizedReturn`)

- [ ] **Step 1: Add `monthlyGrowthFactor`, `gaussianRandom`, `percentileSorted`, `runMonteCarloDCA`**

- [ ] **Step 2: Replace `dcaValue * (1 + growth / 12)` with `dcaValue * monthlyGrowthFactor(growth)` in `runSimulation`**

- [ ] **Step 3: Smoke test in browser — no console errors**

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add Monte Carlo DCA engine and fix CAGR monthly factor (#7)"
```

---

### Task 3: UI — advanced section + probability card

**Files:**
- Modify: `index.html` (HTML + CSS)

- [ ] **Step 1: Add `.mc-advanced` CSS and `.result-card.mc-prob`**

- [ ] **Step 2: Add `<details id="mc-advanced">` with σ and N sliders below growth slider**

- [ ] **Step 3: Add probability result card after winner card**

- [ ] **Step 4: Wire sliders + 150 ms debounce on MC sliders + `updateMcBadge()`**

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: add Monte Carlo UI controls and probability card (#7)"
```

---

### Task 4: Wire `simuler()` + update result card

- [ ] **Step 1: Call `runMonteCarloDCA` after `runSimulation`, display `winProb` in `#res-mc-prob`**

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat: compute and display DCA win probability (#7)"
```

---

### Task 5: Extend `drawLineChart` for confidence bands

- [ ] **Step 1: Scan `p5`/`p95` in min/max when `confidenceBand: true`**

- [ ] **Step 2: Draw filled band before lines**

- [ ] **Step 3: Support `dashed` and `opacity` on line series**

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add confidence band and dashed line support to charts (#7)"
```

---

### Task 6: Update chart rendering in `simuler()`

- [ ] **Step 1: `chart-brut` — band + median + deterministic dashed + immo**

- [ ] **Step 2: `chart-net` — same with net values**

- [ ] **Step 3: Update chart legends**

- [ ] **Step 4: Visual verification in browser**

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: render Monte Carlo bands on brut and net charts (#7)"
```

---

### Task 7: Final verification

- [ ] **Step 1: `pytest tests/ -v` — all PASS**

- [ ] **Step 2: Browser smoke test (σ=0 overlap, σ=30 wide band, N=10000 responsive)**

- [ ] **Step 3: Update `docs/development.md` test table**

- [ ] **Step 4: Final commit**

```bash
git add docs/development.md
git commit -m "docs: document Monte Carlo test coverage (#7)"
```
