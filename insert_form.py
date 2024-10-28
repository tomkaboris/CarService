# insert_form.py
import os
import shutil
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QTextEdit, QDateEdit
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDate, pyqtSignal
from database import insert_record, get_tip_usluge_list

class InsertForm(QWidget):
    record_inserted = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Unos podataka')
        self.setWindowIcon(QIcon('./tb.ico'))  # Replace 'tb.ico' with the path to your icon file
        
        # Backup database if older than one day
        self.backup_database_if_old()

        self.initUI()

    def backup_database_if_old(self):
        db_path = 'app_data.db'
        
        # Check if the database file exists
        if os.path.exists(db_path):
            # Get the modification time of the database file
            modification_time = datetime.fromtimestamp(os.path.getmtime(db_path))
            current_time = datetime.now()
            
            # Check if the file is older than one day
            if current_time - modification_time > timedelta(days=30):
                # Create a backup filename with a timestamp
                backup_filename = f"backup_app_data_{modification_time.strftime('%Y%m%d_%H%M%S')}.db"
                backup_path = os.path.join('backups', backup_filename)

                # Ensure the backups directory exists
                os.makedirs('backups', exist_ok=True)

                # Copy the database file to the backup location
                shutil.copy2(db_path, backup_path)
                print(f"Backup created: {backup_path}")

    def initUI(self):
        layout = QFormLayout()

        self.datum_input = QDateEdit()
        self.datum_input.setCalendarPopup(True)
        self.datum_input.setDate(QDate.currentDate())

        self.broj_sasije_input = QLineEdit()
        self.registarska_oznaka_input = QLineEdit()
        self.marka_model_input = QLineEdit()

        self.tip_usluge_input = QComboBox()
        tipovi_usluge = get_tip_usluge_list()
        for tip in tipovi_usluge:
            self.tip_usluge_input.addItem(tip[1], tip[0])  # tip[1]=naziv, tip[0]=id

        self.opis_rada_input = QTextEdit()
        self.cena_input = QLineEdit()

        self.submit_button = QPushButton('Enter')
        self.submit_button.clicked.connect(self.submit_record)

        layout.addRow('Datum:', self.datum_input)
        layout.addRow('Broj šasije:', self.broj_sasije_input)
        layout.addRow('Registarska oznaka:', self.registarska_oznaka_input)
        layout.addRow('Marka/Model:', self.marka_model_input)
        layout.addRow('Tip usluge:', self.tip_usluge_input)
        layout.addRow('Opis rada:', self.opis_rada_input)
        layout.addRow('Cena:', self.cena_input)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def submit_record(self):
        datum = self.datum_input.date().toString('yyyy-MM-dd')
        broj_sasije = self.broj_sasije_input.text()
        registarska_oznaka = self.registarska_oznaka_input.text()
        marka_model = self.marka_model_input.text()
        tip_usluge_id = self.tip_usluge_input.currentData()
        opis_rada = self.opis_rada_input.toPlainText()
        cena_text = self.cena_input.text()

        if not cena_text.isdigit():
            QMessageBox.warning(self, 'Error', 'Cena mora biti broj.')
            return
        cena = int(cena_text)

        if broj_sasije and registarska_oznaka and marka_model:
            insert_record(datum, broj_sasije, registarska_oznaka, marka_model, tip_usluge_id, opis_rada, cena)
            QMessageBox.information(self, 'Success', 'Rekord je unet usposno.')
            self.record_inserted.emit()  # Emit the signal
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Unesite validne informacije.')
