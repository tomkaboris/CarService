# main
import sys
import os
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox,
    QLineEdit, QAbstractItemView, QMenu, QAction, QFileDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QPoint
from database import (
    connect, search_records, delete_records, get_monthly_report,
    get_yearly_report, insert_record, get_tip_usluge_list, get_record_by_id
)
from insert_form import InsertForm
from fpdf import FPDF
from datetime import datetime
import tempfile
import webbrowser

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DPF PA')
        self.setMinimumSize(800, 600)

        self.setWindowIcon(QIcon('./tb.ico'))  # Replace 'tb.ico' with the path to your icon file

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Top layout with buttons
        top_layout = QHBoxLayout()

        self.insert_button = QPushButton('Unesi')
        self.insert_button.clicked.connect(self.open_insert_form)

        self.report_button = QPushButton('Izvestaj')
        self.report_button.clicked.connect(self.show_reports_menu)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Unesi Broj šasije za pretragu')

        self.search_button = QPushButton('Trazi')
        self.search_button.clicked.connect(self.search)

        top_layout.addWidget(self.insert_button)
        top_layout.addWidget(self.report_button)
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.search_button)

        # Table to display records
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['ID', 'Datum', 'Broj šasije', 'Registarska oznaka',
                                              'Marka/Model', 'Tip usluge', 'Opis rada', 'Cena'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Enable custom context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        # Load all records initially
        self.search()

    def open_insert_form(self):
        self.insert_form = InsertForm()
        self.insert_form.record_inserted.connect(self.search)
        self.insert_form.show()

    def show_reports_menu(self):
        # Create a menu to select between Monthly and Yearly reports
        menu = QMessageBox(self)
        menu.setWindowTitle('Izaberi Izvestaj')
        menu.setText('Izaberi koji izvestaj zelis:')
        monthly_button = menu.addButton('Mesecni Izvestaj', QMessageBox.ActionRole)
        yearly_button = menu.addButton('Godisnji Izvestaj', QMessageBox.ActionRole)
        cancel_button = menu.addButton('Cancel', QMessageBox.RejectRole)
        menu.exec_()

        if menu.clickedButton() == monthly_button:
            self.show_report('mesecni')
        elif menu.clickedButton() == yearly_button:
            self.show_report('godisnji')
        else:
            pass  # Do nothing if cancelled

    def show_report(self, report_type):
        if report_type == 'mesecni':
            report_data = get_monthly_report()
            report_title = 'Mesecni Izvestaj'
            self.generate_pdf_report(report_data, report_title)
        elif report_type == 'godisnji':
            report_data = get_yearly_report()
            report_title = 'Godisnji Izvestaj'
            self.generate_pdf_report(report_data, report_title)
        else:
            return

    def generate_pdf_report(self, report_data, report_title):
        if not report_data:
            QMessageBox.information(self, 'Nema podataka', 'Nema podataka za selektovani period.')
            return

        # Kreiranje PDF-a
        pdf = FPDF()

        # Dodavanje DejaVu fontova (obični i podebljani)
        font_path_regular = os.path.join(os.path.dirname(__file__), './DejaVuSans.ttf')
        font_path_bold = os.path.join(os.path.dirname(__file__), './DejaVuSans-Bold.ttf')
        if not os.path.exists(font_path_regular) or not os.path.exists(font_path_bold):
            QMessageBox.warning(self, 'Error', 'Nedostaje font fajl (DejaVuSans.ttf ili DejaVuSans-Bold.ttf)')
            return

        pdf.add_font("DejaVu", "", font_path_regular)
        pdf.add_font("DejaVu", "B", font_path_bold)

        # Stranica 1 - Pie chart
        pdf.add_page()
        pdf.set_font("DejaVu", 'B', 16)
        pdf.cell(0, 10, report_title, ln=True, align='C')
        pdf.ln(10)

        # Dodavanje pie chart-a
        chart_path = self.create_chart_with_legend(report_data, report_title)
        pdf.image(chart_path, x=10, y=40, w=pdf.w - 20)

        # Datum generisanja u donjem desnom uglu druge stranice
        pdf.set_y(-15)
        pdf.set_font("DejaVu", '', 10)
        pdf.cell(0, 10, f'Datum generisanja: {datetime.now().strftime("%Y-%m-%d")}', align='R')
        pdf.ln(10)

        # Stranica 2 - Tabela sa podacima
        # pdf.add_page()
        pdf.set_font("DejaVu", 'B', 12)
        pdf.cell(60, 10, 'Tip usluge', border=1)
        pdf.cell(30, 10, 'Kolicina', border=1, align='R')
        pdf.cell(50, 10, 'Prosecna Cena', border=1, align='R')
        pdf.cell(50, 10, 'Ukupno Zaradjeno', border=1, align='R')
        pdf.ln()

        # Podaci u tabeli
        pdf.set_font("DejaVu", '', 12)
        for row in report_data:
            tip_usluge, count, avg_cena, sum_cena = row
            pdf.cell(60, 10, str(tip_usluge), border=1)
            pdf.cell(30, 10, str(count), border=1, align='R')
            pdf.cell(50, 10, f'{avg_cena:.2f}', border=1, align='R')
            pdf.cell(50, 10, str(sum_cena), border=1, align='R')
            pdf.ln()

        # Kreiranje privremenog fajla i otvaranje
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            pdf.output(tmp_file.name)
            webbrowser.open(tmp_file.name)

        # Brisanje pie chart slike
        if os.path.exists(chart_path):
            os.remove(chart_path)

    def create_chart_with_legend(self, report_data, report_title):
        # Kreiranje pie chart-a
        tip_usluge = [row[0] for row in report_data]
        sum_cena = [row[3] for row in report_data]

        plt.figure(figsize=(8, 8))
        wedges, texts, autotexts = plt.pie(sum_cena, autopct='%1.1f%%', startangle=140)

        # Dodavanje legende
        plt.legend(wedges, tip_usluge, title="Tip usluge", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.axis('equal')  # Jednaki aspekt da bi pie chart bio krug

        # Čuvanje slike pie chart-a
        chart_path = 'chart.png'
        plt.savefig(chart_path, bbox_inches='tight')  # `bbox_inches='tight'` da smanji praznine oko grafa
        plt.close()

        return chart_path

    def search(self):
        broj_sasije = self.search_input.text()
        results = search_records(broj_sasije)
        self.table.setRowCount(len(results))
        for row_idx, row_data in enumerate(results):
            for col_idx, col_data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def open_context_menu(self, position):
        indexes = self.table.selectedIndexes()
        if indexes:
            selected_row = indexes[0].row()
            record_id_item = self.table.item(selected_row, 0)  # ID is in column 0
            record_id = int(record_id_item.text())

            # Create the context menu
            menu = QMenu()
            
            # Delete action
            delete_action = QAction('Obrisi', self)
            delete_action.triggered.connect(lambda: self.delete_record(record_id))
            menu.addAction(delete_action)
            
            # Edit action
            edit_action = QAction('Izmeni', self)
            edit_action.triggered.connect(lambda: self.edit_record(record_id))
            menu.addAction(edit_action)
            
            # Print action
            print_action = QAction('Stampaj (PDF)', self)
            print_action.triggered.connect(lambda: self.print_record(record_id))
            menu.addAction(print_action)

            # Display the menu
            menu.exec_(self.table.viewport().mapToGlobal(position))

    def edit_record(self, record_id):
        # Fetch record details for editing
        record_data = get_record_by_id(record_id)
        if record_data:
            self.insert_form = InsertForm(record_id=record_id, record_data=record_data)
            self.insert_form.record_inserted.connect(self.search)
            self.insert_form.show()
        else:
            QMessageBox.warning(self, 'Error', 'Record not found for editing.')

    def print_record(self, record_id):
        # Fetch the record data for printing
        record_data = get_record_by_id(record_id)
        if not record_data:
            QMessageBox.warning(self, 'Error', 'Record not found for printing.')
            return

        # Create the PDF document
        pdf = FPDF()
        pdf.add_page()

        # Path to DejaVuSans font
        font_path = os.path.join(os.path.dirname(__file__), './DejaVuSans.ttf')
        if not os.path.exists(font_path):
            QMessageBox.warning(self, 'Error', f'Font file not found: {font_path}')
            return
        
        # Add and set the DejaVuSans font for Unicode support
        pdf.add_font("DejaVu", "", font_path)
        pdf.set_font("DejaVu", '', 12)

        # Title (using a larger font size for emphasis instead of bold)
        pdf.set_font("DejaVu", '', 16)  # Larger size for title
        pdf.cell(0, 10, f'Service broj: {record_id}', ln=True, align='C')
        pdf.ln(10)

        # Table headers and data in a vertical format
        headers = ['Broj', 'Datum', 'Broj šasije', 'Registarska oznaka', 'Marka/Model', 'Tip usluge', 'Opis rada', 'Cena']
        pdf.set_font("DejaVu", '', 12)  # Reset to normal font size
        
        # Adding each field in a separate row, with labels on the left and values on the right
        for header, value in zip(headers, record_data):
            pdf.cell(50, 10, f"{header}:", border=1, align='L')
            pdf.cell(0, 10, str(value), border=1, align='L')
            pdf.ln()

        # Move to near the bottom of the page for the signature area
        pdf.ln(20)  # Adjust this space if needed
        pdf.cell(0, 10, '', ln=True)  # Extra space before signature/stamp area
        pdf.cell(140)  # Move to the right for alignment
        
        # Signature lines
        pdf.cell(50, 10, '_________________________', 0, 1, 'R')
        pdf.cell(140)
        pdf.cell(50, 10, 'Potpis', 0, 1, 'R')
    
        # Create a temporary file and open it in the system's PDF viewer
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            pdf.output(tmp_file.name)
            webbrowser.open(tmp_file.name)  # This opens the PDF in the default viewer

    def delete_record(self, record_id):
        reply = QMessageBox.question(self, 'Potvrdi Brisanje',
                                     f'Da li si siguran da zelis da obrises record ID {record_id}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_records([record_id])
            QMessageBox.information(self, 'Success', f'Record ID {record_id} je obrisan.')
            self.search()


if __name__ == '__main__':
    connect()  # Initialize the database
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
