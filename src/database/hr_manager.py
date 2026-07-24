class HRManager:
    def __init__(self, db_instance):
        self.db = db_instance

    def get_employes(self):
        query = "SELECT id_employe, nom_prenom, fonction, salaire_base, date_embauche FROM Employes"
        return self.db.fetch_all(query)

    def get_drh_master_list(self):
        query = """
            SELECT 
                e.id_employe, e.nom_prenom, e.fonction, e.salaire_base, e.date_naissance, 
                e.lieu_naissance, e.adresse, e.tel_1, e.tel_2, e.nss, e.n_anem, e.nin, e.type_contrat, e.photo_path,
                e.date_embauche, e.date_inscription_cnas, e.date_fin_contrat, e.date_demission, e.remarque_drh,
                (SELECT COUNT(*) FROM Presences p WHERE p.id_employe = e.id_employe AND p.etat_jour = 'CONGE') as jours_conge_pris
            FROM Employes e
            ORDER BY e.nom_prenom
        """
        return self.db.fetch_all(query)

    def get_employes_list(self):
        query = "SELECT id_employe, nom_prenom FROM Employes ORDER BY nom_prenom"
        return self.db.fetch_all(query)

    def get_employe_base_salary(self, id_employe):
        query = "SELECT salaire_base FROM Employes WHERE id_employe = %s"
        row = self.db.fetch_one(query, (id_employe,))
        return float(row['salaire_base'] or 0.0) if row else 0.0

    def add_employe(self, nom_prenom, fonction, salaire_base, date_embauche):
        query = """
            INSERT INTO Employes (nom_prenom, fonction, salaire_base, date_embauche)
            VALUES (%s, %s, %s, %s)
        """
        params = (nom_prenom, fonction, salaire_base, date_embauche)
        success, _ = self.db.execute(query, params)
        return success

    def add_drh_employe(self, data):
        query = """
            INSERT INTO Employes (
                nom_prenom, fonction, salaire_base, date_naissance, lieu_naissance,
                adresse, tel_1, tel_2, nss, n_anem, nin, type_contrat, photo_path,
                date_embauche, date_inscription_cnas,
                date_fin_contrat, date_demission, remarque_drh, heures_travail_jour
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data.get('nom_prenom'), data.get('fonction'), data.get('salaire_base', 0),
            data.get('date_naissance'), data.get('lieu_naissance'), data.get('adresse'),
            data.get('tel_1'), data.get('tel_2'), data.get('nss'), data.get('n_anem'),
            data.get('nin'), data.get('type_contrat'), data.get('photo_path'),
            data.get('date_embauche'), data.get('date_inscription_cnas'),
            data.get('date_fin_contrat'), data.get('date_demission'), data.get('remarque_drh'),
            data.get('heures_travail_jour', 8.0)
        )
        success, _ = self.db.execute(query, params)
        return success

    def update_drh_employe(self, id_employe, data):
        query = """
            UPDATE Employes SET
                nom_prenom=%s, fonction=%s, salaire_base=%s, date_naissance=%s, lieu_naissance=%s,
                adresse=%s, tel_1=%s, tel_2=%s, nss=%s, n_anem=%s, nin=%s, type_contrat=%s, photo_path=%s,
                date_embauche=%s, date_inscription_cnas=%s,
                date_fin_contrat=%s, date_demission=%s, remarque_drh=%s, heures_travail_jour=%s
            WHERE id_employe=%s
        """
        params = (
            data.get('nom_prenom'), data.get('fonction'), data.get('salaire_base', 0),
            data.get('date_naissance'), data.get('lieu_naissance'), data.get('adresse'),
            data.get('tel_1'), data.get('tel_2'), data.get('nss'), data.get('n_anem'),
            data.get('nin'), data.get('type_contrat'), data.get('photo_path'),
            data.get('date_embauche'), data.get('date_inscription_cnas'),
            data.get('date_fin_contrat'), data.get('date_demission'), data.get('remarque_drh'),
            data.get('heures_travail_jour', 8.0),
            id_employe
        )
        success, _ = self.db.execute(query, params)
        return success

    def get_presences(self):
        query = """
            SELECT p.id_presence, e.nom_prenom, p.date_presence, p.etat_jour, p.heures_sup 
            FROM Presences p 
            JOIN Employes e ON p.id_employe = e.id_employe 
            ORDER BY p.date_presence DESC LIMIT 50
        """
        return self.db.fetch_all(query)

    def add_presence(self, id_employe, date_presence, etat_jour, heures_sup):
        query = """
            INSERT INTO Presences (id_employe, date_presence, etat_jour, heures_sup)
            VALUES (%s, %s, %s, %s)
        """
        params = (id_employe, date_presence, etat_jour, heures_sup)
        success, _ = self.db.execute(query, params)
        return success

    def get_monthly_presences_matrix(self, month, year):
        query = """
            SELECT p.id_employe, DAY(p.date_presence) as jour, p.etat_jour, p.heures_sup,
                   p.heure_entree, p.heure_sortie
            FROM Presences p
            WHERE MONTH(p.date_presence) = %s AND YEAR(p.date_presence) = %s
        """
        records = self.db.fetch_all(query, (month, year))
        matrix = {}
        for r in records:
            eid = r['id_employe']
            j = r['jour']
            etat = r['etat_jour']
            h_sup = float(r['heures_sup'] or 0.0)
            
            if eid not in matrix:
                matrix[eid] = {}
            if j not in matrix[eid]:
                matrix[eid][j] = {}
                
            if etat in ('PRESENT', 'RECUPERATION', 'ABSENCE', 'CONGE_MALADIE', 'CONGE'):
                val = ''
                if etat == 'PRESENT':
                    val = 'P+' if h_sup > 0 else 'P'
                elif etat == 'RECUPERATION': val = 'REC'
                elif etat == 'ABSENCE': val = 'ABS'
                elif etat == 'CONGE_MALADIE': val = 'C.M'
                elif etat == 'CONGE': val = 'C'
                matrix[eid][j]['JOUR'] = val
                matrix[eid][j]['heure_entree'] = r['heure_entree']
                matrix[eid][j]['heure_sortie'] = r['heure_sortie']
                
            elif etat in ('GARDE_NUIT', 'GARDE_VENDREDI_JOUR', 'GARDE_VENDREDI_NUIT'):
                val = ''
                if etat == 'GARDE_NUIT': val = 'G'
                elif etat == 'GARDE_VENDREDI_JOUR': val = 'GV-J'
                elif etat == 'GARDE_VENDREDI_NUIT': val = 'GV-N'
                matrix[eid][j]['GARDE'] = val
        return matrix

    def upsert_presence(self, id_employe, date_presence, type_row, value_str):
        value_str = value_str.upper().strip() if value_str else ""
        etat_jour = None
        heures_sup = 0.0
        
        if type_row == 'JOUR':
            if value_str == 'P': etat_jour = 'PRESENT'
            elif value_str == 'P+': 
                etat_jour = 'PRESENT'
                heures_sup = 1.0
            elif value_str == 'REC': etat_jour = 'RECUPERATION'
            elif value_str == 'ABS': etat_jour = 'ABSENCE'
            elif value_str in ('C.M', 'CM'): etat_jour = 'CONGE_MALADIE'
            elif value_str == 'C': etat_jour = 'CONGE'
        elif type_row == 'GARDE':
            if value_str == 'G': etat_jour = 'GARDE_NUIT'
            elif value_str == 'GV-J': etat_jour = 'GARDE_VENDREDI_JOUR'
            elif value_str == 'GV-N': etat_jour = 'GARDE_VENDREDI_NUIT'
            
        if not etat_jour:
            query_find = "SELECT id_presence, etat_jour FROM Presences WHERE id_employe = %s AND date_presence = %s"
            existing = self.db.fetch_all(query_find, (id_employe, date_presence))
            for rec in existing:
                is_jour_rec = rec['etat_jour'] in ('PRESENT', 'RECUPERATION', 'ABSENCE', 'CONGE_MALADIE', 'CONGE')
                is_garde_rec = rec['etat_jour'] in ('GARDE_NUIT', 'GARDE_VENDREDI_JOUR', 'GARDE_VENDREDI_NUIT')
                if (type_row == 'JOUR' and is_jour_rec) or (type_row == 'GARDE' and is_garde_rec):
                    self.db.execute("DELETE FROM Presences WHERE id_presence = %s", (rec['id_presence'],))
            return True
        query_find = "SELECT id_presence, etat_jour FROM Presences WHERE id_employe = %s AND date_presence = %s"
        existing = self.db.fetch_all(query_find, (id_employe, date_presence))
        target_id = None
        for rec in existing:
            is_jour_rec = rec['etat_jour'] in ('PRESENT', 'RECUPERATION', 'ABSENCE', 'CONGE_MALADIE', 'CONGE')
            is_garde_rec = rec['etat_jour'] in ('GARDE_NUIT', 'GARDE_VENDREDI_JOUR', 'GARDE_VENDREDI_NUIT')
            if (type_row == 'JOUR' and is_jour_rec) or (type_row == 'GARDE' and is_garde_rec):
                target_id = rec['id_presence']
                break
                
        if target_id:
            query = "UPDATE Presences SET etat_jour = %s, heures_sup = %s WHERE id_presence = %s"
            success, _ = self.db.execute(query, (etat_jour, heures_sup, target_id))
            return success
        else:
            query = "INSERT INTO Presences (id_employe, date_presence, etat_jour, heures_sup) VALUES (%s, %s, %s, %s)"
            success, _ = self.db.execute(query, (id_employe, date_presence, etat_jour, heures_sup))
            return success

    def get_presence_hours(self, id_employe, date_presence):
        query = "SELECT heure_entree, heure_sortie FROM Presences WHERE id_employe = %s AND date_presence = %s"
        return self.db.fetch_one(query, (id_employe, date_presence))
        
    def get_monthly_remarques(self, mois, annee):
        query = "SELECT id_employe, remarque FROM presences_remarques WHERE mois = %s AND annee = %s"
        records = self.db.fetch_all(query, (mois, annee))
        return {r['id_employe']: r['remarque'] for r in records}
        
    def upsert_monthly_remarque(self, id_employe, mois, annee, remarque):
        query = """
            INSERT INTO presences_remarques (id_employe, mois, annee, remarque)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE remarque = %s
        """
        success, _ = self.db.execute(query, (id_employe, mois, annee, remarque, remarque))
        return success

    def update_presence_hours(self, id_employe, date_presence, heure_entree, heure_sortie):
        query = """
            UPDATE Presences 
            SET heure_entree = %s, heure_sortie = %s
            WHERE id_employe = %s AND date_presence = %s
        """
        success, _ = self.db.execute(query, (heure_entree, heure_sortie, id_employe, date_presence))
        return success

    def get_salaires_matrix(self, month, year):
        query = """
            SELECT 
                e.id_employe, e.nom_prenom, e.fonction, e.salaire_base,
                IFNULL(f.heures_sup_montant, 0.0) as heures_sup_montant,
                IFNULL(f.deplacement, 0.0) as deplacement,
                IFNULL(f.garde_nuit, 0.0) as garde_nuit,
                IFNULL(f.garde_vendredi_jour, 0.0) as garde_vendredi_jour,
                IFNULL(f.garde_vendredi_nuit, 0.0) as garde_vendredi_nuit,
                IFNULL(f.retenue_absence, 0.0) as retenue_absence,
                IFNULL(f.prime, 0.0) as prime,
                IFNULL(f.conge, 0.0) as conge,
                IFNULL(f.penalites, 0.0) as penalites,
                IFNULL(f.avances, 0.0) as avances,
                IFNULL(f.net_a_payer, e.salaire_base) as net_a_payer,
                IFNULL(f.remarques, '') as remarques
            FROM Employes e
            LEFT JOIN Fiches_Paie f ON e.id_employe = f.id_employe AND f.mois = %s AND f.annee = %s
            ORDER BY e.nom_prenom
        """
        return self.db.fetch_all(query, (month, year))

    def get_fiches_paie(self):
        query = """
            SELECT f.id_paie, f.id_employe, f.mois, f.annee, e.nom_prenom, f.net_a_payer, f.prime, f.deplacement, f.retenue_absence, f.avances
            FROM Fiches_Paie f
            JOIN Employes e ON f.id_employe = e.id_employe
            ORDER BY f.annee DESC, f.mois DESC LIMIT 50
        """
        return self.db.fetch_all(query)

    def add_fiche_paie(self, id_employe, mois, annee, prime, deplacement, garde_nuit, garde_vendredi_jour, 
                       garde_vendredi_nuit, heures_sup_montant, conge, retenue_absence, penalites, avances, net_a_payer, remarques):
        query = """
            INSERT INTO Fiches_Paie 
            (id_employe, mois, annee, prime, deplacement, garde_nuit, garde_vendredi_jour, 
             garde_vendredi_nuit, heures_sup_montant, conge, retenue_absence, penalites, avances, net_a_payer, remarques)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            prime=VALUES(prime), deplacement=VALUES(deplacement), garde_nuit=VALUES(garde_nuit),
            garde_vendredi_jour=VALUES(garde_vendredi_jour), garde_vendredi_nuit=VALUES(garde_vendredi_nuit),
            heures_sup_montant=VALUES(heures_sup_montant), conge=VALUES(conge), 
            retenue_absence=VALUES(retenue_absence), penalites=VALUES(penalites), 
            avances=VALUES(avances), net_a_payer=VALUES(net_a_payer), remarques=VALUES(remarques)
        """
        params = (
            id_employe, mois, annee, prime, deplacement, garde_nuit, garde_vendredi_jour,
            garde_vendredi_nuit, heures_sup_montant, conge, retenue_absence, penalites, avances, net_a_payer, remarques
        )
        success, _ = self.db.execute(query, params)
        return success

    def delete_fiche_paie(self, id_employe, mois, annee):
        query = "DELETE FROM Fiches_Paie WHERE id_employe = %s AND mois = %s AND annee = %s"
        success, _ = self.db.execute(query, (id_employe, mois, annee))
        return success
