# rag.py

from __future__ import annotations
from dataclasses import dataclass

import numpy as np

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 150) -> list[str]:
    # 1) Basic cleanup: normalize newlines and trim leading/trailing whitespace.
    text = text.replace("\r\n", "\n").strip()

    # 2) Line-level cleanup: strip each line and remove empties so we avoid
    #    chunking blank content.
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    text = "\n".join(lines).strip()

    # 3) If nothing remains after cleanup, there is nothing to chunk.
    if not text:
        return []
    
    # 4) Split by character count with overlap to preserve context between chunks.
    chunks: list[str] = []
    start = 0
    n = len(text)

    while start < n:
        # Clamp the chunk end to the configured chunk size.
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Stop when we reach the end of the text.
        if end == n:
            break

        # Move the window forward, backing up by the overlap amount.
        start = end - overlap
        if start < 0:
            start = 0

    return chunks

def cosine_top_k(query_vec: np.ndarray, matrix: np.ndarray, k: int = 5)-> tuple[np.ndarray, np.ndarray]:
    """
    query_vec: shape (d,)
    matrix: shape (N, d)
    returns:
        idx: indices (k,)
        scores: cosine similarity scores (k,)
    """
    # 1) Empty matrix means there are no hits.
    if matrix.size == 0:
        return np.array([], dtype=int), np.array([], dtype=np.float32)
    
    # 2) Validate expected dimensions before math.
    if query_vec.ndim != 1:
        raise ValueError("query_vec pitää olla 1D, muoto (d,)")
    
    if matrix.ndim != 2:
        raise ValueError("matrix pitää olla 2D, muoto (N, d)")
    
    if matrix.shape[1] != query_vec.shape[0]:
        raise ValueError("dimensiot ei täsmää")
    
    # 3) Normalize vectors so dot product equals cosine similarity.
    q = query_vec.astype(np.float32)
    q = q / (np.linalg.norm(q) + 1e-12)

    m = matrix.astype(np.float32)
    m = m / (np.linalg.norm(m, axis=1, keepdims=True) + 1e-12)

    # 4) Cosine similarity: dot product of normalized vectors.
    sims = m @ q  # (N,)

    # 5) Top-k: clamp k, select the largest scores, and order them.
    k = max(1, min(int(k), sims.shape[0]))
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