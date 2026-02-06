"""Render PDF manual pages into cached PNGs for OCR workflows.

This script is intentionally small and focused: it converts specific pages
from the service manual PDF into rasterized PNG images that can later be
processed by OCR tooling. The output is cached to disk so repeated runs do
not re-render pages that already exist.
"""

from pathlib import Path
import fitz  # pymupdf

ROOT = Path(__file__).resolve().parents[1]
# Source PDF for the service manual (must exist under data/).
PDF_PATH = ROOT / "data" / "s13servicemanual.pdf"
# Cache folder where rasterized pages are stored for OCR runs.
CACHE_DIR = ROOT / "db" / "cache" / "pages"

def render_page_png(page_num: int, zoom: float = 2.0) -> Path:
    """Render a single page to PNG and return the cached file path."""
    # Ensure the cache directory exists before writing output.
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CACHE_DIR / f"manual_page_{page_num}.png"
    # Skip rendering if we already have a cached file.
    if out_path.exists():
        return out_path

    # Open the PDF and render the page using a scaling matrix.
    doc = fitz.open(str(PDF_PATH))
    # PyMuPDF uses 0-based indexing for page numbers.
    page = doc.load_page(page_num - 1)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    pix.save(str(out_path))
    doc.close()

    return out_path


# Everything below is only for quick manual testing.

def render_pages(pages: list[int]) -> None:
    """Render and print multiple pages for quick verification."""
    for p in pages:
        out = render_page_png(p)
        print(f"Sivu {p} -> {out}")


if __name__ == "__main__":
    # Example page ranges for smoke-testing the PDF rendering.
    pages = (
        list(range(1, 11)) +      # start
        list(range(200, 211)) +   # middle
        list(range(880, 891))     # end
    )

    # Render the sample pages and emit file paths.
    render_pages(pages)