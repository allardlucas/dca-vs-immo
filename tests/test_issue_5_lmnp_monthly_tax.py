#!/usr/bin/env python3
"""
Test script for Issue #5: monthlyTaxEstimate in LMNP réel now accounts for amortization.
Compares BEFORE (old code) vs AFTER (new code with lastYearAnnualRentTax).
"""

# ── Parameters ──────────────────────────────────────────────────────────────
price = 200_000                # Purchase price
loan_amount = 160_000          # Loan amount
loan_rate = 0.035              # 3.5% annual
rent = 900                     # Monthly rent
monthly_rate = loan_rate / 12
loan_months = 25 * 12          # 25-year loan

# Expenses
taxe_fonciere = 1_200          # /year
charges = 200                  # /month copro
assurance = 300 / 12           # /month (25€)
gestion_pct = 0.07             # 7% property management
cfe = 500                      # /year LMNP
travaux_pct = 0.01             # 1% travaux

# Amortization (LMNP réel)
LMNP_BUILDING_PCT = 0.80
LMNP_FURNITURE_PCT = 0.10
LMNP_BUILDING_YEARS = 25
LMNP_FURNITURE_YEARS = 7
building_amort_lmnp = LMNP_BUILDING_PCT * price / LMNP_BUILDING_YEARS    # 6400
furniture_amort_lmnp = LMNP_FURNITURE_PCT * price / LMNP_FURNITURE_YEARS  # 2857.14
monthly_amort_lmnp = (building_amort_lmnp + furniture_amort_lmnp) / 12   # ~771

rent_tax_rate = 0.472  # TMI 30% + PS 17.2% = 47.2%
vacance = 0.05         # 5% vacancy

# Monthly expenses
monthly_rent = rent * (1 - vacance)  # 855
monthly_taxe = taxe_fonciere / 12    # 100
monthly_charges = charges            # 200
monthly_assurance = assurance        # 25
monthly_gestion = monthly_rent * gestion_pct  # ~59.85
monthly_cfe = cfe / 12               # ~41.67
monthly_travaux = price * travaux_pct / 12    # ~166.67
month_expenses = (monthly_taxe + monthly_charges + monthly_assurance
                  + monthly_gestion + monthly_cfe + monthly_travaux)
# ≈ 100 + 200 + 25 + 59.85 + 41.67 + 166.67 = 593.19

# ── Helper functions ────────────────────────────────────────────────────────
def old_monthly_tax(rent_regime, cumul_deficit_foncier=0, cumul_deficit_bic=0):
    """BEFORE fix: does NOT subtract amortization."""
    monthly_rent_rough = monthly_rent - month_expenses
    if rent_regime == 'micro-foncier':
        return monthly_rent * 0.70 * rent_tax_rate
    if rent_regime == 'micro-bic':
        return monthly_rent * 0.50 * rent_tax_rate
    if rent_regime == 'reel-foncier' and cumul_deficit_foncier > 0 and monthly_rent_rough > 0:
        yearly_rough = monthly_rent_rough * 12
        deficit_deduction = min(cumul_deficit_foncier, yearly_rough)
        return max(0, (yearly_rough - deficit_deduction) / 12) * rent_tax_rate
    if rent_regime == 'reel-bic' and cumul_deficit_bic > 0 and monthly_rent_rough > 0:
        yearly_rough = monthly_rent_rough * 12
        deficit_deduction = min(cumul_deficit_bic, yearly_rough)
        return max(0, (yearly_rough - deficit_deduction) / 12) * rent_tax_rate
    return max(0, monthly_rent - month_expenses) * rent_tax_rate


def new_monthly_tax(rent_regime, last_year_tax=0, cumul_deficit_foncier=0, cumul_deficit_bic=0,
                    monthly_amort=0):
    """AFTER fix: uses lastYearAnnualRentTax for years 2+, includes amort in year 1.
    monthly_amort: amortissement mensuel total (0 pour location nue, ~771€ pour LMNP)."""
    if rent_regime == 'micro-foncier':
        return monthly_rent * 0.70 * rent_tax_rate
    if rent_regime == 'micro-bic':
        return monthly_rent * 0.50 * rent_tax_rate

    # Régimes réels
    if last_year_tax > 0:
        return last_year_tax / 12

    # Year 1 estimate with amortization
    monthly_rent_rough = monthly_rent - month_expenses - monthly_amort

    if rent_regime == 'reel-foncier' and cumul_deficit_foncier > 0 and monthly_rent_rough > 0:
        yearly_rough = monthly_rent_rough * 12
        deficit_deduction = min(cumul_deficit_foncier, yearly_rough)
        return max(0, (yearly_rough - deficit_deduction) / 12) * rent_tax_rate
    if rent_regime == 'reel-bic' and cumul_deficit_bic > 0 and monthly_rent_rough > 0:
        yearly_rough = monthly_rent_rough * 12
        deficit_deduction = min(cumul_deficit_bic, yearly_rough)
        return max(0, (yearly_rough - deficit_deduction) / 12) * rent_tax_rate
    return max(0, monthly_rent_rough) * rent_tax_rate


# ── Compute monthly interest for year 1 (for reference) ─────────────────────
remaining = loan_amount
annual_interest_y1 = 0
for m in range(12):
    if monthly_rate > 0 and remaining > 0:
        interest = remaining * monthly_rate
        monthly_payment = (loan_amount * monthly_rate
                          * (1 + monthly_rate) ** loan_months
                          / ((1 + monthly_rate) ** loan_months - 1))
        principal = monthly_payment - interest
        annual_interest_y1 += interest
        remaining = max(0, remaining - principal)
avg_monthly_interest_y1 = annual_interest_y1 / 12

# Annual tax simulation for year 1 (reel-bic)
annual_rent_revenue = monthly_rent * 12
annual_expenses = month_expenses * 12
annual_amort_y1 = building_amort_lmnp + furniture_amort_lmnp
resultat_bic_y1 = annual_rent_revenue - annual_expenses - annual_interest_y1 - annual_amort_y1
annual_tax_y1 = max(0, resultat_bic_y1) * rent_tax_rate if resultat_bic_y1 > 0 else 0

# ── DISPLAY ─────────────────────────────────────────────────────────────────
print("=" * 90)
print("TEST ISSUE #5 : monthlyTaxEstimate AVANT vs APRÈS (LMNP réel amortissement)")
print("=" * 90)
print(f"\nParamètres :")
print(f"  Prix achat           : {price:,.0f} €")
print(f"  Loyer mensuel        : {monthly_rent:.0f} € (après vacance {vacance*100:.0f}%)")
print(f"  Charges mensuelles   : {month_expenses:.0f} €")
print(f"  Amort. bâtiment/an   : {building_amort_lmnp:,.0f} € → {building_amort_lmnp/12:,.0f} €/mois")
print(f"  Amort. mobilier/an   : {furniture_amort_lmnp:,.0f} € → {furniture_amort_lmnp/12:,.0f} €/mois")
print(f"  Amort. total LMNP/mois: {monthly_amort_lmnp:,.0f} €")
print(f"  Intérêts Y1/mois     : {avg_monthly_interest_y1:,.0f} €")
print(f"  TMI+PS               : {rent_tax_rate*100:.1f}%")
print(f"  Résultat BIC Y1      : {resultat_bic_y1:,.0f} € (→ impôt annuel Y1 = {annual_tax_y1:,.0f} €)")
print()

print(f"{'#':<4} {'Scénario':<64} {'AVANT':>8} {'APRÈS':>8} {'Écart':>8}")
print("-" * 90)

tests = []
all_pass = True

# ── CAS 1: Année 1, LMNP réel, pas de déficit BIC antérieur ─────────────────
avant = old_monthly_tax('reel-bic')
apres = new_monthly_tax('reel-bic', monthly_amort=monthly_amort_lmnp)
tests.append((1, "Année 1, LMNP réel, pas de déficit BIC antérieur", avant, apres))
assert apres < avant, f"CAS 1 FAIL: APRÈS ({apres:.0f}) >= AVANT ({avant:.0f})"
assert apres == 0, f"CAS 1 FAIL: APRÈS devrait être 0, got {apres:.0f}"

# ── CAS 2: Année 2, LMNP réel, lastYearTax=0 (année 1 non imposable) ────────
avant = old_monthly_tax('reel-bic')
apres = new_monthly_tax('reel-bic', last_year_tax=0, monthly_amort=monthly_amort_lmnp)
tests.append((2, "Année 2, LMNP réel, lastYearTax=0 (année 1 non imposable)", avant, apres))
assert apres < avant, f"CAS 2 FAIL"
assert apres == 0, f"CAS 2 FAIL: devrait être 0, got {apres:.0f}"

# ── CAS 3: Année 5+, LMNP réel, lastYearAnnualRentTax = 1200 ────────────────
avant = old_monthly_tax('reel-bic')
apres = new_monthly_tax('reel-bic', last_year_tax=1200, monthly_amort=monthly_amort_lmnp)
tests.append((3, "Année 5+, LMNP réel, lastYearTax=1200€ (légèrement imposable)", avant, apres))
assert apres < avant, f"CAS 3 FAIL"
assert abs(apres - 100) < 1, f"CAS 3 FAIL: devrait être 100€, got {apres:.0f}"

# ── CAS 4: Micro-BIC — pas de changement ────────────────────────────────────
avant = old_monthly_tax('micro-bic')
apres = new_monthly_tax('micro-bic')
tests.append((4, "Micro-BIC — forfaitaire, pas de changement", avant, apres))
assert apres == avant, f"CAS 4 FAIL"

# ── CAS 5: Micro-Foncier — pas de changement ────────────────────────────────
avant = old_monthly_tax('micro-foncier')
apres = new_monthly_tax('micro-foncier')
tests.append((5, "Micro-Foncier — forfaitaire, pas de changement", avant, apres))
assert apres == avant, f"CAS 5 FAIL"

# ── CAS 6: Réel-foncier, année 1, amort = 0 (location nue) ──────────────────
avant = old_monthly_tax('reel-foncier')
apres = new_monthly_tax('reel-foncier', last_year_tax=0, monthly_amort=0)
tests.append((6, "Réel-foncier, année 1, amort=0 (location nue) → identique", avant, apres))
assert apres == avant, f"CAS 6 FAIL: APRÈS ({apres:.0f}) != AVANT ({avant:.0f})"

# ── CAS 7: Réel-foncier, année 3, lastYearTax=800€ ──────────────────────────
avant = old_monthly_tax('reel-foncier')
apres = new_monthly_tax('reel-foncier', last_year_tax=800, monthly_amort=0)
tests.append((7, "Réel-foncier, année 3, lastYearTax=800€ → 800/12=67€", avant, apres))
assert apres < avant, f"CAS 7 FAIL"
assert abs(apres - 800/12) < 0.1, f"CAS 7 FAIL: devrait être {800/12:.1f}, got {apres:.0f}"

# ── CAS 8: LMNP réel, année 1, déficit BIC antérieur 5000€ ──────────────────
avant = old_monthly_tax('reel-bic', cumul_deficit_bic=5000)
apres = new_monthly_tax('reel-bic', last_year_tax=0, cumul_deficit_bic=5000,
                        monthly_amort=monthly_amort_lmnp)
tests.append((8, "LMNP réel, année 1, déficit BIC antérieur 5000€", avant, apres))
assert apres <= avant, f"CAS 8 FAIL"

# ── CAS 9: LMNP réel, année 2, lastYearTax négatif (-1500€ gain fiscal) ─────
avant = old_monthly_tax('reel-bic')
apres = new_monthly_tax('reel-bic', last_year_tax=-1500, monthly_amort=monthly_amort_lmnp)
tests.append((9, "LMNP réel, année 2, lastYearTax=-1500€ → fallback année 1", avant, apres))
# Negative lastYearTax → lastYearTax > 0 is FALSE → uses year 1 path with amort
assert apres == 0, f"CAS 9 FAIL: devrait être 0, got {apres:.0f}"

# ── Print results ───────────────────────────────────────────────────────────
for num, scenario, avant, apres in tests:
    ecart = apres - avant
    print(f"{num:<4} {scenario:<64} {avant:>7.0f}€ {apres:>7.0f}€ {ecart:>+7.0f}€")

print()
print("=" * 90)
print("✅ TOUS LES 9 TESTS PASSENT !")
print("=" * 90)
print()

# ── Impact summary ──────────────────────────────────────────────────────────
old_val = old_monthly_tax('reel-bic')
new_val_y1 = new_monthly_tax('reel-bic', monthly_amort=monthly_amort_lmnp)
print("RÉSUMÉ DE L'IMPACT SUR LE DCA EFFORT :")
print(f"  monthlyTaxEstimate AVANT (LMNP réel, n'importe quelle année) : {old_val:>7.0f}€/mois")
print(f"  monthlyTaxEstimate APRÈS (année 1, estimation avec amort)    : {new_val_y1:>7.0f}€/mois")
print(f"  monthlyTaxEstimate APRÈS (année 2+, lastYearTax=0)           : {new_monthly_tax('reel-bic', last_year_tax=0, monthly_amort=monthly_amort_lmnp):>7.0f}€/mois")
print(f"  monthlyTaxEstimate APRÈS (année 5+, lastYearTax=1200)        : {new_monthly_tax('reel-bic', last_year_tax=1200, monthly_amort=monthly_amort_lmnp):>7.0f}€/mois")
print()
print(f"  ➜ Économie DCA mensuelle (année 1)                           : {old_val - new_val_y1:>7.0f}€/mois")
print(f"  ➜ Économie DCA annuelle                                      : {(old_val - new_val_y1) * 12:>7,.0f}€/an")
print()
print("  ⚠️  AVANT : le DCA effort était surévalué de 124€/mois → biais en faveur du DCA")
print("  ✅ APRÈS : le DCA effort reflète la réalité fiscale (amortissement déduit)")
