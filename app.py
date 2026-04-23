"""Streamlit UI: 3-column inline risk PDF | clause details | chat.

Run: streamlit run app.py
"""
import streamlit as st

from src import pipeline, rag

st.set_page_config(page_title="LexAI — Indian Legal Document Simplifier", layout="wide")

# ------------------- Session state -------------------
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "selected_clause" not in st.session_state:
    st.session_state.selected_clause = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------- Header / upload -------------------
st.markdown("## LexAI — Indian Legal Document Simplifier")
st.caption("Upload an Indian rental / employment / ToS contract. Risk flags appear inline; click any flagged clause for plain-English + negotiation script.")

with st.container(border=True):
    c1, c2 = st.columns([3, 1])
    with c1:
        uploaded = st.file_uploader("Upload PDF contract", type=["pdf"], key="pdf_upload", label_visibility="collapsed")
    with c2:
        use_text = st.toggle("paste text instead", value=False)

text_input = None
if use_text:
    text_input = st.text_area("Paste the contract text", height=200, key="text_input")

go = st.button("Analyze contract", type="primary", use_container_width=True, disabled=not (uploaded or text_input))

if go:
    st.session_state.selected_clause = None
    st.session_state.chat_history = []
    with st.status("Analyzing contract — this runs LexBERT classification then parallel Claude analysis...", expanded=True) as status:
        try:
            if uploaded:
                st.write("📄 Parsing PDF + extracting word bounding boxes...")
                pdf_bytes = uploaded.getvalue()
                result = pipeline.analyze(pdf_bytes=pdf_bytes)
            else:
                st.write("📝 Parsing pasted text...")
                result = pipeline.analyze(text=text_input)
            if "error" in result:
                status.update(label=f"❌ {result['error']}", state="error")
                st.stop()
            st.write(f"✅ {len(result['clauses'])} clauses · "
                     f"{result['risk_counts']['high']} High / "
                     f"{result['risk_counts']['medium']} Medium / "
                     f"{result['risk_counts']['low']} Low")
            st.session_state.analysis = result
            status.update(label="Done", state="complete")
        except Exception as e:
            status.update(label=f"❌ {e}", state="error")
            raise

# ------------------- Summary banner -------------------
A = st.session_state.analysis
if A is not None:
    summary = A["summary"]
    risk_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(summary.risk_posture, "⚪")
    with st.container(border=True):
        st.markdown(f"### {risk_color} {summary.doc_type}")
        st.markdown(f"**{summary.summary_line}**")
        if summary.top_concerns:
            for tc in summary.top_concerns:
                st.markdown(f"- {tc}")
        k1, k2, k3 = st.columns(3)
        k1.metric("High risk", A["risk_counts"]["high"])
        k2.metric("Medium risk", A["risk_counts"]["medium"])
        k3.metric("Low / standard", A["risk_counts"]["low"])

    # ------------------- 3-column layout -------------------
    col_pdf, col_detail, col_chat = st.columns([5, 3, 2])

    with col_pdf:
        st.markdown("#### 📄 Document with risk highlights")
        if A["source"] == "pdf" and A["page_images"]:
            for i, img in enumerate(A["page_images"]):
                st.image(img, caption=f"Page {i + 1}", use_container_width=True)
        else:
            st.caption("(text input — no PDF view; use the clause list on the right to inspect)")
        st.divider()
        st.markdown("##### Clauses (click to inspect)")
        for c in A["clauses"]:
            badge = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(c["final_risk"], "⚪")
            jflag = " ⚠️" if c.get("jurisdiction_flag") else ""
            label = f"{badge} [{c['clause_id']}] {c['clause_type']}{jflag} — {c['text'][:90]}..."
            if st.button(label, key=f"clause_{c['clause_id']}", use_container_width=True):
                st.session_state.selected_clause = c["clause_id"]

    with col_detail:
        st.markdown("#### 🔎 Clause details")
        sel_id = st.session_state.selected_clause
        sel = next((c for c in A["clauses"] if c["clause_id"] == sel_id), None)
        if sel is None:
            st.info("Click a clause on the left to see its plain-English rewrite, law reference, and negotiation script.")
        else:
            badge = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(sel["final_risk"], "⚪")
            st.markdown(f"#### {badge} Clause {sel['clause_id']} · {sel['clause_type']}")
            st.caption(f"Risk: **{sel['final_risk']}** · ML risk: {sel['risk_level_ml']} ({sel['risk_confidence']:.0%}) · "
                       f"Type confidence: {sel['type_confidence']:.0%}"
                       + (f" · Percentile: more unusual than {sel['percentile']}% of standard" if sel.get("percentile") is not None else ""))
            if sel.get("jurisdiction_flag"):
                st.warning(f"⚠️ Jurisdiction: {sel['jurisdiction_flag']}")
            st.markdown("**Original clause**")
            st.markdown(f"> {sel['text']}")
            st.markdown("**Plain English**")
            st.success(sel.get("plain_english", "(unavailable)"))
            st.markdown("**Indian law**")
            st.info(f"**{sel['statute']}** — {sel['section']}\n\n_{sel['flag']}_")
            st.markdown("**Negotiation script** (copy + send)")
            st.code(sel.get("negotiation_script", "(unavailable)"), language="text")

    with col_chat:
        st.markdown("#### 💬 Ask a question")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        q = st.chat_input("e.g. Can I legally refuse clause 4?")
        if q:
            st.session_state.chat_history.append({"role": "user", "content": q})
            with st.chat_message("user"):
                st.markdown(q)
            with st.chat_message("assistant"):
                with st.spinner("Retrieving relevant clauses..."):
                    res = rag.answer(q, A["clauses"], st.session_state.chat_history[:-1])
                answer_text = res["answer"]
                cited = ", ".join(f"{r.clause_id}" for r in res["retrieved"])
                if cited:
                    answer_text += f"\n\n*(grounded in clauses: {cited})*"
                st.markdown(answer_text)
            st.session_state.chat_history.append({"role": "assistant", "content": answer_text})
else:
    st.info("Upload a PDF or paste text above to begin.")
