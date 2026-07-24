import os
import json
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox, QFormLayout, QDoubleSpinBox, 
    QFileDialog, QColorDialog, QTabWidget, QScrollArea, 
    QFrame, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QRectF, QRect
from PySide6.QtGui import QColor, QPixmap, QFont, QPainter, QPen, QBrush

class PdfConfigWidget(QWidget):
    settings_updated = Signal(dict)

    def __init__(self, parent=None, settings_input="pdf_settings.json"):
        super().__init__(parent)
        
        if isinstance(settings_input, dict):
            self.settings_path = "pdf_settings.json"
            self.settings = {**self.get_default_settings(), **settings_input}
        else:
            self.settings_path = settings_input
            self.settings = self.load_settings()
            
        self.init_ui()

    def get_default_settings(self):
        return {
            "theme_color": "#007572",
            "doc_title": "MODERNLAM",
            "banner_height_cm": 4.8, 
            "banner_path": "",
            "banner_img_x_cm": 0.0,
            "banner_img_y_cm": 0.0,
            "banner_img_w_cm": 21.0,
            "banner_img_h_cm": 4.8,
            "table_start_y_cm": 8.0,
            "footer_left_label": "Signature de l'Agent",
            "footer_right_label": "Visa Direction",
            "nif": "",
            "rip": ""
        }

    def load_settings(self):
        defaults = self.get_default_settings()
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {**defaults, **data}
            except Exception as e:
                logging.error(f"Error loading PDF settings: {e}")
                return defaults
        return defaults

    def get_updated_settings(self):
        return self.settings

    def save_settings(self):
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Succès", "Le modèle PDF a été mis à jour avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de l'enregistrement: {e}")

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)

        control_panel = QWidget()
        control_panel.setFixedWidth(450)
        vbox = QVBoxLayout(control_panel)
        
        tabs = QTabWidget()
        tabs.setStyleSheet("QTabBar::tab { height: 35px; width: 140px; }")

        # Tab 1: Configuration PDF (ضبط PDF)
        tab_pdf = QScrollArea()
        pdf_content = QWidget()
        pdf_vbox = QVBoxLayout(pdf_content)

        # 1.1 Identité
        group_identity = QGroupBox("Identité & Zone Header")
        identity_form = QFormLayout(group_identity)
        self.edit_title = QLineEdit(self.settings.get('doc_title', ''))
        self.btn_color = QPushButton("Changer la couleur du thème")
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(50, 20)
        self.color_preview.setStyleSheet(f"background-color: {self.settings.get('theme_color', '#007572')}; border: 1px solid gray;")
        self.sp_banner_total_h = self._create_spin(1.0, 15.0, self.settings.get('banner_height_cm', 4.8))
        identity_form.addRow("Titre Document:", self.edit_title)
        identity_form.addRow("Couleur Thème:", self.btn_color)
        identity_form.addRow("", self.color_preview)
        identity_form.addRow("Hauteur Zone Header (cm):", self.sp_banner_total_h)
        pdf_vbox.addWidget(group_identity)

        # 1.2 Image Banner
        group_image = QGroupBox("Position & Taille de l'Image (Banner)")
        image_form = QFormLayout(group_image)
        self.btn_banner = QPushButton("Choisir l'image...")
        current_path = self.settings.get('banner_path', "")
        self.lbl_path = QLabel(os.path.basename(current_path) if current_path else "Aucune image")
        self.lbl_path.setStyleSheet("color: #2c3e50; font-weight: bold; font-size: 10px;")
        self.sp_img_x = self._create_spin(-5.0, 21.0, self.settings.get('banner_img_x_cm', 0.0))
        self.sp_img_y = self._create_spin(-5.0, 10.0, self.settings.get('banner_img_y_cm', 0.0))
        self.sp_img_w = self._create_spin(1.0, 30.0, self.settings.get('banner_img_w_cm', 21.0))
        self.sp_img_h = self._create_spin(1.0, 15.0, self.settings.get('banner_img_h_cm', 4.8))
        image_form.addRow(self.btn_banner, self.lbl_path)
        image_form.addRow("Position X (cm):", self.sp_img_x)
        image_form.addRow("Position Y (cm):", self.sp_img_y)
        image_form.addRow("Largeur Image (cm):", self.sp_img_w)
        image_form.addRow("Hauteur Image (cm):", self.sp_img_h)
        pdf_vbox.addWidget(group_image)

        # 1.3 Marges & Signatures
        group_footer = QGroupBox("Mise en page & Pied de page")
        footer_form = QFormLayout(group_footer)
        self.sp_table_y = self._create_spin(5, 25, self.settings.get('table_start_y_cm', 8.0))
        self.edit_f_left = QLineEdit(self.settings.get('footer_left_label', ''))
        self.edit_f_right = QLineEdit(self.settings.get('footer_right_label', ''))
        footer_form.addRow("Début Tableau Y (cm):", self.sp_table_y)
        footer_form.addRow("Signature Gauche:", self.edit_f_left)
        footer_form.addRow("Signature Droite:", self.edit_f_right)
        pdf_vbox.addWidget(group_footer)

        tab_pdf.setWidget(pdf_content)
        tab_pdf.setWidgetResizable(True)
        tabs.addTab(tab_pdf, "ضبط PDF")

        # Tab 2: Informations Labo (NIF & RIP)
        tab_info = QScrollArea()
        info_content = QWidget()
        info_form = QFormLayout(info_content)
        
        self.edit_nif = QLineEdit(self.settings.get('nif', ''))
        self.edit_rip = QLineEdit(self.settings.get('rip', ''))
        info_form.addRow("NIF (Identifiant Fiscal):", self.edit_nif)
        info_form.addRow("RIP (Compte Bancaire):", self.edit_rip)
        
        tab_info.setWidget(info_content)
        tab_info.setWidgetResizable(True)
        tabs.addTab(tab_info, "Informations")

        vbox.addWidget(tabs)
        
        self.btn_save = QPushButton("💾 Enregistrer les paramètres")
        self.btn_save.setStyleSheet("background-color: #2e7d32; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        self.btn_save.clicked.connect(self.save_settings)
        vbox.addWidget(self.btn_save)

        preview_group = QGroupBox("Aperçu en temps réel (Simulation A4)")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_canvas = LivePreviewCanvas(self.settings)
        preview_layout.addWidget(self.preview_canvas)

        main_layout.addWidget(control_panel)
        main_layout.addWidget(preview_group, stretch=1)

        self._connect_signals()
        self.btn_color.clicked.connect(self.pick_color)
        self.btn_banner.clicked.connect(self.pick_banner)
        self.sync_settings()

    def _create_spin(self, min_v, max_v, current_v):
        sb = QDoubleSpinBox()
        sb.setRange(min_v, max_v)
        sb.setValue(float(current_v))
        sb.setSingleStep(0.1)
        sb.setSuffix(" cm")
        return sb

    def _connect_signals(self):
        txt_widgets = [self.edit_title, self.edit_f_left, self.edit_f_right, self.edit_nif, self.edit_rip]
        for w in txt_widgets: w.textChanged.connect(self.sync_settings)
        spin_widgets = [
            self.sp_banner_total_h, self.sp_img_x, self.sp_img_y, self.sp_img_w, self.sp_img_h,
            self.sp_table_y
        ]
        for s in spin_widgets: s.valueChanged.connect(self.sync_settings)

    def pick_banner(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir Banner", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.settings['banner_path'] = path
            self.lbl_path.setText(os.path.basename(path))
            self.sync_settings()

    def pick_color(self):
        curr = self.settings.get('theme_color', "#007572")
        c = QColorDialog.getColor(QColor(curr), self)
        if c.isValid():
            self.settings['theme_color'] = c.name()
            self.color_preview.setStyleSheet(f"background-color: {c.name()}; border: 1px solid gray;")
            self.sync_settings()

    def sync_settings(self):
        self.settings.update({
            "doc_title": self.edit_title.text(),
            "nif": self.edit_nif.text().strip(),
            "rip": self.edit_rip.text().strip(),
            "banner_height_cm": self.sp_banner_total_h.value(),
            "banner_img_x_cm": self.sp_img_x.value(),
            "banner_img_y_cm": self.sp_img_y.value(),
            "banner_img_w_cm": self.sp_img_w.value(),
            "banner_img_h_cm": self.sp_img_h.value(),
            "table_start_y_cm": self.sp_table_y.value(),
            "footer_left_label": self.edit_f_left.text(),
            "footer_right_label": self.edit_f_right.text()
        })
        self.preview_canvas.settings = self.settings
        self.preview_canvas.update()
        self.settings_updated.emit(self.settings)

class LivePreviewCanvas(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setMinimumSize(450, 600)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        scale = min(self.width() / 210, self.height() / 297) * 0.95
        p.translate(self.width() / 2, self.height() / 2)
        p.scale(scale, scale)
        p.translate(-105, -148.5)
        p.setBrush(Qt.white)
        p.setPen(QPen(Qt.black, 0.2))
        p.drawRect(0, 0, 210, 297)
        
        s = self.settings
        color = QColor(s.get('theme_color', "#007572"))
        total_h_mm = int(s.get('banner_height_cm', 4.8) * 10)
        
        p.save()
        p.setClipRect(0, 0, 210, total_h_mm)
        banner_path = s.get('banner_path', "")
        if banner_path and os.path.exists(banner_path):
            img_x = int(s.get('banner_img_x_cm', 0.0) * 10)
            img_y = int(s.get('banner_img_y_cm', 0.0) * 10)
            img_w = int(s.get('banner_img_w_cm', 21.0) * 10)
            img_h = int(s.get('banner_img_h_cm', 4.8) * 10)
            pixmap = QPixmap(banner_path)
            if not pixmap.isNull():
                p.drawPixmap(QRect(img_x, img_y, img_w, img_h), pixmap)
        else:
            p.setPen(QPen(Qt.lightGray, 0.5, Qt.DashLine))
            p.drawRect(0, 0, 210, total_h_mm)
            p.drawText(QRect(0, 0, 210, total_h_mm), Qt.AlignCenter, "Zone Image / Header")
        p.restore()
        
        p.setPen(color)
        p.setFont(QFont("Arial", 6, QFont.Bold))
        title_y = total_h_mm + 10
        p.drawText(15, title_y, f"{s.get('doc_title', 'Document')}")
        
        nif = s.get('nif', '')
        rip = s.get('rip', '')
        meta_parts = []
        if nif:
            meta_parts.append(f"NIF: {nif}")
        if rip:
            meta_parts.append(f"RIP: {rip}")
        if meta_parts:
            p.setPen(Qt.gray)
            p.setFont(QFont("Arial", 4, QFont.Normal))
            p.drawText(15, title_y + 8, "   |   ".join(meta_parts))
        
        table_y = int(s.get('table_start_y_cm', 8.0) * 10)
        p.setBrush(color)
        p.setPen(Qt.NoPen)
        p.drawRect(10, table_y, 190, 8)
        p.setPen(Qt.black)
        
        p.setFont(QFont("Arial", 4, QFont.Bold))
        p.drawText(15, 270, s.get('footer_left_label', ''))
        p.drawText(130, 270, s.get('footer_right_label', ''))
