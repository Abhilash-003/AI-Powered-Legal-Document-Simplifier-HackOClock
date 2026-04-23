"""Extract text + per-word bounding boxes from a PDF.

Bounding boxes are critical — they are how pdf_renderer.py later draws
colored risk overlays on each page.

For text-paste input, we return `pages=[]` and let downstream code
fall back to a list-only UI (no PDF overlay).
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import fitz  # pymupdf


@dataclass
class Word:
    text: str
    page_num: int
    bbox: tuple  # (x0, y0, x1, y1) in PDF points
    char_start: int  # start offset in full_text
    char_end: int


@dataclass
class Page:
    page_num: int
    text: str
    width: float
    height: float
    words: list  # list[Word]


@dataclass
class ParsedDoc:
    full_text: str
    pages: list  # list[Page]
    source: str  # "pdf" or "text"

    @property
    def has_bboxes(self) -> bool:
        return self.source == "pdf" and len(self.pages) > 0


def parse_pdf(pdf_bytes: bytes) -> ParsedDoc:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages: list[Page] = []
    full_parts: list[str] = []
    cursor = 0  # char offset into full_text

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        words_raw = page.get_text("words")  # list of (x0, y0, x1, y1, word, block_no, line_no, word_no)
        page_text = page.get_text("text")

        words: list[Word] = []
        # map each word to its char offset in full_text by scanning page_text
        text_cursor = 0  # offset within page_text
        for x0, y0, x1, y1, word_str, *_ in words_raw:
            if not word_str.strip():
                continue
            # find word occurrence starting at text_cursor
            idx = page_text.find(word_str, text_cursor)
            if idx == -1:
                # fallback: skip this word for offset mapping, still record bbox
                char_start = cursor + text_cursor
                char_end = char_start + len(word_str)
            else:
                char_start = cursor + idx
                char_end = char_start + len(word_str)
                text_cursor = idx + len(word_str)
            words.append(
                Word(
                    text=word_str,
                    page_num=page_idx,
                    bbox=(x0, y0, x1, y1),
                    char_start=char_start,
                    char_end=char_end,
                )
            )

        pages.append(
            Page(
                page_num=page_idx,
                text=page_text,
                width=page.rect.width,
                height=page.rect.height,
                words=words,
            )
        )
        full_parts.append(page_text)
        cursor += len(page_text)

    doc.close()
    return ParsedDoc(full_text="".join(full_parts), pages=pages, source="pdf")


def parse_text(text: str) -> ParsedDoc:
    """Text-paste input: no bboxes, no PDF rendering downstream."""
    return ParsedDoc(full_text=text, pages=[], source="text")


def parse(input_data: Union[bytes, str], kind: Optional[str] = None) -> ParsedDoc:
    """Unified entry: bytes → parse_pdf, str → parse_text. kind overrides autodetect."""
    if kind == "pdf" or (kind is None and isinstance(input_data, (bytes, bytearray))):
        return parse_pdf(bytes(input_data))
    return parse_text(str(input_data))


def bboxes_for_char_range(doc: ParsedDoc, char_start: int, char_end: int) -> list[tuple[int, tuple]]:
    """Return list of (page_num, (x0, y0, x1, y1)) covering a char range.

    One tuple per page the range spans; bbox is the union of words in that page's portion.
    Used by pdf_renderer to draw overlays for clauses.
    """
    if not doc.has_bboxes:
        return []
    page_to_union: dict[int, list] = {}
    for page in doc.pages:
        for w in page.words:
            if w.char_end <= char_start or w.char_start >= char_end:
                continue
            page_to_union.setdefault(page.page_num, []).append(w.bbox)
    out = []
    for page_num, bboxes in page_to_union.items():
        x0 = min(b[0] for b in bboxes)
        y0 = min(b[1] for b in bboxes)
        x1 = max(b[2] for b in bboxes)
        y1 = max(b[3] for b in bboxes)
        out.append((page_num, (x0, y0, x1, y1)))
    return out
