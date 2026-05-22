# 10 - Permissions, Securite et Audit

## Roles

| Role | Description |
| --- | --- |
| Admin | Permissions completes. |
| Direction | Consultation et validation selon perimetre. |
| Comptable | Operations comptables. |
| Caisse | Cloture caisse et differences. |
| RH | Employes, presence, contrats, salaires. |
| Viewer | Lecture seule. |

## Matrice simplifiee

| Ecran | Admin | Direction | Comptable | Caisse | RH | Viewer |
| --- | --- | --- | --- | --- | --- | --- |
| Dashboard | Complet | Lecture | Lecture | Limite | Limite | Lecture |
| Cloture Caisse | Complet | Lecture | Complet | Saisie | Non | Lecture |
| Caisse & Coffre | Complet | Lecture | Complet | Limite | Non | Lecture |
| Fournisseurs | Complet | Lecture | Complet | Non | Non | Lecture |
| Presence | Complet | Lecture | Lecture | Non | Complet | Lecture |
| Salaires | Complet | Lecture | Revision | Non | Complet | Limite |
| Etats | Complet | Complet | Complet | Limite | Limite | Lecture |
| DRH | Complet | Lecture | Non | Non | Complet | Limite |
| Administration | Complet | Non | Non | Non | Non | Non |

## Audit Log

Operations tracees:

- Creation, modification, annulation financiere.
- Modification de montant.
- Validation salaire.
- Cloture mois.
- Reouverture mois cloture.
- Modification employe ou contrat.
- Changement permissions.

Champs:

- user_id.
- action.
- entity_type.
- entity_id.
- old_values.
- new_values.
- reason.
- created_at.

## Mois cloture

- Lecture seule par defaut.
- Impression et export autorises.
- Modification exceptionnelle avec role Admin.
- Raison obligatoire.
- Recalcul du bilan apres correction.
