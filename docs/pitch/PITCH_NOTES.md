# LexAI — speaker notes

Pitch length: target 3 minutes for a fast round; 5 minutes comfortable.
Open `deck.html` in a browser (Chrome / Safari / Firefox), press **F11** for fullscreen, use **← / →** to navigate. Slide numbers 1-9 jump-keys also work.

Each slide below: **time budget · what to say · what NOT to say · likely judge question + answer**.

---

## 01 · Hero — LexAI
**Budget: 10 seconds.**

*Say:* "LexAI — an Indian-law-aware reader for rental, employment, and consumer-terms contracts. We fine-tuned InLegalBERT with LoRA on a dataset we built ourselves, and paired it with Claude for plain-English rewrites."

*Don't say:* "Hi my name is..." — skip introductions unless asked. Every second you're not showing the product, you're losing judging attention.

---

## 02 · The problem
**Budget: 25 seconds.**

*Say:* "Ordinary Indians sign rental agreements, employment contracts, and terms-of-service drafted by lawyers, for lawyers. Most don't know that post-employment non-competes are *void* under Contract Act §27. Or that eviction requires a statutory 15-day notice under TP Act §106. Or that PF and ESIC contributions are mandatory and cannot be contracted out. The gap between what a clause *says* and what Indian law *actually enforces* is enormous — and it's the ordinary person who pays."

*Don't say:* soft generalities like "contracts are confusing". Be statute-specific — the judges notice.

*Likely question:* **"Why not just build a general legal reader?"**
*Answer:* "Because the direction of risk inverts across jurisdictions. A non-compete that's standard in New York is void in Delhi. A US-trained model gets these cases exactly backwards. We had to build Indian-specific or we'd be a worse Lexaloud."

---

## 03 · What we built
**Budget: 20 seconds.**

*Say:* "Upload any Indian rental, employment, or consumer contract. In under twenty seconds, the user sees their actual PDF with risk-flagged clauses colored inline. Click any flagged clause for a plain-English rewrite, the specific Indian statute it violates, and exact counter-language they can send back to the other party. Ask questions in the chat — the answer is retrieval-grounded in the clauses that matter."

*Don't say:* "We built a platform" — this is not a platform.

---

## 04 · The demo moment
**Budget: 30 seconds · this is the money-shot.**

**Ideally: live-switch to the actual Streamlit demo here.** If demo fails, the mockup on this slide serves as fallback.

*Say (live):* "Here's a real rental agreement from Mumbai. Watch — " *[upload the pre-tested demo PDF]* — "and within ten seconds, the risky clauses show up inline. This red one — *[click]* — LexBERT flagged it as illegal, it waives TP Act §106 notice rights, and here's the exact language you can send back. I can also ask: *[type] can I legally refuse clause four?*" *[Claude answers]*.

*Don't say:* "Let me just wait for this to load..." — if it stalls, switch to fallback immediately.

*Likely question:* **"How fast is inference?"**
*Answer:* "LexBERT risk scoring is under three seconds — runs locally on MPS, no API call. Plain-English rewrites and negotiation scripts are parallel Claude calls, complete in about ten seconds for a typical contract. Q&A is one to two seconds."

---

## 05 · Why this isn't a US tool
**Budget: 25 seconds · our strongest differentiation slide.**

*Say:* "Three examples where the direction of risk inverts across jurisdictions. Non-compete — enforceable in most US states, *void* in India under §27. Eviction notice — US landlords often get waivers enforced, Indian landlords legally *cannot* bypass TP Act §106. PF and ESIC — no US analog, *mandatory and non-waivable* in India. A model trained on CUAD or LEDGAR learns these exactly backwards. We trained Indian."

*Don't say:* "We're better than GPT-4." Don't compare to competitor models by name — keep focus on the jurisdictional argument.

*Likely question:* **"How do you actually detect jurisdictional conflict?"**
*Answer:* "Two ways. Our fine-tuned model is Indian-specific by training data. And Claude's per-clause prompt includes a `jurisdiction_flag` field — if a clause invokes foreign law explicitly, like 'governed by Delaware law', we surface a warning badge in the UI."

---

## 06 · System architecture
**Budget: 30 seconds · tech-depth slide for ML judges.**

*Say:* "Eight stages in four lanes. User uploads a PDF. In the local MPS lane, pymupdf extracts text with per-word bounding boxes; LexBERT — our Advisor — classifies type, risk, and embeds every clause; a similarity scorer compares against statute-grounded anchors to produce a composite risk score. In parallel, the Claude lane — our Executor — runs one segmentation call up front, then N parallel calls per clause that each produce the applicable Indian statute, a plain-English rewrite, and a negotiation script. A final summarizer call produces the top-of-page banner. The UI lane renders the PDF pages with colored overlays; Streamlit serves the three-column view; RAG runs on demand for chat. Everything fits within twenty seconds, end-to-end."

*Don't say:* read each box aloud. Gesture at the lanes, hit the high points.

*Likely question:* **"Why parallel Claude calls, not a mega-call?"**
*Answer:* "Single-call latency for thirty clauses is sequential generation — sixty seconds. Parallel calls finish in ten. Failure is also isolated; a bad JSON parse on clause seventeen doesn't kill the whole run. And we get progressive UI rendering during the demo."

---

## 07 · Dataset
**Budget: 30 seconds · this is where the ML contribution lives.**

*Say:* "No labeled Indian contract-clause corpus existed at this scale, so we built one. Six-thousand-four-hundred clauses, ten Indian-specific classes, generated via statute-grounded Claude prompts, risk-labeled in three tiers. For the five classes that have structural analogs in commercial contracts elsewhere — arbitration, termination, liability, IP ownership, notice — we also include a capped LEDGAR slice to give the model real contract-English grounding. Each LEDGAR class is capped at five hundred rows so the Indian anchor is never drowned. For the five Indian-only classes — rental escalation, eviction, PF/ESIC, probation, non-compete — the synthetic corpus is the entire training signal."

*Don't say:* "We scraped real contracts." We didn't; the corpus is synthetic + LEDGAR. Be honest.

*Likely question:* **"Isn't synthetic data risky? How do you know quality?"**
*Answer:* "Three controls. First, every clause is statute-grounded — Claude's prompt includes the specific Indian statute and the type of violation to generate for. Second, each class has a 45/35/20 split across standard/aggressive/illegal, so the model learns to distinguish. Third, we spot-check by hand. We accept this is a known genre gap with real contracts — it's mentioned explicitly in our README."

---

## 08 · Model training
**Budget: 25 seconds.**

*Say:* "Base model is InLegalBERT — BERT-base continuation-pretrained by IIT Kharagpur on 5.4 million Indian court judgments and statutes. We fine-tune with LoRA at rank eight, targeting only the attention layers' query and value projections. Two-hundred-ninety-seven thousand trainable parameters against one-hundred-ten million — zero-point-two-eight percent. The base encoder is structurally frozen. Following Paul et al.'s paper, we use a hundred-times learning-rate gap between the head and the encoder: one-e-minus-three on the head, one-e-minus-five on the body. This keeps the pretrained Indian-legal knowledge stable while our task-specific adapter learns."

*Don't say:* dive into hyperparameters unless asked. "We used LoRA with the paper's recipe" is enough.

*Likely question:* **"Why not full fine-tune?"**
*Answer:* "Catastrophic forgetting. With 6,400 training examples against 5.4 million pretraining examples, a full fine-tune would overwrite the Indian-legal priors we specifically chose InLegalBERT for. LoRA makes forgetting structurally impossible — the base weights don't change."

---

## 09 · Results
**Budget: 25 seconds.**

*Say:* "Our fine-tuned type classifier achieves macro F1 0.91 on a 2,316-clause held-out test set. Eight of the ten classes are above 0.87 F1 — rent_escalation, probation, ip_ownership and arbitration are all above 0.95. The risk classifier achieves macro F1 0.80 across standard, aggressive, and illegal. Confusion matrices are in `docs/eval/`. We fine-tuned specifically because we needed the output in a structured, deterministic format — clause type and risk level as categorical labels rather than free-text — and because fine-tuning gives us a compact 1.2 MB LoRA adapter that runs in 3 ms per clause locally."

*If asked about termination being weaker:* "Termination sits at 0.77 F1. It confuses most with notice_period because both use employment-contract language with overlapping lexical patterns. Fixing this is in the 'more labeled termination examples' future work list."

---

## 10 · Engineering choices
**Budget: 20 seconds.**

*Say:* "Three choices that don't show up in papers but matter for a live demo. LoRA not full fine-tune — ten-times faster training, ships in a 1.2 MB adapter, can't catastrophically forget. Parallel Claude via asyncio.gather — six-times faster wall latency than a mega-call, with isolated failure modes. RAG over clause embeddings reusing the InLegalBERT encoder we already have — ten lines of code, no vector database, grounded Q&A even on long contracts."

*Don't say:* list every optimization. Three is the memorable number.

---

## 11 · Judging rubric coverage
**Budget: 20 seconds.**

*Say:* "Every rubric line ties to a specific feature. Accuracy of clause risk identification — three signals fused, ML head plus similarity plus rule-based law lookup. Plain-language rewrites — Claude Sonnet with statute-grounded per-clause prompts. Complex nested legal language — Claude-based segmentation, not regex, an architectural choice specifically targeting this line. Indian legal context awareness — end-to-end, from the pretrained base model through the synthetic corpus through the statute engine through the jurisdiction flag."

---

## 12 · Closing
**Budget: 10 seconds.**

*Say:* "Built in eighteen hours for the ordinary citizen who shouldn't need a lawyer to read their own lease. The repo is public — MIT-licensed. Happy to answer questions."

*Don't say:* "That's all!" or "Thank you for listening" — let the slide close you out.

---

## Contingency scripts

### If the live demo fails mid-pitch
1. Switch slides to slide 4 (the demo moment mockup) — it's pre-rendered, looks exactly like the real UI.
2. Say: "Let me show you a pre-recorded walkthrough while we debug — this is what the product looks like on a real rental agreement."
3. **Have a 30-second screen recording ready** (record it before the pitch).

### If LexBERT training hasn't finished in time for the live demo
- Use the epoch-2 checkpoint (already saved at `models/lexbert-type/checkpoint-476/`).
- Or pre-render one demo contract completely, cache the JSON, and show the UI in "demo mode" reading the cached analysis. Much safer than live inference on stage.

### If asked "what's next"
- Publish the Indian contract-clause dataset to HuggingFace (we have the artifact ready).
- Push the LoRA adapter to HuggingFace as a downloadable model card.
- Multi-doc comparison ("is this lease more aggressive than the one I signed last year?").
- Hindi and regional-language support via translation before classification.

### If asked "how's it different from ChatGPT / Claude / a law firm"
- "ChatGPT doesn't know Contract Act §27 voids post-employment non-competes." *(Actually it might — better framing:)*
- "The differentiation isn't what it *can* say — it's structural: we triangulate LexBERT's ML signal, similarity against Indian-standard anchors, and a hand-verified statute rulebook. No single-model output; every risk flag comes from three independent sources."

### If asked "license / commercial viability"
- MIT license on code. Synthetic dataset — our contribution, redistributable. InLegalBERT base — check IIT Kharagpur's license (research-friendly).

---

## Judge-killer questions — rehearsed answers

**Q: Is it synthetic data or real contracts?**
"Six-thousand-four-hundred Indian clauses are Claude-generated with statute-grounded prompts. Real-world validation is future work and we call this out openly."

**Q: What if a contract has clauses outside your 10 types?**
"Model returns the nearest class with a confidence score. If confidence is below 0.4, the UI marks the clause 'uncertain' — grey, not colored — so false positives don't mislead the user."

**Q: How accurate is the negotiation script? Can someone actually use it?**
"Claude generates the exact language grounded in the cited statute. It's drafting quality, not a lawyer's sign-off. The UI says 'copy + send' — the user still chooses whether to send it. No attorney-client relationship implied."

**Q: Could this give legal advice incorrectly?**
"Yes, and we'd surface that as a disclaimer. Risk labels are heuristic — a real dispute needs a lawyer. Our value is surfacing what's worth questioning, not replacing counsel."

**Q: What about privacy — does the contract go to external servers?**
"Yes, Claude API calls send the contract. On-device-only inference is future work. For the hackathon demo we note this in the README."

---

## Technical numbers to memorize

| Thing | Number |
|---|---|
| Base model | InLegalBERT (law-ai/InLegalBERT) |
| Pretrained on | 5.4M Indian legal documents, 27 GB |
| Our dataset | 6,400 Indian synth + 2,473 LEDGAR capped |
| Classes | 10 type + 3 risk |
| LoRA rank | 8 |
| Trainable % | 0.28% |
| Learning rate — head / body | 1e-3 / 1e-5 |
| Macro F1 — type head (10-class) | 0.910 |
| Macro F1 — risk head (3-class) | 0.797 |
| Test set size — type / risk | 2,316 / 640 |
| Parallel Claude concurrency | 20 |
| End-to-end latency (demo) | ~20 s |
| Demo money-shot latency (risk flags) | ~9-10 s |
