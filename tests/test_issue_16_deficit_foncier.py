#!/usr/bin/env python3
"""
Test script for Issue #16: Séparation du déficit foncier en deux masses
(imputation RGlob plafond 10 700 € pour les travaux vs report RF pour les intérêts)

Compares OLD vs NEW tax logic for 7 edge cases.
"""

TMI = 0.30
PS_FONCIER = 0.172
PLAFOND = 10700


def old_logic(loyers, charges, interets):
    """Ancien code : tout le déficit imputable au RGlob (plafond 10 700€)."""
    resultat = loyers - charges - interets
    if resultat < 0:
        deficit = -resultat
        deductible = min(deficit, PLAFOND)
        gain_fiscal = deductible * TMI
        report = deficit - deductible
    else:
        deductible = 0
        gain_fiscal = 0
        report = 0
    return gain_fiscal, report


def new_logic(loyers, charges, interets):
    """Nouveau code LF 2019 : séparation travaux / intérêts."""
    resultat_total = loyers - charges - interets
    if resultat_total < 0:
        # Masse A : résultat avant intérêts (déficit travaux)
        resultat_travaux = loyers - charges
        deficit_travaux = 0
        deficit_interets = 0
        if resultat_travaux < 0:
            deficit_travaux = -resultat_travaux
            deficit_interets = interets
        else:
            deficit_interets = -resultat_total

        deductible = min(deficit_travaux, PLAFOND)
        gain_fiscal = deductible * TMI
        report = (deficit_travaux - deductible) + deficit_interets
    else:
        deductible = 0
        gain_fiscal = 0
        report = 0
    return gain_fiscal, report


cases = [
    (1,  12000,  8000, 10000, "Loyers 12k, charges 8k, intérêts 10k (déficit 6k, tous intérêts)"),
    (2,  12000, 15000,  8000, "Loyers 12k, charges 15k, intérêts 8k (déficit 11k, mixte)"),
    (3,  12000, 20000,  5000, "Loyers 12k, charges 20k, intérêts 5k (déficit 13k, gros travaux)"),
    (4,  12000,  3000, 20000, "Loyers 12k, charges 3k, intérêts 20k (déficit 11k, gros intérêts)"),
    (5,  18000,  5000,  5000, "Loyers 18k, charges 5k, intérêts 5k (bénéfice 8k, pas de déficit)"),
    (6,  10000, 12000,     0, "Loyers 10k, charges 12k, intérêts 0 (déficit 2k, pas d'intérêts)"),
    (7,      0,  5000, 12000, "Loyers 0k (vacance), charges 5k, intérêts 12k (déficit 17k)"),
]

print("=" * 110)
print("TABLEAU COMPARATIF AVANT / APRÈS — Issue #16: Déficit foncier (LF 2019)")
print("=" * 110)
print()
print(f"Hypothèses : TMI = {TMI*100:.0f}% | PS Fonciers = {PS_FONCIER*100:.1f}% | Plafond RGlob = {PLAFOND:,}€".replace(",", " "))
print()
print(f"{'Cas':>4s} | {'Description':<55s} | {'Gain AVANT':>11s} | {'Report AVANT':>12s} | {'Gain APRÈS':>11s} | {'Report APRÈS':>12s} | {'Δ Gain':>10s}")
print("-" * 110)

for num, loyers, charges, interets, desc in cases:
    gain_old, report_old = old_logic(loyers, charges, interets)
    gain_new, report_new = new_logic(loyers, charges, interets)
    delta = gain_new - gain_old

    print(
        f"{num:>4d} | {desc:<55s} | "
        f"{gain_old:>+8.0f} € | "
        f"{report_old:>+9.0f} € | "
        f"{gain_new:>+8.0f} € | "
        f"{report_new:>+9.0f} € | "
        f"{delta:>+8.0f} €"
    )

print("-" * 110)
print()

# Detailed breakdown per case
print("=" * 110)
print("DÉTAIL PAR CAS")
print("=" * 110)

for num, loyers, charges, interets, desc in cases:
    gain_old, report_old = old_logic(loyers, charges, interets)
    gain_new, report_new = new_logic(loyers, charges, interets)

    resultat_total = loyers - charges - interets
    resultat_travaux = loyers - charges

    print(f"\n--- CAS {num} : {desc} ---")
    print(f"    Résultat foncier = {loyers:,}€ - {charges:,}€ - {interets:,}€ = {resultat_total:+,}€")
    print(f"    Résultat travaux (avant intérêts) = {loyers:,}€ - {charges:,}€ = {resultat_travaux:+,}€")

    print(f"    ANCIEN CODE:")
    if resultat_total < 0:
        deficit = -resultat_total
        print(f"      Déficit total = {deficit:,}€  →  déductible RGlob = min({deficit:,}, {PLAFOND:,}) = {min(deficit, PLAFOND):,}€")
        print(f"      Gain fiscal = {min(deficit, PLAFOND):,}€ × {TMI*100:.0f}% = {gain_old:+,.0f}€")
        print(f"      Report RF = {deficit:,} - {min(deficit, PLAFOND):,} = {report_old:,.0f}€")
    else:
        print(f"      Pas de déficit → gain = 0€, report = 0€")

    print(f"    NOUVEAU CODE (LF 2019):")
    if resultat_total < 0:
        if resultat_travaux < 0:
            deficit_travaux = -resultat_travaux
            deficit_interets = interets
        else:
            deficit_travaux = 0
            deficit_interets = -resultat_total
        deductible = min(deficit_travaux, PLAFOND)
        print(f"      Déficit travaux (masse A) = {deficit_travaux:,}€")
        print(f"      Déficit intérêts (masse B) = {deficit_interets:,}€")
        print(f"      Imputation RGlob = min({deficit_travaux:,}, {PLAFOND:,}) = {deductible:,}€")
        print(f"      Gain fiscal = {deductible:,}€ × {TMI*100:.0f}% = {gain_new:+,.0f}€")
        print(f"      Report RF = ({deficit_travaux:,} - {deductible:,}) + {deficit_interets:,} = {report_new:,.0f}€")
    else:
        print(f"      Pas de déficit → gain = 0€, report = 0€")

    delta_case = gain_new - gain_old
    print(f"    → IMPACT : {delta_case:+,.0f}€/an de gain fiscal")

print()
print("=" * 110)
print("RÉSUMÉ : Le nouveau code distingue correctement les deux masses du déficit foncier.")
print("  - Masse A (travaux/charges) : imputable RGlob, plafond 10 700 €/an")
print("  - Masse B (intérêts d'emprunt) : reportable 10 ans UNIQUEMENT sur revenus fonciers")
print("=" * 110)
