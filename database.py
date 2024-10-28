# database.py
import sqlite3
from datetime import datetime

def connect():
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()
    # Create the records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datum TEXT NOT NULL,
            broj_sasije TEXT NOT NULL,
            registarska_oznaka TEXT NOT NULL,
            marka_model TEXT NOT NULL,
            tip_usluge_id INTEGER NOT NULL,
            opis_rada TEXT,
            cena INTEGER,
            FOREIGN KEY (tip_usluge_id) REFERENCES tip_usluge(id)
        )
    ''')
    # Create the tip_usluge table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tip_usluge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT NOT NULL
        )
    ''')
    # Insert default tip_usluge if table is empty
    cursor.execute('SELECT COUNT(*) FROM tip_usluge')
    count = cursor.fetchone()[0]
    if count == 0:
        # Insert some default service types
        tipovi_usluge = ['Servis', 'Popravka', 'Zamena delova', 'Dijagnostika', 'Gume', 'Klima', 'DPF']
        cursor.executemany('INSERT INTO tip_usluge (naziv) VALUES (?)', [(tip,) for tip in tipovi_usluge])
    conn.commit()
    conn.close()

def insert_record(datum, broj_sasije, registarska_oznaka, marka_model, tip_usluge_id, opis_rada, cena):
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO records (datum, broj_sasije, registarska_oznaka, marka_model, tip_usluge_id, opis_rada, cena)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (datum, broj_sasije, registarska_oznaka, marka_model, tip_usluge_id, opis_rada, cena))
    conn.commit()
    conn.close()

def delete_records(record_ids):
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()
    cursor.executemany('DELETE FROM records WHERE id = ?', [(record_id,) for record_id in record_ids])
    conn.commit()
    conn.close()

def get_monthly_report():
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('''
        SELECT tip_usluge.naziv, COUNT(*), AVG(cena), SUM(cena)
        FROM records
        JOIN tip_usluge ON records.tip_usluge_id = tip_usluge.id
        WHERE strftime('%Y-%m', datum) = ?
        GROUP BY tip_usluge.naziv
    ''', (current_month,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_yearly_report():
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()
    current_year = datetime.now().strftime('%Y')
    cursor.execute('''
        SELECT tip_usluge.naziv, COUNT(*), AVG(cena), SUM(cena)
        FROM records
        JOIN tip_usluge ON records.tip_usluge_id = tip_usluge.id
        WHERE strftime('%Y', datum) = ?
        GROUP BY tip_usluge.naziv
    ''', (current_year,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_records(broj_sasije):
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT records.id, datum, broj_sasije, registarska_oznaka, marka_model, tip_usluge.naziv, opis_rada, cena
        FROM records
        JOIN tip_usluge ON records.tip_usluge_id = tip_usluge.id
        WHERE broj_sasije LIKE ?
    ''', ('%' + broj_sasije + '%',))
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_records():
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT records.id, datum, broj_sasije, registarska_oznaka, marka_model, tip_usluge.naziv, opis_rada, cena
        FROM records
        JOIN tip_usluge ON records.tip_usluge_id = tip_usluge.id
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

def get_tip_usluge_list():
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, naziv FROM tip_usluge')
    results = cursor.fetchall()
    conn.close()
    return results
