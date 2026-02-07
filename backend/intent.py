from __future__ import annotations

import re

PATTERN_TOTAL_COST = re.compile(
    r"paljonko\s+(?P<target>.+?)\s+on\s+maksanut\s+yhteensä",
    re.IGNORECASE
)

PATTERN_LAST_DATE = re.compile(
    r"milloin\s+viimeksi\s+(?P<target>.+?)\s+vaihdettiin",
    re.IGNORECASE
)

PATTERN_YES_NO = re.compile(
    r"onko\s+(?P<target>.+?)\s+vaihdettu",
    re.IGNORECASE
)

def parse_total_cost_question(text: str) -> str | None:
    m = PATTERN_TOTAL_COST.search(text.strip())
    if not m:
        return None
    target = m.group("target").strip().lower()
    return target

def parse_last_date_question(text: str) -> str | None:
    m = PATTERN_LAST_DATE.search(text.strip())
    if not m:
        return None
    return m.group("target").strip().lower()

def parse_yes_no_question(text: str) -> str | None:
    m = PATTERN_YES_NO.search(text.strip())
    if not m:
        return None

    return m.group("target").strip().lower()