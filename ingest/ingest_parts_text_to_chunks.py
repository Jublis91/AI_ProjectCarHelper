from __future__ import annotations
from backend.store import init_db, connect
from backend.rag import chunk_text
from pathlib import Path
from sentence_transformers import SentenceTransformer

import sqlite3
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "app.sqlite"

SOURCE = "parts_text"
REF = "parts.csv"

def fmt_money(x) -> str:
    if x is None:
        return ""
    try:
        return f"{float(x):.2f}"
    except Exception:
        return ""

def build_parts_text() -> str:
    c = sqlite3.connect(DB_PATH)
    rows = c.execute(
        "SELECT date, part, cost, notes FROM parts ORDER BY date, id"
    ).fetchall()
    c.close()

    lines = []
    for date, part, cost, notes in rows:
        part_s = (part or "").strip()
        if not part_s:
            continue

        line = (
            f"Päivä: {(date or '').strip()}, "
            f"Osa: {part_s}, "
            f"Hinta: {fmt_money(cost)}, "
            f"Huomio: {(notes or '').strip()}"
        )
        lines.append(line)

    return "\n".join(lines).strip()

def main() -> None:
    init_db()

    if not DB_PATH.exists():
        print("DB puuttuu")
        return

    parts_text = build_parts_text()
    if not parts_text:
        print("Parts-teksti tyhjä. Onko parts-taulu täynnä?")
        return

    chunks = chunk_text(parts_text)
    print(f"Chunkit: {len(chunks)}")
    if not chunks:
        print("Ei chunkkeja")
        return

    print("Ladataan embedding-malli...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Malli ladattu.")

    emb = model.encode(chunks)
    emb = np.asarray(emb, dtype=np.float32)

    conn = connect()
    cur = conn.cursor()

    # 1) poista vanhat
    cur.execute("DELETE FROM chunks WHERE source = ?", (SOURCE,))
    conn.commit()

    # 2) insert uudet
    rows = []
    for ch, vec in zip(chunks, emb):
        rows.append((SOURCE, REF, ch, vec.tobytes()))

    cur.executemany(
        "INSERT INTO chunks(source, ref, text, embedding) VALUES(?, ?, ?, ?)",
        rows,
    )
    conn.commit()

    # 3) varmennus
    n = cur.execute(
        "SELECT COUNT(*) FROM chunks WHERE source = ?",
        (SOURCE,),
    ).fetchone()[0]

    conn.close()

    print(f"Valmis. chunks WHERE source={SOURCE}: {n}")

if __name__ == "__main__":
    main()
