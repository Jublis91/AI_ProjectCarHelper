from __future__ import annotations

import re

PATTERN_TOTAL_COST = re.compile(
    r"paljonko\s+(?P<target>.+?)\s+on\s+maksanut\s+yhteensä",
    re.IGNORECASE
)

def parse_total_cost_question(text: str) -> str | None:
    m = PATTERN_TOTAL_COST.search(text.strip())
    if not m:
        return None
    target = m.group("target").strip().lower()
    return target