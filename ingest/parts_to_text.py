from __future__ import annotations
from pathlib import Path

import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "app.sqlite"

def fmt_money(x) -> str:
    if x is None:
        return ""
    
    try:
        return f"{float(x):.2f}"
    except Exception:
        return ""
    

def main() -> None:
    if not DB_PATH.exists():
        print("DB puuttuu.")
        return
    
    c = sqlite3.connect(DB_PATH)
    rows = c.execute(
        "SELECT date, part, cost, notes FROM parts ORDER BY date, id"
    ).fetchall()
    c.close()

    lines = []
    for date, part, cost, notes in rows:
        date_s = (date or "").strip()
        part_s = (part or "").strip()
        cost_s = fmt_money(cost)
        notes_s = (notes or "").strip()

        if not part_s:
            continue

        line = f"Päivä: {date_s}, Osa: {part_s}, Hinta: {cost_s}, Huomio: {notes_s}"
        lines.append(line)

    text = "\n".join(lines).strip()

    print(f"Rivejä tekstissä: {len(lines)}")
    if lines:
        print("Ensimmäinen rivi:")
        print(lines[0])

    if not text:
        print("EI YHTÄÄN RIVIÄ")
        return
    
if __name__ == "__main__":
    main()