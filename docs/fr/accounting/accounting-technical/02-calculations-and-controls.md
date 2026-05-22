# 02 - Calculs et Controles Comptables

Cette documentation presente les calculs et controles visibles pour la comptabilite et la direction financiere.

## Cloture Caisse

```text
Difference = Montant Reel - Montant Virtuelle
```

| Cas | Signification | Traitement |
| --- | --- | --- |
| Difference = 0 | Aucun ecart | Operation conservee sans alerte. |
| Difference > 0 | Montant reel superieur a SOFTLAM | Valeur positive avec remarque. |
| Difference < 0 | Montant reel inferieur a SOFTLAM | Valeur negative avec remarque. |

Controles:

- Remarque obligatoire en cas de difference.
- Toute difference apparait dans Etat Differences.
- Les differences sont totalisees par utilisateur et par mois.

## Fournisseurs

```text
Reste = Total des Commandes - Payer
```

| Statut | Condition | Signification |
| --- | --- | --- |
| Impaye | Payer = 0 | Aucun paiement. |
| Partiel | Payer > 0 et Reste > 0 | Paiement partiel. |
| Paye | Reste = 0 | Paiement complet. |

Controles:

- Mode Paiement obligatoire en cas de paiement.
- Observation conservee en cas de precision.
- Le paiement partiel reste visible jusqu'au reglement du reste.

## Sous-Traitants et Conventions

```text
Reste = Montant - Versement
```

Controles:

- Date de Reception conservee.
- Mode Paiement obligatoire si versement existe.
- Reste visible dans l'etat correspondant.

## Coffre Net Reel

```text
Coffre Net Reel =
  Caisse CV
  + Caisse C
  + Entrees Supplementaires payees
  + Mouvement Profitabilite
  + Sous-Traitants payes
  + Convention payee
  - Sortie Coffre
```

Controles:

- Sorties Coffre diminue le coffre.
- Entrees Supplementaires est prise selon le statut de paiement.
- Chaque montant doit rester tracable vers son ecran source.

## Bilan Mensuel

| Indicateur | Signification |
| --- | --- |
| Chiffre d'Affaire | Revenus mensuels. |
| Depenses | Total des depenses. |
| Profitabilite | Resultat avant investissements. |
| Investissements | Investissements. |
| Profitabilite Net | Resultat apres investissements. |

```text
Profitabilite = Chiffre d'Affaire - Depenses
```

```text
Profitabilite Net = Profitabilite - Investissements
```

Controles:

- Les pourcentages ne sont pas affiches si le chiffre d'affaires est nul.
- Chaque montant du bilan doit avoir une source identifiable.

## Presence

| Code | Signification |
| --- | --- |
| P | Present. |
| ABS | Absence. |
| G | Garde Nuit. |
| GV-J | Garde Vendredi Jour. |
| GV-N | Garde Vendredi Nuit. |
| C | Conge. |
| C.M | Conge Maladie. |
| REC | Recuperation. |
| P+ | Presence en + / HS. |

Controles:

- Les codes non reconnus ne sont pas comptabilises.
- Chaque jour doit avoir un code clair ou rester vide selon la politique de saisie.

## Salaires

```text
Salaire Final =
  Salaire Net
  + Presence en + / HS
  + Deplacement LAM
  + Garde Nuit
  + Garde Vendredi Jour
  + Garde Vendredi Nuit
  + Prime
  - Absence
  - Penalites
  - Avances
```

Controles:

- Prime, penalites et avances peuvent etre accompagnees d'une remarque.
- Rapport de Salaire reste Brouillon avant validation.
- Apres validation, le statut devient Valide.
- Apres paiement, le statut devient Paye.

## Conges

```text
Jours de Conge = Jours de conge + 2.5 chaque mois de travail
```

Controles:

- Date d'Embauche est utilisee dans le calcul du solde.
- Jours Pris diminue Jours Acquis.
- Reste represente le solde disponible.

## Etat d'Encaissement

Controles:

- Une ligne est generee pour chaque jour du mois.
- La designation par defaut peut etre `DIVERS CLIENTS`.
- Le total mensuel apparait en bas du rapport.
- La version officielle contient cachet et signature.
