"""Chunk OCR text, embed it, and store embeddings into the database."""

from __future__ import annotations
from pathlib import Path
from typing import Iterable
from sentence_transformers import SentenceTransformer
from backend.store import init_db, connect
from backend.rag import chunk_text

import sqlite3
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
# SQLite DB that contains OCR text and target chunks.
DB_PATH = ROOT / "db" / "app.sqlite"
# Metadata for chunk records.
SOURCE = "manual"
PDF_NAME = "s13servicemanual.pdf"
# Number of chunks to embed per batch for efficiency.

BATCH_SIZE = 64

def fetch_manual_pages() -> list[tuple[int, str]]:
    """Load OCR text from the manual_pages table."""
    c = sqlite3.connect(DB_PATH)
    rows = c.execute("SELECT page_num, text FROM manual_pages ORDER BY page_num").fetchall()
    c.close()
    return [(int(p), str(t)) for p, t in rows]

def delete_old_manual_chunks() -> None:
    """Remove existing manual chunks before inserting fresh ones."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM chunks WHERE source = ?", (SOURCE,))
    conn.commit()
    conn.close()

def insert_chunks(rows: Iterable[tuple[str, str, str, bytes]]) -> None:
    """Bulk insert chunk rows into the chunks table."""
    conn = connect()
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO chunks(source, ref, text, embedding) VALUES(?, ?, ?, ?)",
        list(rows),
    )
    conn.commit()
    conn.close()

def main() -> None:
    """Main entry point: chunk, embed, and store manual text."""
    init_db()

    if not DB_PATH.exists():
        print("DB puuttuu.")
        return
    
    pages = fetch_manual_pages()
    if not pages:
        print("manual_pages on tyhjä. Aja ensin OCR.")
        return
    
    # Load embedding model once to reuse across batches.
    print(f"Sivuja DB:ssä {len(pages)}")
    print("Ladataan embedding-malli...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Malli ladattu")
    print("Poistetaan vanhat manual-chunkit...")
    delete_old_manual_chunks()
    print("OK.")

    # Buffers hold data until we have BATCH_SIZE chunks to embed.
    buffer_texts: list[str] = []
    buffer_meta: list[tuple[int, str]] = []

    inserted = 0

    def flush() -> None:
        """Embed buffered chunks and write them to the DB."""
        nonlocal inserted
        if not buffer_texts:
            return
        
        # Encode text to embeddings and convert to float32 for storage.
        emb = model.encode(buffer_texts)
        emb = np.asarray(emb, dtype=np.float32)

        rows = []
        for (page_num, ref), text, vec in zip(buffer_meta, buffer_texts, emb):
            rows.append((SOURCE, ref, text, vec.tobytes()))

        insert_chunks(rows)
        inserted += len(rows)

        buffer_texts.clear()
        buffer_meta.clear()

    for page_num, page_text in pages:
        # Split each page into chunks for embedding.
        chunks = chunk_text(page_text)
        if not chunks:
            continue

        # Reference string links the chunk to the PDF page.
        ref = f"{PDF_NAME}#page={page_num}"

        for ch in chunks:
            buffer_texts.append(ch)
            buffer_meta.append((page_num, ref))

            # Flush whenever we reach a full batch.
            if len(buffer_texts) >= BATCH_SIZE:
                flush()

        print(f"Sivu {page_num}: {len(chunks)} chunkia")

    # Flush remaining chunks.
    flush()

    print(f"Valmis. Inserted chunks: {inserted}")

    # Quick verification of inserted chunk count.
    c = sqlite3.connect(DB_PATH)
    n = c.execute("SELECT COUNT(*) FROM chunks WHERE source=?", (SOURCE,)).fetchone()[0]
    c.close()
    print(f"SELECT COUNT(*) WHERE source=manual: {n}")


if __name__ == "__main__":
    main()
