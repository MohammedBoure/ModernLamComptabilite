# 05 - Interfaces Etats et Rapports

## Principes

Chaque etat doit permettre:

- Choix de la periode.
- Recherche et filtres.
- Impression.
- Export PDF.
- Export Excel.
- Date de generation et utilisateur.

## 05.1 Etat Fournisseurs

Sections:

- Total Fournisseurs.
- Total Equipements.
- Total Consommables.
- Fournisseurs detailles.

Colonnes:

- Fournisseur.
- Montant.
- Versement.
- Reste.
- Observation.

## 05.2 Etat Sous-Traitants

Sections:

- Tous.
- Sous-Traitants.
- Conventions.
- Details par partenaire.

Colonnes:

- ID.
- Nom.
- Montant.
- Versement.
- Reste.
- Date.
- Paiement.
- Observation.

## 05.3 Suivi Vehicule de Service

Colonnes:

- Date.
- Montant.
- Details.
- Kilometrage.
- GPL / Kilometre en +.
- Essence / Kilometre en +.

Calculs:

- Total montant.
- Total GPL.
- Total Essence.
- Moyenne KM/Plein.

## 05.4 Suivi Compte SGA / Etat de Cheques

Champs superieurs:

- Montant du Compte le 31/12/annee precedente.
- Montant du Compte a la date courante.
- Annee.

Colonnes:

- Numero.
- La Date.
- Beneficiaire.
- Numero Cheque.
- Montant.
- Entrees.
- Sorties.
- Designation.
- Mois.

## 05.5 Etat d'Encaissement

Entete:

- Logo ModernLam.
- Nom du laboratoire.
- NIF.
- RIP.
- Date d'impression.
- Mois de l'etat.

Colonnes:

- Numero.
- Date.
- Designation.
- Observations.
- Montants.

Bas du rapport:

- Total.
- Cachet et signature.

## Exports

- PDF officiel.
- Excel.
- CSV optionnel.
