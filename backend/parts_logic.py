from __future__ import annotations
from typing import Optional

import sqlite3
import pandas as pd

def fmt_money(x) -> str:
    if x is None:
        return ""
    try:
        return f"{float(x):.2f}"
    except Exception:
        return ""
    
def format_parts_text(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        "SELECT date, part, cost, notes FROM parts ORDER BY date, id"
    ).fetchall()

    lines = []
    for date, part, cost, notes in rows:
        part_s = (part or "").strip()
        if not part_s:
            continue
        
        line = (
            f"Päivä: {(date or '').strip()}, "
            f"Osa: {part_s}, "
            f"Hinta: {fmt_money(cost)}, "
            f"Huomio: {(notes or '').strip()}"
        )
        lines.append(line)

    return "\n".join(lines).strip()

def load_parts_df(conn: sqlite3.Connection) -> pd.DataFrame:
    df =pd.read_sql_query(
        "SELECT id, date, part, cost, notes FROM parts",
        conn,
    )

    df["part_lc"] = (
        df["part"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return df

def total_cost_contains(df: pd.DataFrame, target: str) -> dict:
    target_lc = (target or "").strip().lower()
    if not target_lc:
        return {"target": target_lc, "matches": 0, "total_eur": 0.0}
    
    if "part_lc" not in df.columns:
        raise ValueError("df: part_lc puuttuu")
    
    mask = df["part_lc"].str.contains(target_lc, na=False, regex=False)
    hits = df.loc[mask].copy()

    hits["cost_num"] = pd.to_numeric(hits.get("cost"), errors="coerce").fillna(0.0)

    total =float(hits["cost_num"].sum())
    matches = int(hits.shape[0])

    return {"target": target_lc, "matches": matches, "total_eur": total}