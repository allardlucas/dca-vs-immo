# Développement

Guide pour contribuer au simulateur DCA vs Immobilier.

## Prérequis

- Un navigateur récent (Chrome, Firefox, Safari, Edge)
- Python 3.10+ pour les tests de non-régression

## Lancer l'application en local

```bash
# Option 1 : ouvrir directement le fichier
open index.html   # macOS
xdg-open index.html   # Linux

# Option 2 : serveur HTTP local (recommandé pour éviter les restrictions CORS)
python -m http.server 8000
# → http://localhost:8000
```

Aucune installation de dépendances n'est nécessaire pour l'application elle-même.

## Tests

Les tests Python reproduisent la logique fiscale du simulateur (extrait de `index.html`) pour valider les correctifs sur des cas concrets.

```bash
pip install -r requirements.txt

# Tests pytest
pytest tests/ -v

# Scripts de non-régression (sortie détaillée cas par cas)
python tests/test_issue_4_lmnp_pv.py
python tests/test_issue_5_lmnp_monthly_tax.py
python tests/test_issue_6_surtaxe_pv.py
python tests/test_issue_16_deficit_foncier.py
```

### Couverture des tests

| Fichier | Sujet |
|---------|-------|
| `test_expert_comptable.py` | Charge expert-comptable (800 €/an) en LMNP réel uniquement |
| `test_issue_4_lmnp_pv.py` | Amortissement LMNP non déduit de la base de plus-value |
| `test_issue_5_lmnp_monthly_tax.py` | Estimation mensuelle d'impôt tenant compte de l'amortissement |
| `test_issue_6_surtaxe_pv.py` | Surtaxe progressive sur PV > 50 000 € |
| `test_issue_16_deficit_foncier.py` | Séparation déficit travaux / intérêts (plafond 10 700 €) |
| `test_issue_7_monte_carlo.py` | Monte Carlo DCA GBM engine (issue #7) |

## Modifier le simulateur

1. Éditer `index.html` (paramètres UI, fonction `runSimulation()`, fiscalité…).
2. Ajouter ou mettre à jour un test de non-régression si le changement touche la fiscalité.
3. Ouvrir `index.html` dans le navigateur et vérifier les graphiques et le récapitulatif.
4. Lancer `pytest tests/ -v` et les scripts de non-régression.

## Déploiement

- **Production** — merge sur `main` → workflow [deploy.yml](../.github/workflows/deploy.yml) → [GitHub Pages](https://allardlucas.github.io/dca-vs-immo/)
- **Preview PR** — chaque pull request obtient une URL de preview commentée automatiquement

## Structure du dépôt

```
dca-vs-immo/
├── index.html              # Application complète (HTML + CSS + JS)
├── README.md               # Présentation et guide utilisateur
├── requirements.txt        # Dépendances Python (tests uniquement)
├── docs/
│   ├── architecture.md       # Diagramme et flux de calcul
│   ├── development.md        # Ce fichier
│   ├── diagram.excalidraw  # Source du diagramme d'architecture
│   └── images/
│       └── architecture.svg
├── tests/                  # Tests de non-régression fiscale
└── .github/workflows/      # CI : tests, déploiement, previews PR
```
