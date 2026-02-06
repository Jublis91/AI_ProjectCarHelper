"""Inspect parts CSV data for ingestion readiness."""

from __future__ import annotations
from pathlib import Path
from backend.store import init_db, connect

import csv
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
# Source CSV containing parts data (replace if Excel import is added later).
PARTS_PATH = ROOT / "data" / "parts.csv"  # vaihda myöhemmin jos excel tms

REQUIRED_COLUMMS = ["date", "part", "cost", "notes"]

def main() -> None:
    init_db()

    if not PARTS_PATH.exists():
        print("parts.csv ei löydy")
        return

    df = pd.read_csv(PARTS_PATH)

    for col in REQUIRED_COLUMMS:
        if col not in df.columns:
            df[col] = None

    df = df[REQUIRED_COLUMMS]

    # part pakolinen
    df["part"] = df["part"].astype(str).str.strip()
    df = df[df["part"].notna() & (df["part"] != "")]

    #cost float tai null
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")

    #date ja notes siistiksi
    df["date"] = df["date"].astype(str).where(df["date"].notna(), None)
    df["notes"] = df["notes"].astype(str).where(df["notes"].notna(), None)

    expected = len(df)

    conn = connect()
    cur = conn.cursor()

    cur.execute("DELETE FROM parts")
    conn.commit()

    rows = [
        (row["part"], row["date"], None if pd.isna(row["cost"]) else float(row["cost"]), row["notes"])
        for _, row in df.iterrows()
    ]

    cur.executemany(
        "INSERT INTO parts(part, date, cost, notes) VALUES(?, ?, ?, ?)",
        rows,
    )
    conn.commit()

    actual = cur.execute("SELECT COUNT(*) FROM parts").fetchone()[0]
    conn.close()

    # jos nämä ei täsmää joku no pielessä
    print(f"Odotus: {expected}")
    print(f"DB count: {actual}")

if __name__ == "__main__":
    main()