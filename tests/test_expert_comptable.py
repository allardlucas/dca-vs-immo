"""
Test: Expert-comptable parameter for LMNP Réel (reel-bic) regime.

The expert-comptable charge (default 800€/year) should ONLY be added to
monthly expenses when the rent tax regime is 'reel-bic' (LMNP Réel).

For micro-bic and reel-foncier, it should NOT be included.
"""

import pytest


# --- Reproduction de la logique JS du simulateur ---

DEFAULT_EXPERT_COMPTABLE = 800  # €/an


def monthly_expenses(taxe_fonciere, charges, price, travaux_pct, gestion_pct,
                     cfe, expert_comptable, rent_tax_regime, monthly_rent):
    """
    Calcule les charges mensuelles comme dans la boucle mensuelle de runSimulation().
    """
    monthly_taxe = taxe_fonciere / 12
    monthly_charges = charges
    monthly_travaux = price * travaux_pct / 12
    monthly_assurance = 300 / 12
    monthly_gestion = monthly_rent * gestion_pct

    is_lmnp = rent_tax_regime in ('micro-bic', 'reel-bic')
    monthly_cfe = cfe / 12 if is_lmnp else 0
    monthly_expert = expert_comptable / 12 if rent_tax_regime == 'reel-bic' else 0

    return (monthly_taxe + monthly_charges + monthly_travaux +
            monthly_assurance + monthly_gestion + monthly_cfe + monthly_expert)


# --- Tests ---

def test_expert_comptable_reel_bic():
    """Avec reel-bic : l'expert-comptable ajoute 800/12 = 66.67€ aux charges mensuelles."""
    expenses_with = monthly_expenses(
        taxe_fonciere=1200,
        charges=100,
        price=200000,
        travaux_pct=0.005,
        gestion_pct=0.05,
        cfe=400,
        expert_comptable=800,
        rent_tax_regime='reel-bic',
        monthly_rent=800,
    )
    expenses_without = monthly_expenses(
        taxe_fonciere=1200,
        charges=100,
        price=200000,
        travaux_pct=0.005,
        gestion_pct=0.05,
        cfe=400,
        expert_comptable=0,  # pas d'expert-comptable
        rent_tax_regime='reel-bic',
        monthly_rent=800,
    )

    diff = expenses_with - expenses_without
    expected = 800 / 12  # 66.666...
    assert abs(diff - expected) < 0.01, (
        f"L'ajout de l'expert-comptable devrait être {expected}€/mois, "
        f"mais la différence est {diff}€/mois"
    )


def test_expert_comptable_micro_bic():
    """Avec micro-bic : les charges mensuelles n'incluent PAS l'expert-comptable."""
    expenses_with_800 = monthly_expenses(
        taxe_fonciere=1200,
        charges=100,
        price=200000,
        travaux_pct=0.005,
        gestion_pct=0.05,
        cfe=400,
        expert_comptable=800,
        rent_tax_regime='micro-bic',
        monthly_rent=800,
    )
    expenses_with_0 = monthly_expenses(
        taxe_fonciere=1200,
        charges=100,
        price=200000,
        travaux_pct=0.005,
        gestion_pct=0.05,
        cfe=400,
        expert_comptable=0,
        rent_tax_regime='micro-bic',
        monthly_rent=800,
    )

    # Même avec expert_comptable=800, le micro-bic ne doit pas l'inclure
    assert abs(expenses_with_800 - expenses_with_0) < 0.01, (
        f"En micro-bic, l'expert-comptable ne devrait pas impacter les charges. "
        f"expenses_with_800={expenses_with_800}, expenses_with_0={expenses_with_0}"
    )


def test_expert_comptable_reel_foncier():
    """Avec reel-foncier : pas d'expert-comptable non plus."""
    expenses_with_800 = monthly_expenses(
        taxe_fonciere=1200,
        charges=100,
        price=200000,
        travaux_pct=0.005,
        gestion_pct=0.05,
        cfe=400,
        expert_comptable=800,
        rent_tax_regime='reel-foncier',
        monthly_rent=800,
    )
    expenses_with_0 = monthly_expenses(
        taxe_fonciere=1200,
        charges=100,
        price=200000,
        travaux_pct=0.005,
        gestion_pct=0.05,
        cfe=400,
        expert_comptable=0,
        rent_tax_regime='reel-foncier',
        monthly_rent=800,
    )

    assert abs(expenses_with_800 - expenses_with_0) < 0.01, (
        f"En reel-foncier, l'expert-comptable ne devrait pas impacter les charges."
    )


def test_default_value():
    """La valeur par défaut est bien 800."""
    assert DEFAULT_EXPERT_COMPTABLE == 800, (
        f"La valeur par défaut de l'expert-comptable devrait être 800, "
        f"pas {DEFAULT_EXPERT_COMPTABLE}"
    )


def test_expert_comptable_custom_value_reel_bic():
    """Vérifie qu'une valeur custom (ex: 1200€) fonctionne correctement en reel-bic."""
    expenses_1200 = monthly_expenses(
        taxe_fonciere=1200,
        charges=100,
        price=200000,
        travaux_pct=0.005,
        gestion_pct=0.05,
        cfe=400,
        expert_comptable=1200,
        rent_tax_regime='reel-bic',
        monthly_rent=800,
    )
    expenses_0 = monthly_expenses(
        taxe_fonciere=1200,
        charges=100,
        price=200000,
        travaux_pct=0.005,
        gestion_pct=0.05,
        cfe=400,
        expert_comptable=0,
        rent_tax_regime='reel-bic',
        monthly_rent=800,
    )

    diff = expenses_1200 - expenses_0
    expected = 1200 / 12  # 100€/mois
    assert abs(diff - expected) < 0.01, (
        f"Avec expert_comptable=1200€, la différence devrait être {expected}€/mois, "
        f"mais elle est de {diff}€/mois"
    )


def test_expert_comptable_absent_from_micro_foncier():
    """Le micro-foncier ne doit jamais inclure l'expert-comptable."""
    expenses = monthly_expenses(
        taxe_fonciere=1200,
        charges=100,
        price=200000,
        travaux_pct=0.005,
        gestion_pct=0.05,
        cfe=400,
        expert_comptable=9999,  # Valeur absurde
        rent_tax_regime='micro-foncier',
        monthly_rent=800,
    )
    # En micro-foncier, la CFE ne s'applique pas non plus (is_lmnp=False)
    # et l'expert-comptable non plus
    expenses_no_cfe = monthly_expenses(
        taxe_fonciere=1200,
        charges=100,
        price=200000,
        travaux_pct=0.005,
        gestion_pct=0.05,
        cfe=0,
        expert_comptable=0,
        rent_tax_regime='micro-foncier',
        monthly_rent=800,
    )
    assert abs(expenses - expenses_no_cfe) < 0.01, (
        f"En micro-foncier, ni la CFE ni l'expert-comptable ne devraient s'appliquer."
    )


def test_monthly_cost_simplified():
    """Test de la formule monthlyCosts simplifiée dans simulate()."""
    taxe_fonciere = 1200
    charges = 100
    price = 200000
    travaux_pct = 0.005
    expert_comptable = 800

    # Sans expert-comptable (micro-bic, reel-foncier, micro-foncier)
    monthly_no_expert = (taxe_fonciere + charges * 12 + price * travaux_pct + 300) / 12
    # Avec expert-comptable (reel-bic)
    monthly_with_expert = (taxe_fonciere + charges * 12 + price * travaux_pct + 300 + expert_comptable) / 12

    diff = monthly_with_expert - monthly_no_expert
    expected = 800 / 12
    assert abs(diff - expected) < 0.01, (
        f"La différence de monthlyCosts devrait être {expected}, pas {diff}"
    )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
