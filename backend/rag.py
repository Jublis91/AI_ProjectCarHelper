# rag.py

from __future__ import annotations

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    #  Perussiivous
    text = text.replace("\r\n", "\n").strip()

    # poistetaan turhat välit ja tyhjät rivit
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    text = "\n".join(lines).strip()

    if not text:
        return []
    
    # pilkotaan merkkimäärän mukaan, overlap mukana
    chunks: list[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == n:
            break

        start = end - overlap
        if start < 0:
            start = 0

    return chunks