# 04 - Interfaces Comptabilite

## 04.1 Cloture de Caisse

Objectif: enregistrer les depenses caisse et calculer la difference entre Montant Reel et Montant Virtuelle.

Tabs:

| Tab | Contenu |
| --- | --- |
| Depenses Caisse | Date, designation, montant, remarque. |
| Differences | Date, utilisateur, Montant Reel, Montant Virtuelle, Difference, Net, Remarques. |
| Etat Differences | Synthese des differences par utilisateur. |

Regles:

```text
Difference = Montant Reel - Montant Virtuelle
Net = Somme(Difference)
```

Remarque obligatoire si Difference non nulle.

## 04.2 Caisse & Coffre

### Mouvement Caisse

Colonnes:

- Date.
- Caisse CV.
- Caisse C.
- TPE.
- Depenses.
- Remboursement.
- Convention.
- Sous-Traitants.
- Total.

Lignes de calcul:

- Total.
- Min (-Ven).
- Max (-Ven).
- Moyenne (-Ven).

### Entrees Supplementaires

Colonnes:

- Date.
- Montant.
- Detail.
- Statut paiement.
- Remarque.

### Sorties Coffre

Colonnes:

- Date.
- Designation.
- Montant.
- Categorie.
- Piece jointe.
- Remarque.

### Resume Coffre

- Coffre Net Reel.
- Chiffre d'affaire LAM.
- Chiffre d'affaire Convention.
- Chiffre d'affaire ST.
- Chiffre d'affaire Entrees Supplementaires.
- Chiffre d'Affaire Globale.

## 04.3 Bilan Mensuel

Sections:

| Section | Champs |
| --- | --- |
| Resultat du mois | Caisse CV, Caisse C, Convention, Sous-Traitance, Entrees Supplementaires. |
| Prelevements | Total Prelev CV, Total Prelev C, Total Prelev S/T, Total Prelev. |
| Rentabilite | Chiffre d'Affaire, Depenses, Profitabilite. |
| Investissements | Investissements, Profitabilite Net. |

L'ecran est principalement en lecture calculee.

## 04.4 Fournisseurs

Categories:

- Reactifs & Consommables.
- Sous-Traitances.
- Impots.
- Informatique & Bureautique.
- Vehicule de Service.
- Location.
- Energie Labo.
- Depenses Internes.
- Salaires.
- Transport Sous-Traitants.
- Autres Depenses.
- Investissement.

Colonnes:

- Numero.
- Categorie.
- Fournisseur LAM.
- Total des Commandes.
- Payer.
- Reste.
- Date.
- Observation.

```text
Reste = Total des Commandes - Payer
```

## 04.5 Sous-Traitants & Conventions

Colonnes:

- Nom.
- Montant.
- Versement.
- Date de Reception.
- Mode Paiement.
- Reste.
- Remarques.

```text
Reste = Montant - Versement
```

## 04.6 Presence

Codes:

| Code | Signification |
| --- | --- |
| P | Present. |
| G | Garde Nuit. |
| ABS | Absence. |
| REC | Recuperation. |
| GV-J | Garde Vendredi Jour. |
| GV-N | Garde Vendredi Nuit. |
| P+ | Presence supplementaire / HS. |
| C.M | Conge Maladie. |
| C | Conge. |

## 04.7 Rapport de Salaire

Colonnes:

- Personne.
- Poste.
- Salaire Net.
- Presence en + / HS.
- Deplacement LAM.
- Garde Nuit.
- Garde Vendredi Jour.
- Garde Vendredi Nuit.
- Absence.
- Prime.
- Conge.
- Penalites.
- Avances.
- Salaire.
- Remarque.
