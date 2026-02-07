from __future__ import annotations
from fastapi import FastAPI
from backend.store import init_db, connect, DB_PATH
from backend.rag import cosine_top_k
from pydantic import BaseModel, Field
from backend.rules import try_rules
from backend.parts_logic import load_parts_df

import numpy as np
import sqlite3
import re

app = FastAPI(title="AI Project Car Helper")

PARTS_DF = None

class AskIn(BaseModel):
    question: str = Field(..., description="User question in natural language")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")

@app.on_event("startup")
def on_startup() -> None:
    global PARTS_DF

    init_db()
    c = connect()
    PARTS_DF = load_parts_df(c)
    c.close()
    
    print("Loading embedding model...")
    from sentence_transformers import SentenceTransformer
    app.state.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Embedding model loaded.")

    print("Loading chunks from DB...")
    with sqlite3.connect(DB_PATH) as conn:
        try:
            rows = conn.execute(
                "SELECT source, ref, text, embedding FROM chunks"
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []

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
    print(f"Parts rows loaded: {0 if PARTS_DF is None else len(PARTS_DF)}")

@app.get("/health")
def health() -> dict:
    matrix = getattr(app.state, "chunk_matrix", None)
    n_chunks = int(matrix.shape[0]) if matrix is not None else 0
    n_parts = 0 if PARTS_DF is None else int(len(PARTS_DF))
    return {"ok": True, "chunks": n_chunks, "parts_rows": n_parts}


def page_from_ref(ref: str) -> int | None:
    m = re.search(r"#page=(\d+)", ref)
    return int(m.group(1)) if m else None


def clean_ocr(t: str) -> str:
    t = t.replace("\n", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def looks_readable(t: str) -> bool:
    if len(t) < 120:
        return False
    letters = sum(ch.isalpha() for ch in t)
    if letters / max(1, len(t)) < 0.55:
        return False
    weird = sum((not ch.isalnum()) and (ch not in " .,:;()/-'") for ch in t)
    if weird / max(1, len(t)) > 0.08:
        return False
    if " " not in t:
        return False
    return True


@app.post("/ask")
def ask(payload: AskIn) -> dict:
    q = (payload.question or "").strip()
    if not q:
        return {"answer": "", "sources": []}

    # 1) Osalistasäännöt ensin, ohittaa RAGin
    if PARTS_DF is not None:
        rule_result = try_rules(q, PARTS_DF)
        if rule_result is not None:
            return rule_result

    # 2) Muuten RAG manual-chunkeista
    model = getattr(app.state, "embed_model", None)
    matrix = getattr(app.state, "chunk_matrix", None)

    if model is None or matrix is None or matrix.shape[0] == 0:
        return {"answer": "", "sources": []}

    q_vec = model.encode([q], convert_to_numpy=True).astype(np.float32)[0]

    idx, scores = cosine_top_k(q_vec, matrix, k=payload.top_k)

    sources_out = []
    for i, s in zip(idx, scores):
        i2 = int(i)
        ref = app.state.chunk_refs[i2]
        sources_out.append(
            {
                "source": app.state.chunk_sources[i2],
                "ref": ref,
                "page": page_from_ref(ref),
                "score": float(s),
                "snippet": app.state.chunk_texts[i2][:300].strip(),
            }
        )

    answer = ""
    for i in idx:
        cand = clean_ocr(app.state.chunk_texts[int(i)])
        if looks_readable(cand):
            answer = cand[:600]
            break

    if not answer and len(idx) > 0:
        answer = clean_ocr(app.state.chunk_texts[int(idx[0])])[:600]

    return {"answer": answer, "sources": sources_out}