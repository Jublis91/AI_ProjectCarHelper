# store.py

import sqlite3

from pathlib import Path

# Tietokantatiedoston sijainti: projektin /db/app.sqlite
DB_PATH = Path(__file__).resolve().parents[1] / "db" / "app.sqlite"

def connect() -> sqlite3.Connection:
    # 1) Varmista, että db-kansio on olemassa.
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    # 2) Avaa yhteys SQLite-tiedostoon.
    conn = sqlite3.connect(DB_PATH)
    # 3) Suorituskykyasetukset: WAL ja normaalisynkronointi.
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db() -> None:
    # 1) Avataan yhteys ja luodaan cursor, jolla ajetaan skeema.
    conn = connect()
    cur = conn.cursor()

    # 2) chunks-taulu: indeksoitavat tekstipätkät + embedding.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        ref TEXT NOT NULL,
        text TEXT NOT NULL,
        embedding BLOB NOT NULL
    );
    """)

    # 3) parts-taulu: varaosien kirjanpito (päivä, osa, kustannus, muistiinpanot).
    cur.execute("""
    CREATE TABLE IF NOT EXISTS parts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        part TEXT NOT NULL,
        cost REAL,
        notes TEXT
    );
    """)

    # 4) manual_pages-taulu: manuaalin sivut tekstinä.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS manual_pages (
                page_num INTEGER PRIMARY KEY,
                text TEXT NOT NULL
    );
    """)

    # 5) Indeksit: nopeuttavat hakuja yleisillä hakukentillä.
    cur.execute("CREATE INDEX IF NOT EXISTS idx_manual_pages_page ON manual_pages(page_num)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_part ON parts(part);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_date ON parts(date);")

    # 6) Tallennetaan muutokset ja suljetaan yhteys.
    conn.commit()
    conn.close()