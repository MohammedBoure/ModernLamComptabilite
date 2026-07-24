from PySide6.QtWidgets import QMessageBox, QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QSpinBox, QLabel, QFileDialog, QPushButton, QHBoxLayout, QTextEdit
from PySide6.QtCore import QDate, Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
import os
import shutil
from ui.base_dialog import BaseDialog
from database import data_manager

class EmployeDialog(BaseDialog):
    def __init__(self, parent=None, record=None):
        super().__init__("Modifier Employé" if record else "Ajouter Employé", parent)
        self.record = record
        self.setMinimumWidth(800)
        
        self.photo_path = record.get('photo_path') if record else None
        
        # We will create a custom layout structure and inject it into main_layout
        # instead of using the tall default form_layout
        from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout
        
        main_h_layout = QHBoxLayout()
        
        # --- Left Panel: Photo & Personal Info ---
        left_v_layout = QVBoxLayout()
        
        # Photo
        photo_group = QGroupBox("Photo de Profil")
        photo_layout = QVBoxLayout(photo_group)
        self.btn_photo = QPushButton()
        self.btn_photo.setFixedSize(160, 160)
        self.btn_photo.setCursor(Qt.PointingHandCursor)
        self.btn_photo.setStyleSheet("border: 1px solid #ccc; border-radius: 8px; background-color: #f8f9fa;")
        self.btn_photo.clicked.connect(self.select_photo)
        self.update_photo_preview()
        
        lbl_photo_help = QLabel("Cliquez pour changer la photo")
        lbl_photo_help.setAlignment(Qt.AlignCenter)
        lbl_photo_help.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        
        photo_layout.addWidget(self.btn_photo, 0, Qt.AlignCenter)
        photo_layout.addWidget(lbl_photo_help)
        
        left_v_layout.addWidget(photo_group)
        
        # Personal Info
        perso_group = QGroupBox("Informations Personnelles")
        from PySide6.QtWidgets import QFormLayout
        perso_form = QFormLayout(perso_group)
        
        self.txt_nom = QLineEdit()
        self.txt_naissance = QLineEdit()
        self.txt_naissance.setPlaceholderText("YYYY-MM-DD")
        self.txt_lieu_naissance = QLineEdit()
        self.txt_adresse = QLineEdit()
        self.txt_tel1 = QLineEdit()
        self.txt_tel2 = QLineEdit()
        self.txt_nin = QLineEdit()
        
        perso_form.addRow("Nom & Prénom:", self.txt_nom)
        perso_form.addRow("Date Naissance:", self.txt_naissance)
        perso_form.addRow("Lieu Naissance:", self.txt_lieu_naissance)
        perso_form.addRow("Adresse:", self.txt_adresse)
        perso_form.addRow("Tél 1:", self.txt_tel1)
        perso_form.addRow("Tél 2:", self.txt_tel2)
        perso_form.addRow("NIN:", self.txt_nin)
        
        left_v_layout.addWidget(perso_group)
        
        # --- Right Panel: Professional & Contract ---
        right_v_layout = QVBoxLayout()
        
        prof_group = QGroupBox("Informations Professionnelles")
        prof_form = QFormLayout(prof_group)
        
        self.txt_fonction = QLineEdit()
        self.val_salaire = QDoubleSpinBox()
        self.val_salaire.setMaximum(999999999.0)
        
        self.val_heures_travail = QDoubleSpinBox()
        self.val_heures_travail.setRange(1.0, 24.0)
        self.val_heures_travail.setSingleStep(0.5)
        self.val_heures_travail.setValue(8.0)
        self.val_heures_travail.setSuffix(" Heures/Jour")
        
        self.txt_nss = QLineEdit()
        self.txt_anem = QLineEdit()
        
        prof_form.addRow("Fonction:", self.txt_fonction)
        prof_form.addRow("Salaire de Base:", self.val_salaire)
        prof_form.addRow("Temps de Travail:", self.val_heures_travail)
        prof_form.addRow("N° SS:", self.txt_nss)
        prof_form.addRow("N° ANEM:", self.txt_anem)
        
        right_v_layout.addWidget(prof_group)
        
        contrat_group = QGroupBox("Détails du Contrat")
        contrat_form = QFormLayout(contrat_group)
        
        self.txt_embauche = QLineEdit()
        self.txt_embauche.setPlaceholderText("YYYY-MM-DD")
        if not record:
            self.txt_embauche.setText(QDate.currentDate().toString("yyyy-MM-dd"))
            
        self.txt_cnas = QLineEdit()
        self.txt_cnas.setPlaceholderText("YYYY-MM-DD")
        self.cb_type_contrat = QComboBox()
        self.cb_type_contrat.addItems(["", "CDI", "CDD", "CTA", "ANEM", "AUTRE"])
        self.txt_fin_contrat = QLineEdit()
        self.txt_fin_contrat.setPlaceholderText("YYYY-MM-DD")
        self.txt_demission = QLineEdit()
        self.txt_demission.setPlaceholderText("YYYY-MM-DD")
        self.txt_remarque = QLineEdit()
        
        contrat_form.addRow("Date Embauche:", self.txt_embauche)
        contrat_form.addRow("Date Inscription CNAS:", self.txt_cnas)
        contrat_form.addRow("Type de Contrat:", self.cb_type_contrat)
        contrat_form.addRow("Fin de Contrat (AU):", self.txt_fin_contrat)
        contrat_form.addRow("Date de Démission:", self.txt_demission)
        contrat_form.addRow("Remarque DRH:", self.txt_remarque)
        
        right_v_layout.addWidget(contrat_group)
        
        # Assemble
        main_h_layout.addLayout(left_v_layout)
        main_h_layout.addLayout(right_v_layout)
        
        # Insert our custom layout BEFORE the empty form_layout in BaseDialog's layout
        self.layout().insertLayout(1, main_h_layout)

        if record:
            self.txt_nom.setText(record.get('nom_prenom') or '')
            self.txt_fonction.setText(record.get('fonction') or '')
            self.val_salaire.setValue(float(record.get('salaire_base', 0.0) or 0.0))
            self.txt_naissance.setText(str(record.get('date_naissance') or ''))
            self.txt_lieu_naissance.setText(record.get('lieu_naissance') or '')
            self.txt_adresse.setText(record.get('adresse') or '')
            self.txt_tel1.setText(record.get('tel_1') or '')
            self.txt_tel2.setText(record.get('tel_2') or '')
            self.txt_nin.setText(record.get('nin') or '')
            self.txt_nss.setText(record.get('nss') or '')
            self.txt_anem.setText(record.get('n_anem') or '')
            self.txt_embauche.setText(str(record.get('date_embauche') or ''))
            self.txt_cnas.setText(str(record.get('date_inscription_cnas') or ''))
            self.cb_type_contrat.setCurrentText(record.get('type_contrat') or '')
            self.txt_fin_contrat.setText(str(record.get('date_fin_contrat') or ''))
            self.txt_demission.setText(str(record.get('date_demission') or ''))
            self.txt_remarque.setText(record.get('remarque_drh') or '')
            self.val_heures_travail.setValue(float(record.get('heures_travail_jour', 8.0) or 8.0))

    def update_photo_preview(self):
        if self.photo_path and os.path.exists(self.photo_path):
            pixmap = QPixmap(self.photo_path)
            # Scale the pixmap to fit the button, keeping aspect ratio
            pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon = QIcon(pixmap)
            self.btn_photo.setIcon(icon)
            self.btn_photo.setIconSize(QSize(150, 150))
        else:
            self.btn_photo.setIcon(QIcon())
            self.btn_photo.setText("📸")
            self.btn_photo.setFont(self.btn_photo.font())

    def select_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une photo", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            # We will copy the selected file to our assets directory
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "photos")
            os.makedirs(assets_dir, exist_ok=True)
            
            # Generate a clean filename
            ext = os.path.splitext(file_path)[1]
            safe_name = self.txt_nom.text().strip().replace(" ", "_")
            if not safe_name:
                safe_name = "employe"
            
            import time
            new_filename = f"{safe_name}_{int(time.time())}{ext}"
            new_path = os.path.join(assets_dir, new_filename)
            
            try:
                shutil.copy2(file_path, new_path)
                self.photo_path = new_path
                self.update_photo_preview()
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible de copier l'image: {e}")

    def save_data(self):
        if not self.txt_nom.text().strip():
            QMessageBox.warning(self, "Attention", "Le nom de l'employé est requis.")
            return
            
        def clean_date(d_str, field_name):
            d = d_str.strip()
            if not d:
                return None
            from datetime import datetime
            try:
                datetime.strptime(d, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"La date '{d}' pour '{field_name}' est invalide.\nLe format attendu est YYYY-MM-DD.")
            return d
            
        try:
            date_naissance = clean_date(self.txt_naissance.text(), "Date Naissance")
            date_embauche = clean_date(self.txt_embauche.text(), "Date Embauche")
            date_cnas = clean_date(self.txt_cnas.text(), "Date Inscription CNAS")
            date_fin_contrat = clean_date(self.txt_fin_contrat.text(), "Fin de Contrat")
            date_demission = clean_date(self.txt_demission.text(), "Date de Démission")
        except ValueError as e:
            QMessageBox.warning(self, "Erreur de Date", str(e))
            return
            
        data = {
            "nom_prenom": self.txt_nom.text().strip(),
            "fonction": self.txt_fonction.text().strip(),
            "salaire_base": self.val_salaire.value(),
            "date_naissance": date_naissance,
            "lieu_naissance": self.txt_lieu_naissance.text().strip(),
            "adresse": self.txt_adresse.text().strip(),
            "tel_1": self.txt_tel1.text().strip(),
            "tel_2": self.txt_tel2.text().strip(),
            "nin": self.txt_nin.text().strip(),
            "nss": self.txt_nss.text().strip(),
            "n_anem": self.txt_anem.text().strip(),
            "date_embauche": date_embauche,
            "date_inscription_cnas": date_cnas,
            "type_contrat": self.cb_type_contrat.currentText(),
            "date_fin_contrat": date_fin_contrat,
            "date_demission": date_demission,
            "remarque_drh": self.txt_remarque.text().strip(),
            "heures_travail_jour": self.val_heures_travail.value(),
            "photo_path": self.photo_path
        }

        if self.record:
            success = data_manager.hr.update_drh_employe(self.record['id_employe'], data)
        else:
            success = data_manager.hr.add_drh_employe(data)
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

class PresenceDialog(BaseDialog):
    def __init__(self, parent=None, record=None):
        super().__init__("Modifier Présence" if record else "Pointer Présence", parent)
        self.record = record
        
        self.cb_employe = QComboBox()
        self.load_employes()
        
        self.txt_date = QDateEdit()
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setCalendarPopup(True)
        
        self.cb_etat = QComboBox()
        self.cb_etat.addItems([
            "PRESENT", "RECUPERATION", "GARDE_NUIT", 
            "GARDE_VENDREDI_JOUR", "GARDE_VENDREDI_NUIT", 
            "ABSENCE", "CONGE_MALADIE", "CONGE", "NON_CONSIDERE"
        ])
        
        self.val_hs = QDoubleSpinBox()
        self.val_hs.setSuffix(" Heures")
        
        self.form_layout.addRow("Employé:", self.cb_employe)
        self.form_layout.addRow("Date:", self.txt_date)
        self.form_layout.addRow("État:", self.cb_etat)
        self.form_layout.addRow("Heures Sup:", self.val_hs)

        if record:
            idx = self.cb_employe.findData(record.get('id_employe'))
            if idx >= 0:
                self.cb_employe.setCurrentIndex(idx)
            if record.get('date_presence'):
                self.txt_date.setDate(QDate.fromString(str(record['date_presence']), "yyyy-MM-dd"))
            self.cb_etat.setCurrentText(str(record.get('etat_jour', 'PRESENT')))
            self.val_hs.setValue(float(record.get('heures_sup', 0.0) or 0.0))

    def load_employes(self):
        employes = data_manager.hr.get_employes_list()
        for emp in employes:
            self.cb_employe.addItem(emp['nom_prenom'], emp['id_employe'])

    def save_data(self):
        emp_id = self.cb_employe.currentData()
        if not emp_id:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord ajouter des employés.")
            return
            
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        if self.record:
            success, _ = data_manager.db.update_record(
                "Presences", "id_presence", self.record['id_presence'],
                {
                    "id_employe": emp_id,
                    "date_presence": date_str,
                    "etat_jour": self.cb_etat.currentText(),
                    "heures_sup": self.val_hs.value()
                }
            )
        else:
            success = data_manager.hr.add_presence(
                emp_id, date_str, self.cb_etat.currentText(), self.val_hs.value()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

class FichePaieDialog(BaseDialog):
    def __init__(self, parent=None, record=None):
        super().__init__("Modifier Fiche de Paie" if record else "Générer Fiche de Paie", parent)
        self.record = record
        self.setMinimumWidth(500)
        
        self.cb_employe = QComboBox()
        self.load_employes()
        self.cb_employe.currentIndexChanged.connect(self.on_employe_changed)
        
        self.txt_mois = QSpinBox()
        self.txt_mois.setRange(1, 12)
        self.txt_mois.setValue(QDate.currentDate().month())
        
        self.txt_annee = QSpinBox()
        self.txt_annee.setRange(2020, 2050)
        self.txt_annee.setValue(QDate.currentDate().year())
        
        self.lbl_salaire_base = QLabel("0.00 DZD")
        self.lbl_salaire_base.setStyleSheet("font-weight: bold; color: #0f6b63;")
        
        self.val_prime = QDoubleSpinBox()
        self.val_prime.setMaximum(999999999.0)
        
        self.val_deplacement = QDoubleSpinBox()
        self.val_deplacement.setMaximum(999999999.0)
        
        self.val_garde_nuit = QDoubleSpinBox()
        self.val_garde_nuit.setMaximum(999999999.0)
        
        self.val_garde_vj = QDoubleSpinBox()
        self.val_garde_vj.setMaximum(999999999.0)
        
        self.val_garde_vn = QDoubleSpinBox()
        self.val_garde_vn.setMaximum(999999999.0)
        
        self.val_hs_montant = QDoubleSpinBox()
        self.val_hs_montant.setMaximum(999999999.0)
        
        self.val_conge = QDoubleSpinBox()
        self.val_conge.setMaximum(999999999.0)
        
        self.val_retenue = QDoubleSpinBox()
        self.val_retenue.setMaximum(999999999.0)
        
        self.val_penalites = QDoubleSpinBox()
        self.val_penalites.setMaximum(999999999.0)
        
        self.val_avances = QDoubleSpinBox()
        self.val_avances.setMaximum(999999999.0)
        
        self.val_net = QDoubleSpinBox()
        self.val_net.setMaximum(999999999.0)
        
        self.txt_remarques = QLineEdit()
        
        for widget in [self.val_prime, self.val_deplacement, self.val_garde_nuit, 
                       self.val_garde_vj, self.val_garde_vn, self.val_hs_montant, 
                       self.val_conge, self.val_retenue, self.val_penalites, self.val_avances]:
            widget.valueChanged.connect(self.calculate_net)
            
        self.form_layout.addRow("Employé:", self.cb_employe)
        self.form_layout.addRow("Mois:", self.txt_mois)
        self.form_layout.addRow("Année:", self.txt_annee)
        self.form_layout.addRow("Salaire de Base:", self.lbl_salaire_base)
        self.form_layout.addRow("Prime:", self.val_prime)
        self.form_layout.addRow("Déplacement:", self.val_deplacement)
        self.form_layout.addRow("Garde Nuit:", self.val_garde_nuit)
        self.form_layout.addRow("Garde Vendredi Jour:", self.val_garde_vj)
        self.form_layout.addRow("Garde Vendredi Nuit:", self.val_garde_vn)
        self.form_layout.addRow("Heures supplémentaires (Montant HS):", self.val_hs_montant)
        self.form_layout.addRow("Congé:", self.val_conge)
        self.form_layout.addRow("Retenue Absence:", self.val_retenue)
        self.form_layout.addRow("Pénalités:", self.val_penalites)
        self.form_layout.addRow("Avances:", self.val_avances)
        self.form_layout.addRow("Net à Payer:", self.val_net)
        self.form_layout.addRow("Remarques:", self.txt_remarques)
        
        self.current_base_salary = 0.0
        self.on_employe_changed()

        if record:
            idx = self.cb_employe.findData(record.get('id_employe'))
            if idx >= 0:
                self.cb_employe.setCurrentIndex(idx)
            self.cb_employe.setEnabled(False)
            self.txt_mois.setValue(record.get('mois', 1))
            self.txt_mois.setEnabled(False)
            self.txt_annee.setValue(record.get('annee', 2026))
            self.txt_annee.setEnabled(False)
            
            self.val_prime.setValue(float(record.get('prime', 0.0) or 0.0))
            self.val_deplacement.setValue(float(record.get('deplacement', 0.0) or 0.0))
            self.val_garde_nuit.setValue(float(record.get('garde_nuit', 0.0) or 0.0))
            self.val_garde_vj.setValue(float(record.get('garde_vendredi_jour', 0.0) or 0.0))
            self.val_garde_vn.setValue(float(record.get('garde_vendredi_nuit', 0.0) or 0.0))
            self.val_hs_montant.setValue(float(record.get('heures_sup_montant', 0.0) or 0.0))
            self.val_conge.setValue(float(record.get('conge', 0.0) or 0.0))
            self.val_retenue.setValue(float(record.get('retenue_absence', 0.0) or 0.0))
            self.val_penalites.setValue(float(record.get('penalites', 0.0) or 0.0))
            self.val_avances.setValue(float(record.get('avances', 0.0) or 0.0))
            self.val_net.setValue(float(record.get('net_a_payer', 0.0) or 0.0))
            self.txt_remarques.setText(record.get('remarques', '') or '')

    def load_employes(self):
        employes = data_manager.hr.get_employes_list()
        for emp in employes:
            self.cb_employe.addItem(emp['nom_prenom'], emp['id_employe'])

    def on_employe_changed(self):
        emp_id = self.cb_employe.currentData()
        if emp_id:
            self.current_base_salary = data_manager.hr.get_employe_base_salary(emp_id)
            self.lbl_salaire_base.setText(f"{self.current_base_salary:.2f} DZD")
            self.calculate_net()

    def calculate_net(self):
        net = (
            self.current_base_salary + 
            self.val_prime.value() + 
            self.val_deplacement.value() + 
            self.val_garde_nuit.value() + 
            self.val_garde_vj.value() + 
            self.val_garde_vn.value() + 
            self.val_hs_montant.value() + 
            self.val_conge.value() - 
            self.val_retenue.value() - 
            self.val_penalites.value() - 
            self.val_avances.value()
        )
        self.val_net.setValue(max(0.0, net))

    def save_data(self):
        emp_id = self.cb_employe.currentData()
        if not emp_id:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord ajouter des employés.")
            return
            
        if self.record:
            success, _ = data_manager.db.update_record(
                "Fiches_Paie", "id_paie", self.record['id_paie'],
                {
                    "prime": self.val_prime.value(),
                    "deplacement": self.val_deplacement.value(),
                    "garde_nuit": self.val_garde_nuit.value(),
                    "garde_vendredi_jour": self.val_garde_vj.value(),
                    "garde_vendredi_nuit": self.val_garde_vn.value(),
                    "heures_sup_montant": self.val_hs_montant.value(),
                    "conge": self.val_conge.value(),
                    "retenue_absence": self.val_retenue.value(),
                    "penalites": self.val_penalites.value(),
                    "avances": self.val_avances.value(),
                    "net_a_payer": self.val_net.value(),
                    "remarques": self.txt_remarques.text().strip()
                }
            )
        else:
            success = data_manager.hr.add_fiche_paie(
                emp_id, self.txt_mois.value(), self.txt_annee.value(),
                self.val_prime.value(), self.val_deplacement.value(), self.val_garde_nuit.value(),
                self.val_garde_vj.value(), self.val_garde_vn.value(), self.val_hs_montant.value(),
                self.val_conge.value(), self.val_retenue.value(), self.val_penalites.value(),
                self.val_avances.value(), self.val_net.value(), self.txt_remarques.text().strip()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

class HeuresPresenceDialog(BaseDialog):
    def __init__(self, id_employe, nom_prenom, date_presence, parent=None):
        super().__init__(f"Pointage des heures - {nom_prenom}", parent)
        self.id_employe = id_employe
        self.date_presence = date_presence
        self.setMinimumWidth(350)
        
        from PySide6.QtWidgets import QTimeEdit, QLabel, QFormLayout, QCheckBox, QHBoxLayout
        from PySide6.QtCore import QTime
        import datetime
        
        lbl_date = QLabel(f"<b>Date:</b> {date_presence}")
        lbl_date.setStyleSheet("font-size: 14px; color: #34495e; margin-bottom: 10px;")
        
        # Entree
        self.chk_entree = QCheckBox("Définir Heure d'Entrée")
        self.chk_entree.setChecked(True)
        self.time_entree = QTimeEdit()
        self.time_entree.setDisplayFormat("HH:mm")
        self.time_entree.setTime(QTime(8, 0))
        self.chk_entree.toggled.connect(self.time_entree.setEnabled)
        
        layout_entree = QHBoxLayout()
        layout_entree.addWidget(self.chk_entree)
        layout_entree.addWidget(self.time_entree)
        
        # Sortie
        self.chk_sortie = QCheckBox("Définir Heure de Sortie")
        self.chk_sortie.setChecked(True)
        self.time_sortie = QTimeEdit()
        self.time_sortie.setDisplayFormat("HH:mm")
        self.time_sortie.setTime(QTime(16, 30))
        self.chk_sortie.toggled.connect(self.time_sortie.setEnabled)
        
        layout_sortie = QHBoxLayout()
        layout_sortie.addWidget(self.chk_sortie)
        layout_sortie.addWidget(self.time_sortie)
        
        # Load existing if available
        record = data_manager.hr.get_presence_hours(id_employe, date_presence)
        if record:
            entree = record.get('heure_entree')
            sortie = record.get('heure_sortie')
            
            if entree:
                self.chk_entree.setChecked(True)
                if isinstance(entree, datetime.timedelta):
                    hours = entree.seconds // 3600
                    minutes = (entree.seconds % 3600) // 60
                    self.time_entree.setTime(QTime(hours, minutes))
                else:
                    self.time_entree.setTime(QTime.fromString(str(entree), "HH:mm:ss"))
            else:
                self.chk_entree.setChecked(False)
                self.time_entree.setEnabled(False)
                    
            if sortie:
                self.chk_sortie.setChecked(True)
                if isinstance(sortie, datetime.timedelta):
                    hours = sortie.seconds // 3600
                    minutes = (sortie.seconds % 3600) // 60
                    self.time_sortie.setTime(QTime(hours, minutes))
                else:
                    self.time_sortie.setTime(QTime.fromString(str(sortie), "HH:mm:ss"))
            else:
                self.chk_sortie.setChecked(False)
                self.time_sortie.setEnabled(False)
        else:
            # Default state when creating a new record
            self.chk_entree.setChecked(False)
            self.time_entree.setEnabled(False)
            self.chk_sortie.setChecked(False)
            self.time_sortie.setEnabled(False)
        
        self.layout().insertWidget(1, lbl_date)
        
        form = QFormLayout()
        form.addRow(layout_entree)
        form.addRow(layout_sortie)
        self.layout().insertLayout(2, form)

    def save_data(self):
        entree_str = self.time_entree.time().toString("HH:mm:ss") if self.chk_entree.isChecked() else None
        sortie_str = self.time_sortie.time().toString("HH:mm:ss") if self.chk_sortie.isChecked() else None
        
        success = data_manager.hr.update_presence_hours(
            self.id_employe, self.date_presence, entree_str, sortie_str
        )
        
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de la sauvegarde des heures.")

class RemarquePresenceDialog(BaseDialog):
    def __init__(self, eid, nom_prenom, current_remarque, parent=None):
        super().__init__('Remarque Mensuelle', parent)
        self.eid = eid
        
        self.lbl_info = QLabel(f'Employé : {nom_prenom}')
        self.lbl_info.setStyleSheet('font-weight: bold; color: #007572;')
        
        self.txt_remarque = QTextEdit()
        self.txt_remarque.setPlainText(current_remarque)
        self.txt_remarque.setPlaceholderText('Entrez la remarque ici...')
        self.txt_remarque.setMinimumHeight(100)
        
        self.form_layout.addRow(self.lbl_info)
        self.form_layout.addRow(self.txt_remarque)
        
    def get_remarque(self):
        return self.txt_remarque.toPlainText().strip()
    
    def save_data(self):
        self.accept()
