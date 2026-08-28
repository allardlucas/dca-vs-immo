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
python tests/test_issues_23_24_25_26.py
```

Les scripts standalone (issues 4, 5, 6, 16, 23–26) ne sont pas collectés comme tests pytest : ils exposent des helpers `test_*` et s'exécutent via `python tests/…`. La CI fait de même : `pytest tests/` (en les ignorant) puis chaque script.

### Couverture des tests

| Fichier | Sujet |
|---------|-------|
| `test_expert_comptable.py` | Charge expert-comptable (800 €/an) en LMNP réel uniquement |
| `test_issue_4_lmnp_pv.py` | Amortissement LMNP non déduit de la base de plus-value |
| `test_issue_5_lmnp_monthly_tax.py` | Estimation mensuelle d'impôt tenant compte de l'amortissement |
| `test_issue_6_surtaxe_pv.py` | Surtaxe progressive sur PV > 50 000 € |
| `test_issue_7_monte_carlo.py` | Monte Carlo DCA GBM engine (issue #7) |
| `test_issue_16_deficit_foncier.py` | Séparation déficit travaux / intérêts (plafond 10 700 €) |
| `test_issues_23_24_25_26.py` | Amortissement LMNP (base + notaire), GLI, frais de revente, indexation des charges |

## Modifier le simulateur

1. Éditer `index.html` (paramètres UI, fonction `runSimulation()`, fiscalité…).
2. Ajouter ou mettre à jour un test de non-régression si le changement touche la fiscalité.
3. Ouvrir `index.html` dans le navigateur et vérifier les graphiques et le récapitulatif.
4. Lancer `pytest tests/ -v` et les scripts de non-régression.

## Déploiement

- **Production** — un push (merge) sur `main` déclenche le workflow [tests.yml](../.github/workflows/tests.yml) : le job de tests exécute toute la suite (`pytest tests/` plus les scripts de non-régression). Le job de déploiement GitHub Pages (`peaceiris/actions-gh-pages`, `publish_dir: .`, mêmes `exclude_assets` / `keep_files`) ne s'exécute **que si ce job de tests a réussi** (`needs: test`). Un échec de tests bloque le déploiement prod ; il n'y a plus de déploiement parallèle indépendant. Site : [allardlucas.github.io/dca-vs-immo](https://allardlucas.github.io/dca-vs-immo/)
- **Preview PR** — inchangé : chaque pull request ciblant `main` obtient une URL de preview commentée automatiquement ([preview.yml](../.github/workflows/preview.yml)), indépendamment des tests. La preview est nettoyée à la fermeture de la PR.

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
