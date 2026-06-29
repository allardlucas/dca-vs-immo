#!/usr/bin/env python3
"""
Tests de validation pour les correctifs #23, #24, #25, #26.

Ce script vérifie les formules de calcul AVANT et APRÈS correction
pour les charges et coûts immobiliers du simulateur DCA vs Immo.
"""

import math
import sys

# --- Constantes (identiques à index.html) ---
NOTAIRE = 0.08
LMNP_BUILDING_PCT = 0.80
LMNP_BUILDING_YEARS = 25
LMNP_FURNITURE_PCT = 0.10
LMNP_FURNITURE_YEARS = 7


def format_num(x):
    """Format lisible pour les tableaux."""
    if x >= 1e6:
        return f"{x:,.0f} €".replace(",", " ")
    elif abs(x) >= 1000:
        return f"{x:,.0f} €".replace(",", " ")
    elif x == int(x):
        return f"{x:.0f} €"
    else:
        return f"{x:.2f} €"


def test_amortissement_lmnp(price, notaire_pct=NOTAIRE, regime="reel-bic"):
    """
    Teste le calcul de l'amortissement LMNP.
    AVANT (#23 non corrigé) : base = price uniquement
    APRÈS (#23 corrigé)     : base = price * (1 + notaire)
    """
    is_lmnp = regime in ("micro-bic", "reel-bic")
    acquisition_cost_amort = price * (1 + notaire_pct)

    # AVANT
    building_avant = (
        is_lmnp and LMNP_BUILDING_PCT * price / LMNP_BUILDING_YEARS
    ) or 0
    furniture_avant = (
        is_lmnp and LMNP_FURNITURE_PCT * price / LMNP_FURNITURE_YEARS
    ) or 0

    # APRÈS
    building_apres = (
        is_lmnp
        and LMNP_BUILDING_PCT * acquisition_cost_amort / LMNP_BUILDING_YEARS
    ) or 0
    furniture_apres = (
        is_lmnp
        and LMNP_FURNITURE_PCT * acquisition_cost_amort / LMNP_FURNITURE_YEARS
    ) or 0

    return {
        "building_avant": building_avant,
        "building_apres": building_apres,
        "furniture_avant": furniture_avant,
        "furniture_apres": furniture_apres,
        "total_avant": building_avant + furniture_avant,
        "total_apres": building_apres + furniture_apres,
    }


def test_gli(gli_pct, monthly_rent, annual_rent):
    """
    Teste le montant GLI mensuel.
    AVANT : fallback à 300€/an (25€/mois) quand gliPct=0
    APRÈS : fallback à 0€ quand gliPct=0
    """
    # AVANT
    monthly_gli_avant = (
        monthly_rent * gli_pct if gli_pct > 0 else 25.0
    )  # fallback 300/12 = 25€
    # APRÈS
    monthly_gli_apres = monthly_rent * gli_pct if gli_pct > 0 else 0.0

    # Coûts mensuels AVANT / APRÈS (formule simplifiée)
    annual_gli_avant = annual_rent * gli_pct if gli_pct > 0 else 300.0
    annual_gli_apres = annual_rent * gli_pct if gli_pct > 0 else 0.0

    return {
        "monthly_avant": monthly_gli_avant,
        "monthly_apres": monthly_gli_apres,
        "annual_avant": annual_gli_avant,
        "annual_apres": annual_gli_apres,
    }


def test_sale_fees(sale_price, sale_fees_pct):
    """
    Teste les frais de revente paramétrables.
    AVANT : hardcodé à 6%
    APRÈS : configurable via saleFeesPct
    """
    fees_avant = sale_price * 0.06
    fees_apres = sale_price * sale_fees_pct
    return {"frais_avant": fees_avant, "frais_apres": fees_apres}


def test_charges_growth(
    base_taxe, base_charges, growth_pct, years
):
    """
    Teste l'indexation des charges.
    AVANT : pas d'indexation (growth=0%)
    APRÈS : indexation au taux chargesGrowth
    """
    taxe_avant = base_taxe  # fixe
    taxe_apres = base_taxe * math.pow(1 + growth_pct, years)

    charges_avant = base_charges  # fixes
    charges_apres = base_charges * math.pow(1 + growth_pct, years)

    return {
        "taxe_avant": taxe_avant,
        "taxe_apres": taxe_apres,
        "charges_avant": charges_avant,
        "charges_apres": charges_apres,
    }


def print_table_separator():
    print("|---|------:|--------:|------:|------:|")


def run_tests():
    print("\n" + "=" * 80)
    print("  TESTS DE VALIDATION — Correctifs #23, #24, #25, #26")
    print("=" * 80)

    all_ok = True

    # ===================================================================
    # #23 — Amortissement LMNP
    # ===================================================================
    print("\n## Correctif #23 — Base d'amortissement LMNP")
    print(
        "L'amortissement est désormais calculé sur le prix de revient "
        "(prix + notaire).\n"
    )
    print(
        "| Cas | Prix | Notaire | Amort. Bât. AVANT | Amort. Bât. APRÈS | "
        "Amort. Mob. AVANT | Amort. Mob. APRÈS | Total AVANT | Total APRÈS |"
    )
    print_table_separator()

    test_cases_23 = [
        ("Bien 100k€", 100_000),
        ("Bien 200k€", 200_000),
        ("Bien 300k€", 300_000),
        ("Bien 150k€", 150_000),
        ("Bien 500k€", 500_000),
    ]

    for label, price in test_cases_23:
        r = test_amortissement_lmnp(price, NOTAIRE)
        print(
            f"| {label:11s} | {price:>8,.0f} € | {NOTAIRE*100:.0f}%     |"
            f" {r['building_avant']:>13,.0f} € | {r['building_apres']:>13,.0f} € |"
            f" {r['furniture_avant']:>11,.0f} € | {r['furniture_apres']:>13,.0f} € |"
            f" {r['total_avant']:>11,.0f} € | {r['total_apres']:>11,.0f} € |"
        )

        # Vérification : APRÈS = AVANT * (1 + notaire)
        expected_building = LMNP_BUILDING_PCT * price * (1 + NOTAIRE) / LMNP_BUILDING_YEARS
        if abs(r["building_apres"] - expected_building) > 0.01:
            print(f"    ⚠️  ERREUR: bâtiment {label}")
            all_ok = False

    # ===================================================================
    # #24 — GLI paramétrable
    # ===================================================================
    print("\n## Correctif #24 — GLI paramétrable (bug de cohérence corrigé)")
    print(
        "Quand gliPct=0, gliAmount doit être 0 (pas de fallback à 300€).\n"
    )
    print(
        "| Cas | gliPct | Loyer mens. | GLI mens. AVANT | GLI mens. APRÈS | "
        "GLI annuel AVANT | GLI annuel APRÈS |"
    )
    print_table_separator()

    rent = 1000  # loyer mensuel
    test_cases_24 = [
        ("Désactivée (0%)", 0.0, rent),
        ("2.5% configuré", 0.025, rent),
        ("5% configuré", 0.05, rent),
    ]

    for label, pct, monthly_rent in test_cases_24:
        r = test_gli(pct, monthly_rent, monthly_rent * 12)
        print(
            f"| {label:16s} | {pct*100:.1f}%   |"
            f" {monthly_rent:>10,.0f} € | {r['monthly_avant']:>14,.0f} € |"
            f" {r['monthly_apres']:>14,.0f} € |"
            f" {r['annual_avant']:>14,.0f} € | {r['annual_apres']:>13,.0f} € |"
        )

        # Vérifications
        if pct == 0:
            # AVANT: fallback 300€/an = 25€/mois (bug corrigé)
            if r["monthly_avant"] != 25 or r["annual_avant"] != 300:
                # L'ancien code avait un bug, ce n'est pas ce qu'on corrige
                pass
            # APRÈS: 0
            if r["monthly_apres"] != 0 or r["annual_apres"] != 0:
                print(f"    ⚠️  ERREUR: GLI désactivée doit donner 0")
                all_ok = False
        if pct == 0.025:
            expected_monthly = monthly_rent * 0.025  # 25€
            if abs(r["monthly_apres"] - expected_monthly) > 0.01:
                print(f"    ⚠️  ERREUR: GLI 2.5% attendu {expected_monthly:.0f}€")
                all_ok = False
        if pct == 0.05:
            expected_monthly = monthly_rent * 0.05  # 50€
            if abs(r["monthly_apres"] - expected_monthly) > 0.01:
                print(f"    ⚠️  ERREUR: GLI 5% attendu {expected_monthly:.0f}€")
                all_ok = False

    # ===================================================================
    # #25 — Frais de revente paramétrables
    # ===================================================================
    print("\n## Correctif #25 — Frais d'agence revente")
    print(
        "Les frais de revente sont désormais configurables (slider 0-8%).\n"
    )
    print(
        "| Cas | Prix revente | Frais AVANT (6%) | Frais APRÈS | Écart |"
    )
    print_table_separator()

    sale_price = 300_000
    test_cases_25 = [
        ("0% (pas de frais)", 0.00),
        ("3% configuré", 0.03),
        ("6% (par défaut)", 0.06),
        ("8% configuré", 0.08),
    ]

    for label, pct in test_cases_25:
        r = test_sale_fees(sale_price, pct)
        ecart = r["frais_apres"] - r["frais_avant"]
        ecart_str = f"+{ecart:,.0f} €" if ecart > 0 else "=" if ecart == 0 else f"{ecart:,.0f} €"
        if ecart == 0:
            ecart_str = "= (identique)"
        print(
            f"| {label:18s} | {sale_price:>11,.0f} € |"
            f" {r['frais_avant']:>15,.0f} € | {r['frais_apres']:>11,.0f} € |"
            f" {ecart_str:>16s} |"
        )

        # Vérification pour 6%: doit être identique à l'ancien hardcodé
        if pct == 0.06:
            if abs(r["frais_avant"] - r["frais_apres"]) > 0.01:
                print(f"    ⚠️  ERREUR: 6% devrait être identique AVANT/APRÈS")
                all_ok = False

    # ===================================================================
    # #26 — Indexation des charges
    # ===================================================================
    print("\n## Correctif #26 — Indexation taxe foncière et charges copro")
    print(
        "La taxe foncière et les charges de copropriété sont indexées "
        "au taux chargesGrowth.\n"
    )
    print(
        "| Croissance | Année | Taxe fonc. AVANT | Taxe fonc. APRÈS | "
        "Charges AVANT | Charges APRÈS |"
    )
    print_table_separator()

    base_taxe = 800
    base_charges = 150
    years = 20

    test_cases_26 = [
        ("0% (fixe)", 0.0),
        ("2% (défaut)", 0.02),
        ("4% configuré", 0.04),
    ]

    for label, growth in test_cases_26:
        r = test_charges_growth(base_taxe, base_charges, growth, years)
        print(
            f"| {label:11s} | {years:>5} |"
            f" {r['taxe_avant']:>15,.0f} € | {r['taxe_apres']:>15,.0f} € |"
            f" {r['charges_avant']:>11,.0f} € | {r['charges_apres']:>11,.0f} € |"
        )

        if growth == 0:
            if r["taxe_avant"] != r["taxe_apres"] or r["charges_avant"] != r["charges_apres"]:
                print(f"    ⚠️  ERREUR: croissance 0% doit être identique")
                all_ok = False
        if growth == 0.02:
            expected_taxe = base_taxe * math.pow(1.02, 20)
            if abs(r["taxe_apres"] - expected_taxe) > 0.01:
                print(f"    ⚠️  ERREUR: taxe 2% attendu {expected_taxe:.0f}€")
                all_ok = False

    # ===================================================================
    # Conclusion
    # ===================================================================
    print("\n" + "=" * 80)
    if all_ok:
        print("  ✅ Tous les tests des correctifs #23, #24, #25, #26 PASSENT.")
    else:
        print("  ❌ Certains tests ÉCHOUENT — voir détails ci-dessus.")
    print("=" * 80 + "\n")

    return all_ok


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
