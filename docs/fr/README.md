# Documentation Francaise - ModernLam Comptabilite

Cette documentation presente le logiciel ModernLam Comptabilite en version francaise. Elle est organisee en deux parties: une documentation de gestion pour la comptabilite, la direction et les ressources humaines, et une documentation technique pour la conception et l'implementation.

## Rapport de reference

| Type | Fichier | Remarques |
| --- | --- | --- |
| Rapport principal | [Rapport Logiciel Comptabilite PDF](<../../Rapport Logiciel Comptabilité_720ec9a3-2c6d-4f36-87b8-5ecbc04ea00e.pdf>) | Source initiale des tableaux, modules, calculs et remarques. |

## Sections

| Section | Lien | Public | Contenu |
| --- | --- | --- | --- |
| Documentation comptable et administrative | [accounting/README.md](./accounting/README.md) | Comptabilite, direction, RH | Documentation generale, technique comptable, organisation des interfaces. |
| Documentation technique | [technical/README.md](./technical/README.md) | Conception, developpement, maintenance | Specifications techniques generales separees de la documentation pratique d'implementation qui sera completee apres le choix de la technologie. |

## Ordre de lecture de reference

| Ordre | Section | Objectif |
| --- | --- | --- |
| 1 | [accounting/general/README.md](./accounting/general/README.md) | Comprendre le logiciel du point de vue metier. |
| 2 | [accounting/accounting-technical/README.md](./accounting/accounting-technical/README.md) | Comprendre les donnees, les calculs et les controles comptables. |
| 3 | [accounting/ui/README.md](./accounting/ui/README.md) | Comprendre l'organisation des ecrans et des elements d'interface. |
| 4 | [technical/specification/README.md](./technical/specification/README.md) | Lire les specifications techniques generales non liees a une technologie precise. |
| 5 | [technical/implementation/README.md](./technical/implementation/README.md) | Consulter le perimetre reserve a la documentation pratique d'implementation. |
| 6 | [technical/specification/08-data-model.md](./technical/specification/08-data-model.md) | Consulter le modele general de donnees. |

## Regles de maintenance documentaire

- Toute modification d'une regle de calcul doit etre repercutee dans la documentation technique et dans la documentation comptable si elle impacte la lecture metier.
- Toute modification d'un ecran doit etre repercutee dans la documentation UI et, si necessaire, dans les specifications techniques.
- Toute decision administrative nouvelle doit etre integree aux regles ou aux questions ouvertes.
