from __future__ import annotations

import re
from typing import Sequence


def _clean_text(t: str) -> str:
    t = (t or "").replace("\n", " ").replace("\r", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def format_context(
    *,
    idx: Sequence[int],
    chunk_sources: Sequence[str],
    chunk_refs: Sequence[str],
    chunk_texts: Sequence[str],
    per_chunk_char_limit: int = 900,
    max_context_chars: int = 6000,
) -> str:
    parts: list[str] = []
    total = 0

    def add_line(line: str) -> bool:
        nonlocal total
        line = line or ""
        add_len = len(line) + 1
        if total + add_len > max_context_chars:
            return False
        parts.append(line)
        total += add_len
        return True

    for rank, raw_i in enumerate(idx, start=1):
        i = int(raw_i)

        source = _clean_text(chunk_sources[i]) if i < len(chunk_sources) else ""
        ref = _clean_text(chunk_refs[i]) if i < len(chunk_refs) else ""
        text = _clean_text(chunk_texts[i]) if i < len(chunk_texts) else ""

        if not text:
            continue

        if len(text) > per_chunk_char_limit:
            text = text[:per_chunk_char_limit].rstrip() + "..."

        header = f"[{rank}] source={source} ref={ref}"

        if not add_line(header):
            break
        if not add_line(text):
            break
        if not add_line(""):
            break

    return "\n".join(parts).strip()
