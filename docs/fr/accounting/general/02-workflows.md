# 02 - Workflows Fonctionnels

## Ouverture d'un nouveau mois

| Etape | Description |
| --- | --- |
| Selection de la periode | Choix du mois et de l'annee. |
| Creation de la periode | Creation du mois si la periode n'existe pas. |
| Chargement des listes | Affichage des employes actifs, fournisseurs et partenaires connus. |
| Statut du mois | Le mois commence avec le statut `Ouvert`. |

## Travail quotidien de caisse

| Etape | Description |
| --- | --- |
| Saisie des depenses | Saisie de la date, designation et montant. |
| Saisie du montant reel | Enregistrement du montant physiquement present. |
| Saisie du montant SOFTLAM | Enregistrement du Montant Virtuelle provenant de SOFTLAM. |
| Calcul de la difference | Calcul automatique de Difference. |
| Justification | Remarque obligatoire en cas de difference. |

```text
Difference = Montant Reel - Montant Virtuelle
```

## Suivi caisse et coffre

| Etape | Description |
| --- | --- |
| Saisie du mouvement journalier | Caisse CV, Caisse C, TPE, depenses, remboursement, convention, sous-traitants. |
| Calcul du total jour | Calcul automatique du total quotidien. |
| Mise a jour mensuelle | Mise a jour des total, min, max, moyenne. |
| Mise a jour coffre | Impact des entrees et sorties sur le Coffre Net Reel. |

## Suivi fournisseurs

| Etape | Description |
| --- | --- |
| Enregistrement du fournisseur | Selection ou creation du fournisseur. |
| Enregistrement facture/commande | Saisie de la categorie, du montant et des details. |
| Enregistrement paiement | Saisie du versement et du mode de paiement. |
| Calcul du reste | Calcul automatique du reste a payer. |
| Statut | Paye, Partiel ou Impaye. |

```text
Reste = Montant - Versement
```

## Suivi sous-traitants et conventions

| Etape | Description |
| --- | --- |
| Saisie de l'operation | Identification du sous-traitant ou de la convention. |
| Saisie du montant | Montant du dossier ou de l'operation. |
| Saisie des versements | Versement et mode de paiement. |
| Calcul du reste | Calcul automatique du reste. |
| Rapport | Apparition dans Etat Sous-Traitants ou Convention. |

## Presence

| Etape | Description |
| --- | --- |
| Selection du mois | Affichage des jours et des employes actifs. |
| Saisie des codes | Utilisation des codes P, ABS, G, GV-J, GV-N, C, C.M, REC, P+. |
| Calcul des totaux | Total presence, absence, conges et gardes. |
| Lien salaires | Les totaux alimentent le Rapport de Salaire. |

## Salaires

| Etape | Description |
| --- | --- |
| Recuperation presence | Lecture des resultats mensuels de presence. |
| Valeurs manuelles | Primes, penalites et avances. |
| Calcul du salaire | Calcul du salaire final selon les regles validees. |
| Validation | Le rapport reste Brouillon avant validation. |
| Paiement | Apres paiement, le statut devient Paye. |

## Cloture du mois

Conditions:

- Pas de differences caisse non justifiees.
- Donnees fournisseurs et partenaires completes.
- Rapport de salaire finalise.
- Bilan mensuel calcule.
- Rapports principaux verifies.

Resultat:

- Le mois devient `Cloture`.
- Les modifications ordinaires sont bloquees.
- Les rapports restent disponibles pour impression et archivage.
