from __future__ import annotations
from fastapi import FastAPI

app = FastAPI(title="AI Project Car Helper")

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}