from __future__ import annotations
from pathlib import Path
from backend.rag import chunk_text

ROOT = Path(__file__).resolve().parents[1]
NOTES_PATH = ROOT / "data" / "notes.md" # vaihdetaan tarvittaessa notes.md muuksi

def main() -> None:
    print(f"Notes path: {NOTES_PATH}")

    if not NOTES_PATH.exists():
        print("EI NOTES TIEDOSTOA. Luo data/notes.md tai muuta NOTES_PATH.")
        return
    
    text = NOTES_PATH.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        print("Notes on tyhjä.")
        return
    
    chunks = chunk_text(text)
    print(f"Tekstiä: {len(text)} merkkiä")
    print(f"Chunkit: {len(chunks)}")

    if chunks:
        print("Ensimmäinen chunk (alku):")
        print(chunks[0][:400])

if __name__ == "__main__":
    main()