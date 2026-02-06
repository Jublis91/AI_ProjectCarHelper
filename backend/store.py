# store.py

import sqlite3

from pathlib import Path

# Database file location: project /db/app.sqlite
DB_PATH = Path(__file__).resolve().parents[1] / "db" / "app.sqlite"

def connect() -> sqlite3.Connection:
    # 1) Ensure the DB directory exists.
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    # 2) Open a SQLite connection.
    conn = sqlite3.connect(DB_PATH)
    # 3) Performance settings: WAL mode and normal sync.
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db() -> None:
    # 1) Open a connection and create a cursor to run schema setup.
    conn = connect()
    cur = conn.cursor()

    # 2) chunks table: indexed text chunks plus embeddings.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        ref TEXT NOT NULL,
        text TEXT NOT NULL,
        embedding BLOB NOT NULL
    );
    """)

    # 3) parts table: parts ledger (date, part, cost, notes).
    cur.execute("""
    CREATE TABLE IF NOT EXISTS parts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        part TEXT NOT NULL,
        cost REAL,
        notes TEXT
    );
    """)

    # 4) manual_pages table: manual pages stored as text.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS manual_pages (
                page_num INTEGER PRIMARY KEY,
                text TEXT NOT NULL
    );
    """)

    # 5) Indexes to speed up common lookups.
    cur.execute("CREATE INDEX IF NOT EXISTS idx_manual_pages_page ON manual_pages(page_num)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_part ON parts(part);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_date ON parts(date);")

    # 6) Persist schema changes and close the connection.
    conn.commit()
    conn.close()