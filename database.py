import sqlite3
from pathlib import Path

DB_PATH = str(Path.home() / "data/measurements.db")

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as e:
        print(f"Erreur de connexion à la DB: {e}")
    return conn

def init_db():
    conn = create_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # Table pour les mesures (existante)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                lat REAL, lng REAL, day INTEGER, month INTEGER, year INTEGER,
                hour INTEGER, minute INTEGER, second INTEGER,
                distanceMin_cm REAL, speed_kmh REAL, valid INTEGER
            )
        ''')

        # Table pour les utilisateurs (nouvelle)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        ''')

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur d'initialisation DB: {e}")
        return False
    finally:
        conn.close()
