# ingest_manual.py

from pathlib import Path
import fitz  # pymupdf

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "data" / "s13servicemanual.pdf"
CACHE_DIR = ROOT / "db" / "cache" / "pages"

def render_page_png(page_num: int, zoom: float = 2.0) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CACHE_DIR / f"manual_page_{page_num}.png"
    if out_path.exists():
        return out_path

    doc = fitz.open(str(PDF_PATH))
    page = doc.load_page(page_num - 1)  # PyMuPDF on 0-indeksoitu
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    pix.save(str(out_path))
    doc.close()

    return out_path


if __name__ == "__main__":
    for p in [1, 10, 50]:
        out = render_page_png(p)
        print(f"Sivu {p} -> {out}")
