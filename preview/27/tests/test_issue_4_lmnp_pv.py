#!/usr/bin/env python3
"""
Tests de non-régression pour la PR #13 — Issue #4
==================================================
Correction : en LMNP réel, l'amortissement comptable ne réduit PAS
la base de calcul de la plus-value immobilière (art. 150 U CGI, dernier alinéa).

Ce script compare les résultats AVANT le fix (bug) et APRÈS (corrigé)
sur 7 cas concrets AVANT / APRÈS.

Périmètre du fix #4 :
  - AVANT (bug) : l'amortissement est TOUJOURS déduit de la base fiscale,
    y compris en LMNP → base PV minorée → PV majorée → impôt indu.
  - APRÈS (fix) : l'amortissement LMNP n'est PAS déduit de la base PV.

Note sur les barèmes : la PR #15 (barème dual IR/PS) est déjà mergée.
Ce test isole l'effet du fix #4 en comparant :
  - AVANT = barème dual + amort déduit en LMNP (bug #4)
  - Pour CAS A/D/E, on compare aussi avec l'ancien barème unique (6%/an, max 60%)
    pour montrer l'impact cumulé des deux correctifs.
"""

import sys

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
PS_FONCIER = 0.172
IR_RATE = 0.19
ACHAT = 200_000
NOTAIRE_PCT = 0.08
ACQUISITION_BASE = ACHAT * (1 + NOTAIRE_PCT)  # 216 000 €
REVENTE = 300_000


# ===================================================================
# Barèmes
# ===================================================================
def ab_old(holding_years: int) -> float:
    """Ancien barème unique : 6%/an après 5 ans, max 60%."""
    y = max(0, holding_years)
    if y < 6:
        return 0.0
    return min((y - 5) * 0.06, 0.60)


def ab_ir(holding_years: int) -> float:
    """Barème dual IR (art. 150 VC CGI)."""
    y = max(0, holding_years)
    if y < 6:
        return 0.0
    if y >= 22:
        return 1.0
    return min((y - 5) * 0.06, 0.96)


def ab_ps(holding_years: int) -> float:
    """Barème dual PS (art. 150 VC CGI)."""
    y = max(0, holding_years)
    if y < 6:
        return 0.0
    if y >= 30:
        return 1.0
    a = 0.0
    if y > 5:
        a += min(y - 5, 16) * 0.0165
    if y >= 22:
        a += 0.016
    if y > 22:
        a += min(y - 22, 7) * 0.09
    return min(a, 1.0)


# ===================================================================
# Simulateurs
# ===================================================================
def _zero():
    return {"pv": 0.0, "acq": 0.0, "ab_ir": 0.0, "ab_ps": 0.0,
            "t_ir": 0.0, "t_ps": 0.0, "ir": 0.0, "ps": 0.0, "tax": 0.0}


def compute(acquisition_base: float, amort_cumule: float, revente: float,
            holding_years: int, is_lmnp: bool,
            old_barème: bool,      # True = ancien barème unique 6%/an max 60%
            amort_bug: bool) -> dict:  # True = amort toujours déduit (bug)
    """Simule un calcul de PV avec les paramètres donnés."""
    if amort_bug:
        acq_fisc = acquisition_base - amort_cumule
    else:
        acq_fisc = acquisition_base - (0.0 if is_lmnp else amort_cumule)

    pv = max(0.0, revente - acq_fisc)

    if pv <= 0:
        return _zero()

    if old_barème:
        ab = ab_old(holding_years)
        t_ir = pv * (1.0 - ab)
        t_ps = t_ir
        a_ir = ab
        a_ps = ab
    else:
        a_ir = ab_ir(holding_years)
        a_ps = ab_ps(holding_years)
        t_ir = pv * (1.0 - a_ir)
        t_ps = pv * (1.0 - a_ps)

    ir = t_ir * IR_RATE
    ps = t_ps * PS_FONCIER
    return {"pv": pv, "acq": acq_fisc,
            "ab_ir": a_ir, "ab_ps": a_ps,
            "t_ir": t_ir, "t_ps": t_ps,
            "ir": ir, "ps": ps, "tax": ir + ps}


# ===================================================================
# Helpers
# ===================================================================
def e(v: float) -> str:
    return f"{round(v):,}€".replace(",", " ")


def pct(v: float) -> str:
    return f"{v * 100:.1f}%"


# ===================================================================
# MAIN
# ===================================================================
def main() -> int:
    # ------------------------------------------------------------------
    # Tableau comparatif : 7 cas
    # AVANT  = barème DUAL + amort déduit en LMNP (bug #4)
    # APRÈS  = barème DUAL + amort NON déduit en LMNP (fix #4)
    # ANCIEN = barème UNIQUE + amort déduit en LMNP (avant #4 + #15)
    # ------------------------------------------------------------------
    cases_def = [
        # (label, amort, years, is_lmnp, revente)
        ("CAS A — LMNP réel, 15 ans, amort 100 k€",   100_000, 15, True,  REVENTE),
        ("CAS B — LMNP micro-BIC, 15 ans, amort 0 €",       0, 15, True,  REVENTE),
        ("CAS C — Location nue, 15 ans, amort 0 €",         0, 15, False, REVENTE),
        ("CAS D — LMNP réel, 22 ans, amort 100 k€",   100_000, 22, True,  REVENTE),
        ("CAS E — LMNP réel, 30 ans, amort 100 k€",   100_000, 30, True,  REVENTE),
        ("CAS F — PV nulle (revente = achat)",                   0, 15, True,  ACHAT),
        ("CAS G — PV négative (revente < achat)",                0, 15, True,  150_000),
    ]

    results = []
    for label, amort, yrs, is_lmnp, rev in cases_def:
        ancien = compute(ACQUISITION_BASE, amort, rev, yrs, is_lmnp,
                         old_barème=True, amort_bug=True)
        avant  = compute(ACQUISITION_BASE, amort, rev, yrs, is_lmnp,
                         old_barème=False, amort_bug=True)
        apres  = compute(ACQUISITION_BASE, amort, rev, yrs, is_lmnp,
                         old_barème=False, amort_bug=False)
        eco = avant["tax"] - apres["tax"]
        results.append((label, ancien, avant, apres, eco, amort, yrs, is_lmnp, rev))

    # ---- Tableau synthétique ----
    hdr = (f"{'Cas':<43} {'Base AV':>14} {'Base AP':>14} "
           f"{'PV AV':>12} {'PV AP':>12} {'Tax AV':>12} {'Tax AP':>12} {'Économie':>12}")
    sep = "─" * len(hdr)

    print()
    print("=" * len(hdr))
    print("  PR #13 — Issue #4 : Amortissement LMNP & base de la plus-value")
    print("  Achat 200 k€, notaire 8 %, revente 300 k€ (sauf F & G)")
    print()
    print("  AVANT = barème dual IR/PS  +  amort TOUJOURS déduit (bug #4)")
    print("  APRÈS = barème dual IR/PS  +  amort ignoré en LMNP (fix #4)")
    print("=" * len(hdr))
    print()
    print(hdr)
    print(sep)

    for label, ancien, avant, apres, eco, amort, yrs, is_lmnp, rev in results:
        print(f"{label:<43} {e(avant['acq']):>14} {e(apres['acq']):>14} "
              f"{e(avant['pv']):>12} {e(apres['pv']):>12} "
              f"{e(avant['tax']):>12} {e(apres['tax']):>12} "
              f"{e(eco):>12}")

    # ---- Détail cas par cas ----
    print()
    print(sep)
    print("  DÉTAIL PAR CAS")
    print(sep)
    print()

    for label, ancien, avant, apres, eco, amort, yrs, is_lmnp, rev in results:
        print(f"▸ {label}")
        print(f"  Paramètres : amort cumulé = {e(amort)}, "
              f"détention = {yrs} ans, LMNP = {'oui' if is_lmnp else 'non'}, "
              f"revente = {e(rev)}")
        print()

        # ANCIEN (avant #4 + #15)
        print(f"  ┌─ ANCIEN (barème unique 6 %/an max 60 % + amort déduit)")
        print(f"  │  Base fiscale = {e(ancien['acq'])}  →  PV = {e(ancien['pv'])}")
        print(f"  │  Abattement unique : {pct(ancien['ab_ir'])}")
        print(f"  │  Assiette taxable = {e(ancien['t_ir'])}")
        print(f"  │  IR = {e(ancien['ir'])}  |  PS = {e(ancien['ps'])}  |  TOTAL = {e(ancien['tax'])}")

        # AVANT (dual barème mais bug #4)
        print(f"  ├─ AVANT bug #4 (barème dual + amort déduit en LMNP)")
        print(f"  │  Base fiscale = {e(avant['acq'])}  →  PV = {e(avant['pv'])}")
        print(f"  │  Abattement IR = {pct(avant['ab_ir'])}  |  PS = {pct(avant['ab_ps'])}")
        print(f"  │  Assiette IR = {e(avant['t_ir'])}  →  IR = {e(avant['ir'])}")
        print(f"  │  Assiette PS = {e(avant['t_ps'])}  →  PS = {e(avant['ps'])}")
        print(f"  │  TOTAL = {e(avant['tax'])}")

        # APRÈS (dual barème + fix #4)
        print(f"  └─ APRÈS (barème dual + amort ignoré en LMNP)")
        print(f"     Base fiscale = {e(apres['acq'])}  →  PV = {e(apres['pv'])}")
        print(f"     Abattement IR = {pct(apres['ab_ir'])}  |  PS = {pct(apres['ab_ps'])}")
        print(f"     Assiette IR = {e(apres['t_ir'])}  →  IR = {e(apres['ir'])}")
        print(f"     Assiette PS = {e(apres['t_ps'])}  →  PS = {e(apres['ps'])}")
        print(f"     TOTAL = {e(apres['tax'])}")

        print()
        # Résumé de la différence
        eco_ancien = ancien["tax"] - apres["tax"]
        if eco > 0.5:
            print(f"     💸 Économie du fix #4 seul     = {e(eco)}")
            print(f"     💸 Économie cumulée (#4 + #15)  = {e(eco_ancien)}")
        elif eco < -0.5:
            print(f"     ⚠️  Surcoût apparent = {e(-eco)}  (le fix #4 n'a pas d'effet")
            print(f"         car amort = 0 ; seule la comparaison ancien/APRÈS")
            print(f"         montre l'impact cumulé des deux correctifs)")
        else:
            print(f"     ✅ Pas d'effet du fix #4 seul (amort = 0 ou régime inchangé)")
            if abs(eco_ancien) > 0.5:
                print(f"     💸 Économie cumulée (#4 + #15)  = {e(eco_ancien)}")
        print()

    # ===================================================================
    # Vérifications
    # ===================================================================
    print("=" * len(hdr))
    print("  VÉRIFICATIONS")
    print("=" * len(hdr))
    print()

    errors = 0

    # --- CAS A ---
    _, anc_a, av_a, ap_a, eco_a, *_ = results[0]
    # AVANT vs APRÈS : l'économie du fix #4
    # AVANT: PV=184k, dual barème → IR: 184k×0.4×0.19=13 984, PS: 184k×0.835×0.172=26 426, total=40 410
    # APRÈS: PV=84k, dual barème → IR: 84k×0.4×0.19=6 384, PS: 84k×0.835×0.172=12 064, total=18 448
    # Économie: 40 410 - 18 448 = 21 962
    exp_a = 21_962
    if abs(round(eco_a) - exp_a) <= 2:
        print(f"✅ CAS A : économie fix #4 = {e(eco_a)}  (attendu ~{e(exp_a)})")
    else:
        print(f"❌ CAS A : économie = {e(eco_a)}  (attendu ~{e(exp_a)})")
        errors += 1
    # ANCIEN vs APRÈS: 26 643 - 18 448 = 8 195
    eco_anc_a = anc_a["tax"] - ap_a["tax"]
    exp_anc_a = 8_195
    if abs(round(eco_anc_a) - exp_anc_a) <= 2:
        print(f"   économie cumulée (ancien→APRÈS) = {e(eco_anc_a)}  ✓")
    else:
        print(f"   ❌ économie cumulée = {e(eco_anc_a)}  (attendu ~{e(exp_anc_a)})")
        errors += 1

    # --- CAS B : micro-BIC, amort = 0 → fix #4 sans effet ---
    _, anc_b, av_b, ap_b, eco_b, *_ = results[1]
    if abs(round(eco_b)) == 0:
        print(f"✅ CAS B : économie fix #4 = {e(eco_b)}  (micro-BIC, amort=0 → pas d'effet)")
    else:
        print(f"❌ CAS B : économie = {e(eco_b)}  (attendu 0)")
        errors += 1
    # ANCIEN vs APRÈS: 12 163 - 18 448 = -6 285 (surcoût lié au changement de barème PS)
    eco_anc_b = anc_b["tax"] - ap_b["tax"]
    print(f"   Note : ancien→APRÈS = {e(eco_anc_b)}  (le barème dual PS 16.5% est moins favorable")
    print(f"   que l'ancien 60% pour les détentions < 22 ans)")

    # --- CAS C : location nue → même logique ---
    _, anc_c, av_c, ap_c, eco_c, *_ = results[2]
    if abs(round(eco_c)) == 0:
        print(f"✅ CAS C : économie fix #4 = {e(eco_c)}  (location nue, pas d'amort → pas d'effet)")
    else:
        print(f"❌ CAS C : économie = {e(eco_c)}  (attendu 0)")
        errors += 1
    eco_anc_c = anc_c["tax"] - ap_c["tax"]
    print(f"   Note : ancien→APRÈS = {e(eco_anc_c)}  (idem CAS B)")

    # --- CAS D : 22 ans, exonération IR ---
    _, anc_d, av_d, ap_d, eco_d, *_ = results[3]
    assert ap_d["ir"] < 0.5, f"CAS D : IR APRÈS doit être 0"
    # AVANT: PV=184k, dual: IR=13 984, PS: 184k×0.72×0.172=22 775, total=36 759
    # APRÈS: PV=84k, dual: IR=0, PS: 84k×0.72×0.172=10 403, total=10 403
    # Économie: 36 759 - 10 403 = 26 356
    exp_d = 12_384
    if abs(round(eco_d) - exp_d) <= 2:
        print(f"✅ CAS D : IR APRÈS = 0€, économie fix #4 = {e(eco_d)}  (attendu ~{e(exp_d)})")
    else:
        print(f"❌ CAS D : économie = {e(eco_d)}  (attendu ~{e(exp_d)})")
        errors += 1
    # ANCIEN vs APRÈS: 26 643 - 10 403 = 16 240
    eco_anc_d = anc_d["tax"] - ap_d["tax"]
    exp_anc_d = 16_240
    if abs(round(eco_anc_d) - exp_anc_d) <= 2:
        print(f"   économie cumulée (ancien→APRÈS) = {e(eco_anc_d)}  ✓")
    else:
        print(f"   ❌ économie cumulée = {e(eco_anc_d)}  (attendu ~{e(exp_anc_d)})")
        errors += 1

    # --- CAS E : 30 ans, exonération totale IR+PS ---
    _, anc_e, av_e, ap_e, eco_e, *_ = results[4]
    assert ap_e["ir"] < 0.5 and ap_e["ps"] < 0.5, \
        f"CAS E : IR+PS APRÈS doivent être 0"
    # AVANT: PV=184k, dual: IR exo, PS exo → total=0? No wait!
    # At 30 years, both barèmes give 100% exemption. But the BUG makes PV=184k.
    # AVANT: PV=184k, IR ab=100%, PS ab=100% → IR=0, PS=0, total=0 (barème masks the bug!)
    # Hmm, actually at 30 years the abatement is 100% for both, so even with bug, tax=0.
    # Wait, that doesn't make sense. Let me recalculate.
    # AVANT: PV=184k, ab_ir(30)=100%, ab_ps(30)=100% → taxable_ir=0, taxable_ps=0 → tax=0
    # APRÈS: PV=84k, same → tax=0
    # So économie = 0 for fix #4 alone at 30 years!
    # But ANCIEN: PV=184k, ab=60%, taxable=73.6k, total=26 643.
    # ANCIEN vs APRÈS = 26 643.

    # Actually, let me check: ab_ps(30) = 1.0 because y >= 30 returns 1.0.
    # And ab_ir(30) = 1.0 because y >= 22 returns 1.0.
    # So AVANT at 30 years with dual barème: tax = 0 (bug masked by full exemption).
    # This means the fix #4 alone doesn't change anything at 30 years!
    # Only when combined with the old→new barème change does it matter.

    # But the task says CAS E économie = 26 643€. Let me re-check...
    # The task: "CAS E : LMNP réel, détention 30 ans — exonération totale IR+PS"
    # "AVANT (bug) : acquisitionCostFiscal = 116k → PV = 184k, abattement 60% → taxable = 73.6k → total = 26 643€"
    # This uses the OLD barème (60% single) — consistent with the ANCIEN column.
    # "APRÈS (fix) : acquisitionCostFiscal = 216k → PV = 84k → IR exo, PS exo → total = 0€"
    # So CAS E for AVANT refers to ANCIEN (old barème + bug).

    # The task is comparing ANCIEN vs APRÈS for CAS E, not AVANT dual vs APRÈS.
    # Let me just verify: ANCIEN vs APRÈS économie = 26 643€.
    eco_anc_e = anc_e["tax"] - ap_e["tax"]
    exp_anc_e = 26_643
    if abs(round(eco_anc_e) - exp_anc_e) <= 2:
        print(f"✅ CAS E : IR+PS APRÈS = 0€, économie cumulée = {e(eco_anc_e)}  (attendu ~{e(exp_anc_e)})")
    else:
        print(f"❌ CAS E : économie cumulée = {e(eco_anc_e)}  (attendu ~{e(exp_anc_e)})")
        errors += 1
    if abs(round(eco_e)) <= 2:
        print(f"   Note : fix #4 seul → économie = {e(eco_e)}  (barème dual exonère déjà à 30 ans)")
    else:
        print(f"   Note : fix #4 seul → économie = {e(eco_e)}")

    # --- CAS F : PV nulle ---
    _, anc_f, av_f, ap_f, eco_f, *_ = results[5]
    ok_f = anc_f["tax"] < 0.5 and av_f["tax"] < 0.5 and ap_f["tax"] < 0.5
    if ok_f:
        print(f"✅ CAS F : taxe = 0€ dans les trois scénarios (PV nulle)")
    else:
        print(f"❌ CAS F : ANCIEN={e(anc_f['tax'])}, AVANT={e(av_f['tax'])}, APRÈS={e(ap_f['tax'])}")
        errors += 1

    # --- CAS G : PV négative ---
    _, anc_g, av_g, ap_g, eco_g, *_ = results[6]
    ok_g = anc_g["tax"] < 0.5 and av_g["tax"] < 0.5 and ap_g["tax"] < 0.5
    if ok_g:
        print(f"✅ CAS G : taxe = 0€ dans les trois scénarios (PV négative)")
    else:
        print(f"❌ CAS G : ANCIEN={e(anc_g['tax'])}, AVANT={e(av_g['tax'])}, APRÈS={e(ap_g['tax'])}")
        errors += 1

    print()
    if errors:
        print(f"❌ {errors} erreur(s) — EXIT 1")
        return 1
    else:
        print("✅ Tous les tests sont passés.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
