# Car Service Management Application

**Version:** 1.0

## Purpose

The Car Service Management Application is designed to help manage and keep track of all car services performed, including detailed records for each service. With a user-friendly interface, this application allows users to add new service records, search existing records, and generate monthly or yearly reports to analyze service trends and performance.

## Features

- **Insert Service Records**: Easily record details such as the type of service (e.g., 'Servis', 'Popravka', 'Zamena delova', 'Dijagnostika', 'Gume', 'Klima', 'DPF'), price, car serial number, and other relevant details.
- **Search and View Records**: Quickly search through records to view all services performed on a car, including specific details.
- **Generate Reports**: Create monthly and yearly reports that provide insights into the most frequently performed services, total earnings, and other useful statistics.

## Requirements

This application requires Python and several libraries. Install the following dependencies before running the application:

- **Python**: Version 3.9.13 or newer
- **Python Libraries**:
  - `PyQt5==5.15.11`: for the graphical user interface
  - `fpdf2==2.8.1`: for PDF generation
  - `matplotlib==3.9.2`: for chart generation
  - `pyinstaller==6.11.0`: for creating standalone executables
  - `cx_Freeze==7.2.3`: for freezing the Python application into a Windows executable

### Installation

To install the required libraries, you can use the following pip commands:

```bash
pip install PyQt5==5.15.11 fpdf2==2.8.1 matplotlib==3.9.2 pyinstaller==6.11.0 cx_Freeze==7.2.3
```
