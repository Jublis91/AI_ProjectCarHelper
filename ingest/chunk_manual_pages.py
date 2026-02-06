"""Create text chunks for manual pages and report counts.

This helper reads OCR text from the database, splits it into RAG-friendly
chunks, and prints summary statistics. It does not persist the chunks; use
ingest_manual_to_db.py for actual chunk storage.
"""

from __future__ import annotations
from pathlib import Path
from backend.rag import chunk_text

import sqlite3

ROOT = Path(__file__).resolve().parents[1]
# Path to the SQLite database containing OCR text.
DB_PATH = ROOT / "db" / "app.sqlite"

def main() -> None:
    """Print chunk counts for each OCRed manual page."""
    if not DB_PATH.exists():
        print("DB puuttuu. aja ensin init_db ja OCR.")
        return
    
    # Read OCR text from the manual_pages table.
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT page_num, text FROM manual_pages ORDER BY page_num"
    ).fetchall()

    if not rows:
        print("manual_pages on tyhjä. Aja ensin OCR")
        conn.close()
        return
    
    # Aggregate counts for reporting.
    total_pages = 0
    total_chunks = 0

    for page_num, page_text in rows:
        # page_text on yhden sivun OCR- teksti
        # Split the OCR text into smaller chunks for embedding usage.
        chunks = chunk_text(page_text)
        print(f"Sivu {page_num}: {len(chunks)} chunkia")
        total_pages += 1
        total_chunks += len(chunks)

    conn.close()
    print(f"Valmis. Sivut: {total_pages}. Chunkit yhteensä: {total_chunks}.")

if __name__ == "__main__":
    main()