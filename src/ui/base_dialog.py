from PySide6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLabel

class BaseDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(12)
        
        self.btn_save = QPushButton("Enregistrer")
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setObjectName("secondary_btn")
        
        self.btn_save.clicked.connect(self.save_data)
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_save)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Dialog Title header
        header = QLabel(title)
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f6b63; margin-bottom: 10px;")
        main_layout.addWidget(header)
        
        main_layout.addLayout(self.form_layout)
        main_layout.addLayout(button_layout)

    def save_data(self):
        self.accept()
