# AI-Powered Legal Document Simplifier

> Turn complex Indian legal documents into plain English, with risk flags, law references, and negotiation scripts.

**Status:** Work in progress — built during Hack O'Clock (18-hour hackathon, 2026-04-23).

---

## Problem

Legal documents like rental agreements, employment contracts, and terms-of-service are written in language ordinary people cannot understand. In India, millions sign these documents daily without knowing what rights they are waiving or what predatory clauses they are accepting.

## Solution

A multi-layer AI pipeline that:

1. **Segments** uploaded PDFs into individual clauses.
2. **Scores** each clause against a reference corpus of standard Indian contracts using semantic similarity.
3. **Explains** every flagged clause in plain language via an LLM — grounded in Indian law (Contract Act 1872, Labour Law, Rent Control Act, Consumer Protection Act 2019).
4. **Generates** negotiation scripts with exact counter-proposal language users can send back.

## Key Features

- PDF upload and automatic clause extraction
- Risk rating per clause — **Low / Medium / High** — backed by similarity scoring
- Plain-language rewrite of every flagged clause
- Indian law references cited per clause
- Negotiation script generator with exact counter-proposal wording
- Q&A chat interface for follow-up questions on any clause

## Team

2-person team — Hack O'Clock 2026.

## License

[MIT](LICENSE)
