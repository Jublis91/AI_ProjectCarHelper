from __future__ import annotations
from pathlib import Path

import csv

ROOT = Path(__file__).resolve().parents[1]
PARTS_PATH = ROOT / "data" / "parts.csv"  # vaihda myöhemmin jos excel tms

def main() -> None:
    print(f"Parts path: {PARTS_PATH}")

    if not PARTS_PATH.exists():
        print("Ei parts.csv TIEDOSTOA. Luo data/parts.csv tai muuta PARTS_PATH.")
        return
    
    with PARTS_PATH.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Rivejä: {len(rows)}")

    if rows:
        print("Sarakkeet:", list(rows[0].keys()))
        print("Ensimmäinen rivi:", rows[0])

if __name__ == "__main__":
    main()