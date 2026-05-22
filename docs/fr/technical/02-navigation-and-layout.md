# 02 - Navigation et Structure des Ecrans

## Structure generale

Chaque ecran contient:

- Barre superieure: laboratoire, periode, statut, utilisateur.
- Menu lateral: modules principaux.
- Zone de contenu: tableau, formulaire ou rapport.
- Barre d'actions: nouveau, enregistrer, imprimer, exporter, historique.

## Menu lateral

| Entree | Destination |
| --- | --- |
| Tableau de Bord | Synthese mensuelle. |
| Cloture Caisse | Depenses caisse et differences. |
| Caisse & Coffre | Mouvements de caisse et coffre. |
| Fournisseurs | Fournisseurs, factures, paiements. |
| Sous-Traitants | Sous-traitants et conventions. |
| Presence | Presence mensuelle. |
| Salaires | Rapport de salaire. |
| Etats | Rapports et impressions. |
| DRH | Employes, contrats, conges. |
| Administration | Utilisateurs, permissions, audit. |

## Periode

Champs:

- Mois.
- Annee.
- Statut: Ouvert, En revision, Cloture.

Regles:

- Le mois courant s'affiche par defaut.
- Un mois cloture est en lecture seule.
- Les rapports annuels peuvent utiliser l'annee seule.

## Actions communes

| Action | Fonction |
| --- | --- |
| Nouveau | Creer un enregistrement. |
| Enregistrer | Sauvegarder. |
| Annuler | Annuler la saisie. |
| Supprimer | Supprimer ou annuler selon droit. |
| Imprimer | Impression. |
| Exporter Excel | Export Excel. |
| Exporter PDF | Export PDF. |
| Historique | Audit de l'element. |

## Etats des enregistrements

| Statut | Signification |
| --- | --- |
| Brouillon | Non valide. |
| Valide | Valide et comptabilise. |
| Paye | Regle integralement. |
| Partiel | Regle partiellement. |
| Impaye | Non regle. |
| Annule | Annule et exclu des calculs. |
