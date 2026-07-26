import datetime

class RapportManager:
    def __init__(self, db_instance):
        self.db = db_instance

    def get_rapport_comptabilite(self, month, year):
        """
        Gathers complete monthly accounting report data matching 
        'excel/01) Rapport de comptabilité Décembre 2025.docx'.
        """
        # --------------------------------------------------------
        # 1. REVENUS
        # --------------------------------------------------------
        # Ville (Caisse CV)
        q_cv = """
            SELECT SUM(caisse_cv) as total_cv, SUM(tpe) as total_tpe
            FROM Mouvement_Caisse 
            WHERE MONTH(date_mouvement) = %s AND YEAR(date_mouvement) = %s
        """
        r_cv = self.db.fetch_one(q_cv, (month, year))
        revenus_ville = float((r_cv['total_cv'] or 0.0) + (r_cv['total_tpe'] or 0.0)) if r_cv else 0.0

        # Sous-Traitance (Per partner breakdown)
        q_st = """
            SELECT p.nom_partenaire, SUM(o.montant_total) as total 
            FROM Operations_Partenaires o 
            JOIN Partenaires p ON o.id_partenaire = p.id_partenaire 
            WHERE p.type_partenaire = 'SOUS_TRAITANT' 
              AND MONTH(o.date_operation) = %s 
              AND YEAR(o.date_operation) = %s
            GROUP BY p.id_partenaire, p.nom_partenaire
        """
        st_items = self.db.fetch_all(q_st, (month, year))
        total_st = sum(float(it['total'] or 0.0) for it in st_items)

        # Revenus Supplémentaires (Coffre)
        q_supp = """
            SELECT designation, SUM(montant) as total 
            FROM Mouvement_Coffre 
            WHERE type_operation = 'ENTREE' 
              AND categorie_operation = 'ENTREES_SUPP' 
              AND MONTH(date_transaction) = %s 
              AND YEAR(date_transaction) = %s
            GROUP BY designation
        """
        supp_items = self.db.fetch_all(q_supp, (month, year))
        total_supp = sum(float(it['total'] or 0.0) for it in supp_items)

        chiffre_affaires_mensuel = revenus_ville + total_st + total_supp

        # --------------------------------------------------------
        # 2. DÉPENSES (CATEGORIZED BREAKDOWN)
        # --------------------------------------------------------
        categories_depenses = {}

        # Catégorie 01: Réactifs & Consommables (Fournisseurs)
        q_fourn = """
            SELECT f.nom_fournisseur, 
                   IFNULL(SUM(d.montant_total), 0.0) as total_cmd,
                   IFNULL((SELECT SUM(p.montant_paye) 
                           FROM Paiements_Fournisseurs p 
                           JOIN Depenses_Achats d2 ON p.id_depense = d2.id_depense 
                           WHERE d2.id_fournisseur = f.id_fournisseur 
                             AND MONTH(p.date_paiement) = %s 
                             AND YEAR(p.date_paiement) = %s), 0.0) as total_paye
            FROM Fournisseurs f
            LEFT JOIN Depenses_Achats d ON f.id_fournisseur = d.id_fournisseur 
                 AND MONTH(d.date_facture) = %s AND YEAR(d.date_facture) = %s
            GROUP BY f.id_fournisseur, f.nom_fournisseur
            HAVING total_cmd > 0 OR total_paye > 0
        """
        reactifs_rows = self.db.fetch_all(q_fourn, (month, year, month, year))
        cat01_paye = sum(float(r['total_paye'] or 0.0) for r in reactifs_rows)
        cat01_total = sum(float(r['total_cmd'] or 0.0) for r in reactifs_rows)
        cat01_dette = max(0.0, cat01_total - cat01_paye)

        categories_depenses["01. Réactifs & Consommables"] = {
            "items": [{"label": r['nom_fournisseur'], "paye": float(r['total_paye'] or 0.0), "dette": max(0.0, float(r['total_cmd'] or 0.0) - float(r['total_paye'] or 0.0))} for r in reactifs_rows],
            "paye": cat01_paye,
            "dette": cat01_dette,
            "total": cat01_total
        }

        # Catégorie 02: Salaires
        q_paie = "SELECT SUM(net_a_payer) as total_paie FROM Fiches_Paie WHERE mois = %s AND annee = %s"
        r_paie = self.db.fetch_one(q_paie, (month, year))
        total_salaires = float(r_paie['total_paie'] or 0.0) if r_paie else 0.0
        categories_depenses["02. Salaires"] = {
            "items": [{"label": "Salaires Employés (Fiches de Paie)", "paye": total_salaires, "dette": 0.0}],
            "paye": total_salaires,
            "dette": 0.0,
            "total": total_salaires
        }

        # Catégorie 03: Dépenses Internes (Caisse)
        q_dep_int = "SELECT SUM(depenses) as total FROM Mouvement_Caisse WHERE MONTH(date_mouvement) = %s AND YEAR(date_mouvement) = %s"
        r_dep_int = self.db.fetch_one(q_dep_int, (month, year))
        total_dep_int = float(r_dep_int['total'] or 0.0) if r_dep_int else 0.0
        categories_depenses["03. Dépenses Internes"] = {
            "items": [{"label": "Dépenses Internes Caisse", "paye": total_dep_int, "dette": 0.0}],
            "paye": total_dep_int,
            "dette": 0.0,
            "total": total_dep_int
        }

        # Catégorie 04: Véhicule de Service
        q_veh = "SELECT SUM(montant_carburant) as total FROM Vehicule_Service WHERE MONTH(date_suivi) = %s AND YEAR(date_suivi) = %s"
        r_veh = self.db.fetch_one(q_veh, (month, year))
        total_veh = float(r_veh['total'] or 0.0) if r_veh else 0.0
        categories_depenses["04. Véhicule de Service"] = {
            "items": [{"label": "Carburant & Entretien Véhicules", "paye": total_veh, "dette": 0.0}],
            "paye": total_veh,
            "dette": 0.0,
            "total": total_veh
        }

        # Catégorie 05: Autre Dépenses (Impôts, Location, Informatique, etc.)
        total_charges_paye = sum(c['paye'] for c in categories_depenses.values())
        total_charges_dette = sum(c['dette'] for c in categories_depenses.values())
        total_dépenses_globales = total_charges_paye + total_charges_dette

        # --------------------------------------------------------
        # 3. RÉSULTAT FINAL & PROFITABILITÉ
        # --------------------------------------------------------
        profitabilite_nette = chiffre_affaires_mensuel - total_dépenses_globales

        return {
            'month': month,
            'year': year,
            'revenus': {
                'ville': revenus_ville,
                'sous_traitance_items': st_items,
                'total_st': total_st,
                'supp_items': supp_items,
                'total_supp': total_supp,
                'chiffre_affaires': chiffre_affaires_mensuel
            },
            'depenses': {
                'categories': categories_depenses,
                'total_paye': total_charges_paye,
                'total_dette': total_charges_dette,
                'total_global': total_dépenses_globales
            },
            'resultat': {
                'revenus_totaux': chiffre_affaires_mensuel,
                'charges_totales': total_dépenses_globales,
                'profitabilite_nette': profitabilite_nette,
                'investissements': 0.0,
                'profitabilite_apres_invest': profitabilite_nette,
                'mouvement_profitabilite': 0.0,
                'reste_profitabilite': profitabilite_nette
            }
        }
