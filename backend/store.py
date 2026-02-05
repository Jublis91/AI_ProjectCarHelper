# store.py

import sqlite3

from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "db" / "app.sqlite"

def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db() -> None:
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                ref TEXT NOT NULL,
                text TEXT NOT NULL,
                embedding BLOB NOT NULL
            );
            """)
    
    conn.commit()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS parts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part TEXT NOT NULL,
                date TEXT,
                cost REAL NOT NULL,
                notes TEXT
            );    
            """)
    
    conn.commit()
    conn.close()