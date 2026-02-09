from __future__ import annotations
from backend.prompts import SYSTEM_PROMPT

def build_prompt(*, question: str, context: str) -> str:
    """
    Bulds one whole prompt:
    - system prompt first
    - question prompt cleary seperated
    - context always at the end
    """
    q = (question or "").strip()
    ctx = (context or "").strip()

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"QUESTION:\n"
        f"{q}\n\n"
        f"CONTEXT:\n"
        f"{ctx}\n\n"
        f"ANSWER:\n"
    )