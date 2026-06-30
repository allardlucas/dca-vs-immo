# Architecture

Diagramme d'architecture du simulateur DCA vs Immobilier.

![Diagramme d'architecture](images/architecture.svg)

[Ouvrir le diagramme interactif sur Excalidraw](https://excalidraw.com/#json=EIUrCV7Qj7VyRqk691wfk,8WiZm2bQ2vXWG9NbJNeflg) · [Fichier source local](diagram.excalidraw)

## Légende des blocs

| Couleur | Rôle |
|---------|------|
| Bleu | Paramètres d'entrée — DCA financier |
| Orange | Paramètres d'entrée — Immobilier locatif |
| Violet | Cœur de la simulation (boucle mois par mois) |
| Vert | Résultats et visualisations |
| Rouge | Analyse de sensibilité (seuils de rentabilité) |
| Jaune | Correctifs fiscaux et points d'attention |

## Flux de calcul

1. **Entrées** — L'utilisateur règle les paramètres DCA et immobilier (prix, crédit, loyers, fiscalité…).
2. **Simulation mensuelle** — Chaque mois, le même effort d'épargne alimente le DCA (cash-flow négatif immo) et le crédit immobilier (capital + intérêts, loyers, charges).
3. **Fiscalité annuelle** — En fin d'année civile : impôt sur les loyers (4 régimes), déficits reportables, amortissement LMNP.
4. **Clôture** — Calcul de la plus-value immobilière (barème dual IR/PS, surtaxe progressive > 50 k€), comparaison du patrimoine net DCA vs Immo.
5. **Affichage** — Graphiques, tableau annuel, seuils de rentabilité par dichotomie.

## Fichier source

Toute la logique est contenue dans [`index.html`](../index.html) à la racine du dépôt : HTML, CSS et JavaScript vanilla, sans build ni dépendance externe.
