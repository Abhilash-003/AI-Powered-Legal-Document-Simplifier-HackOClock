# LexAI pipeline — text-only flow

Three views below. **Advisor-Executor loop** (the architectural pattern, matching Anthropic's reference). **Linear ASCII flow** (the sequential pipeline). **Mermaid** (renders to a real diagram in GitHub / Notion / Obsidian / mermaid.live).

---

## Advisor ↔ Executor loop (our adaptation of Anthropic's pattern)

```
                      ┌────── main loop ──────┐
                      │                       │
                      ▼                       │
         ┌─────────────────────────┐          │         ┌────────────────────────────┐
         │   Claude Sonnet 4.6     │          │         │         LexBERT            │
         │      ═ EXECUTOR ═       │───── tool call ───▶│        ═ ADVISOR ═          │
         │   runs per clause       │          │         │      (on-demand)           │
         │   runs per Q&A turn     │          │         │    local · MPS             │
         │   produces:             │          │         │   InLegalBERT + LoRA       │
         │     plain_english       │          │         │   → type · risk · embed    │
         │     negotiation_script  │          │         │                            │
         └────────────┬────────────┘          │         └─────────────┬──────────────┘
                      │                       │                       │
                read  │  write                │                       │  reviews
                      ▼                       │                       │   context
         ┌────────────────────────────────────────────────────────────────────────────┐
         │                              SHARED CONTEXT                                 │
         │                                                                              │
         │    clauses = [                                                               │
         │      { id, text, page, bbox,                   ← parser.py                   │
         │        clause_type, risk_level_ml, embedding,  ← LexBERT  (Advisor)          │
         │        final_risk, percentile, similarity,     ← scorer.py                   │
         │        statute, section, flag,                 ← Claude   (Executor)         │
         │        plain_english, negotiation_script,      ← Claude   (Executor)         │
         │        jurisdiction_flag },                                                   │
         │      ... × N clauses                                                         │
         │    ]                                                                          │
         │                                                                              │
         │                            ◀── sends advice ──                                │
         └────────────────────────────────────────────────────────────────────────────┘

                     Advisor reads the same context as Executor.
```

**Mapping to Anthropic's "advisor strategy":**
| Anthropic's diagram | LexAI |
|---|---|
| Executor (Sonnet) | **Claude Sonnet 4.6** — rewrites, negotiation, Q&A |
| Advisor (Opus) | **LexBERT** — fine-tuned InLegalBERT + LoRA, domain-specialized |
| Tool call | LexBERT consultation per clause |
| Sends advice (dashed) | LexBERT writes `{type, risk_level, embedding}` into the clause dict |
| Reviews context | Advisor reads the clause text from Shared Context |
| Read / write | Executor reads Advisor's fields + clause text; writes its own outputs |
| Main loop | Our `asyncio.gather` loop over N clauses (upload flow) + per-question loop (Q&A) |

**Implementation — literal tool-use, not simulated.** Claude (Executor) has the `consult_lexbert_advisor` tool available in every per-clause prompt and every Q&A turn. When Claude needs to verify an Indian statute citation, it **emits a tool call**; our runtime executes it against LexBERT's embedding index over our 6,400-clause reference corpus; Claude receives the top-3 retrieved passages (each tagged with its Indian Act + section + risk level) and grounds its final JSON in what LexBERT returned. Up to 2 tool-use turns per clause, capped for latency. The classification heads (type + risk) also run eagerly in an earlier phase — so the Executor has BOTH initial LexBERT classifications AND the ability to retrieve more grounded references on demand. Real round-trip Advisor-Executor, not simulated.

---

## Linear ASCII flow (top-to-bottom sequential pipeline, with shared memory rail)

Pipeline runs **left column, top to bottom**. Every stage reads from and/or writes to the **shared-context rail on the right** — the Python `clauses = [{...}]` list that the Advisor and Executor both mutate. Dashed arrows show where each stage interacts with shared memory.

```
       PIPELINE (top-to-bottom)                              SHARED MEMORY (rail)
   ┌──────────────────────────────┐
   │           USER               │
   │        upload PDF            │
   └──────────────┬───────────────┘
                  │
                  ▼
   ┌──────────────────────────────┐
   │         parser.py            │   local · pymupdf · ~1s
   │   full text + word bboxes    │
   └──────────────┬───────────────┘ ·· writes · text, bboxes  ·· ▶┐
                  │                                                │
                  ▼                                                │
   ┌──────────────────────────────┐                                │
   │        segmenter.py          │   CLAUDE · 1 call · ~5s        │
   │   clause list + char spans   │ ·· writes · clause list   ·· ▶ │
   └──────────────┬───────────────┘                                │
                  │                                                │
                  ▼                                                │
   ╔══════════════════════════════╗                                │    ┌────────────────────┐
   ║ ◀── A D V I S O R ──▶         ║   local · MPS · ~3s            │    │     S H A R E D    │
   ║        lexbert.py             ║                                │    │   C O N T E X T    │
   ║    InLegalBERT + LoRA         ║ ·· writes · type, risk,    ·· ▶├───▶│                    │
   ║  → type · risk · embedding    ║            embedding           │    │  clauses = [       │
   ╚══════════════╤═══════════════╝                                │    │   { id, text,      │
                  │                                                │    │     page, bbox,    │
                  ▼                                                │    │     clause_type,   │
   ┌──────────────────────────────┐                                │    │     risk_level_ml, │
   │         scorer.py            │   local · <1s                  │    │     embedding,     │
   │   composite final_risk       │ ·· writes · final_risk,    ·· ▶├───▶│     final_risk,    │
   └──────────────┬───────────────┘            percentile          │    │     percentile,    │
                  │                                                │    │     statute,       │
                  ▼                                                │    │     section, flag, │
 ★ ┌──────────────────────────────┐ ★                              │    │     plain_english, │
 ★ │      pdf_renderer.py         │ ★  DEMO MOMENT  (t ≈ 10 s)     │    │     negotiation,   │
 ★ │ PDF pages w/ risk overlays   │ ★ ◀·· reads · bbox +      ··───┤◀───│     jurisdiction } │
 ★ └──────────────┬───────────────┘ ★           final_risk         │    │   × N clauses      │
                  │                                                │    │  ]                 │
                  ▼                                                │    │                    │
   ╔══════════════════════════════╗                                │    │   (Python list of  │
   ║ ◀── E X E C U T O R ──▶        ║  CLAUDE · N parallel · ~10s   │    │    dicts in        │
   ║    claude_analyzer.py         ║                                │    │    memory)          │
   ║    asyncio.gather              ║ ◀·· reads · text, type,  ·· ──┤◀───│                    │
   ║                               ║          risk                  │    │                    │
   ║                               ║                                │    │                    │
   ║ → statute + section + flag    ║ ·· writes · statute,       ·· ▶├───▶│                    │
   ║   plain_english + negotiation ║           section, flag,       │    │                    │
   ║   + jurisdiction_flag         ║           plain_english,       │    │                    │
   ║                               ║           negotiation,         │    │                    │
   ║                               ║           jurisdiction         │    │                    │
   ╚══════════════╤═══════════════╝                                │    │                    │
                  │                                                │    │                    │
                  ▼                                                │    │                    │
   ┌──────────────────────────────┐                                │    │                    │
   │       summarizer.py          │   CLAUDE · 1 call · ~2s        │    │                    │
   │  doc type · posture · top-3  │ ◀·· reads · all clauses  ·· ──┤◀───│                    │
   │                              │ ·· writes · doc_summary  ·· ▶ ├───▶│                    │
   └──────────────┬───────────────┘                                │    │                    │
                  │                                                │    │                    │
                  ▼                                                │    │                    │
   ┌──────────────────────────────┐                                │    │                    │
   │          app.py              │   Streamlit · renders          │    │                    │
   │     3-column UI              │ ◀·· reads · entire state ·· ──┤◀───│                    │
   └──────────────┬───────────────┘                                │    │                    │
                  │                                                │    │                    │
       (user asks a question)                                      │    │                    │
                  │                                                │    │                    │
                  ▼                                                │    │                    │
   ┌──────────────────────────────┐                                │    │                    │
   │           rag.py             │   local cosine + CLAUDE · ~2s  │    │                    │
   │  embed query → top-3 clauses │ ◀·· reads · embeddings + ·· ──┤◀───│                    │
   │  Claude answers w/ citations │           text                 │    │                    │
   │                              │ ·· writes · chat answer   ·· ▶├───▶│                    │
   └──────────────┬───────────────┘                                │    └────────────────────┘
                  │                                                │
                  ▼
           answer in chat panel
```

**How to read this diagram:**
- Solid vertical arrows (│ ▼) = sequential pipeline order
- Dashed horizontal arrows (·· ▶) = writes to the shared clauses list
- Dashed reversed arrows (◀··) = reads from the shared clauses list
- The **Advisor** (LexBERT) writes `{clause_type, risk_level_ml, embedding}` into each clause dict
- The **Executor** (Claude Analyzer) reads those Advisor-written fields then writes back `{plain_english, negotiation_script, jurisdiction_flag}`
- Every subsequent stage (pdf_renderer, summarizer, app.py, rag.py) is a shared-memory reader

---

## Timeline strip

```
  t=0s        t=6s            t=9s        t=10s ★         t=20s                 Q&A on demand
  ────────────────────────────────────────────────────────────────────────────────────────────
  upload   segment (Claude)   LexBERT   RENDER PDF      Claude analyzer        rag + answer
                              classify   w/ risk         N parallel            ~2s per question
                              risk       overlays        plain-English +
                              embed                      negotiation
                                         ▲
                                         │
                                    DEMO MOMENT
                                 (risk flags on PDF)
```

---

## Mermaid version (renders to a real diagram)

Paste into GitHub README, Notion, or <https://mermaid.live>:

~~~mermaid
flowchart TB
    U([USER uploads PDF]):::user --> PARSE
    PARSE[parser.py<br/><i>pymupdf · text + bboxes · 1s</i>]:::local --> SEG
    SEG[segmenter.py<br/><i>Claude · 1 call · 5s</i>]:::claude --> LX
    LX[["<b>LexBERT</b> — ADVISOR<br/>InLegalBERT + LoRA<br/>type · risk · embed · 3s"]]:::advisor --> SCORE
    SCORE[scorer.py<br/><i>composite risk · percentile</i>]:::local --> REND
    REND[("<b>pdf_renderer.py</b><br/>★ DEMO MOMENT ★<br/>risk-colored PDF · 10s")]:::demo --> AN
    AN[["<b>claude_analyzer.py</b> — EXECUTOR<br/>N parallel calls · asyncio.gather<br/>statute · plain-English · negotiation · 10s"]]:::executor --> SUM
    SUM[summarizer.py<br/><i>Claude · 1 call · 2s</i>]:::claude --> UI
    UI[/app.py · Streamlit<br/>PDF · details · chat/]:::ui --> Q{user asks Q?}
    Q -- yes --> RAG[rag.py<br/><i>embed query · top-3 · Claude answer · 2s</i>]:::claude
    RAG --> UI

    classDef user      fill:#faf6ec,stroke:#0f0d0a,color:#0f0d0a
    classDef local     fill:#e8dfce,stroke:#0f0d0a,color:#0f0d0a
    classDef claude    fill:#f7e6e6,stroke:#8b1c1c,color:#0f0d0a
    classDef advisor   fill:#e6eef7,stroke:#1f3a5f,stroke-width:2px,color:#1f3a5f
    classDef executor  fill:#f7e6e6,stroke:#8b1c1c,stroke-width:2px,color:#8b1c1c
    classDef demo      fill:#fff3d9,stroke:#c97a2a,stroke-width:2.5px,color:#c97a2a
    classDef ui        fill:#faf6ec,stroke:#0f0d0a,color:#0f0d0a
~~~

---

## Legend

| Symbol | Meaning |
|---|---|
| **━━** box | component (file) |
| **╔═╗** box | role-tagged component (Advisor or Executor) |
| **★** box | the demo moment — what judges see first |
| **━▶** | data flow |
| **local** tag | runs on local MPS / CPU |
| **CLAUDE** tag | runs via Anthropic API |

---

## One-line pitch of the flow

> PDF in → parser extracts text with bboxes → Claude segments into clauses → **LexBERT** (our fine-tuned Advisor) classifies type + risk + embeds each clause locally → scorer + law engine attach the Indian statute reference → pdf_renderer overlays colored rectangles onto the original PDF (**the demo moment** — user sees risk flags inline, t ≈ 10 s) → in parallel, **Claude** (the Executor) generates plain-English rewrites + negotiation scripts for every clause via asyncio.gather → summarizer produces a doc-level banner → Streamlit's 3-column UI paints it all → user asks a question → RAG retrieves top-3 clauses by cosine similarity → Claude answers grounded in them.
