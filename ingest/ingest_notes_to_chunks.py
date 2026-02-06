"""Chunk a notes markdown file and store placeholder embeddings."""

from __future__ import annotations
from pathlib import Path
from backend.rag import chunk_text
from backend.store import init_db, connect

ROOT = Path(__file__).resolve().parents[1]
# Path to the notes file used for ingestion.
NOTES_PATH = ROOT / "data" / "notes.md"
# Metadata for the chunk table.
SOURCE = "notes"
REF = "notes.md"

def main() -> None:
    """Read notes, chunk text, and upsert into the chunks table."""
    init_db()

    if not NOTES_PATH.exists():
        print("notes.md ei löydy")
        return

    # Load the notes content with safe encoding behavior.
    text = NOTES_PATH.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        print("notes.md on tyhjä")
        return

    # Split into RAG-friendly chunks.
    chunks = chunk_text(text)
    print(f"Chunkit: {len(chunks)}")

    if not chunks:
        print("Ei chunkkeja. Lopetetaan.")
        return

    conn = connect()
    cur = conn.cursor()

    # 1) Remove existing notes chunks before inserting new ones.
    cur.execute("DELETE FROM chunks WHERE source = ?", (SOURCE,))
    conn.commit()

    # 2) Insert the new chunks.
    rows = []
    for ch in chunks:
        # Embeddings are not computed here; empty bytes placeholder.
        rows.append((SOURCE, REF, ch, b""))  # embedding placeholder

    cur.executemany(
        "INSERT INTO chunks(source, ref, text, embedding) VALUES(?, ?, ?, ?)",
        rows,
    )
    conn.commit()

    # 3) Verify insert count for sanity.
    n = cur.execute(
        "SELECT COUNT(*) FROM chunks WHERE source = ?",
        (SOURCE,),
    ).fetchone()[0]

    conn.close()

    print(f"Valmis. chunks WHERE source=notes: {n}")

if __name__ == "__main__":
    main()
