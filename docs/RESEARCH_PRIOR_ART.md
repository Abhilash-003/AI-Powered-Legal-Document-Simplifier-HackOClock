# LexAI — Prior Art Survey

Survey of comparable projects and products to inform the LexAI pitch. Compiled 2026-04-23. Not a design doc — architecture is locked.

---

## 1. Open-source GitHub projects

| Project | URL | Stars / Activity | Stack | What's different | Learn from |
|---|---|---|---|---|---|
| **TheAtticusProject/cuad** | https://github.com/TheAtticusProject/cuad | NeurIPS 2021 paper repo, canonical | RoBERTa-base/large, DeBERTa on CUAD (510 contracts, 13,101 labels, 41 clause types) | US commercial-contract oriented, QA formulation, no risk head | Clause taxonomy vocabulary; benchmark numbers for our 10-class head |
| **Sreeja2002-Andela/Contract-Clause-Extraction-Analysis-Engine** | https://github.com/Sreeja2002-Andela/Contract-Clause-Extraction-Analysis-Engine | small, recent | CUAD + LLM QA; 41 clauses + risk flag + NL Q&A | Explicitly ships risk flagging and accuracy-vs-expert metric | The "measure accuracy vs expert annotations" framing — strong pitch hook |
| **tomasonjo-labs/legal-tech-chat** | https://github.com/tomasonjo-labs/legal-tech-chat | small, 2024+ | LangChain + LangGraph + Neo4j knowledge graph over CUAD | Builds a KG from contracts and queries via agent | KG-backed Q&A demo pattern; looks sophisticated on a slide |
| **Open-Source-Legal/OpenContracts** | https://github.com/Open-Source-Legal/OpenContracts | active, multi-contributor | Self-hosted annotation + semantic search + MCP | Collaborative human+AI annotation workflow; version control of docs | Document annotation UI idioms (highlight + side-panel rationale) |
| **evolsb/claude-legal-skill** | https://github.com/evolsb/claude-legal-skill | recent | Claude "skill" wrapping CUAD 41 risk cats + market benchmarks + redlines | Targets Claude Code/Cursor dev workflow | Market-benchmark framing ("your clause vs typical terms") |
| **law-ai (group)** | https://github.com/Law-AI | active research org | InLegalBERT, ILDC, judgment-prediction repos | Source of our base model; not contract-focused | Provenance — cite the lab we fine-tuned from |

Gap we confirmed: we found **no open-source Indian-law contract analyzer** combining InLegalBERT + clause-type + risk head on rental/employment/ToS. That is a real gap.

---

## 2. Commercial products

| Product | One-line differentiator | Market | India? |
|---|---|---|---|
| **Harvey.ai** | GPT-based law-firm copilot; research, drafting, Q&A across matter files | Am Law 100, enterprise | No India offering |
| **Spellbook** | MS Word plug-in, real-time clause suggestions + redlining while you type | SMB/commercial law | No |
| **Ironclad** | Enterprise CLM with AI Playbooks enforcing company contract standards | Enterprise in-house legal | Global |
| **Evisort** | AI-native CLM with "Document X-Ray" NL querying across contract portfolios | Mid-large enterprise | Global |
| **Juro** | End-to-end contract lifecycle (draft → sign → store) with embedded AI | In-house legal, SMB-mid | Global |
| **Lexion** (Docusign) | GPT-backed contract assistant, obligation tracking | In-house legal | Global |
| **LinkSquares** | Agentic CLM, portfolio-level risk dashboards, 1000+ customers | Mid-large enterprise | Global |
| **DoNotPay** | Consumer-facing "robot lawyer" — disputes, refunds, cancellations (not contract analysis) | Consumer US | No |
| **goHeather** | Consumer lease/contract review, red-flag + severity ratings | Consumer US/CA | No India |
| **GetPlainDoc** | Plain-language breakdown in <60s, multi-language incl. Hindi | Consumer global | Hindi supported, not India-law grounded |
| **LegalCheckPro** | Employment/NDA/lease/service-contract risk scan | Consumer/SMB | No |
| **SpotDraft** | Indian-founded CLM; $113M raised; in-house legal CLM with AI | Enterprise (India + global) | Yes — but B2B CLM, not consumer |

**Landscape read:** enterprise CLMs dominate (Ironclad/Evisort/Juro/LinkSquares/Lexion). Consumer-facing analyzers exist (goHeather, GetPlainDoc, LegalCheckPro) but are **US/generic**. Nobody combines consumer UX + Indian-statute grounding + clause/risk ML heads.

---

## 3. Indian-specific legal AI

| Name | What it does (India-specific) |
|---|---|
| **CaseMine** | AI legal research over Indian + US/UK judgments; case-law graph; "CaseIQ" argument builder |
| **VakilSearch / Zolvit** | Compliance automation, document drafting templates, IP services — drafting-heavy, not analysis |
| **SpotDraft** | Indian-origin B2B CLM; AI review/extraction; enterprise customers — closest commercial analogue but enterprise-only |
| **Provakil** | Litigation ops for banks/insurers; indexes 19,000+ Indian courts; drafting tied to court records |
| **Legistify** (YC) | YC-backed Indian legaltech; contract + litigation management for enterprises |
| **KanoonGPT** | Consumer chatbot over Indian statutes — Q&A only, no doc upload/clause classification |
| **Nyaaya** (Vidhi Centre) | Plain-language explainers of Indian laws; static content, not AI — good content source |
| **Jhana AI / Vidur AI / NyaySaathi / DraftBotPro** | Drafting + research assistants for Indian lawyers |
| **NYAI** (Bhosale, 2025) | Regulatory intelligence for Indian statutes/compliance workflows |
| **Bharatlaw.ai** | Indian drafting/research focused on advocates |

Indian legaltech funding: **960 companies, 86 funded, $793M cumulative, +781% YoY in 2025** (Inc42/Inventiva). Signal: hot space, crowded on B2B CLM / research / drafting, **thin on consumer-facing contract analysis with statute citations**.

---

## 4. Academic papers with code

| Paper | Contribution | Code |
|---|---|---|
| **Paul, Mandal, Goyal, Ghosh — "Pre-trained LMs for the Legal Domain: A Case Study on Indian Law"** (ICAIL 2023, arXiv:2209.06049) | InLegalBERT + InCaseLawBERT; 5.4M Indian SC/HC docs; 300K MLM steps over LegalBERT-SC | https://github.com/Law-AI + HF `law-ai/InLegalBERT` |
| **Hendrycks et al. — CUAD** (NeurIPS 2021, arXiv:2103.06268) | 510 contracts, 13,101 annotations, 41 clause types; RoBERTa/DeBERTa baselines | https://github.com/TheAtticusProject/cuad |
| **Malik et al. — ILDC + CJPE** (ACL 2021) | Indian Legal Documents Corpus for judgment prediction + explanation | github.com/Exploration-Lab/CJPE |
| **Chalkidis et al. — LexGLUE** (ACL 2022) | 7-task legal-NLP benchmark (EU/US); de-facto evaluation suite | github.com/coastalcph/lex-glue |
| **Joshi et al. — IL-TUR** (arXiv 2407.05399, 2024) | Benchmark for Indian Legal Text Understanding & Reasoning across 8 tasks | Releases referenced in paper |
| **ContractEval** (arXiv 2508.03080, 2025) | Benchmarks LLMs on clause-level legal risk: F1, Jaccard, "no-related-clause" rate | Paper + dataset released |
| **ACORD** (ACL 2025) | Expert-annotated dataset for contract retrieval | aclanthology.org/2025.acl-long.1206 |

We can cite Paul et al. directly as the InLegalBERT source and CUAD as the clause-taxonomy ancestor even though we reduced to 10 classes.

---

## 5. Hackathon / student projects

| Event & Project | What they built |
|---|---|
| **Stanford LLM x Law (Fall 2024) — Comply AI** (Best First Build) | Agentic compliance review over video + comms; region-specific laws; "weeks → hours" framing |
| **Stanford LLM x Law (Fall 2024) — Hammurabi** (Best VC) | Contract-logic reasoner for insurers: "what happens under these terms if X?" scenario engine |
| **Hack_the_Law Cambridge 2025 — Hallucin8** (Founder's prize) | AI auditor that flags fake precedents/citations/flawed logic in legal text |
| **LegalTechTalk 2025 winner** | "Two-way living intelligence layer" — conversational Q&A + plain-English summaries + lawyer escalation |
| **Chat Kanoon** (journal paper, India) | Academic RAG chatbot over Indian statutes — closest academic peer to our RAG layer |

Recurring judge-pleasers: (a) **scenario reasoning** over the contract, (b) a **time-saved** number, (c) **lawyer-escalation** path, (d) **citation grounding** to real law.

---

## 6. Things worth borrowing (ideas already present in prior art)

Concrete patterns we could lean into verbally in the pitch without changing architecture:

1. **"Weeks → hours / hours → minutes" time-saved metric** (Comply AI, every CLM pitch) — a single headline number on slide 1.
2. **Severity-rated red flags** (goHeather, GetPlainDoc, LegalCheckPro) — pair our 3-class risk head with explicit severity chips.
3. **Market-benchmark framing** ("your clause vs typical terms") — evolsb/claude-legal-skill, Spellbook "benchmarking". We can phrase our statute citations this way.
4. **Single headline "deal risk score"** (Harvey, LinkSquares dashboards) — aggregate our clause-level risks into one number at the top of the Streamlit page.
5. **Scenario reasoning** ("what happens if I break the lease in month 3?") — Hammurabi. Falls out of our RAG + Claude stack, just frame it this way in the demo.
6. **Clause highlight + side-panel rationale** (OpenContracts, CUAD demos) — standard annotation UI idiom judges recognize.
7. **Lawyer-escalation CTA** (LegalTechTalk winner, Lexion) — "Flagged: talk to a lawyer" button. Cheap, signals responsibility.
8. **Plain-language + multi-language** (GetPlainDoc supports Hindi) — even a single Hindi toggle in the demo strengthens the "Bharat" story.
9. **Negotiation-script output** (Spellbook redlining, our own feature) — most consumer tools lack this; lean on it as a differentiator.
10. **"Accuracy vs expert annotations" number** (Sreeja2002, CUAD, ContractEval) — report a single F1 on a held-out set during the demo for credibility.

---

## Differentiator crystallization

Combining the survey, LexAI's defensible wedge is the **intersection of four things nobody ships together**:

1. **Indian-statute grounded** (Contract Act §27, TP Act §106, EPF/ESI) — Indian tools are research/drafting/CLM, not consumer clause-risk.
2. **Consumer-facing** (rental / employment / ToS) — Indian consumer analyzer niche is essentially empty.
3. **Local fine-tuned classifier** (InLegalBERT + LoRA, 10-class + 3-class risk) — commercial tools are LLM-only; open-source uses generic LegalBERT/CUAD.
4. **Negotiation scripts, not just flagging** — consumer tools stop at red flags; enterprise tools stop at redlines.

Closest single competitor: **goHeather** (consumer, severity-rated, but US/CA-only, no fine-tuned classifier, no statute citations). Closest Indian competitor: **SpotDraft** (enterprise B2B CLM, not the same market). No direct overlap found.
