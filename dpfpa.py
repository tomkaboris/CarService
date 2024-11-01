# main.py
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
    connect, search_records, delete_records,
    get_monthly_report, get_yearly_report
)
from insert_form import InsertForm
from fpdf import FPDF
from datetime import datetime


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

        # Ask the user where to save the PDF file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Sacuvaj PDF Izvestaj", "", "PDF Files (*.pdf)", options=options)
        if not file_path:
            return  # User cancelled the save dialog

        # Create a PDF object
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)

        # Add izvestaj title
        pdf.cell(0, 10, report_title, ln=True, align='C')

        # Add date
        current_date = datetime.now().strftime('%Y-%m-%d')
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f'Datum generisanja: {current_date}', ln=True, align='R')
        pdf.ln(10)  # Add space

        # Create and insert the pie chart
        chart_path = self.create_chart(report_data, report_title)
        pdf.image(chart_path, x=10, y=None, w=pdf.w - 20)  # Adjust image size and position
        pdf.ln(10)  # Add space after the chart

        # Table headers (optional)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(60, 10, 'Tip usluge', border=1)
        pdf.cell(30, 10, 'Kolicina', border=1, align='R')
        pdf.cell(50, 10, 'Prosecna Cena', border=1, align='R')
        pdf.cell(50, 10, 'Ukupno Zaradjeno', border=1, align='R')
        pdf.ln()

        # Table data (optional)
        pdf.set_font("Arial", '', 12)
        for row in report_data:
            tip_usluge = row[0]
            count = row[1]
            avg_cena = round(row[2], 2)
            sum_cena = row[3]
            pdf.cell(60, 10, str(tip_usluge), border=1)
            pdf.cell(30, 10, str(count), border=1, align='R')
            pdf.cell(50, 10, f'{avg_cena:.2f}', border=1, align='R')
            pdf.cell(50, 10, str(sum_cena), border=1, align='R')
            pdf.ln()

        # Save the PDF to the selected file path
        try:
            pdf.output(file_path)
            QMessageBox.information(self, 'Success', f'Izvestaj je sacuvan uspesno {file_path}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Greska: {e}')

        # Cleanup the chart image
        if os.path.exists(chart_path):
            os.remove(chart_path)

    def create_chart(self, report_data, report_title):
        # Extract data for the pie chart
        tip_usluge = [row[0] for row in report_data]
        sum_cena = [row[3] for row in report_data]

        # Create a pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(sum_cena, labels=tip_usluge, autopct='%1.1f%%', startangle=140)
        plt.title(f'{report_title} - Prinosa')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()

        # Save the chart as an image file
        chart_path = 'chart.png'
        plt.savefig(chart_path)
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
            delete_action = QAction('Obrisi', self)
            delete_action.triggered.connect(lambda: self.delete_record(record_id))
            menu.addAction(delete_action)

            # Display the menu
            menu.exec_(self.table.viewport().mapToGlobal(position))

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
