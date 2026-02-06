import sqlite3

from backend import store


def test_init_db_creates_schema(tmp_path, monkeypatch):
    db_path = tmp_path / "app.sqlite"
    monkeypatch.setattr(store, "DB_PATH", db_path)

    store.init_db()
    assert db_path.exists()

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cur.fetchall()}
    finally:
        conn.close()

    assert {"chunks", "parts", "manual_pages"}.issubset(tables)
