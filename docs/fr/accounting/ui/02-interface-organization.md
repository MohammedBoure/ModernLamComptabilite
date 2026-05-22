# 02 - Organisation des Elements d'Interface

Cette documentation decrit l'organisation fonctionnelle des ecrans. Elle ne fixe pas le design graphique final.

## Structure generale

Chaque ecran contient des zones stables:

| Zone | Emplacement | Contenu |
| --- | --- | --- |
| Barre superieure | Haut de l'ecran | Nom du logiciel, mois, annee, statut du mois, utilisateur courant. |
| Menu lateral | Cote de l'ecran | Dashboard, Caisse, Coffre, Fournisseurs, Etats, DRH. |
| Barre de filtres | Haut du contenu | Mois, annee, statut, recherche, type de rapport. |
| Zone de travail | Centre | Tableau principal ou formulaire. |
| Barre d'actions | Haut ou bas de la zone | Nouveau, Enregistrer, Imprimer, Exporter, Historique. |
| Zone de totaux | Bas des tableaux | Total, Reste, Difference, Profitabilite selon l'ecran. |

## Barre superieure

Contenu:

- Nom ModernLam ou nom du logiciel.
- Mois et annee selectionnes.
- Statut: Ouvert, En revision, Cloture.
- Utilisateur courant.
- Deconnexion.

Objectif:

- Identifier la periode courante.
- Eviter la confusion entre les mois.
- Afficher si le mois est modifiable ou cloture.

## Menu lateral

| Element | Ecran |
| --- | --- |
| Dashboard | Synthese du mois et alertes. |
| Cloture Caisse | Depenses caisse et differences. |
| Caisse & Coffre | Mouvements de caisse et coffre. |
| Fournisseurs | Fournisseurs, paiements et restes. |
| Sous-Traitants | Sous-traitants et conventions. |
| Presence | Presence mensuelle. |
| Salaires | Rapport de salaire. |
| Etats | Rapports et impression. |
| DRH | Employes, contrats et conges. |

## Barre de filtres

Elements courants:

- Mois.
- Annee.
- Statut.
- Recherche.
- Categorie.
- Fournisseur ou employe selon le contexte.

Regles:

- Les ecrans financiers et administratifs affichent toujours la periode.
- Les filtres changent l'affichage, pas les donnees.
- Le changement de periode recharge les donnees.

## Tableaux

Chaque tableau financier ou administratif contient:

- Entete de colonnes.
- Lignes de donnees.
- Colonne remarques si necessaire.
- Ligne de total si montants.
- Statut si necessaire: Paye, Partiel, Impaye, Brouillon, Valide.

Regles:

- Les montants sont dans des colonnes separees.
- Reste est affiche pres du montant paye.
- Les differences sont visibles dans l'ecran Differences.
- Les mois clotures sont affiches en lecture seule.

## Formulaires

Un formulaire est utilise pour ajouter ou modifier un enregistrement.

Elements:

- Champs de saisie.
- Remarques.
- Pieces jointes si necessaire.
- Boutons Enregistrer et Annuler.
- Message de controle en cas de champ obligatoire manquant.

Exemples:

- Ajouter depense caisse.
- Ajouter fournisseur.
- Ajouter paiement.
- Ajouter employe.
- Ajouter contrat.

## Barre d'actions

| Bouton | Fonction |
| --- | --- |
| Nouveau | Creer un enregistrement. |
| Enregistrer | Sauvegarder les modifications. |
| Annuler | Annuler la saisie. |
| Supprimer | Supprimer ou annuler selon autorisation. |
| Imprimer | Imprimer l'ecran ou le rapport. |
| Exporter PDF | Export PDF. |
| Exporter Excel | Export Excel. |
| Historique | Afficher les modifications. |

## Dashboard

| Zone | Contenu |
| --- | --- |
| Cartes de synthese | Caisse, Coffre, Chiffre d'Affaire, Profitabilite. |
| Alertes | Differences, restes, salaires non valides, mois non cloture. |
| Raccourcis | Cloture Caisse, Fournisseurs, Presence, Etats. |
| Synthese du mois | Statut du mois et derniere mise a jour. |

## Cloture Caisse

Zones:

1. Filtre mois/annee.
2. Tab Depenses Caisse.
3. Tab Differences.
4. Tab Etat Differences.
5. Totaux des depenses et differences.

## Caisse & Coffre

Zones:

1. Tableau Mouvement Caisse.
2. Tableau Entrees Supplementaires.
3. Tableau Sorties Coffre.
4. Tableau Mouvement Profitabilite.
5. Resume Coffre Net Reel et Chiffre d'Affaire.

## Fournisseurs

Zones:

1. Liste des fournisseurs ou categories.
2. Tableau operations/factures.
3. Tableau paiements.
4. Resume Total, Payer, Reste.
5. Details fournisseur.

## Presence

Zones:

1. Mois et annee.
2. Tableau des employes.
3. Colonnes des jours.
4. Codes de presence.
5. Totaux employe ou mois.

## Salaires

Zones:

1. Mois et annee.
2. Tableau employes/salaires.
3. Colonnes ajouts.
4. Colonnes retenues.
5. Salaire Final.
6. Statut: Brouillon, Valide, Paye.

## Etats

Zones:

1. Type de rapport.
2. Periode.
3. Apercu.
4. Actions PDF, Excel, Imprimer.
5. Historique des versions officielles si necessaire.

## DRH

Zones:

1. Liste employes.
2. Fiche Employe.
3. Tabs: Identite, Contrat, Conges, Presence, Salaires, Documents.
4. Alertes contrats et conges.

## Etats de l'interface

| Etat | Comportement |
| --- | --- |
| Loading | Indicateur de chargement. |
| Empty | Message d'absence de donnees. |
| Read-only | Boutons de modification desactives pour mois cloture. |
| Error | Message clair sans termes techniques. |
| Saved | Confirmation de sauvegarde. |

## Impression et apercu

Avant impression:

- Apercu du rapport.
- Titre et periode.
- Totaux.
- Type: Draft ou Officiel.

Apres validation officielle:

- Enregistrement de l'export ou impression dans l'historique.
