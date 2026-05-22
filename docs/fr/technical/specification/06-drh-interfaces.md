# 06 - Interfaces DRH

## Liste Employes

Colonnes:

- Numero.
- Nom/Prenom.
- Fonction.
- Date Naissance.
- Age.
- Telephone 01.
- Telephone 02.
- Statut.
- Contrat actif.
- Conge annee.

Filtres:

- Fonction.
- Statut.
- Contrat.
- Recherche par nom.

## Fiche Employe

Tabs:

| Tab | Contenu |
| --- | --- |
| Identite | Donnees personnelles. |
| Contrat | Embauche, CNAS, contrat. |
| Conges | Solde annuel. |
| Presence | Presence par mois. |
| Salaires | Historique salaires. |
| Documents | Pieces jointes. |
| Historique | Modifications. |

## Identite

Champs:

- Nom/Prenom.
- Fonction.
- Date Naissance.
- Age calcule.
- Lieu de Naissance.
- Adresse.
- Telephone 01.
- Telephone 02.
- Numero SS.
- Numero ANEM.

## Contrat

Champs:

- Date d'Embauche.
- Date d'Inscription CNAS.
- Contrat.
- Du.
- Au.
- Demission.
- Statut contrat.
- Remarque.

Regles:

- `Au` ne peut pas etre avant `Du`.
- Un seul contrat actif par employe.
- Demission rend l'employe inactif a partir de la date indiquee.

## Conges

Champs:

- Annee.
- Employe.
- Fonction.
- Date d'Embauche.
- Jours acquis.
- Jours pris.
- Reste.

Regle de base:

```text
Jours de Conge = Jours de conge + 2.5 par mois de travail
```
