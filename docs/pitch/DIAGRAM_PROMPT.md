# Prompt — build the LexAI architecture flowchart

Paste this entire document to the diagramming AI. It contains (1) product context, (2) the reference pattern we're adapting, (3) our specific implementation, (4) full 9-stage pipeline, (5) what the final diagram must communicate, and (6) output format requirements.

---

## 1. What you're diagramming

**LexAI** is an AI-powered Indian legal document simplifier built during an 18-hour hackathon. A user uploads any Indian rental, employment, or consumer terms-of-service contract as a PDF. The system, in under 20 seconds, returns:

1. The user's actual PDF with **risky clauses highlighted inline** (red = illegal, amber = aggressive, green = standard) — this is the "demo moment."
2. For each flagged clause: a **plain-English rewrite**, the specific **Indian statute + section** it violates or relates to, and an **exact negotiation script** the user can copy and send back to the landlord / employer.
3. A **RAG-powered chat interface** where the user can ask questions about any clause and get statute-grounded answers.

The Indian-law-specificity is the core differentiator. Post-employment non-competes are void under Indian Contract Act §27; the Transfer of Property Act §106 requires statutory eviction notice; EPF/ESIC contributions are mandatory and cannot be contracted out. A US-trained model gets these backwards. LexAI is trained on Indian-specific data.

## 2. The reference pattern — Anthropic's Advisor strategy

We adapt the following published pattern (reference image, "The advisor strategy"):

```
┌──────────────┐                 ┌──────────────┐
│   Executor   │ ── Tool call ──▶│   Advisor    │
│   (Sonnet)   │                 │   (Opus)     │
│ Runs every   │◀── Sends advice │  On-demand   │
│   turn       │                 │              │
└──────┬───────┘                 └──────┬───────┘
       │ Read / write                   │ Reviews context
       ▼                                │
┌────────────────────────┐              │
│    Shared context      │◀─────────────┘
│ Conversation · tools · │
│       history          │
└────────────────────────┘
```

**Anthropic's pattern, in our words:**
- An **Executor** model (Sonnet) runs the main loop every user turn — it reads from and writes to a **shared context** (the conversation, tools, call history).
- When the Executor needs specialized expert judgment, it calls an **Advisor** model (Opus) **on-demand** as a tool. The Advisor reads the same shared context, produces focused advice, writes it back to the shared context.
- Key idea: the Advisor runs selectively where the Executor needs deeper reasoning, rather than as a constant expensive model on every step.

## 3. How LexAI adapts this pattern

Our adaptation swaps the roles and model classes:

| Anthropic's pattern | LexAI's version |
|---|---|
| Executor = Sonnet (general-purpose LLM) | **Executor = Claude Sonnet 4.6** (plain-English rewrites, negotiation scripts, Q&A) |
| Advisor = Opus (more powerful LLM) | **Advisor = LexBERT** — our fine-tuned InLegalBERT (0.86 macro-F1) + LoRA adapter |
| Shared context = conversation + tools | **Shared context = clause state dict** (raw text, bboxes, type, risk, embedding, statute) |
| Advisor is on-demand for hard reasoning | **LexBERT is on-demand for every clause** — specialized Indian-law classifier with 0.28%-of-parameters adapter |

The Executor-Advisor mapping is philosophical and pitch-friendly: we have a general-purpose LLM (Claude) that produces the user-facing outputs, and a specialized domain model (LexBERT, fine-tuned on 8,000+ Indian contract clauses) that the Executor consults for every clause.

## 4. Implementation note — why we don't use literal tool-calls

The Advisor strategy, taken literally, would have Claude emit a tool call per clause (e.g., `assess_clause_risk("...")`), Claude stops, our runtime invokes LexBERT locally, injects the result, Claude resumes. For a 30-clause contract that's **60 Claude API round-trips = ~2 minutes of sequential latency**. Too slow for a live demo.

**Our optimization:** we run LexBERT eagerly over ALL clauses in parallel first (takes ~3 seconds on local MPS), then fire **N parallel Claude calls** (one per clause) where each call's prompt already contains LexBERT's classification + risk + statute as context. Same philosophical pattern, **6× faster wall latency** (~10 seconds), isolated failure modes.

So in our diagram, the arrow from Executor to Advisor is still there — but it's a batch operation, not a per-clause round-trip. The shared context is populated from LexBERT's output before the Executor's per-clause fan-out begins.

## 5. Full pipeline — nine stages in four lanes

Four logical lanes based on where work runs:

| Lane | Components |
|---|---|
| **User** | File upload, text paste, chat input |
| **Local · MPS** (Apple Silicon GPU) | parser · lexbert · scorer · law_engine · embedder · pdf_renderer |
| **Claude · parallel** (Anthropic API) | segmenter (1 call) · claude_analyzer (N parallel calls) · summarizer (1 call) · rag Q&A (per-turn) |
| **Rendering · UI** | app.py (Streamlit), 3-column layout: PDF + details + chat |

Nine pipeline stages, ordered:

| # | Stage | File | Runs on | Timing | Input | Output |
|---|---|---|---|---|---|---|
| 1 | Parse | `src/parser.py` | Local CPU | ~1s | PDF bytes (or text) | Full text + per-word bounding boxes per page |
| 2 | Segment | `src/segmenter.py` | Claude (1 call) | ~5s | Full text | List of clauses with character offsets |
| 3 | Classify + risk + embed | `src/lexbert.py` | Local MPS | ~3s | Clause texts | Per-clause: clause_type, risk_level, embedding (768-dim) |
| 4 | Score | `src/scorer.py` | Local CPU | <1s | Embedding + clause type | Similarity to standard-clause anchor + composite final_risk |
| 5 | Law lookup | `src/law_engine.py` | Local dict | <1s | clause_type | Applicable Indian statute + section + violation pattern |
| 6 | Render PDF with overlays | `src/pdf_renderer.py` | Local CPU | ~1s | PDF + per-clause bboxes + final_risk | PIL images with colored rectangles drawn |
| 7 | Analyze per clause | `src/claude_analyzer.py` | Claude (N parallel) | ~10s | Clause + classification + statute | plain_english + negotiation_script + jurisdiction_flag per clause |
| 8 | Summarize | `src/summarizer.py` | Claude (1 call) | ~2s | All clause analyses | Doc-level summary: type, risk posture, top 3 concerns |
| 9 | Q&A (on demand) | `src/rag.py` | Local embed + Claude (1 call per question) | ~2s | User question + clause embeddings | Answer with citations |

### Demo-moment timeline

```
t=0s   User uploads PDF                       [UI: "Parsing..."]
t=1s   parser extracts text + bboxes
t=6s   segmenter returns clauses              [UI: "Finding clauses..."]
t=9s   lexbert + scorer + law_engine done     [UI: "Scoring risk..."]
t=10s  pdf_renderer produces overlay pages    ← DEMO MONEY-SHOT: RISK FLAGS APPEAR
t=10s  N parallel Claude analyzer calls fire  [UI: right panel "Generating..."]
t=20s  All per-clause analyses streamed in    [UI: fully populated]
t=22s  summarizer call completes              [UI: top summary banner set]
user   Asks question → rag flow → 2s answer
```

## 6. What the diagram must communicate

### Primary diagram (required)
A **block diagram / flowchart** showing:
- All 9 stages as labeled boxes
- Four lanes (User / Local-MPS / Claude-parallel / Rendering-UI) as visual bands or grouped regions
- Arrows showing data flow between stages
- A **highlighted / emphasized arrow set** showing the **Executor → Advisor consultation** (Claude analyzer → LexBERT result injection, which is stage 7 drawing from stages 3-5)
- A **callout or timeline strip** showing the "risk flags appear at t=10s" demo moment
- Distinction between stages that run **once per upload** vs stages that run **per user question** (Q&A lives in its own mini-flow)

### Key visual distinctions
- Local MPS work vs Claude API work should be visually separated (different colors or different lane)
- The "demo moment" (stage 6 — PDF renderer outputting to UI) should be visually emphasized — this is the payoff of the whole system
- N parallel Claude calls in stage 7 should visibly show parallelism (fan-out to N, fan-in to aggregated state)

### Secondary diagram (nice-to-have but useful)
A **mini sequence / timeline** showing the 22-second end-to-end latency broken down by stage, with the "risk flags appear" checkpoint at t=10s clearly marked.

## 7. Style requirements

- **Clean, professional, presentation-grade.** The diagram will be used in a live hackathon pitch and screenshot for PowerPoint slides.
- **No AI-slop visual patterns:** avoid rainbow gradients, generic purple/pink backgrounds, cartoon icons, Comic Sans, or neon colors.
- **Committed color palette:** 3-4 colors maximum. Suggest an editorial, muted, India-legal-document-inspired palette:
  - Deep ink navy / near-black for base text and main boxes
  - Aged paper cream or off-white background
  - Seal-red accent (`#8b1c1c` area) for the Advisor / emphasis elements
  - Saffron or court blue for one secondary accent
- **Distinctive typography:** serif display font for headers (Cormorant Garamond, Playfair Display, or similar); sans-serif for body if needed (Inter is overused — prefer something like IBM Plex Sans or Source Sans).
- **Light theme only.** No dark backgrounds.
- **Labels must be legible** at the zoom level used for slide embedding (ideally readable at 50% slide scale).

## 8. Output format — preferred order

1. **Mermaid** diagram source (renders in GitHub, Notion, Obsidian, most markdown tools, and can be exported to SVG/PNG). Easiest to iterate on. Start here.
2. **SVG** (raw, hand-structured) if Mermaid can't express the four-lane layout cleanly. Gives full visual control.
3. **Excalidraw** JSON if a hand-drawn aesthetic suits the presentation.
4. Do NOT output as a generic web-page HTML/CSS "slide deck" — the user explicitly wants a proper diagram, not a website.

## 9. Deliverables

1. The primary flowchart (format above).
2. The secondary timeline strip (format above) — can be Mermaid `gantt` or a simple labeled horizontal band.
3. A **brief written caption** (2-3 sentences) for the diagram that can sit under it in a slide, explaining what it shows.
4. If the diagramming AI has alternative interpretations or simplifications, include one additional "simplified-for-one-slide" version of the primary diagram (fewer boxes, more narrative — 4-5 high-level groupings instead of 9 stages).

## 10. Hard constraints

- Every box label must be accurate — do not rename files, invent stages, or swap in different models.
- The InLegalBERT / LoRA / Claude Sonnet names are load-bearing for the pitch; preserve them exactly.
- "Executor" = Claude Sonnet, "Advisor" = LexBERT — preserve this mapping when echoing the Anthropic pattern.
- Do not add speculative future features to the diagram (e.g., no multi-doc comparison, no Hindi support, no HuggingFace publish arrows) — diagram current system only.
- Do not introduce a "vector database" block anywhere — we do in-memory cosine similarity against a numpy array, not a vector DB.

Produce the diagrams now.
