# 01 - Vue Generale Fonctionnelle

## Objectif

ModernLam Comptabilite est un systeme interne destine a organiser la comptabilite et la gestion du laboratoire ModernLam. Le logiciel transforme les tableaux manuels actuels en ecrans, workflows et rapports structures.

## Public concerne

| Public | Besoin principal |
| --- | --- |
| Comptabilite | Saisie de la caisse, du coffre, des fournisseurs, des paiements et du bilan mensuel. |
| Direction | Suivi du chiffre d'affaires, des depenses, de la profitabilite et des restes a payer. |
| Ressources humaines | Suivi des employes, contrats, presences, conges et salaires. |
| Caisse | Saisie de la cloture de caisse et des differences quotidiennes. |

## Modules principaux

| Module | Role |
| --- | --- |
| Dashboard | Synthese du mois et alertes principales. |
| Cloture Caisse | Depenses caisse et differences entre montant reel et SOFTLAM. |
| Caisse & Coffre | Mouvements de caisse, coffre, entrees et sorties. |
| Fournisseurs | Factures, paiements et restes fournisseurs. |
| Sous-Traitants & Conventions | Suivi des partenaires externes et conventions. |
| Presence & Salaires | Presence, absences, gardes et salaires. |
| Etats | Rapports, impression et export. |
| DRH | Employes, contrats et conges. |

## Fonctionnement mensuel

Toutes les operations sont rattachees a un mois et a une annee. Le mois est ouvert, les operations sont saisies, les resultats sont verifies, puis le mois est cloture apres validation.

| Statut | Signification |
| --- | --- |
| Ouvert | Les donnees peuvent etre saisies. |
| En revision | Les donnees sont en verification avant cloture. |
| Cloture | Le mois est ferme et devient modifiable uniquement avec autorisation. |

## Resultats attendus

- Total mensuel de la caisse.
- Total du coffre et coffre net reel.
- Differences entre Montant Reel et Montant Virtuelle.
- Restes fournisseurs, sous-traitants et conventions.
- Bilan mensuel.
- Profitabilite et profitabilite apres investissements.
- Rapports de presence et salaires.
- Etat d'Encaissement imprimable.
- Etat Cheques et Suivi Vehicule de Service.
