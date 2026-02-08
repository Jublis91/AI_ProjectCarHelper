from __future__ import annotations

import re
import sqlite3

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, Field

from backend.parts_logic import load_parts_df
from backend.rag import cosine_top_k
from backend.rules import try_rules
from backend.store import DB_PATH, connect, init_db
from backend.settings import USE_OLLAMA, OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT_SEC
from backend.ollama_process import start_ollama, stop_ollama
from backend.prompt_builder import build_prompt
from backend.ollama_client import (
    ollama_generate,
    OllamaError,
    OllamaConnectionError,
    OllamaTimeoutError,
    OllamaBadResponseError,
)

app = FastAPI(title="AI Project Car Helper")

# Loaded once at startup to serve parts lookups without re-querying per request.
PARTS_DF = None
OLLAMA_PROC = None
OLLAMA_HANDLE = None

class AskIn(BaseModel):
    question: str = Field(..., description="User question in natural language")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")


@app.on_event("startup")
def on_startup() -> None:
    global PARTS_DF
    global OLLAMA_HANDLE
    if USE_OLLAMA:
        OLLAMA_HANDLE = start_ollama(
            base_url=OLLAMA_BASE_URL,
            timeout_sec=OLLAMA_TIMEOUT_SEC,
        )

    # Initialize the local database and cache parts for rule-based matches.
    init_db()
    c = connect()
    PARTS_DF = load_parts_df(c)
    c.close()

    # Load the embedding model once so requests reuse it.
    print("Loading embedding model...")
    from sentence_transformers import SentenceTransformer
    app.state.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Embedding model loaded.")

    # Load stored chunk embeddings for RAG retrieval.
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

    # Decode stored embeddings to numpy vectors while keeping metadata aligned.
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

    # Helpful diagnostics to confirm startup cache sizes.
    print(f"Chunks loaded: {matrix.shape[0]}")
    print(f"Parts rows loaded: {0 if PARTS_DF is None else len(PARTS_DF)}")
    print(
        f"USE_OLLAMA={USE_OLLAMA} "
        f"OLLAMA_BASE_URL={OLLAMA_BASE_URL} "
        f"OLLAMA_MODEL={OLLAMA_MODEL} "
        f"OLLAMA_TIMEOUT_SEC={OLLAMA_TIMEOUT_SEC}"
    )

@app.on_event("shutdown")
def on_shutdown() -> None:
    global OLLAMA_HANDLE
    if OLLAMA_HANDLE is not None:
        stop_ollama(OLLAMA_HANDLE)
        OLLAMA_HANDLE = None

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


def build_sources(idx, scores) -> list[dict]:
    sources_out: list[dict] = []
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
    return sources_out


def pick_answer_from_chunks(idx) -> str:
    answer = ""
    for i in idx:
        cand = clean_ocr(app.state.chunk_texts[int(i)])
        if looks_readable(cand):
            answer = cand[:600]
            break

    if not answer and len(idx) > 0:
        answer = clean_ocr(app.state.chunk_texts[int(idx[0])])[:600]

    return answer


def normalize_response(resp: dict, llm_mode: str) -> dict:
    if not isinstance(resp, dict):
        return {"answer": str(resp), "sources": [], "llm_mode": llm_mode}

    out = dict(resp)

    if out.get("answer") is None:
        out["answer"] = ""
    if out.get("sources") is None:
        out["sources"] = []
    if "llm_mode" not in out:
        out["llm_mode"] = llm_mode

    return out


@app.post("/ask")
def ask(payload: AskIn) -> dict:
    q = (payload.question or "").strip()
    if not q:
        return {"answer": "", "sources": [], "llm_mode": "off"}

    if PARTS_DF is not None:
        rule_result = try_rules(q, PARTS_DF)
        if rule_result is not None:
            return normalize_response(rule_result, llm_mode="rules")

    model = getattr(app.state, "embed_model", None)
    matrix = getattr(app.state, "chunk_matrix", None)

    # Guard: without cached embeddings, return empty response instead of erroring.
    if model is None or matrix is None or matrix.shape[0] == 0:
        return {"answer": "", "sources": [], "llm_mode": "off"}

    # Embed the query and retrieve top-k similar chunks.
    q_vec = model.encode([q], convert_to_numpy=True).astype(np.float32)[0]
    idx, scores = cosine_top_k(q_vec, matrix, k=payload.top_k)

    sources_out = build_sources(idx, scores)

    if USE_OLLAMA:
        prompt = build_prompt(question=q, context="...tähän chunkit myöhemmin...")
        try:
            txt = ollama_generate(
                base_url=OLLAMA_BASE_URL,
                model=OLLAMA_MODEL,
                prompt=prompt,
                timeout_sec=OLLAMA_TIMEOUT_SEC,
            )
            return normalize_response({"answer": txt, "sources": sources_out}, llm_mode="ollama")
        except OllamaTimeoutError:
            return {"answer": "LLM timeout", "sources": sources_out, "llm_mode": "ollama_error", "error": "timeout"}
        except OllamaConnectionError:
            return {"answer": "LLM not available", "sources": sources_out, "llm_mode": "ollama_error", "error": "connection"}
        except OllamaBadResponseError:
            return {"answer": "LLM bad response", "sources": sources_out, "llm_mode": "ollama_error", "error": "bad_response"}
        except OllamaError:
            return {"answer": "LLM error", "sources": sources_out, "llm_mode": "ollama_error", "error": "unknown"}

    answer = pick_answer_from_chunks(idx)
    return normalize_response(
        {"answer": answer, "sources": sources_out},
        llm_mode="off",
    )
