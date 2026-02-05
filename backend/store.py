# store.py

import sqlite3

from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "db" / "app.sqlite"

def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronus=NORMAL;")
    return conn