# 01 - Vision Generale du Produit

## Objectif

ModernLam Comptabilite est une application interne pour organiser la comptabilite, les etats, les salaires et les donnees RH du laboratoire. Elle remplace des tableaux separes par un systeme coherent.

## Utilisateurs

| Role | Responsabilite |
| --- | --- |
| Administrateur | Utilisateurs, permissions, periodes, audit. |
| Direction | Consultation du bilan, profitabilite, alertes. |
| Comptable | Caisse, coffre, fournisseurs, paiements, etats. |
| Caisse | Saisie cloture caisse et differences. |
| RH | Employes, contrats, presence, conges, salaires. |
| Viewer | Lecture seule selon autorisation. |

## Perimetre initial

Inclus:

- Gestion des periodes mensuelles.
- Caisse et coffre.
- Fournisseurs, sous-traitants, conventions.
- Presence, salaires et DRH.
- Etats, PDF et Excel.
- Audit log des modifications importantes.

Exclus au depart:

- Connexion bancaire directe.
- Integration SOFTLAM automatique sans format defini.
- Comptabilite fiscale complete hors Etat d'Encaissement.
- Gestion de stock laboratoire detaillee.

## Modules

| Module | Role |
| --- | --- |
| Dashboard | Synthese et alertes. |
| Comptabilite | Caisse, coffre, depenses, profitabilite. |
| Fournisseurs | Factures, paiements, restes. |
| Sous-Traitants & Conventions | Partenaires et conventions. |
| Presence & Salaires | Presence, gardes, absences, salaires. |
| Etats | Rapports, impression, export. |
| DRH | Employes, contrats, conges. |
| Administration | Permissions, parametres, audit. |

## Principe

Le systeme fonctionne par mois. Les operations sont rattachees a une periode. Un mois cloture devient en lecture seule, sauf modification exceptionnelle avec trace d'audit.
