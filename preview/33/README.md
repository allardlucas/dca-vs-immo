# DCA vs Immobilier

Comparateur interactif : **investissement financier en DCA** versus **investissement locatif immobilier**.

**[Ouvrir l'outil en ligne](https://allardlucas.github.io/dca-vs-immo/)** — aucune installation requise.

## Principe

Chaque mois, le même **effort d'épargne** est investi dans les deux approches :

- **DCA** — le cash-flow négatif de l'immo est placé en bourse (capitalisation mensuelle)
- **Immo** — crédit amortissable, loyers indexés, charges complètes, fiscalité réelle

À la fin de la simulation, on compare le patrimoine net (après impôt) des deux stratégies.

## Paramètres

### DCA financier

- Apport initial (partagé avec l'immo)
- Croissance annuelle (rendement boursier espéré)
- Durée de simulation
- Fiscalité : Flat tax 31,4 % / PEA (PS 18,6 %) / TMI + PS

### Immobilier locatif

- Prix d'achat, apport, frais de notaire (payés sur l'apport)
- Taux et durée du crédit
- Loyer (fixe ou rendement brut), croissance des loyers et du prix
- Taxe foncière, charges copro, travaux, vacance locative, frais de gestion
- **CFE** en régime LMNP
- **Expert-comptable** (800 €/an par défaut) en LMNP au réel uniquement
- **4 régimes fiscaux** : Micro-foncier, Réel (nu), Micro-BIC, **Réel LMNP** (amortissement bâtiment 80 %/25 ans + mobilier 10 %/7 ans)

## Résultats

- Patrimoine net final (DCA vs Immo) après impôt
- Rendement annualisé, cash-flow mensuel et cash-flow moyen
- **4 graphiques** : avant impôt, après impôt, capital vs immo hors PV, effort d'épargne
- **Tableau année par année** : effort annuel, capital investi, valeur nette, écart, gagnant
- **Seuils de rentabilité** : rendement locatif et croissance DCA à partir desquels l'immo devient gagnante (ou l'inverse)

## Utilisation

### En ligne

Rendez-vous sur [allardlucas.github.io/dca-vs-immo](https://allardlucas.github.io/dca-vs-immo/), ajustez les curseurs — tout se recalcule en temps réel — puis cliquez sur **Copier le résumé** pour partager les chiffres.

### En local

1. Clonez le dépôt ou téléchargez [`index.html`](index.html)
2. Ouvrez-le dans votre navigateur, ou servez-le avec `python -m http.server`
3. Aucune dépendance : un seul fichier HTML, CSS et JavaScript vanilla

Voir [docs/development.md](docs/development.md) pour le guide développeur et les tests.

## Architecture

Voir [docs/architecture.md](docs/architecture.md) pour le diagramme détaillé et le flux de calcul.

## Notes fiscales

- Les frais de notaire sont payés sur l'apport (pas financés par le crédit)
- En LMNP réel, l'amortissement est une charge comptable (non décaissée) : il réduit l'impôt annuel mais pas le cash-flow mensuel
- L'amortissement LMNP **n'est pas déduit** de la base de plus-value immobilière
- Plus-value immobilière : barème dual IR/PS (art. 150 VC CGI) + surtaxe progressive au-delà de 50 000 €
- Déficit foncier : imputation sur le revenu global plafonnée à 10 700 €/an pour les travaux ; intérêts reportables 10 ans sur revenus fonciers
- Le DCA cesse après la fin du crédit (le capital continue de croître seul)

## Licence

Projet open source — utilisez et adaptez librement.
