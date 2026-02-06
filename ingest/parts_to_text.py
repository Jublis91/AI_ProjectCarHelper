from __future__ import annotations
from pathlib import Path
from backend.rag import chunk_text
from sentence_transformers import SentenceTransformer

import sqlite3
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "app.sqlite"

def fmt_money(x) -> str:
    if x is None:
        return ""
    
    try:
        return f"{float(x):.2f}"
    except Exception:
        return ""
    

def main() -> None:
    if not DB_PATH.exists():
        print("DB puuttuu")
        return

    c = sqlite3.connect(DB_PATH)
    rows = c.execute(
        "SELECT date, part, cost, notes FROM parts ORDER BY date, id"
    ).fetchall()
    c.close()

    lines = []
    for date, part, cost, notes in rows:
        if not part:
            continue

        line = (
            f"Päivä: {date or ''}, "
            f"Osa: {part}, "
            f"Hinta: {fmt_money(cost)}, "
            f"Huomio: {notes or ''}"
        )
        lines.append(line)

    parts_text = "\n".join(lines).strip()

    if not parts_text:
        print("EI TEKSTIÄ")
        return

    chunks = chunk_text(parts_text)
    print(f"Chunks: {len(chunks)}")
    if not chunks:
        print("Ei chunkkeja")
        return
    
    print("Ladataan embedding-malli...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Malli ladattu")

    emb = model.encode(chunks)
    emb = np.asanyarray(emb, dtype=np.float32)

    print("emb dtype:", emb.dtype)
    print("emb shape:", emb.shape)
    print("ensimmäinen embedding dim:", emb[0].shape[0])

if __name__ == "__main__":
    main()