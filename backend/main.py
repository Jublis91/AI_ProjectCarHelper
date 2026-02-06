from __future__ import annotations
from fastapi import FastAPI
from backend.store import init_db
from pydantic import BaseModel, Field

import numpy as np
import sqlite3

app = FastAPI(title="AI Project Car Helper")

class AskIn(BaseModel):
    question: str = Field(..., description="User question in natural lanfuafe")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")

@app.on_event("startup")
def on_startup() -> None:
    init_db()

    print("Loading embedding model...")
    from sentence_transformers import SentenceTransformer
    app.state.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Embedding model loaded.")

    print("Loading chunks from DB...")
    conn = sqlite3.connect("db/app.sqlite")
    try:
        rows = conn.execute(
            "SELECT source, ref, text, embedding FROM chunks"
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()

    sources: list[str] = []
    refs: list[str] = []
    texts: list[str] = []
    vectors: list[np.ndarray] = []

    for source, ref, text, emb_blob in rows:
        vec = np.frombuffer(emb_blob, dtype=np.float32)
        if vec.size == 0:
            continue
        sources.append(source)
        refs.append(ref)
        texts.append(text)
        vectors.append(vec)

    if vectors:
        matrix = np.vstack(vectors)
    else:
        matrix = np.empty((0, 384), dtype=np.float32)

    app.state.chunk_sources = sources
    app.state.chunk_refs = refs
    app.state.chunk_texts = texts
    app.state.chunk_matrix = matrix

    print(f"Chunks loaded: {matrix.shape[0]}")

@app.get("/health")
def health() -> dict:
    matrix = getattr(app.state, "chunk_matrix", None)
    n_chunks = int(matrix.shape[0]) if matrix is not None else 0
    return {
        "ok": True,
        "chunks": n_chunks,
    }

@app.post("/ask")
def ask(payload: AskIn) -> dict:
    # Placeholder
    return {
        "question": payload.question,
        "top_k": payload.top_k,
    }