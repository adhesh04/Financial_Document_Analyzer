import sqlite3
from datetime import datetime

DB_NAME = "financial_analysis.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            query TEXT,
            analysis TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_analysis(filename: str, query: str, analysis: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analyses (filename, query, analysis, created_at)
        VALUES (?, ?, ?, ?)
    """, (filename, query, analysis, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()