from __future__ import annotations
from backend.prompts import SYSTEM_PROMPT

def build_prompt(*, question: str, context: str) -> str:
    question = (question or "").strip()
    context = (context or "").strip()

    return (
        f"{SYSTEM_PROMPT}\n"
        f"CONTEXT:\n{context}"
        f"QUESTION:\n{question}\n\n"
        f"ANSWER:\n"
    )