from __future__ import annotations

import sqlite3
import pandas as pd


def mask_all_tokens(series: pd.Series, target: str) -> pd.Series:
    toks = [t for t in (target or "").lower().split() if t]
    if not toks:
        return pd.Series([False] * len(series), index=series.index)

    m = pd.Series([True] * len(series), index=series.index)
    for tok in toks:
        m = m & series.str.contains(tok, na=False, regex=False)
    return m


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
    df = pd.read_sql_query(
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

    mask = mask_all_tokens(df["part_lc"], target_lc)
    hits = df.loc[mask].copy()

    hits["cost_num"] = pd.to_numeric(hits.get("cost"), errors="coerce").fillna(0.0)

    total = float(hits["cost_num"].sum())
    matches = int(hits.shape[0])

    return {"target": target_lc, "matches": matches, "total_eur": total}


def last_change_date_contains(df: pd.DataFrame, target: str) -> dict:
    target_lc = (target or "").strip().lower()
    if not target_lc:
        return {"target": target_lc, "date": None, "matches": 0}

    if "part_lc" not in df.columns:
        raise ValueError("df: part_lc puuttuu")

    mask = mask_all_tokens(df["part_lc"], target_lc)
    hits = df.loc[mask].copy()

    if hits.empty:
        return {"target": target_lc, "date": None, "matches": 0}

    hits["date_dt"] = pd.to_datetime(hits.get("date"), errors="coerce")
    hits = hits.dropna(subset=["date_dt"])

    if hits.empty:
        return {"target": target_lc, "date": None, "matches": 0}

    last_date = hits["date_dt"].max().date().isoformat()
    matches = int(hits.shape[0])

    return {"target": target_lc, "date": last_date, "matches": matches}


def format_last_date_result(r: dict) -> str:
    if not r.get("date"):
        return f"Ei päivämäärää löytynyt osalle '{r.get('target','')}'."
    return f"Viimeksi vaihdettu {r['date']} ({r['matches']} merkintää)."


def yes_no_changed_contains(df: pd.DataFrame, target: str) -> dict:
    target_lc = (target or "").strip().lower()
    if not target_lc:
        return {"target": target_lc, "changed": False, "matches": 0, "last_date": None}

    if "part_lc" not in df.columns:
        raise ValueError("df: part_lc puuttuu")

    mask = mask_all_tokens(df["part_lc"], target_lc)
    hits = df.loc[mask].copy()
    matches = int(len(hits))

    if matches == 0:
        return {"target": target_lc, "changed": False, "matches": 0, "last_date": None}

    hits["date_dt"] = pd.to_datetime(hits.get("date"), errors="coerce")
    hits = hits.dropna(subset=["date_dt"])

    last_date = None
    if not hits.empty:
        last_date = hits["date_dt"].max().date().isoformat()

    return {"target": target_lc, "changed": True, "matches": matches, "last_date": last_date}


def format_yes_no_result(r: dict) -> str:
    if not r.get("changed"):
        return f"Ei. Osaa '{r.get('target','')}' ei ole vaihdettu."

    if r.get("last_date"):
        return f"Kyllä. Viimeksi vaihdettu {r['last_date']} ({r['matches']} merkintää)."

    return f"Kyllä. Vaihdettu {r['matches']} kertaa, mutta päivämäärä puuttuu."
