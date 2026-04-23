"""Generate a clean, editorial-style architecture flowchart for LexAI → PNG.

Uses matplotlib (already installed). Output: docs/pitch/diagrams/architecture.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = Path("docs/pitch/diagrams/architecture.png")
OUT.parent.mkdir(parents=True, exist_ok=True)

# ---- palette (light theme, editorial) ----
INK        = "#0f0d0a"
INK_SOFT   = "#2a2520"
PAPER      = "#faf6ec"
PAPER_EDGE = "#e8dfce"
SEAL       = "#8b1c1c"
COURT      = "#1f3a5f"
SAFFRON    = "#c97a2a"
MUTED      = "#6e6759"
RULE       = "#b8ab90"
ARROW_CLR  = "#4a4033"

# ---- figure ----
fig, ax = plt.subplots(figsize=(16, 9), dpi=160)
fig.patch.set_facecolor(PAPER)
ax.set_facecolor(PAPER)
ax.set_xlim(0, 100)
ax.set_ylim(0, 56)
ax.set_aspect("equal")
ax.axis("off")

# ---- Title ----
ax.text(50, 53.2, "LexAI — pipeline at a glance",
        fontsize=22, fontweight="semibold", fontfamily="serif",
        color=INK, ha="center", va="center", style="italic")
ax.text(50, 50.2, "upload to risk-annotated PDF in ~10 seconds · full UI in ~20 seconds",
        fontsize=10, color=MUTED, ha="center", va="center", fontfamily="serif")
ax.plot([12, 88], [48, 48], color=RULE, linewidth=0.5)


def box(cx, cy, w, h, title, tag, desc,
        tag_color=INK, fill=PAPER_EDGE, edge=INK, badge=None, badge_color=None):
    x, y = cx - w/2, cy - h/2
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.15,rounding_size=0.35",
                                facecolor=fill, edgecolor=edge, linewidth=1.0))
    # TAG (small-caps, at top inside box)
    ax.text(cx, cy + h/2 - 1.1, tag, fontsize=6.5, fontweight="bold",
            color=tag_color, ha="center", va="top", family="monospace")
    # TITLE
    ax.text(cx, cy + 0.3, title, fontsize=11.5, fontweight="semibold",
            color=INK, ha="center", va="center", fontfamily="serif")
    # DESC
    ax.text(cx, cy - h/2 + 1.2, desc, fontsize=7.5, color=INK_SOFT,
            ha="center", va="bottom", fontfamily="serif", style="italic")
    # BADGE above box
    if badge:
        ax.text(cx, cy + h/2 + 0.8, badge, fontsize=8, fontweight="bold",
                color=badge_color or tag_color, ha="center", va="bottom",
                family="monospace")


def arrow(x1, y1, x2, y2, color=ARROW_CLR, lw=1.3, style="->"):
    """Clean thin arrow via annotate — small head, no giant triangles."""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                shrinkA=1, shrinkB=1))


# ========== ROW 1 — main pipeline (y=34) ==========
# Step 1 — Upload
box(10, 34, 13, 7,
    title="Upload PDF",
    tag="USER",
    desc="rental / employment / ToS\n(text-paste fallback)")

# Step 2 — Parse + Segment
box(29, 34, 14, 7,
    title="Parse + Segment",
    tag="LOCAL + CLAUDE · 1 CALL",
    desc="pymupdf + word bboxes,\nClaude returns clauses")

# Step 3 — LexBERT (ADVISOR) — highlighted
box(50, 34, 16, 7,
    title="LexBERT",
    tag="LOCAL · MPS",
    desc="InLegalBERT + LoRA\ntype · risk · embed",
    fill="#e6eef7", edge=COURT, tag_color=COURT,
    badge="▼  ADVISOR", badge_color=COURT)

# Step 4 — Render with overlays (DEMO MOMENT)
box(74, 34, 16, 7,
    title="Render with overlays",
    tag="LOCAL · t ≈ 10 s",
    desc="PDF pages as PNG,\nrisk-colored rectangles",
    fill="#fff3d9", edge=SAFFRON, tag_color=SAFFRON,
    badge="★  DEMO MOMENT", badge_color=SAFFRON)

# Arrows — row 1
arrow(16.5, 34, 22, 34)
arrow(36, 34, 42, 34)
arrow(58, 34, 66, 34)

# ========== ROW 2 — Claude analysis + UI (y=21) ==========
# Step 5 — Claude Analyzer (EXECUTOR)
box(42, 21, 22, 7,
    title="Claude Analyzer — N parallel calls",
    tag="CLAUDE · asyncio.gather · ~10 s",
    desc="plain-English + negotiation script\n+ jurisdiction flag per clause",
    fill="#f7e6e6", edge=SEAL, tag_color=SEAL,
    badge="▲  EXECUTOR", badge_color=SEAL)

# Step 6 — 3-column UI
box(72, 21, 16, 7,
    title="3-column UI",
    tag="STREAMLIT",
    desc="PDF · clause details · chat")

# Arrow: LexBERT → Claude Analyzer (cross-row, drawn as 2 segments going down-left)
# from LexBERT bottom (50, 30.5) down to Analyzer top
arrow(50, 30.5, 42, 24.5, color=COURT, lw=1.2)

# Arrow: Render with overlays → UI (straight down-right)
arrow(74, 30.5, 72, 24.5, color=ARROW_CLR, lw=1.2)

# Arrow: Claude Analyzer → UI (row 2 horizontal)
arrow(53.2, 21, 63.8, 21, color=SEAL, lw=1.3)

# ========== ROW 3 — Q&A loop (y=8) ==========
# Step 7 — User asks Q
box(15, 8, 14, 6,
    title="User asks Q",
    tag="USER · CHAT",
    desc="natural-language question")

# Step 8 — RAG retrieval
box(36, 8, 15, 6,
    title="RAG retrieval",
    tag="LOCAL · COSINE",
    desc="embed query · top-3 clauses")

# Step 9 — Claude answer
box(57, 8, 14, 6,
    title="Claude answer",
    tag="CLAUDE · ~2 s",
    desc="grounded · cites clause IDs",
    fill="#f7e6e6", edge=SEAL, tag_color=SEAL)

# Step 10 — UI chat display
box(78, 8, 12, 6,
    title="UI chat panel",
    tag="DISPLAY",
    desc="answer with citations")

# Arrows — row 3
arrow(22, 8, 28.5, 8)
arrow(43.5, 8, 48.5, 8)
arrow(64, 8, 71, 8)

# Arrow: UI (row 2) → User asks Q (row 3) — dashed/curved to indicate "on demand"
ax.annotate("", xy=(15, 11), xytext=(72, 17.5),
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.8,
                            linestyle=(0, (4, 3)),
                            connectionstyle="arc3,rad=-0.12",
                            shrinkA=3, shrinkB=3))
ax.text(36, 14.2, "user clicks into chat", fontsize=7.5, color=MUTED,
        ha="center", style="italic", fontfamily="serif")

# ========== Dividers between section rows ==========
for y_div in (28.3, 14.5):
    ax.plot([6, 94], [y_div, y_div], color=RULE, linewidth=0.3, linestyle=":")

# Section labels (left edge)
ax.text(3, 34, "upload\n& analyze", fontsize=8, color=MUTED, fontfamily="serif",
        style="italic", ha="left", va="center")
ax.text(3, 21, "enrich\n& display", fontsize=8, color=MUTED, fontfamily="serif",
        style="italic", ha="left", va="center")
ax.text(3, 8, "Q & A\nloop", fontsize=8, color=MUTED, fontfamily="serif",
        style="italic", ha="left", va="center")

# ========== Legend ==========
legend_y = 1.5
legend_items = [
    ("LOCAL · MPS / CPU",    PAPER_EDGE, INK),
    ("LEXBERT (Advisor)",    "#e6eef7",  COURT),
    ("CLAUDE (Executor)",    "#f7e6e6",  SEAL),
    ("DEMO MOMENT",          "#fff3d9",  SAFFRON),
]
x0 = 14
for label, fill, edge in legend_items:
    ax.add_patch(Rectangle((x0, legend_y), 2.2, 1.4,
                           facecolor=fill, edgecolor=edge, linewidth=0.7))
    ax.text(x0 + 2.8, legend_y + 0.7, label, fontsize=7.5, color=INK_SOFT,
            va="center", family="monospace")
    x0 += 20

# ========== Footer ==========
ax.text(50, -0.4, "LexAI · Hack O'Clock 2026 · github.com/Abhilash-003",
        fontsize=7, color=MUTED, ha="center", va="top", family="monospace")

plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
plt.savefig(OUT, dpi=180, bbox_inches="tight", facecolor=PAPER)
print(f"Saved → {OUT}")
