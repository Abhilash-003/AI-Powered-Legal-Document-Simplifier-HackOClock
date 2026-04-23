"""Render PDF pages as PIL Images with colored semi-transparent risk overlays.

Each clause's (page_num, bbox) is drawn as a filled rectangle whose color
reflects its final_risk. The rendered images are what the Streamlit UI
displays in the left column — this is the demo money-shot.
"""
from dataclasses import dataclass
from typing import Optional

import fitz  # pymupdf
from PIL import Image, ImageDraw

RENDER_DPI = 150  # good balance of clarity and size for Streamlit
RISK_COLORS = {
    "High": (239, 68, 68, 90),     # red, ~35% alpha
    "Medium": (234, 179, 8, 80),   # amber, ~31% alpha
    "Low": (34, 197, 94, 45),      # green, ~18% alpha (subtle)
}
RISK_BORDERS = {
    "High": (239, 68, 68, 220),
    "Medium": (234, 179, 8, 200),
    "Low": (34, 197, 94, 140),
}


@dataclass
class ClauseHighlight:
    clause_id: int
    page_num: int
    bbox: tuple         # (x0, y0, x1, y1) in PDF points
    final_risk: str     # "High" | "Medium" | "Low"


def render_pages(pdf_bytes: bytes, highlights: list[ClauseHighlight],
                 dpi: int = RENDER_DPI) -> list[Image.Image]:
    """Return one PIL Image per PDF page, with overlays drawn."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    # group highlights by page
    by_page: dict[int, list[ClauseHighlight]] = {}
    for h in highlights:
        by_page.setdefault(h.page_num, []).append(h)

    zoom = dpi / 72.0  # PDF is 72 DPI native
    images: list[Image.Image] = []
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for h in by_page.get(page_idx, []):
            x0, y0, x1, y1 = h.bbox
            rect = (int(x0 * zoom), int(y0 * zoom), int(x1 * zoom), int(y1 * zoom))
            draw.rectangle(rect, fill=RISK_COLORS[h.final_risk], outline=RISK_BORDERS[h.final_risk], width=2)
        composited = Image.alpha_composite(img, overlay).convert("RGB")
        images.append(composited)
    doc.close()
    return images
