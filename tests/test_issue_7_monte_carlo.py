"""
Regression tests for issue #7 — Monte Carlo DCA (GBM).

Python mirror of the JS engine to be added in index.html (Task 2).
"""

import math
import random

import pytest

EFFORTS_24M = [500.0] * 24


def monthly_growth_factor(annual_growth: float) -> float:
    return math.exp(math.log(1 + annual_growth) / 12)


def percentile_sorted(sorted_values: list[float], p: float) -> float:
    n = len(sorted_values)
    if n == 0:
        return 0.0
    if n == 1:
        return sorted_values[0]
    rank = (p / 100) * (n - 1)
    lo = int(math.floor(rank))
    hi = int(math.ceil(rank))
    if lo == hi:
        return sorted_values[lo]
    frac = rank - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def apply_dca_tax(value: float, total_invested: float, dca_tax_rate: float) -> float:
    gain = value - total_invested
    tax = max(0.0, gain * dca_tax_rate)
    return value - tax


def run_deterministic_dca(
    dca_initial: float,
    annual_growth: float,
    monthly_efforts: list[float],
    dca_tax_rate: float,
) -> dict:
    factor = monthly_growth_factor(annual_growth)
    value = dca_initial
    total_invested = dca_initial
    num_years = len(monthly_efforts) // 12

    yearly_brut = [{"year": 0, "value": value}]
    yearly_net = [
        {"year": 0, "netValue": apply_dca_tax(value, total_invested, dca_tax_rate)}
    ]

    for year in range(1, num_years + 1):
        for m in range(12):
            idx = (year - 1) * 12 + m
            effort = monthly_efforts[idx]
            value = value * factor + effort
            total_invested += effort
        yearly_brut.append({"year": year, "value": value})
        yearly_net.append(
            {"year": year, "netValue": apply_dca_tax(value, total_invested, dca_tax_rate)}
        )

    return {
        "yearly_brut": yearly_brut,
        "yearly_net": yearly_net,
        "final_net": apply_dca_tax(value, total_invested, dca_tax_rate),
    }


def run_monte_carlo_dca(
    dca_initial: float,
    annual_growth: float,
    volatility: float,
    num_simulations: int,
    monthly_efforts: list[float],
    dca_tax_rate: float,
    immo_final: float,
    seed: int | None = None,
) -> dict:
    rng = random.Random(seed)
    mu_m = math.log(1 + annual_growth) / 12
    sigma_m = volatility / math.sqrt(12)
    num_years = len(monthly_efforts) // 12
    num_months = len(monthly_efforts)

    brut_by_year = [[] for _ in range(num_years + 1)]
    net_by_year = [[] for _ in range(num_years + 1)]
    finals_net: list[float] = []
    wins = 0

    for _ in range(num_simulations):
        value = dca_initial
        total_invested = dca_initial

        brut_by_year[0].append(value)
        net_by_year[0].append(apply_dca_tax(value, total_invested, dca_tax_rate))

        for month_idx in range(num_months):
            z = rng.gauss(0, 1)
            factor = math.exp(mu_m - sigma_m**2 / 2 + sigma_m * z)
            effort = monthly_efforts[month_idx]
            value = value * factor + effort
            total_invested += effort

            if (month_idx + 1) % 12 == 0:
                year = (month_idx + 1) // 12
                brut_by_year[year].append(value)
                net_val = apply_dca_tax(value, total_invested, dca_tax_rate)
                net_by_year[year].append(net_val)

        final_net = net_by_year[num_years][-1]
        finals_net.append(final_net)
        if final_net > immo_final:
            wins += 1

    win_prob = wins / num_simulations if num_simulations > 0 else 0.0

    yearly_brut = []
    yearly_net = []
    for year in range(num_years + 1):
        brut_sorted = sorted(brut_by_year[year])
        net_sorted = sorted(net_by_year[year])
        yearly_brut.append(
            {
                "year": year,
                "p5": percentile_sorted(brut_sorted, 5),
                "p50": percentile_sorted(brut_sorted, 50),
                "p95": percentile_sorted(brut_sorted, 95),
            }
        )
        yearly_net.append(
            {
                "year": year,
                "p5": percentile_sorted(net_sorted, 5),
                "p50": percentile_sorted(net_sorted, 50),
                "p95": percentile_sorted(net_sorted, 95),
            }
        )

    return {
        "win_prob": win_prob,
        "yearly_brut": yearly_brut,
        "yearly_net": yearly_net,
        "finals_net": finals_net,
    }


def test_zero_volatility_matches_deterministic():
    """σ=0: all MC paths equal the deterministic CAGR path exactly."""
    dca_initial = 10_000.0
    annual_growth = 0.08
    dca_tax_rate = 0.30
    immo_final = 50_000.0
    num_simulations = 50

    det = run_deterministic_dca(dca_initial, annual_growth, EFFORTS_24M, dca_tax_rate)
    mc = run_monte_carlo_dca(
        dca_initial,
        annual_growth,
        volatility=0.0,
        num_simulations=num_simulations,
        monthly_efforts=EFFORTS_24M,
        dca_tax_rate=dca_tax_rate,
        immo_final=immo_final,
        seed=42,
    )

    for det_brut, mc_brut in zip(det["yearly_brut"], mc["yearly_brut"]):
        assert mc_brut["p5"] == mc_brut["p50"] == mc_brut["p95"]
        assert mc_brut["p50"] == pytest.approx(det_brut["value"])

    for det_net, mc_net in zip(det["yearly_net"], mc["yearly_net"]):
        assert mc_net["p5"] == mc_net["p50"] == mc_net["p95"]
        assert mc_net["p50"] == pytest.approx(det_net["netValue"])

    assert len(set(mc["finals_net"])) == 1
    assert mc["finals_net"][0] == pytest.approx(det["final_net"])


def test_percentile_ordering():
    """P5 ≤ P50 ≤ P95 at every year with σ > 0."""
    mc = run_monte_carlo_dca(
        dca_initial=10_000.0,
        annual_growth=0.08,
        volatility=0.15,
        num_simulations=500,
        monthly_efforts=EFFORTS_24M,
        dca_tax_rate=0.30,
        immo_final=50_000.0,
        seed=123,
    )

    for entry in mc["yearly_brut"]:
        assert entry["p5"] <= entry["p50"] <= entry["p95"]

    for entry in mc["yearly_net"]:
        assert entry["p5"] <= entry["p50"] <= entry["p95"]


def test_win_prob_bounds():
    """Win probability stays in [0, 1]."""
    mc = run_monte_carlo_dca(
        dca_initial=10_000.0,
        annual_growth=0.08,
        volatility=0.15,
        num_simulations=200,
        monthly_efforts=EFFORTS_24M,
        dca_tax_rate=0.30,
        immo_final=50_000.0,
        seed=7,
    )
    assert 0.0 <= mc["win_prob"] <= 1.0


def test_monthly_factor_not_linear():
    """Monthly factor uses compound CAGR, not arithmetic growth/12."""
    annual_growth = 0.08
    linear_approx = 1 + annual_growth / 12
    compound_factor = monthly_growth_factor(annual_growth)
    expected = (1 + annual_growth) ** (1 / 12)

    assert compound_factor != pytest.approx(linear_approx)
    assert compound_factor == pytest.approx(expected)
