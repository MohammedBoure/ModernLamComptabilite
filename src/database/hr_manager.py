from datetime import date, datetime

try:
    from .governance_manager import GovernanceManager
    from .hr_policies import leave_accrual_days
except ImportError:  # Direct manager execution used by legacy tests/tools.
    from governance_manager import GovernanceManager
    from hr_policies import leave_accrual_days

class HRManager:
    def __init__(self, db_instance):
        self.db = db_instance

    def create_contract(self, id_employe, contract_type, starts_on, ends_on=None, cnas_registered_on=None, notes=None, actor_username="system"):
        actor = self.governance.assert_can_write(actor_username, {"ADMIN", "HR"})
        period = self.governance.assert_writable_period(starts_on, actor)
        if ends_on and str(ends_on) < str(starts_on):
            raise ValueError("A contract end date cannot precede its start date.")
        active = self.db.fetch_one(
            "SELECT id_contract FROM Employee_Contracts WHERE id_employe = %s AND status = 'ACTIVE'", (id_employe,)
        )
        if active:
            raise ValueError("The employee already has an active contract; end or cancel it first.")
        success, contract_id = self.db.execute(
            """INSERT INTO Employee_Contracts
               (id_employe, contract_type, starts_on, ends_on, cnas_registered_on, status, notes)
               VALUES (%s, %s, %s, %s, %s, 'ACTIVE', %s)""",
            (id_employe, contract_type, starts_on, ends_on, cnas_registered_on, notes),
        )
        if success:
            self.governance.record_audit(actor, "EMPLOYEE_CONTRACT_CREATED", "Employee_Contracts", contract_id, period["id_period"], new_values={"employee_id": id_employe, "type": contract_type}, reason=notes)
        return success

    def end_contract(self, contract_id, ends_on, actor_username="system", notes=None):
        actor = self.governance.assert_can_write(actor_username, {"ADMIN", "HR"})
        contract = self.db.fetch_one("SELECT * FROM Employee_Contracts WHERE id_contract = %s", (contract_id,))
        if not contract or contract["status"] != "ACTIVE":
            raise ValueError("Only an active contract can be ended.")
        period = self.governance.assert_writable_period(ends_on, actor)
        success, _ = self.db.execute(
            "UPDATE Employee_Contracts SET status = 'ENDED', ends_on = %s, notes = COALESCE(%s, notes) WHERE id_contract = %s",
            (ends_on, notes, contract_id),
        )
        if success:
            self.governance.record_audit(actor, "EMPLOYEE_CONTRACT_ENDED", "Employee_Contracts", contract_id, period["id_period"], old_values={"status": "ACTIVE"}, new_values={"status": "ENDED"}, reason=notes)
        return success

    def record_leave(self, id_employe, entry_type, days, effective_on, notes=None, actor_username="system"):
        actor = self.governance.assert_can_write(actor_username, {"ADMIN", "HR"})
        if entry_type not in {"ACCRUAL", "TAKEN", "ADJUSTMENT"} or float(days) <= 0:
            raise ValueError("Leave entries require a supported type and a positive number of days.")
        period = self.governance.assert_writable_period(effective_on, actor)
        success, leave_id = self.db.execute(
            """INSERT INTO Leave_Ledger (id_employe, period_id, entry_type, days, effective_on, notes, created_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (id_employe, period["id_period"], entry_type, days, effective_on, notes, actor),
        )
        if success:
            self.governance.record_audit(actor, "LEAVE_LEDGER_CREATED", "Leave_Ledger", leave_id, period["id_period"], new_values={"employee_id": id_employe, "entry_type": entry_type, "days": days}, reason=notes)
        return success

    def accrue_annual_leave(self, id_employe, hire_date, year, monthly_days=2.5, actor_username="system"):
        hire = hire_date if isinstance(hire_date, date) else datetime.strptime(str(hire_date), "%Y-%m-%d").date()
        amount = leave_accrual_days(hire, int(year), monthly_days)
        if amount <= 0:
            return False
        return self.record_leave(id_employe, "ACCRUAL", amount, f"{int(year)}-12-31", "Annual leave accrual (day-15 rule)", actor_username)

    def get_leave_balance(self, id_employe, year=None):
        where = " WHERE id_employe = %s"
        params = [id_employe]
        if year:
            where += " AND YEAR(effective_on) = %s"
            params.append(year)
        row = self.db.fetch_one(
            """SELECT COALESCE(SUM(CASE WHEN entry_type = 'TAKEN' THEN -days ELSE days END), 0) AS balance
               FROM Leave_Ledger""" + where,
            tuple(params),
        ) or {}
        return float(row.get("balance") or 0)

    def save_payroll_rate(self, rate_code, amount, effective_from, effective_to=None, notes=None, actor_username="system"):
        actor = self.governance.assert_can_write(actor_username, {"ADMIN", "HR", "ACCOUNTANT"})
        if float(amount) < 0:
            raise ValueError("Payroll rates cannot be negative.")
        period = self.governance.assert_writable_period(effective_from, actor)
        success, rate_id = self.db.execute(
            """INSERT INTO Payroll_Rates (rate_code, amount, effective_from, effective_to, approved_by, notes)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE amount=VALUES(amount), effective_to=VALUES(effective_to), approved_by=VALUES(approved_by), notes=VALUES(notes)""",
            (rate_code, amount, effective_from, effective_to, actor, notes),
        )
        if success:
            self.governance.record_audit(actor, "PAYROLL_RATE_SAVED", "Payroll_Rates", rate_id, period["id_period"], new_values={"rate_code": rate_code, "amount": amount}, reason=notes)
        return success

    def payroll_rate_for(self, rate_code, effective_on):
        row = self.db.fetch_one(
            """SELECT amount FROM Payroll_Rates WHERE rate_code = %s AND effective_from <= %s
               AND (effective_to IS NULL OR effective_to >= %s)
               ORDER BY effective_from DESC LIMIT 1""",
            (rate_code, effective_on, effective_on),
        )
        return float(row["amount"]) if row else None
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
                       garde_vendredi_nuit, heures_sup_montant, conge, retenue_absence, penalites, avances, net_a_payer, remarques,
                       actor_username="system"):
        actor = self.governance.assert_can_write(actor_username, {"ADMIN", "HR", "ACCOUNTANT"})
        period = self.governance.assert_writable_period(f"{int(annee)}-{int(mois):02d}-01", actor)
        query = """
            INSERT INTO Fiches_Paie
            (id_employe, mois, annee, prime, deplacement, garde_nuit, garde_vendredi_jour,
             garde_vendredi_nuit, heures_sup_montant, conge, retenue_absence, penalites, avances,
             net_a_payer, remarques, period_id, statut)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'DRAFT')
            ON DUPLICATE KEY UPDATE
            prime=VALUES(prime), deplacement=VALUES(deplacement), garde_nuit=VALUES(garde_nuit),
            garde_vendredi_jour=VALUES(garde_vendredi_jour), garde_vendredi_nuit=VALUES(garde_vendredi_nuit),
            heures_sup_montant=VALUES(heures_sup_montant), conge=VALUES(conge),
            retenue_absence=VALUES(retenue_absence), penalites=VALUES(penalites), avances=VALUES(avances),
            net_a_payer=VALUES(net_a_payer), remarques=VALUES(remarques), period_id=VALUES(period_id)
        """
        params = (
            id_employe, mois, annee, prime, deplacement, garde_nuit, garde_vendredi_jour,
            garde_vendredi_nuit, heures_sup_montant, conge, retenue_absence, penalites, avances,
            net_a_payer, remarques, period["id_period"]
        )
        success, entity_id = self.db.execute(query, params)
        if success:
            self.governance.record_audit(actor, "PAYROLL_SHEET_SAVED", "Fiches_Paie", entity_id, period["id_period"], new_values={"employee_id": id_employe, "net": net_a_payer, "month": mois, "year": annee}, reason=remarques)
        return success
    def delete_fiche_paie(self, id_employe, mois, annee, reason, actor_username="system"):
        """Void payroll evidence; financial payroll sheets are never physically deleted."""
        if not (reason or "").strip():
            raise ValueError("A reason is required to void a payroll sheet.")
        actor = self.governance.assert_can_write(actor_username, {"ADMIN", "HR", "ACCOUNTANT"})
        period = self.governance.assert_writable_period(f"{int(annee)}-{int(mois):02d}-01", actor)
        sheet = self.db.fetch_one(
            "SELECT id_paie, statut FROM Fiches_Paie WHERE id_employe = %s AND mois = %s AND annee = %s",
            (id_employe, mois, annee),
        )
        if not sheet or sheet.get("statut") == "VOID":
            raise ValueError("The payroll sheet does not exist or has already been voided.")
        success, _ = self.db.execute(
            "UPDATE Fiches_Paie SET statut = 'VOID' WHERE id_paie = %s AND statut <> 'VOID'", (sheet["id_paie"],)
        )
        if success:
            self.governance.record_audit(actor, "PAYROLL_SHEET_VOIDED", "Fiches_Paie", sheet["id_paie"], period["id_period"], old_values={"status": sheet.get("statut")}, reason=reason.strip())
        return success
    def get_presences_stats_by_period(self, start_date, end_date, id_employe=None):
        """
        Retrieves presence records between start_date and end_date (inclusive).
        If id_employe is provided, filters for that specific employee.
        """
        params = [start_date, end_date]
        emp_filter = ""
        if id_employe:
            emp_filter = " AND p.id_employe = %s"
            params.append(id_employe)

        query = f"""
            SELECT 
                p.id_presence,
                p.id_employe,
                e.nom_prenom,
                e.fonction,
                IFNULL(e.heures_travail_jour, 8.0) as heures_travail_jour,
                p.date_presence,
                p.etat_jour,
                p.heures_sup,
                p.heure_entree,
                p.heure_sortie
            FROM Presences p
            JOIN Employes e ON p.id_employe = e.id_employe
            WHERE p.date_presence >= %s AND p.date_presence <= %s {emp_filter}
            ORDER BY p.date_presence DESC, e.nom_prenom ASC
        """
        return self.db.fetch_all(query, tuple(params))

