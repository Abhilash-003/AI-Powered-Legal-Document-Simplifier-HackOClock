"""Streamlit UI: 3-column inline risk PDF | clause details | chat.

Run: streamlit run app.py
"""
import html as _html

import streamlit as st

from src import pipeline, rag

st.set_page_config(
    page_title="LexAI — Indian Legal Document Simplifier",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------- Design tokens + global CSS -------------------
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
      :root {
        --paper:      #fbf9f4;
        --paper-2:    #f4f0e6;
        --ink:        #171412;
        --ink-2:      #3b3530;
        --ink-3:      #756b62;
        --rule:       #e8e2d5;
        --rule-2:     #d9d1bf;
        --crimson:    #b91c1c;
        --crimson-2:  #991b1b;
        --ochre:      #b45309;
        --forest:     #15803d;
        --serif:      'Instrument Serif', 'Iowan Old Style', Georgia, serif;
        --sans:       'Inter Tight', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --mono:       'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
      }

      /* App chrome */
      html, body { background: var(--paper) !important; color: var(--ink); }
      .stApp { background: var(--paper) !important; font-family: var(--sans); color: var(--ink); }

      /* Preserve Material icon fonts (button close ×, status chevron, etc.) */
      .material-icons,
      .material-icons-outlined,
      .material-symbols-outlined,
      [class*="MaterialSymbol"],
      [class*="material-icons"],
      [class*="material-symbols"],
      span[data-baseweb="icon"],
      [data-testid*="stIcon"] {
        font-family: 'Material Symbols Outlined', 'Material Icons Outlined',
                     'Material Icons' !important;
      }
      [data-testid="stHeader"],
      [data-testid="stAppHeader"],
      header[data-testid="stHeader"] {
        background: var(--paper) !important;
        border-bottom: 1px solid var(--rule) !important;
        height: 0 !important;
        min-height: 0 !important;
        visibility: hidden;
      }
      [data-testid="stToolbar"] { display: none !important; }
      [data-testid="stDecoration"] { display: none !important; }
      footer { display: none !important; }
      .block-container { padding-top: 1.4rem !important; max-width: 1400px; }

      /* Headings — serif everywhere */
      h1, h2, h3, h4, h5, h6,
      .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5 {
        font-family: var(--serif) !important;
        font-weight: 400 !important;
        letter-spacing: -0.005em;
        color: var(--ink);
      }
      .stMarkdown h4 { font-size: 22px !important; margin: 4px 0 10px 0 !important; }
      .stMarkdown h5 { font-size: 17px !important; margin: 4px 0 8px 0 !important; color: var(--ink-2); }

      /* Hero wordmark */
      .hero {
        padding: 8px 0 18px 0;
        border-bottom: 1px solid var(--rule);
        margin-bottom: 20px;
      }
      .wordmark {
        font-family: var(--serif);
        font-size: 64px;
        line-height: 1.0;
        letter-spacing: -0.03em;
        color: var(--ink);
        font-weight: 400;
      }
      .wordmark em {
        font-style: italic;
        color: var(--crimson);
      }
      .hero-sub {
        font-family: var(--serif);
        font-style: italic;
        font-size: 22px;
        color: var(--ink-3);
        margin-top: 6px;
        letter-spacing: -0.005em;
      }
      .hero-lede {
        font-family: var(--sans);
        font-size: 15px;
        line-height: 1.55;
        color: var(--ink-2);
        max-width: 760px;
        margin-top: 14px;
      }
      .hero-lede b { color: var(--ink); font-weight: 600; }

      /* Capability chips */
      .caps { display: flex; gap: 10px; margin-top: 18px; flex-wrap: wrap; }
      .cap {
        font-family: var(--sans); font-size: 12.5px; font-weight: 500;
        padding: 7px 12px; border: 1px solid var(--rule-2); border-radius: 999px;
        background: var(--paper-2); color: var(--ink-2); letter-spacing: 0.01em;
      }
      .cap b { color: var(--crimson); font-weight: 600; }

      /* Intake card (pre-upload) */
      div[data-testid="stFileUploader"] {
        background: var(--paper-2);
        border: 1px dashed var(--rule-2);
        border-radius: 6px;
        padding: 10px;
      }
      div[data-testid="stFileUploader"] section { background: transparent; border: none; }
      div[data-testid="stFileUploaderDropzone"] {
        background: transparent; border: none;
      }
      div[data-testid="stFileUploader"] small, div[data-testid="stFileUploader"] span { color: var(--ink-3); }

      /* Containers with borders — warm rule */
      div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--rule) !important;
        background: var(--paper) !important;
        border-radius: 6px !important;
      }

      /* Primary button — ink-black, hover crimson. Force text color on all
         children because Streamlit nests <p>/<div> inside <button>. */
      .stButton > button[kind="primary"],
      .stButton > button[kind="primary"] * {
        color: var(--paper) !important;
      }
      .stButton > button[kind="primary"] {
        background: var(--ink) !important;
        border: 1px solid var(--ink) !important;
        font-family: var(--sans) !important;
        font-weight: 500 !important;
        letter-spacing: 0.01em;
        border-radius: 4px !important;
        padding: 10px 18px !important;
        box-shadow: none !important;
      }
      .stButton > button[kind="primary"]:hover:not(:disabled) {
        background: var(--crimson) !important; border-color: var(--crimson) !important;
      }
      .stButton > button[kind="primary"]:disabled,
      .stButton > button[kind="primary"]:disabled * {
        background: var(--paper-2) !important; color: var(--ink-3) !important;
        border-color: var(--rule-2) !important; opacity: 1 !important;
      }

      /* Secondary buttons — clause list */
      .stButton > button:not([kind="primary"]) {
        background: var(--paper) !important;
        border: 1px solid var(--rule) !important;
        color: var(--ink) !important;
        font-family: var(--sans) !important;
        font-weight: 400 !important;
        text-align: left !important;
        padding: 10px 12px !important;
        border-radius: 4px !important;
        white-space: pre-wrap !important;
        line-height: 1.35 !important;
        box-shadow: none !important;
        transition: border-color 120ms ease, background 120ms ease;
      }
      .stButton > button:not([kind="primary"]):hover {
        border-color: var(--ink-3) !important;
        background: var(--paper-2) !important;
      }

      /* Metric cards — editorial numbers (kept for any fallback st.metric usage) */
      div[data-testid="stMetric"] {
        background: var(--paper-2);
        border: 1px solid var(--rule);
        border-radius: 6px;
        padding: 12px 14px;
      }
      div[data-testid="stMetricValue"] {
        font-family: var(--serif) !important;
        font-size: 2.2rem !important;
        color: var(--ink) !important;
        line-height: 1.0;
      }
      div[data-testid="stMetricLabel"] {
        font-family: var(--sans) !important;
        font-size: 11.5px !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--ink-3) !important;
      }

      /* Risk metric grid — custom, colour-coded */
      .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 14px;
      }
      .metric-card {
        background: var(--paper-2);
        border: 1px solid var(--rule);
        border-left: 4px solid var(--ink-3);
        border-radius: 6px;
        padding: 14px 16px 12px 16px;
        position: relative;
      }
      .metric-card .metric-label {
        font-family: var(--sans);
        font-size: 11px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--ink-3);
        margin-bottom: 6px;
      }
      .metric-card .metric-value {
        font-family: var(--serif);
        font-size: 2.4rem;
        line-height: 1.0;
        color: var(--ink);
      }
      .metric-card .metric-pct {
        font-family: var(--sans);
        font-size: 12px;
        color: var(--ink-3);
        margin-top: 6px;
      }
      .metric-card .metric-pct b {
        font-weight: 600;
        color: var(--ink-2);
      }
      .metric-high       { border-left-color: var(--crimson); background: #fbecec; }
      .metric-high .metric-value { color: var(--crimson); }
      .metric-high .metric-label { color: var(--crimson-2); }
      .metric-med        { border-left-color: var(--ochre);   background: #fdf3e3; }
      .metric-med  .metric-value { color: var(--ochre); }
      .metric-med  .metric-label { color: var(--ochre); }
      .metric-low        { border-left-color: var(--forest);  background: #e9f7ef; }
      .metric-low  .metric-value { color: var(--forest); }
      .metric-low  .metric-label { color: var(--forest); }
      .metric-total      { border-left-color: var(--ink);     background: var(--paper-2); }
      .metric-total .metric-value { color: var(--ink); }

      /* Risk pip (inline dot) */
      .pip { display: inline-block; width: 9px; height: 9px; border-radius: 50%;
             vertical-align: middle; margin-right: 8px; }
      .pip-high { background: var(--crimson); }
      .pip-med  { background: var(--ochre); }
      .pip-low  { background: var(--forest); }
      .pip-muted{ background: var(--ink-3); }

      .risk-label { font-family: var(--sans); font-weight: 600; font-size: 12px;
                    text-transform: uppercase; letter-spacing: 0.08em; }
      .risk-high  { color: var(--crimson); }
      .risk-med   { color: var(--ochre); }
      .risk-low   { color: var(--forest); }

      /* Clause detail boxes */
      .clause-original {
        background: var(--paper-2) !important;
        padding: 14px 16px;
        border-left: 3px solid var(--ink-3);
        border-radius: 3px;
        font-family: var(--serif);
        font-size: 15px;
        line-height: 1.55;
        color: var(--ink) !important;
      }
      .clause-plain {
        background: #f2faf5 !important;
        padding: 14px 16px;
        border-left: 3px solid var(--forest);
        border-radius: 3px;
        font-family: var(--sans);
        font-size: 14px;
        line-height: 1.55;
        color: #0f3b24 !important;
      }
      .statute-box {
        background: #faf6ec !important;
        padding: 12px 14px;
        border-left: 3px solid var(--crimson);
        border-radius: 3px;
        font-family: var(--serif);
        font-size: 15px;
        line-height: 1.5;
        color: #3a1a14 !important;
      }
      .statute-box b { color: var(--crimson-2) !important; font-weight: 500; }
      .statute-box i { color: var(--ink-2) !important; }
      .negotiation-box {
        background: #fff8e6 !important;
        color: #3a2a08 !important;
        padding: 14px 16px;
        border-left: 3px solid var(--ochre);
        border-radius: 3px;
        font-family: var(--mono);
        font-size: 13px;
        line-height: 1.65;
        white-space: pre-wrap;
        word-break: break-word;
      }

      /* Empty-state card (no analysis yet) */
      .empty-card {
        border: 1px solid var(--rule);
        background: var(--paper);
        border-radius: 6px;
        padding: 22px 26px;
        margin-top: 8px;
      }
      .empty-card h3 {
        font-family: var(--serif); font-weight: 400; font-size: 24px;
        margin: 0 0 6px 0; color: var(--ink);
      }
      .empty-card p { font-size: 14px; color: var(--ink-2); line-height: 1.55; margin: 0 0 10px 0; }
      .empty-card .hint {
        font-family: var(--mono); font-size: 12px; color: var(--ink-3);
        background: var(--paper-2); padding: 6px 10px; border-radius: 3px;
        border: 1px solid var(--rule); display: inline-block;
      }

      /* Section rule */
      hr, .stDivider > div { border-color: var(--rule) !important; background: var(--rule) !important; }

      /* Chat */
      div[data-testid="stChatMessage"] { background: var(--paper-2); border: 1px solid var(--rule); border-radius: 6px; }
      div[data-testid="stChatMessageContent"] { font-size: 14px; font-family: var(--sans); }
      div[data-testid="stChatInput"] textarea { font-family: var(--sans) !important; }

      /* Posture row (summary banner) */
      .posture-row {
        display: flex; align-items: baseline; gap: 14px;
        font-family: var(--serif);
      }
      .posture-badge {
        font-family: var(--sans); font-size: 11.5px; font-weight: 600;
        letter-spacing: 0.1em; text-transform: uppercase;
        padding: 4px 10px; border-radius: 3px;
        border: 1px solid currentColor;
      }
      .posture-high  { color: var(--crimson); background: #fbecec; }
      .posture-med   { color: var(--ochre);   background: #fdf3e3; }
      .posture-low   { color: var(--forest);  background: #e9f7ef; }

      /* Caption tightening */
      .stCaption, div[data-testid="stCaption"] {
        font-family: var(--sans); color: var(--ink-3) !important; font-size: 12.5px;
      }

      /* File uploader — "Browse files" is the primary action,
         the × remove-file button must keep a visible icon. */
      div[data-testid="stFileUploader"] button {
        font-family: var(--sans) !important;
        border-radius: 3px !important;
      }
      /* Browse files (black pill) */
      div[data-testid="stFileUploaderDropzone"] button,
      div[data-testid="stFileUploaderDropzone"] button * {
        background: var(--ink) !important;
        color: var(--paper) !important;
        border: none !important;
      }
      /* Remove-file × — transparent icon button, ink glyph */
      div[data-testid="stFileUploaderDeleteBtn"] button,
      div[data-testid="stFileUploaderFile"] button {
        background: transparent !important;
        border: none !important;
        color: var(--ink-2) !important;
      }
      div[data-testid="stFileUploaderDeleteBtn"] button *,
      div[data-testid="stFileUploaderFile"] button * {
        color: var(--ink-2) !important;
      }
      div[data-testid="stFileUploaderDeleteBtn"] svg,
      div[data-testid="stFileUploaderFile"] svg {
        fill: var(--ink-2) !important;
      }
</style>""", unsafe_allow_html=True)

# ------------------- Session state -------------------
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "selected_clause" not in st.session_state:
    st.session_state.selected_clause = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------- Hero -------------------
st.markdown(
    """
    <div class="hero">
      <div class="wordmark">Lex<em>AI</em></div>
      <div class="hero-sub">An Indian legal document, read back to you.</div>
      <div class="caps">
        <div class="cap"><b>Flags</b> illegal + aggressive clauses</div>
        <div class="cap"><b>Cites</b> Indian statutes &amp; sections</div>
        <div class="cap"><b>Drafts</b> negotiation language</div>
        <div class="cap"><b>Answers</b> follow-up questions</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------- Upload / paste -------------------
with st.container(border=True):
    c1, c2 = st.columns([3, 1])
    with c1:
        uploaded = st.file_uploader(
            "Upload PDF contract",
            type=["pdf"],
            key="pdf_upload",
            label_visibility="collapsed",
            help="Indian rental agreement, employment contract, or terms-of-service PDF",
        )
    with c2:
        use_text = st.toggle("paste text instead", value=False)

    text_input = None
    if use_text:
        text_input = st.text_area(
            "Paste the contract text",
            height=200,
            key="text_input",
            placeholder="Paste contract clauses here. Each clause on its own line or numbered.",
            label_visibility="collapsed",
        )

    go = st.button(
        "Analyze contract",
        type="primary",
        use_container_width=True,
        disabled=not (uploaded or text_input),
    )

if go:
    st.session_state.selected_clause = None
    st.session_state.chat_history = []
    with st.status(
        "Analyzing — local LexBERT classification + parallel Claude analysis…",
        expanded=True,
    ) as status:
        try:
            if uploaded:
                st.write("Parsing PDF + extracting word bounding boxes…")
                pdf_bytes = uploaded.getvalue()
                result = pipeline.analyze(pdf_bytes=pdf_bytes)
            else:
                st.write("Parsing pasted text…")
                result = pipeline.analyze(text=text_input)
            if "error" in result:
                status.update(label=result["error"], state="error")
                st.stop()
            st.write(
                f"{len(result['clauses'])} clauses · "
                f"{result['risk_counts']['high']} high · "
                f"{result['risk_counts']['medium']} medium · "
                f"{result['risk_counts']['low']} low"
            )
            st.session_state.analysis = result
            status.update(label="Done", state="complete")
        except Exception as e:
            status.update(label=str(e), state="error")
            raise

# ------------------- Render results -------------------
A = st.session_state.analysis
if A is None:
    st.markdown(
        """
        <div class="empty-card">
          <h3>No document loaded yet.</h3>
          <p>Drop a PDF above, or toggle <b>paste text</b> if you already have clauses on your clipboard.
          Analysis runs in about 30–40 seconds and surfaces every risky clause inline.</p>
          <p>Want to try it empty-handed? Copy the 8-clause demo from
          <span class="hint">docs/DEMO_CONTRACT.md</span> — it exercises every feature end-to-end.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

summary = A["summary"]

# ---- Summary banner ----
posture_css = {"high": "posture-high", "medium": "posture-med", "low": "posture-low"}.get(
    summary.risk_posture, "posture-med"
)
posture_label = {"high": "High risk", "medium": "Medium risk", "low": "Low risk"}.get(
    summary.risk_posture, "Unassessed"
)
with st.container(border=True):
    st.markdown(
        f"""
        <div class="posture-row">
          <span class="posture-badge {posture_css}">{posture_label}</span>
          <span style="font-size:26px; line-height:1.2;">{_html.escape(summary.doc_type)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if summary.summary_line:
        st.markdown(
            f"<div style='margin-top:8px; font-family:var(--serif); font-size:18px; "
            f"font-style:italic; color:var(--ink-2);'>{_html.escape(summary.summary_line)}</div>",
            unsafe_allow_html=True,
        )
    if summary.top_concerns:
        st.markdown(
            "<div style='margin-top:12px; font-family:var(--sans); font-size:11.5px; "
            "letter-spacing:0.08em; text-transform:uppercase; color:var(--ink-3);'>Top concerns</div>",
            unsafe_allow_html=True,
        )
        concerns_html = "<ul style='margin:4px 0 0 18px; font-family:var(--sans); font-size:14px; color:var(--ink); line-height:1.55;'>"
        for tc in summary.top_concerns:
            concerns_html += f"<li>{_html.escape(tc)}</li>"
        concerns_html += "</ul>"
        st.markdown(concerns_html, unsafe_allow_html=True)
    _total = len(A["clauses"]) or 1
    _h = A["risk_counts"]["high"]
    _m = A["risk_counts"]["medium"]
    _l = A["risk_counts"]["low"]
    _pct = lambda n: f"{round(n / _total * 100)}%"
    st.markdown(
        f"""
        <div class="metric-grid">
          <div class="metric-card metric-high">
            <div class="metric-label">High risk</div>
            <div class="metric-value">{_h}</div>
            <div class="metric-pct"><b>{_pct(_h)}</b> of clauses</div>
          </div>
          <div class="metric-card metric-med">
            <div class="metric-label">Medium risk</div>
            <div class="metric-value">{_m}</div>
            <div class="metric-pct"><b>{_pct(_m)}</b> of clauses</div>
          </div>
          <div class="metric-card metric-low">
            <div class="metric-label">Low / standard</div>
            <div class="metric-value">{_l}</div>
            <div class="metric-pct"><b>{_pct(_l)}</b> of clauses</div>
          </div>
          <div class="metric-card metric-total">
            <div class="metric-label">Total clauses</div>
            <div class="metric-value">{len(A["clauses"])}</div>
            <div class="metric-pct">all analysed</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---- 3-column layout ----
col_pdf, col_detail, col_chat = st.columns([5, 4, 3], gap="medium")

with col_pdf:
    st.markdown("#### Document")
    st.caption("Risk-coloured overlay on the original PDF." if A["source"] == "pdf"
               else "Text input — no PDF view. Pick a clause below.")
    if A["source"] == "pdf" and A["page_images"]:
        for i, img in enumerate(A["page_images"]):
            st.image(img, caption=f"Page {i + 1}", use_container_width=True)
    st.divider()
    st.markdown("##### Clauses")
    st.caption("Click any clause to inspect.")

    # Emit per-clause colour rules — Streamlit 1.36+ adds a `st-key-<key>`
    # class to the wrapper div for every keyed widget, which lets us paint
    # risk-coloured borders + tints per clause without touching the button text.
    # Saturation deliberately pushed up so red/yellow/green read at a glance.
    _risk_color = {
        "High":   ("#b91c1c", "#fde0e0", "#7a1313"),   # border, bg, text
        "Medium": ("#b45309", "#fbe6c1", "#6b3206"),
        "Low":    ("#15803d", "#d9f0e1", "#0d4e26"),
    }
    _rules = []
    for c in A["clauses"]:
        border, tint, text = _risk_color.get(
            c["final_risk"], ("#d9d1bf", "#f4f0e6", "#171412")
        )
        _rules.append(
            f".st-key-clause_{c['clause_id']} button, "
            f"div[data-testid='stButton']:has(button[aria-label]) "
            f".st-key-clause_{c['clause_id']} button {{ "
            f"border-left: 6px solid {border} !important; "
            f"background: {tint} !important; "
            f"color: {text} !important; }}"
        )
        _rules.append(
            f".st-key-clause_{c['clause_id']} button * {{ "
            f"color: {text} !important; }}"
        )
        _rules.append(
            f".st-key-clause_{c['clause_id']} button:hover {{ "
            f"border-color: {border} !important; "
            f"filter: brightness(0.96); }}"
        )
    st.markdown("<style>" + "\n".join(_rules) + "</style>", unsafe_allow_html=True)

    for c in A["clauses"]:
        fr = c["final_risk"]
        jflag = "  ⚑" if c.get("jurisdiction_flag") else ""
        preview = c["text"][:110].replace("\n", " ").strip()
        label = (
            f"[{c['clause_id']:02d}]  {c['clause_type'].replace('_', ' ')}"
            f"  ·  {fr}{jflag}\n{preview}…"
        )
        if st.button(
            label,
            key=f"clause_{c['clause_id']}",
            use_container_width=True,
        ):
            st.session_state.selected_clause = c["clause_id"]

with col_detail:
    st.markdown("#### Clause details")
    sel_id = st.session_state.selected_clause
    sel = next((c for c in A["clauses"] if c["clause_id"] == sel_id), None)
    if sel is None:
        st.markdown(
            """
            <div class="empty-card" style="margin-top:0;">
              <p style="margin:0; font-family:var(--serif); font-style:italic; font-size:17px; color:var(--ink-2);">
                Pick a clause on the left.
              </p>
              <p style="margin-top:10px;">Each clause opens with:</p>
              <ul style="margin:4px 0 0 18px; font-size:14px; color:var(--ink-2); line-height:1.55;">
                <li>Original legalese vs. plain-English rewrite, side-by-side</li>
                <li>Indian statute and section reference</li>
                <li>Negotiation language you can copy and send</li>
                <li>Jurisdiction warning if foreign law is invoked</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        fr = sel["final_risk"]
        pip_cls = {"High": "pip-high", "Medium": "pip-med", "Low": "pip-low"}.get(fr, "pip-muted")
        risk_cls = {"High": "risk-high", "Medium": "risk-med", "Low": "risk-low"}.get(fr, "")
        st.markdown(
            f"""
            <div style="display:flex; align-items:baseline; gap:10px; margin:2px 0 8px 0;">
              <span class="pip {pip_cls}" style="width:11px; height:11px;"></span>
              <span style="font-family:var(--serif); font-size:24px; line-height:1.1;">
                Clause {sel['clause_id']:02d}
                <span style="color:var(--ink-3); font-style:italic;">·</span>
                {_html.escape(sel['clause_type'].replace('_', ' '))}
              </span>
              <span class="risk-label {risk_cls}" style="margin-left:auto;">{fr}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        meta_parts = [
            f"ML risk {sel['risk_level_ml']} ({sel['risk_confidence']:.0%})",
            f"type confidence {sel['type_confidence']:.0%}",
        ]
        if sel.get("percentile") is not None:
            meta_parts.append(f"more unusual than {sel['percentile']}% of standard clauses")
        st.caption(" · ".join(meta_parts))

        if sel.get("jurisdiction_flag"):
            st.warning(f"Jurisdiction flag — {sel['jurisdiction_flag']}")

        d1, d2 = st.columns(2)
        with d1:
            st.markdown(
                "<div style='font-family:var(--sans); font-size:11.5px; letter-spacing:0.08em; "
                "text-transform:uppercase; color:var(--ink-3); margin:8px 0 4px 0;'>Original</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='clause-original'>{_html.escape(sel['text'])}</div>",
                unsafe_allow_html=True,
            )
        with d2:
            st.markdown(
                "<div style='font-family:var(--sans); font-size:11.5px; letter-spacing:0.08em; "
                "text-transform:uppercase; color:var(--ink-3); margin:8px 0 4px 0;'>Plain English</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='clause-plain'>{_html.escape(sel.get('plain_english','(unavailable)'))}</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='font-family:var(--sans); font-size:11.5px; letter-spacing:0.08em; "
            "text-transform:uppercase; color:var(--ink-3); margin:16px 0 4px 0;'>Indian law</div>",
            unsafe_allow_html=True,
        )
        statute = _html.escape(sel.get("statute", "?"))
        section = _html.escape(sel.get("section", "?"))
        flag = sel.get("flag")
        statute_html = f"<div class='statute-box'><b>{statute}</b> — {section}"
        if flag:
            statute_html += f"<br><i>{_html.escape(flag)}</i>"
        statute_html += "</div>"
        st.markdown(statute_html, unsafe_allow_html=True)

        st.markdown(
            "<div style='font-family:var(--sans); font-size:11.5px; letter-spacing:0.08em; "
            "text-transform:uppercase; color:var(--ink-3); margin:16px 0 4px 0;'>Negotiation script</div>",
            unsafe_allow_html=True,
        )
        neg = sel.get("negotiation_script", "(unavailable)")
        st.markdown(
            f"<div class='negotiation-box'>{_html.escape(neg)}</div>",
            unsafe_allow_html=True,
        )

with col_chat:
    st.markdown("#### Ask about this contract")
    st.caption(
        "Answers are grounded in your clauses plus Indian statute references "
        "retrieved from LexBERT."
    )
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    q = st.chat_input("e.g. Can I legally refuse clause 4?")
    if q:
        st.session_state.chat_history.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            with st.spinner("Retrieving relevant clauses + Indian law refs…"):
                res = rag.answer(q, A["clauses"], st.session_state.chat_history[:-1])
            answer_text = res["answer"]
            cited = ", ".join(str(r.clause_id) for r in res["retrieved"])
            if cited:
                answer_text += f"\n\n*(grounded in clauses: {cited})*"
            st.markdown(answer_text)
        st.session_state.chat_history.append({"role": "assistant", "content": answer_text})
