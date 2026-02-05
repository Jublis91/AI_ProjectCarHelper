from __future__ import annotations
from pathlib import Path
from PIL import Image
from backend.store import connect, init_db

import re
import pytesseract

ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = ROOT / "db" / "cache" / "pages"
PAGE_RE = re.compile(r"manual_page_(\d+)\.png$", re.IGNORECASE)

def parse_page_num(path: Path) -> int:
    m = PAGE_RE.search(path.name)
    if not m:
        raise ValueError(f"Virheellinen tiedosto nimi: {path.name}")
    return int(m.group(1))

def ocr_image(path: Path, lang: str = "eng") -> str:
    img = Image.open(path)
    text = pytesseract.image_to_string(img, lang=lang)
    return (text or "").strip()

def upsert_manual_page(page_num: int, text: str) -> None:
    conn = connect()
    cur  = conn.cursor()
    cur.execute(
        """
        INSERT INTO manual_pages(page_num, text)
        VALUES(?, ?)
        ON CONFLICT(page_num) DO UPDATE SET
            text = excluded.text
        """,
        (page_num, text),
    )
    conn.commit()
    conn.close()

def main() -> None:
    init_db()

    if not PAGES_DIR.exists():
        print("EI SIVUKUVIA. Aja ensin rederöinti, joka luo db/cache/pages/manual_page_{n}.png")
        return
    
    pngs = sorted(PAGES_DIR.glob("manual_page_*.png"))
    if not pngs:
        print("EI PNG-TIEDOSTOJA. Kansio on tyhjä: db/cache/pages")
        return
    
    total = 0
    nonempty = 0

    for png in pngs:
        page_num = parse_page_num(png)
        text = ocr_image(png, lang="eng")

        total += 1
        if text:
            nonempty += 1
            upsert_manual_page(page_num, text)

        print(f"Sivu {page_num}: {len(text)} merkkiä")

    print(f"Valmis. Sivut: {total}. Sivut joissa tekstiä: {nonempty}.")

if __name__ == "__main__":
    main()