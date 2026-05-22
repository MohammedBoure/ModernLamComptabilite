# 03 - Tableau de Bord

## Objectif

Le Dashboard donne une vue rapide du mois: caisse, coffre, chiffre d'affaires, profitabilite, restes et alertes.

## Composants

### Periode

| Champ | Description |
| --- | --- |
| Mois | Mois affiche. |
| Annee | Annee affichee. |
| Statut | Ouvert, En revision, Cloture. |
| Derniere mise a jour | Dernier calcul. |

### Cartes de synthese

- Caisse CV.
- Caisse C.
- TPE.
- Depenses.
- Coffre Net Reel.
- Chiffre d'Affaires Global.
- Profitabilite.
- Profitabilite Net.

### Alertes

- Difference caisse non justifiee.
- Fournisseur avec reste.
- Sous-traitant ou convention non solde.
- Salaire non valide.
- Employe sans contrat actif.
- Cheque incomplet.

## Regles

- Les valeurs sont calculees depuis les ecrans sources.
- Une carte ouvre son detail source.
- Les erreurs de type division par zero sont affichees comme non disponibles.
- Un mois cloture affiche des donnees en lecture seule.
