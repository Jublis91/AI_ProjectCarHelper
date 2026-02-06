# rag.py

from __future__ import annotations
from dataclasses import dataclass

import numpy as np

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 150) -> list[str]:
    # 1) Perussiivous: normalisoidaan rivinvaihdot ja poistetaan
    #    alusta/lopusta ylimääräiset välit.
    text = text.replace("\r\n", "\n").strip()

    # 2) Rivikohtainen siivous: trimmaa rivit ja poista tyhjät rivit,
    #    jotta pätkiminen ei ota mukaan pelkkää tyhjää sisältöä.
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    text = "\n".join(lines).strip()

    # 3) Jos siivouksen jälkeen ei ole sisältöä, ei ole mitään pätkittävää.
    if not text:
        return []
    
    # 4) Pilkotaan merkkimäärän mukaan: muodostetaan chunkit, joissa on
    #    päällekkäinen alue (overlap), jotta konteksti ei katkea.
    chunks: list[str] = []
    start = 0
    n = len(text)

    while start < n:
        # Rajataan chunkin loppu merkkimäärän mukaisesti.
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Kun ollaan lopussa, lopetetaan silmukka.
        if end == n:
            break

        # Siirrytään seuraavan chunkin alkuun huomioiden overlap.
        start = end - overlap
        if start < 0:
            start = 0

    return chunks

def cosine_top_k(query_vec: np.ndarray, matrix: np.ndarray, k: int = 5)-> tuple[np.ndarray, np.ndarray]:
    """
    query_vec: muoto (d,)
    matrix: muoto (N, d)
    palautaa:
        idx: indeksit (k,)
        scores: cos-sim scoret (k,)
    """
    # 1) Tyhjä tietomassa -> ei osumia
    if matrix.size == 0:
        return np.array([], dtype=int), np.array([], dtype=np.float32)
    
    # 2) Varmistetaan oikeat dimensioformaatit ennen laskentaa.
    if query_vec.ndim != 1:
        raise ValueError("query_vec pitää olla 1D, muoto (d,)")
    
    if matrix.ndim != 2:
        raise ValueError("matrix pitää olla 2D, muoto (N, d)")
    
    if matrix.shape[1] != query_vec.shape[0]:
        raise ValueError("dimensiot ei täsmää")
    
    # 3) Normalisoidaan vektorit, jotta dot product = cosine-sim.
    q = query_vec.astype(np.float32)
    q = q / (np.linalg.norm(q) + 1e-12)

    m = matrix.astype(np.float32)
    m = m / (np.linalg.norm(m, axis=1, keepdims=True) + 1e-12)

    # 4) Cos-sim: normalisoidun vektorin dot product.
    sims = m @ q # (N,)

    # 5) Top-k: rajataan k, poimitaan suurimmat ja järjestetään.
    k = max(1,min(int(k), sims.shape[0]))
    idx = np.argpartition(-sims, kth=k - 1)[:k]
    idx = idx[np.argsort(-sims[idx])]
    scores = sims[idx]

    return idx.astype(int), scores.astype(np.float32)


@dataclass
class Hit:
    text: str
    source: str
    ref: str
    score: float