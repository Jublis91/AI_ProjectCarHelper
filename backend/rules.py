from __future__ import annotations
from backend.intent import (
    parse_total_cost_question,
    parse_last_date_question,
    parse_yes_no_question,
)
from backend.parts_logic import (
    total_cost_contains,
    last_change_date_contains,
    yes_no_changed_contains,
)

def try_rules(question: str, parts_df) -> dict | None:
    q = question.strip()

    # 1) Paljonko X on maksanut yhteensä
    target = parse_total_cost_question(q)
    if target:
        r = total_cost_contains(parts_df, target)
        return {
            "answer": f"{r['total_eur']:.2f} € ({r['matches']} osumaa)",
            "sources": [],
            "type": "parts_cost",
        }

    # 2) Milloin viimeksi X vaihdettiin
    target = parse_last_date_question(q)
    if target:
        r = last_change_date_contains(parts_df, target)
        if r["date"]:
            answer = f"Viimeksi vaihdettu {r['date']} ({r['matches']} merkintää)."
        else:
            answer = f"Ei päivämäärätietoa osalle '{target}'."
        return {
            "answer": answer,
            "sources": [],
            "type": "parts_last_date",
        }

    # 3) Onko X vaihdettu
    target = parse_yes_no_question(q)
    if target:
        r = yes_no_changed_contains(parts_df, target)
        if r["changed"]:
            if r["last_date"]:
                answer = f"Kyllä. Viimeksi vaihdettu {r['last_date']} ({r['matches']} merkintää)."
            else:
                answer = f"Kyllä. Vaihdettssu {r['matches']} kertaa."
        else:
            answer = f"Ei. Osaa '{target}' ei ole vaihdettu."
        return {
            "answer": answer,
            "sources": [],
            "type": "parts_yes_no",
        }

    return None