from __future__ import annotations
from pathlib import Path
from backend.rag import chunk_text
from backend.store import init_db, connect

ROOT = Path(__file__).resolve().parents[1]
NOTES_PATH = ROOT / "data" / "notes.md"
SOURCE = "notes"
REF = "notes.md"

def main() -> None:
    init_db()

    if not NOTES_PATH.exists():
        print("notes.md ei löydy")
        return

    text = NOTES_PATH.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        print("notes.md on tyhjä")
        return

    chunks = chunk_text(text)
    print(f"Chunkit: {len(chunks)}")

    if not chunks:
        print("Ei chunkkeja. Lopetetaan.")
        return

    conn = connect()
    cur = conn.cursor()

    # 1) poista vanhat notes-chunkit
    cur.execute("DELETE FROM chunks WHERE source = ?", (SOURCE,))
    conn.commit()

    # 2) lisää uudet
    rows = []
    for ch in chunks:
        rows.append((SOURCE, REF, ch, b""))  # embedding placeholder

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

    print(f"Valmis. chunks WHERE source=notes: {n}")

if __name__ == "__main__":
    main()
