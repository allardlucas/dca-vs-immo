# Monte Carlo DCA — Design Spec

> Issue: [#7 — Monte Carlo sur la croissance DCA](https://github.com/allardlucas/dca-vs-immo/issues/7)
> Date: 2026-06-30
> Status: Approved

## Goal

Replace the purely deterministic DCA growth model with a stochastic Monte Carlo simulation (GBM) so users can assess the probability that DCA beats real estate, while keeping the deterministic path as a reference.

## Decisions (validated with product owner)

| Topic | Decision |
|-------|----------|
| Activation | Monte Carlo always on; advanced params in a collapsible section |
| Section default | Collapsed, badge in title: `σ = 15 % · 1 000 sim.` |
| Charts | `chart-brut` and `chart-net` only |
| Win probability | New dedicated result card; deterministic winner card unchanged |
| Engine | Single immo simulation + DCA Monte Carlo overlay (Approach 1) |
| Bull/bear scenarios | Out of scope v1 |
| Immo stochasticity | Immo stays fully deterministic |

## Return model (GBM discrete monthly)

The slider « Croissance annuelle X » is a **compound annual growth rate (CAGR)** target. Dividing by 12 is incorrect for compounded returns.

### Stochastic path (Monte Carlo)

Monthly multiplicative factor:

```
S_{t+1} = S_t × exp(μ_m − σ_m²/2 + σ_m × Z) + effort_t
```

where `Z ~ N(0, 1)` and:

| Parameter | Formula | Notes |
|-----------|---------|-------|
| `μ_m` | `ln(1 + X) / 12` | X = annual growth from slider (decimal) |
| `σ_m` | `σ / √12` | σ = annualized log-return volatility from slider |
| `−σ_m²/2` | convexity adjustment | Ensures E[S_{t+1}/S_t] = exp(μ_m) |

Gaussian draws via Box-Muller transform.

### Deterministic path (reference dashed line)

Aligned with the CAGR slider:

```
monthlyFactor = exp(ln(1 + X) / 12)
S_{t+1} = S_t × monthlyFactor + effort_t
```

This **replaces** the current `growth / 12` arithmetic approximation in `runSimulation()`.

At σ = 0, all MC paths must equal the deterministic path exactly.

### DCA tax

Per simulation path, at each year end:

```
gain = value − totalInvested
netValue = value − max(0, gain × dcaTaxRate)
```

## Architecture

```
runSimulation(p)              → immo + deterministic DCA + monthlyEfforts[]
runMonteCarloDCA(opts)        → { winProb, yearlyBrut, yearlyNet }
gaussianRandom()              → Box-Muller pair generator
drawLineChart()               → extended with confidenceBand series type
```

### Data flow

1. `simuler()` calls `runSimulation()` once → `monthlyEfforts`, `dcaYears`, `immoFinal`
2. `runMonteCarloDCA()` uses `monthlyEfforts` (deterministic, from immo cash-flow) and stochastic returns
3. Percentiles P5 / P50 / P95 computed per year across N simulations
4. `winProb` = fraction of paths where `dcaNet_final > immoFinal`

### Performance

Target: N = 1 000 × 25 years × 12 months ≈ 300 k iterations < 100 ms in browser.
Debounce 150 ms on volatility and N sliders only.

## UI

### Collapsible section (column DCA, below « Croissance annuelle »)

```html
<details id="mc-advanced" class="mc-advanced">
  <summary>
    Simulation avancée
    <span id="mc-badge" class="mc-badge">σ = 15 % · 1 000 sim.</span>
  </summary>
  <!-- Volatilité σ: slider 5–30 %, default 15 %, step 0.5 -->
  <!-- Simulations N: slider 100–10 000, default 1 000, step 100 -->
</details>
```

### New result card

```
🎲 Probabilité DCA
   68 %
   DCA > Immo dans 68 % des scénarios
```

Placed in `results-grid` after the winner card. Neutral/violet styling.

### Charts (`chart-brut`, `chart-net`)

| Layer | Style |
|-------|-------|
| P5–P95 band | Semi-transparent fill `#00cec9` at 15 % opacity |
| Median P50 | Solid line `#00cec9`, width 2.5 |
| Deterministic | Dashed `[4, 4]`, same color, 60 % opacity |
| Immo | Unchanged (solid orange) |

Updated legends:

- `DCA médiane (MC)` · `DCA déterministe` · `Zone P5–P95` · `Immo`

Tooltips show P5 / median / P95 at hovered year when MC data is present.

## Testing

New file: `tests/test_issue_7_monte_carlo.py`

Python reimplementation (same pattern as fiscal tests):

- σ = 0 → all paths equal deterministic (exact)
- `winProb ∈ [0, 1]`
- P5 ≤ P50 ≤ P95 at every year
- With fixed seed, mean of finals ≈ deterministic (loose tolerance)

## Out of scope (v1)

- Bull/bear market scenario presets
- Reproducible seed exposed in UI
- Stochastic immo price growth
- MC bands on `chart-nopv` or `chart-effort`
- JS module extraction / build step

## Files to modify

| File | Changes |
|------|---------|
| `index.html` | GBM engine, UI, charts, deterministic fix, result card |
| `tests/test_issue_7_monte_carlo.py` | New regression tests |
| `docs/development.md` | Add test file to coverage table (optional, during impl) |
