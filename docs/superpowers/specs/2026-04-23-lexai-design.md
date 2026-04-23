# AI-Powered Indian Legal Document Simplifier — Design

**Hackathon:** Hack O'Clock 2026-04-23
**Team:** Abhilash Bikkannavar, Nachiket Bikkannavar
**Status:** Design locked

## Product goals

Upload an Indian legal contract (PDF or pasted text), surface risky clauses with inline visual highlights on the original document, explain each flagged clause in plain English, cite the applicable Indian statute, provide an exact negotiation script, and answer follow-up questions via retrieval-grounded chat.

### In scope (MVP)
- PDF upload (primary) + text paste (fallback)
- Clause segmentation via Claude
- Risk classification: clause-type (10 classes) + risk-level (standard / aggressive / illegal) via fine-tuned InLegalBERT
- Plain-English rewrite per clause
- Indian law reference per clause (statute + section)
- Negotiation script per flagged clause (exact counter-proposal language)
- RAG-based Q&A over clause embeddings
- Inline PDF risk heatmap (demo moment)

### Out of scope
- DOCX input, multi-document comparison, persistent history, auth, export to DOCX.

### Demo-ranked priorities (A > B > C > D > E)
1. **A** — Inline risk flags on the original PDF (demo money-shot)
2. **B** — Negotiation script with exact counter-language
3. **C** — Q&A chat with statute-grounded answers
4. **D** — Side-by-side original ↔ plain-English transformation
5. **E** — Risk summary + Indian law citations

## Architecture

```
app.py                         Streamlit UI (3-column: PDF | Details+diff | Chat)
├── src/parser.py              pymupdf: PDF → text + per-char page/bbox metadata
├── src/segmenter.py           Claude Sonnet: one call → [{text, page, bbox}, ...]
├── src/lexbert.py             InLegalBERT + LoRA: type head (10-class) + risk head (3-class) + embedding
├── src/scorer.py              Cosine-sim vs standard-clause reference embeddings → composite risk
├── src/claude_analyzer.py     asyncio.gather — N parallel Claude calls, each returns
│                              {statute, section, flag, plain_english, negotiation_script, jurisdiction_flag}
│                              (statute citation produced by Claude Executor from its Indian-law knowledge,
│                               grounded in LexBERT's type + risk classification)
├── src/summarizer.py          ONE Claude call after all analyses → document-level summary
│                              (doc type, top 3 concerns, overall risk posture)
├── src/pdf_renderer.py        pymupdf renders pages as PNG with colored overlay rectangles
├── src/rag.py                 Embed query → cosine-sim over clause embeddings → top-3 → Claude
└── src/pipeline.py            Orchestrates the full flow; returns UI state dict
```

**Per-clause analysis output:**
```
{statute, section, flag, plain_english, negotiation_script, jurisdiction_flag}
```
`jurisdiction_flag` is `null` for Indian-law clauses or a string like `"governed by laws of Delaware — conflicts with Indian jurisdiction"` when Claude detects foreign-law invocation. UI renders a ⚠️ badge next to such clauses.

**UI details (Column 2 per selected clause):**
- Original clause text (quoted, gray border) — the "before"
- Plain-English rewrite (green border) — the "after"
- Side-by-side gives the ranked-D demo moment for free.
- Indian law badge + negotiation script below.

**Document-level summary banner (above the 3 columns):**
> *"Rental agreement, Mumbai. **3 high-risk clauses.** Main concerns: security deposit non-standard (§4), eviction waives TP Act §106 notice rights (§8), rent escalation 15% exceeds Maharashtra RCA (§6)."*

Generated from all clause analyses in one final Claude call. ~2s, ~$0.003.

### Models
| Role | Model |
|---|---|
| Clause type + risk classifier | Fine-tuned InLegalBERT + LoRA (type head + risk head) |
| Clause embeddings (similarity, RAG) | Pre-fine-tune InLegalBERT `[CLS]` pooling |
| Segmentation, clause analysis, Q&A | Claude Sonnet 4.6 |

## Data flow — progressive eager with streaming

```
t=0s    User uploads PDF (or pastes text)         [UI: "Parsing..."]
t=1s    parser: extract text + coords
t=1s    segmenter: 1 Claude call                  [UI: "Finding clauses..."]
t=6s    lexbert: classify + risk-score N clauses  [UI: "Scoring risk..."]
t=9s    pdf_renderer: overlay PNGs per page       [UI: RISK FLAGS APPEAR ← demo moment]
t=9s    claude_analyzer: N parallel calls fire    [UI: right panel shows "Generating..." placeholders]
t=19s   All clause analyses streamed in           [UI: clause details filled in]
t=21s   summarizer: 1 Claude call → doc summary   [UI: summary banner populated]
user    Ask question → rag retrieves top-3 → Claude answers (1-2s)
```

Total upload-to-full-UI: **~19 seconds**. Risk flags visible at **~9 seconds**. Demo rhythm lets presenter fill the 9s with narration before the money-shot lands.

### Why this architecture (design rationale)
- **Fine-tuning not pure LLM prompting:** judging criteria include Indian legal context awareness. A trained model demonstrably better than zero-shot is the ML contribution. Without fine-tuning, product reads as "API wrapper with a UI."
- **LoRA with frozen base:** 0.27% of parameters train; pretrained knowledge cannot be catastrophically forgotten.
- **Per-clause parallel Claude calls, not one mega-call:** 6× faster wall latency, isolated failures, enables progressive UI rendering during the demo.
- **Pure RAG over clause embeddings:** reuses existing embeddings (zero infra cost), keeps context window small, scales to long contracts, gives judges a "proper retrieval" talking point.
- **pymupdf + overlay rectangles (not streamlit-pdf-viewer):** zero third-party component risk on live stage; full control over highlight styling.

## UI layout (locked)

```
┌──────────────────────────┬───────────────────┬────────────────┐
│                          │  Clause 1         │  💬 Ask AI     │
│  📄 Rental.pdf           │  HIGH · non-comp. │  [history…]    │
│                          │                   │                │
│  [page 1 with colored    │  Plain English:   │                │
│   risk overlays; click   │  "This clause…"   │                │
│   to select a clause]    │                   │                │
│                          │  Law: §27         │                │
│                          │                   │                │
│                          │  Negotiation:     │                │
│                          │  "I cannot agree" │                │
│                          │  [Copy button]    │  [input box]   │
└──────────────────────────┴───────────────────┴────────────────┘
  50% width                   30% width            20% width
```

Header: upload button · filename · summary cards (X high / Y med / Z low).

## Error handling & fallbacks

| Failure | UX |
|---|---|
| PDF parse fails | Error + "try text paste" affordance |
| Segmentation returns 0 or >100 clauses | Flag as "unusual format", enable manual text paste |
| Claude analyzer fails per clause | Clause shows "analysis unavailable — click retry"; others render |
| LexBERT confidence < 0.4 | Clause tagged "uncertain" (grey), not colored |
| Q&A Claude fails | Error in chat column; chat stays usable |

## Testing & demo prep

- 3 curated test contracts (1 rental, 1 employment, 1 consumer ToS), end-to-end validated before demo
- Fallback plan: if a live PDF breaks mid-demo, switch to a pre-loaded known-good contract

## Deliverables

- Code in public repo `Abhilash-003/AI-Powered-Legal-Document-Simplifier-HackOClock`
- Working live demo (local Streamlit or hosted)
- Demo video
- Fine-tuned model (optionally pushed to HuggingFace as bonus polish)
- Indian contract-clause dataset (optionally published to HF as bonus artifact)
