#!/usr/bin/env python3
"""
Test de la surtaxe progressive sur PV > 50 000 € (art. 1609 nonies G CGI)
9 edge cases AVANT/APRÈS
"""

def surtaxe_pv(assiette):
    """Surtaxe progressive par tranches sur la PV après abattement IR."""
    if assiette <= 50000:
        return 0
    tax = 0
    tranches = [
        (50000, 60000, 0.02),
        (60000, 100000, 0.03),
        (100000, 150000, 0.04),
        (150000, 200000, 0.05),
        (200000, 250000, 0.06),
        (250000, float('inf'), 0.06),
    ]
    for mini, maxi, rate in tranches:
        if assiette > mini:
            tax += (min(assiette, maxi) - mini) * rate
    return tax


def ir_tax(assiette):
    """Impôt IR : 19% de l'assiette."""
    return assiette * 0.19


def ps_tax(assiette):
    """Prélèvements sociaux : 17,2% de l'assiette PS.
    Pour les tests, on suppose assiette PS = assiette IR (pas d'abattement dual)."""
    return assiette * 0.172


# 9 CAS DE TEST
cases = [
    # (nom, irTaxable, psTaxable, description)
    ("CAS 1 : PV=30k€", 30000, 30000, "sous le seuil → surtaxe = 0"),
    ("CAS 2 : PV=55k€", 55000, 55000, "2e tranche 2% → 100€"),
    ("CAS 3 : PV=80k€", 80000, 80000, "tranches 2%+3% → 800€"),
    ("CAS 4 : PV=120k€", 120000, 120000, "2%+3%+4% → 2200€"),
    ("CAS 5 : PV=180k€", 180000, 180000, "2+3+4+5% → 4900€"),
    ("CAS 6 : PV=220k€", 220000, 220000, "2+3+4+5+6% → 7100€"),
    ("CAS 7 : PV=300k€", 300000, 300000, "toutes tranches → 11900€"),
    ("CAS 8 : PV=0€", 0, 0, "zéro → 0€"),
    ("CAS 9 : PV=50000€", 50000, 50000, "pile au seuil (exclu) → 0€"),
]

print()
print("=" * 110)
print("  TEST SURTAXE PROGRESSIVE PV > 50 000 € (art. 1609 nonies G CGI)")
print("=" * 110)
print(f"{'Cas':<28} {'PV ap.abatt':>12} {'IR (19%)':>10} {'PS (17.2%)':>10} {'Surtaxe':>10} {'TOTAL AVANT':>12} {'TOTAL APRÈS':>12} {'Δ':>10}")
print("-" * 110)

all_ok = True
for name, ir_t, ps_t, desc in cases:
    ir = ir_tax(ir_t)
    ps = ps_tax(ps_t)
    surtaxe = surtaxe_pv(ir_t)
    total_avant = ir + ps
    total_apres = total_avant + surtaxe
    delta = total_apres - total_avant

    # Vérifications spécifiques
    if "PV=30k" in name:
        expected_surtaxe = 0
    elif "PV=55k" in name:
        expected_surtaxe = 100
    elif "PV=80k" in name:
        expected_surtaxe = 800
    elif "PV=120k" in name:
        expected_surtaxe = 2200
    elif "PV=180k" in name:
        expected_surtaxe = 4900
    elif "PV=220k" in name:
        expected_surtaxe = 7100
    elif "PV=300k" in name:
        expected_surtaxe = 11900
    elif "PV=0" in name:
        expected_surtaxe = 0
    elif "PV=50000" in name:
        expected_surtaxe = 0
    else:
        expected_surtaxe = None

    ok = expected_surtaxe is not None and abs(surtaxe - expected_surtaxe) < 0.01
    status = "✅" if ok else "❌"
    if not ok:
        all_ok = False

    print(f"{status} {name:<25} {ir_t:>12,.0f} € {ir:>10,.0f} € {ps:>10,.0f} € {surtaxe:>10,.0f} € {total_avant:>12,.0f} € {total_apres:>12,.0f} € {delta:>10,.0f} €")
    print(f"   → {desc} | surtaxe attendue = {expected_surtaxe:,.0f} € | obtenue = {surtaxe:,.0f} €")

print("-" * 110)

# Vérifications détaillées du calcul par tranches
print()
print("VÉRIFICATIONS DÉTAILLÉES PAR TRANCHE :")
print()

detail_cases = [
    ("CAS 1 : 30k€", 30000, []),
    ("CAS 2 : 55k€", 55000, [("50k-55k (2%)", 5000, 0.02, 100)]),
    ("CAS 3 : 80k€", 80000, [
        ("50k-60k (2%)", 10000, 0.02, 200),
        ("60k-80k (3%)", 20000, 0.03, 600),
    ]),
    ("CAS 4 : 120k€", 120000, [
        ("50k-60k (2%)", 10000, 0.02, 200),
        ("60k-100k (3%)", 40000, 0.03, 1200),
        ("100k-120k (4%)", 20000, 0.04, 800),
    ]),
    ("CAS 5 : 180k€", 180000, [
        ("50k-60k (2%)", 10000, 0.02, 200),
        ("60k-100k (3%)", 40000, 0.03, 1200),
        ("100k-150k (4%)", 50000, 0.04, 2000),
        ("150k-180k (5%)", 30000, 0.05, 1500),
    ]),
    ("CAS 6 : 220k€", 220000, [
        ("50k-60k (2%)", 10000, 0.02, 200),
        ("60k-100k (3%)", 40000, 0.03, 1200),
        ("100k-150k (4%)", 50000, 0.04, 2000),
        ("150k-200k (5%)", 50000, 0.05, 2500),
        ("200k-220k (6%)", 20000, 0.06, 1200),
    ]),
    ("CAS 7 : 300k€", 300000, [
        ("50k-60k (2%)", 10000, 0.02, 200),
        ("60k-100k (3%)", 40000, 0.03, 1200),
        ("100k-150k (4%)", 50000, 0.04, 2000),
        ("150k-200k (5%)", 50000, 0.05, 2500),
        ("200k-250k (6%)", 50000, 0.06, 3000),
        ("250k-300k (6%)", 50000, 0.06, 3000),
    ]),
]

for name, assiette, tranches in detail_cases:
    total = 0
    print(f"{name} :")
    for desc, base, taux, montant in tranches:
        print(f"  {desc:<25} : {base:>8,.0f} × {taux*100:.0f}% = {montant:>8,.0f} €")
        total += montant
    print(f"  TOTAL SURTAXE : {total:,.0f} €")
    computed = surtaxe_pv(assiette)
    if abs(total - computed) < 0.01:
        print(f"  ✅ Cohérent avec surtaxePV() = {computed:,.0f} €")
    else:
        print(f"  ❌ ERREUR : calculé = {total:,.0f} €, surtaxePV() = {computed:,.0f} €")
        all_ok = False
    print()

print("=" * 110)
if all_ok:
    print("✅ TOUS LES TESTS SONT PASSÉS — La surtaxe progressive est correctement implémentée.")
else:
    print("❌ CERTAINS TESTS ONT ÉCHOUÉ — Vérifier l'implémentation.")
    exit(1)
print("=" * 110)
