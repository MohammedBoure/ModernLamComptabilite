# 01 - Tableaux Fonctionnels et Donnees Conservees

Cette documentation decrit les tableaux visibles ou conserves dans le logiciel du point de vue comptable et administratif. Il ne s'agit pas du modele interne de base de donnees.

## Periode mensuelle

| Donnee | Description |
| --- | --- |
| Mois | Mois comptable concerne. |
| Annee | Annee de travail. |
| Statut du mois | Ouvert, En revision, Cloture. |
| Date d'ouverture | Date de creation de la periode. |
| Date de cloture | Date de cloture apres validation. |

Objectif: rattacher toutes les operations a un mois et une annee.

## Depenses Caisse

| Donnee | Description |
| --- | --- |
| Date | Date de la depense. |
| Designation | Motif ou description. |
| Montant | Montant de la depense. |
| Remarque | Information complementaire. |
| Piece | Document facultatif. |

Objectif: enregistrer les sorties de la caisse.

## Differences Caisse

| Donnee | Description |
| --- | --- |
| Date | Jour de comparaison. |
| Utilisateur | Personne associee a l'operation caisse. |
| Montant Reel | Montant physiquement present. |
| Montant Virtuelle | Montant SOFTLAM ou reference. |
| Difference | Ecart calcule. |
| Net | Total des differences selon periode ou utilisateur. |
| Remarques | Justification de l'ecart. |

Objectif: controler l'ecart entre la realite et SOFTLAM.

## Mouvement Caisse

| Donnee | Description |
| --- | --- |
| Date | Jour du mouvement. |
| Caisse CV | Montant Caisse CV. |
| Caisse C | Montant Caisse C. |
| TPE | Paiements electroniques. |
| Depenses | Depenses du jour. |
| Remboursement | Montants rembourses. |
| Convention | Montants conventions. |
| Sous-Traitants | Montants sous-traitants. |
| Total | Total du jour. |

Objectif: suivre la caisse au jour et au mois.

## Entrees Supplementaires

| Donnee | Description |
| --- | --- |
| Date | Date de l'entree. |
| Montant | Montant de l'entree. |
| Detail | Source ou motif. |
| Statut paiement | Paye, non paye, partiel. |
| Remarque | Information complementaire. |

Objectif: enregistrer les entrees non classees dans la caisse principale.

## Sorties Coffre

| Donnee | Description |
| --- | --- |
| Date | Date de sortie. |
| Designation | Motif de sortie. |
| Montant | Montant sorti. |
| Categorie | Type de depense. |
| Remarque | Information complementaire. |

Objectif: enregistrer toutes les sorties du coffre.

## Bilan Mensuel

| Donnee | Description |
| --- | --- |
| Caisse CV | Total mensuel Caisse CV. |
| Caisse C | Total mensuel Caisse C. |
| Convention | Total convention. |
| Sous-Traitance | Total sous-traitance. |
| Entrees Supplementaires | Total entrees supplementaires. |
| Chiffre d'Affaire | Chiffre d'affaires mensuel. |
| Depenses | Total des depenses. |
| Profitabilite | Profitabilite avant investissements. |
| Investissements | Total des investissements. |
| Profitabilite Net | Profitabilite apres investissements. |
| Coffre Net Reel | Solde reel du coffre. |

Objectif: presenter le resultat mensuel.

## Fournisseurs

| Donnee | Description |
| --- | --- |
| Fournisseur | Nom du fournisseur. |
| Categorie | Reactifs, consommables, impots, salaires, etc. |
| Date | Date de l'operation. |
| Total des Commandes | Montant commande ou facture. |
| Payer | Montant paye. |
| Reste | Reste non paye. |
| Statut | Paye, Partiel, Impaye. |
| Observation | Note complementaire. |

Objectif: suivre dettes et paiements fournisseurs.

## Paiements

| Donnee | Description |
| --- | --- |
| Date paiement | Date du versement. |
| Partie concernee | Fournisseur, sous-traitant ou convention. |
| Montant | Montant du paiement. |
| Mode paiement | Cash, cheque, virement ou autre. |
| Reference | Numero de cheque ou reference operation. |
| Remarque | Information complementaire. |

Objectif: conserver les paiements partiels ou complets.

## Sous-Traitants

| Donnee | Description |
| --- | --- |
| Sous-traitant | Nom du sous-traitant. |
| Montant | Montant du dossier. |
| Versement | Montant paye. |
| Date de Reception | Date de reception. |
| Mode Paiement | Mode de paiement. |
| Reste | Reste a payer. |
| Remarques | Notes. |

Objectif: suivre les partenaires externes.

## Conventions

| Donnee | Description |
| --- | --- |
| Convention | Nom de la convention. |
| Montant | Montant du dossier. |
| Versement | Montant paye. |
| Date de Reception | Date de reception. |
| Mode Paiement | Mode de paiement. |
| Reste | Reste a payer. |
| Remarques | Notes. |

Objectif: suivre les conventions et leurs paiements.

## Presence

| Donnee | Description |
| --- | --- |
| Employe | Nom de l'employe. |
| Mois | Mois de presence. |
| Jour | Jour du mois. |
| Code | P, ABS, G, GV-J, GV-N, C, C.M, REC, P+. |
| Remarque | Note complementaire. |

Objectif: conserver la presence et alimenter les salaires.

## Rapport de Salaire

| Donnee | Description |
| --- | --- |
| Employe | Nom de l'employe. |
| Poste | Fonction. |
| Salaire Net | Salaire net de base. |
| Presence en + / HS | Presence supplementaire ou heures supplementaires. |
| Deplacement LAM | Indemnite de deplacement. |
| Gardes | Garde nuit et garde vendredi. |
| Absence | Retenue d'absence. |
| Prime | Prime. |
| Penalites | Retenues ou penalites. |
| Avances | Avances sur salaire. |
| Salaire Final | Salaire final. |
| Remarque | Note. |

Objectif: calculer et verifier les salaires mensuels.

## Employes

| Donnee | Description |
| --- | --- |
| Nom/Prenom | Identite de l'employe. |
| Fonction | Poste occupe. |
| Date Naissance | Date de naissance. |
| Age | Age calcule. |
| Lieu Naissance | Lieu de naissance. |
| Adresse | Adresse. |
| Telephone 01/02 | Numeros de telephone. |
| Numero SS | Numero securite sociale. |
| Numero ANEM | Numero ANEM. |

Objectif: conserver le dossier administratif de base.

## Contrats

| Donnee | Description |
| --- | --- |
| Employe | Employe rattache au contrat. |
| Date d'Embauche | Date d'embauche. |
| Date d'Inscription CNAS | Date CNAS. |
| Contrat | Type de contrat. |
| Du | Date de debut. |
| Au | Date de fin. |
| Demission | Date de sortie si existe. |

Objectif: suivre la situation contractuelle.

## Conges

| Donnee | Description |
| --- | --- |
| Employe | Nom de l'employe. |
| Annee | Annee de conge. |
| Date d'Embauche | Date d'embauche. |
| Jours Acquis | Jours acquis. |
| Jours Pris | Jours consommes. |
| Reste | Solde restant. |
| Remarque | Note. |

Objectif: suivre le solde annuel de conges.

## Vehicule de Service

| Donnee | Description |
| --- | --- |
| Date | Date de l'operation. |
| Montant | Montant de la depense. |
| Details | Details. |
| Kilometrage | Kilometrage. |
| GPL / Kilometre en + | Donnees GPL. |
| Essence / Kilometre en + | Donnees essence. |

Objectif: suivre les frais du vehicule de service.

## Etat Cheques / Compte SGA

| Donnee | Description |
| --- | --- |
| Date | Date de l'operation. |
| Beneficiaire | Beneficiaire. |
| Numero Cheque | Numero du cheque. |
| Montant | Montant. |
| Entrees | Entrees. |
| Sorties | Sorties. |
| Designation | Motif. |
| Mois | Mois associe. |

Objectif: suivre les cheques et le compte SGA.

## Etat d'Encaissement

| Donnee | Description |
| --- | --- |
| Jour | Numero du jour. |
| Date | Date du jour. |
| Designation | Souvent DIVERS CLIENTS. |
| Observations | Notes. |
| Montants | Montant du jour. |
| Total | Total mensuel. |

Objectif: produire le rapport mensuel d'encaissement.
