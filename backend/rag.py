# rag.py

from __future__ import annotations
from dataclasses import dataclass

import numpy as np

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

def cosine_top_k(query_vec: np.ndarray, matrix: np.ndarray, k: int = 5)-> tuple[np.ndarray, np.ndarray]:
    """
    query_vec: muoto (d,)
    matrix: muoto (N, d)
    palautaa:
        idx: indeksit (k,)
        scores: cos-sim scoret (k,)
    """
    if matrix.size == 0:
        return np.array([], dtype=int), np.array([], dtype=np.float32)
    
    if query_vec.ndim != 1:
        raise ValueError("query_vec pitää olla 1D, muoto (d,)")
    
    if matrix.ndim != 2:
        raise ValueError("matrix pitää olla 2D, muoto (N, d)")
    
    if matrix.shape[1] != query_vec.shape[0]:
        raise ValueError("dimensiot ei täsmää")
    
    # normalisoidaan
    q = query_vec.astype(np.float32)
    q = q / (np.linalg.norm(q) + 1e-12)

    m = matrix.astype(np.float32)
    m = m / (np.linalg.norm(m, axis=1, keepdims=True) + 1e-12)

    # cos - sim (dot product normalisoidulla vektorilla)
    sims = m @ q # (N,)

    # top-k
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