# 09 - Regles Metier et Calculs

## Caisse

```text
Difference = Montant Reel - Montant Virtuelle
Net = Somme(Difference)
```

Regles:

- Remarque obligatoire si Difference non nulle.
- Differences regroupees par utilisateur et par mois.
- Les differences ne deviennent pas automatiquement profit ou perte sans decision.

## Fournisseurs

```text
Reste = Total des Commandes - Payer
```

Statuts:

- Paye si Reste = 0.
- Partiel si Payer > 0 et Reste > 0.
- Impaye si Payer = 0.

## Sous-Traitants et Conventions

```text
Reste = Montant - Versement
```

Mode Paiement obligatoire si Versement existe.

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

## Chiffre d'Affaires

```text
Chiffre d'Affaires Global =
  Coffre Net Reel
  + Chiffre d'Affaires LAM
  + Chiffre d'Affaires Convention
  + Chiffre d'Affaires ST
  + Chiffre d'Affaires Entrees Supplementaires
```

Point a confirmer:

```text
Chiffre d'affaires LAM = Caisse C + Caisse C + Depenses
```

Cette formule contient une repetition apparente de `Caisse C`.

## Profitabilite

```text
Profitabilite = Chiffre d'Affaire - Depenses
Profitabilite Net = Profitabilite - Investissements
```

Les ratios ne sont pas affiches si Chiffre d'Affaire = 0.

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

La formule finale doit etre validee fonctionnellement.

## Conges

```text
Jours de Conge = Jours de conge + 2.5 par mois de travail
```

La regle liee au jour 15 doit etre confirmee avant implementation.

## Cloture du mois

Blocages:

- Differences non justifiees.
- Salaires Brouillon.
- Bilan non calcule.
- Operations financieres Brouillon.
