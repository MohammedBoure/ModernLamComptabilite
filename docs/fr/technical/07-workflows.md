# 07 - Workflows Fonctionnels

## Nouveau mois

Entrees:

- Mois.
- Annee.
- Utilisateur responsable.

Traitement:

1. Selection de la periode.
2. Creation si inexistante.
3. Chargement des employes actifs et fournisseurs.
4. Statut `Ouvert`.

Sorties:

- Periode ouverte.
- Saisie active pour caisse, coffre, presence, fournisseurs.

## Caisse quotidienne

Entrees:

- Date.
- Depenses caisse.
- Montant Reel.
- Montant Virtuelle.
- Remarque si ecart.

Traitement:

1. Enregistrement des depenses.
2. Saisie des montants.
3. Calcul Difference.
4. Remarque obligatoire si difference.

Sorties:

- Cloture caisse.
- Etat Differences mis a jour.
- Alertes Dashboard.

## Fournisseurs

Entrees:

- Fournisseur.
- Facture ou commande.
- Montant.
- Versement.
- Mode paiement.

Traitement:

1. Rattachement au fournisseur.
2. Enregistrement du montant.
3. Enregistrement des paiements.
4. Calcul reste.
5. Statut Impaye, Partiel ou Paye.

## Presence et salaires

Traitement:

1. Saisie des codes presence.
2. Calcul des totaux.
3. Generation Rapport de Salaire.
4. Ajout primes, penalites, avances.
5. Calcul salaire final.
6. Validation puis paiement.

## Cloture du mois

Conditions:

- Differences justifiees.
- Rapports generes.
- Salaires non Brouillon.
- Restes visibles.
- Bilan calcule.

Traitement:

1. Checklist de cloture.
2. Verification automatique.
3. Validation par role autorise.
4. Passage a `Cloture`.
5. Blocage des modifications ordinaires.

## Modification d'un mois cloture

- Demande de modification exceptionnelle.
- Motif obligatoire.
- Validation administrateur.
- Modification limitee.
- Audit log obligatoire.
- Recalcul du bilan.
- Nouvelle cloture.
