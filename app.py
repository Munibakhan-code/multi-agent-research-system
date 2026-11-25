# app.py
import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain
import base64
from datetime import datetime
import json

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

/* ── Reset & base ── */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #e8e8e8;
}

.stApp {
    background: #0b0b12;
    background-image: 
        radial-gradient(ellipse at 10% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(236, 72, 153, 0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(0, 0, 0, 0.3) 0%, transparent 100%);
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { display: none !important; }
.block-container { 
    padding: 1.5rem 2.5rem 3rem !important; 
    max-width: 1400px !important;
}

/* ── Sidebar Styling ── */
.css-1d391kg, .css-1lcbmhc {
    background: rgba(15, 15, 25, 0.95) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
}
.css-1d391kg .stSelectbox, .css-1lcbmhc .stSelectbox {
    background: transparent !important;
}

/* ── Sidebar content ── */
.sidebar-brand {
    text-align: center;
    padding: 1.5rem 0 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    margin-bottom: 1.5rem;
}
.sidebar-brand h2 {
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    font-size: 1.6rem;
    background: linear-gradient(135deg, #818cf8, #a78bfa, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
}
.sidebar-brand p {
    font-size: 0.7rem;
    color: #6b6b7a;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

.sidebar-section {
    margin-bottom: 1.8rem;
}
.sidebar-section-title {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #6b6b7a;
    margin-bottom: 0.8rem;
}

.sidebar-stat {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    font-size: 0.85rem;
}
.sidebar-stat-label {
    color: #9a9aab;
}
.sidebar-stat-value {
    color: #e8e8e8;
    font-weight: 600;
}

.status-badge {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.status-badge.idle {
    background: rgba(107, 107, 122, 0.2);
    color: #6b6b7a;
}
.status-badge.running {
    background: rgba(129, 140, 248, 0.2);
    color: #818cf8;
    animation: pulse 1.5s ease-in-out infinite;
}
.status-badge.done {
    background: rgba(52, 211, 153, 0.2);
    color: #34d399;
}

@keyframes pulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}

/* ── Hero section ── */
.hero-section {
    padding: 1rem 0 2rem;
    position: relative;
}
.hero-section .badge {
    display: inline-block;
    background: rgba(129, 140, 248, 0.12);
    border: 1px solid rgba(129, 140, 248, 0.15);
    border-radius: 20px;
    padding: 0.3rem 1.2rem;
    font-size: 0.7rem;
    font-weight: 500;
    color: #818cf8;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero-section h1 {
    font-family: 'Inter', sans-serif;
    font-size: clamp(2.5rem, 4.5vw, 4rem);
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: -0.03em;
    color: #f0f0f0;
}
.hero-section h1 .highlight {
    background: linear-gradient(135deg, #818cf8, #a78bfa, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-section .subtitle {
    font-size: 1.05rem;
    color: #9a9aab;
    max-width: 600px;
    margin-top: 0.8rem;
    line-height: 1.6;
    font-weight: 300;
}

/* ── Input area ── */
.input-container {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin: 1.5rem 0;
    backdrop-filter: blur(12px);
    transition: border-color 0.3s;
}
.input-container:focus-within {
    border-color: rgba(129, 140, 248, 0.3);
}

.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    color: #f0f0f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.9rem 1.2rem !important;
    transition: all 0.3s !important;
}
.stTextInput > div > div > input::placeholder {
    color: #5a5a6a !important;
}
.stTextInput > div > div > input:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 4px rgba(129, 140, 248, 0.1) !important;
    background: rgba(255, 255, 255, 0.07) !important;
}
.stTextInput > label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: #818cf8 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #818cf8 0%, #a78bfa 50%, #ec4899 100%) !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 2.5rem !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 20px rgba(129, 140, 248, 0.25) !important;
    width: 100%;
    letter-spacing: 0.02em;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 35px rgba(129, 140, 248, 0.35) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 4px 15px rgba(129, 140, 248, 0.2) !important;
}
.stButton > button:disabled {
    opacity: 0.5 !important;
    transform: none !important;
}

/* ── Topic chips ── */
.chip-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.8rem;
}
.chip {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 0.35rem 1rem;
    font-size: 0.75rem;
    color: #9a9aab;
    font-family: 'Inter', sans-serif;
    cursor: pointer;
    transition: all 0.2s;
}
.chip:hover {
    background: rgba(129, 140, 248, 0.1);
    border-color: rgba(129, 140, 248, 0.2);
    color: #f0f0f0;
}

/* ── Pipeline steps ── */
.pipeline-container {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.04);
    margin-top: 0.5rem;
}
.pipeline-title {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #6b6b7a;
    margin-bottom: 1.2rem;
}

.step-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem 1rem;
    border-radius: 10px;
    margin-bottom: 0.4rem;
    transition: all 0.3s;
    border: 1px solid transparent;
}
.step-item:hover {
    background: rgba(255, 255, 255, 0.02);
}
.step-item.active {
    background: rgba(129, 140, 248, 0.06);
    border-color: rgba(129, 140, 248, 0.15);
}
.step-item.done {
    background: rgba(52, 211, 153, 0.04);
    border-color: rgba(52, 211, 153, 0.1);
}
.step-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    color: #6b6b7a;
    min-width: 30px;
}
.step-icon {
    font-size: 1.1rem;
    width: 28px;
    text-align: center;
}
.step-name {
    font-size: 0.9rem;
    font-weight: 500;
    color: #e8e8e8;
    flex: 1;
}
.step-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.2rem 0.8rem;
    border-radius: 12px;
}
.step-status.waiting {
    color: #6b6b7a;
    background: rgba(107, 107, 122, 0.1);
}
.step-status.running {
    color: #818cf8;
    background: rgba(129, 140, 248, 0.12);
    animation: pulse 1.5s ease-in-out infinite;
}
.step-status.done {
    color: #34d399;
    background: rgba(52, 211, 153, 0.1);
}

/* ── Results cards ── */
.result-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    margin-top: 1rem;
    transition: all 0.3s;
}
.result-card:hover {
    border-color: rgba(255, 255, 255, 0.08);
}
.result-card-title {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: #e8e8e8;
    margin-bottom: 1rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.result-card-title .icon {
    font-size: 1.2rem;
}
.result-card-content {
    font-size: 0.9rem;
    line-height: 1.8;
    color: #c8c8d4;
    white-space: pre-wrap;
    font-family: 'Inter', sans-serif;
}

/* ── Report panel ── */
.report-panel {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(129, 140, 248, 0.15);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1.5rem;
}
.report-panel .title {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #818cf8;
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(129, 140, 248, 0.1);
}

/* ── Feedback panel ── */
.feedback-panel {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(52, 211, 153, 0.15);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1.5rem;
}
.feedback-panel .title {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #34d399;
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(52, 211, 153, 0.1);
}

/* ── Download button ── */
.download-btn {
    margin-top: 1.5rem;
}
.download-btn .stButton > button {
    background: rgba(255, 255, 255, 0.05) !important;
    color: #e8e8e8 !important;
    box-shadow: none !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    padding: 0.6rem 1.5rem !important;
    font-size: 0.85rem !important;
    width: auto !important;
}
.download-btn .stButton > button:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(255, 255, 255, 0.15) !important;
    transform: translateY(-1px) !important;
}

/* ── Expander styling ── */
.streamlit-expanderHeader {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    color: #9a9aab !important;
    background: rgba(255, 255, 255, 0.02) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.04) !important;
}
.streamlit-expanderHeader:hover {
    background: rgba(255, 255, 255, 0.04) !important;
    color: #e8e8e8 !important;
}

/* ── Spinner ── */
.stSpinner > div {
    color: #818cf8 !important;
}
.stSpinner > div > div {
    border-color: #818cf8 !important;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 2rem 0 0.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    margin-top: 2.5rem;
}
.footer p {
    font-size: 0.7rem;
    color: #4a4a5a;
    letter-spacing: 0.08em;
}
.footer .tech-stack {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-top: 0.5rem;
    flex-wrap: wrap;
}
.footer .tech-stack span {
    font-size: 0.6rem;
    color: #5a5a6a;
    background: rgba(255, 255, 255, 0.04);
    padding: 0.2rem 0.8rem;
    border-radius: 12px;
    letter-spacing: 0.05em;
}

/* ── Responsive ── */
@media (max-width: 768px) {
    .block-container { padding: 1rem 1.2rem !important; }
    .input-container { padding: 1.2rem; }
    .report-panel, .feedback-panel { padding: 1.2rem; }
    .hero-section h1 { font-size: 2rem; }
}
</style>
""", unsafe_allow_html=True)


# ── Session state init ──────────────────────────────────────────────────────
for key in ("results", "running", "done", "start_time"):
    if key not in st.session_state:
        if key == "results":
            st.session_state[key] = {}
        elif key == "start_time":
            st.session_state[key] = None
        else:
            st.session_state[key] = False



# ── Hero Section ────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="badge">⚡ Multi-Agent Research System</div>
    <h1>
        Research<br>
        <span class="highlight">Mind</span>
    </h1>
    <p class="subtitle">
        Four specialized AI agents collaborate in sequence — searching, scraping, 
        writing, and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
""", unsafe_allow_html=True)


# ── Main Layout ─────────────────────────────────────────────────────────────
col_input, col_pipeline = st.columns([2, 1])

with col_input:
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    topic = st.text_input(
        "🔬 Research Topic",
        placeholder="Enter any research topic...",
        key="topic_input",
        label_visibility="visible",
    )
    
    # Example chips
    st.markdown("""
    <div style="font-size:0.65rem;color:#6b6b7a;margin-top:0.3rem;letter-spacing:0.05em;">
        Try these topics:
    </div>
    <div class="chip-container">
    """, unsafe_allow_html=True)
    
    examples = [
        "Quantum Computing 2025",
        "CRISPR Gene Editing",
        "Fusion Energy Progress",
        "LLM Agent Architectures",
        "Climate Tech Innovation"
    ]
    
    cols = st.columns(len(examples))
    for i, ex in enumerate(examples):
        with cols[i]:
            if st.button(ex, key=f"chip_{i}", use_container_width=True):
                st.session_state.topic_input = ex
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Run button
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("⚡ Run Research Pipeline", use_container_width=True, 
                        disabled=st.session_state.running)
    st.markdown('</div>', unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="pipeline-container">', unsafe_allow_html=True)
    st.markdown('<div class="pipeline-title">🤖 Pipeline Status</div>', unsafe_allow_html=True)
    
    r = st.session_state.results
    
    def get_step_status(step):
        if not r:
            return "waiting"
        if step in r:
            return "done"
        if st.session_state.running:
            steps = ["search", "reader", "writer", "critic"]
            for s in steps:
                if s not in r:
                    return "running" if s == step else "waiting"
        return "waiting"
    
    steps = [
        ("search", "🔍", "Search Agent", "Gathers recent information"),
        ("reader", "📄", "Reader Agent", "Scrapes & extracts content"),
        ("writer", "✍️", "Writer Chain", "Drafts research report"),
        ("critic", "🧐", "Critic Chain", "Reviews & scores report"),
    ]
    
    for step_id, icon, name, desc in steps:
        status = get_step_status(step_id)
        cls = "active" if status == "running" else "done" if status == "done" else ""
        status_display = {
            "waiting": "⏸ Waiting",
            "running": "⚡ Running",
            "done": "✅ Done"
        }.get(status, "⏸ Waiting")
        
        status_cls = {
            "waiting": "waiting",
            "running": "running",
            "done": "done"
        }.get(status, "waiting")
        
        st.markdown(f"""
        <div class="step-item {cls}">
            <span class="step-number">0{steps.index((step_id, icon, name, desc)) + 1}</span>
            <span class="step-icon">{icon}</span>
            <span class="step-name">{name}</span>
            <span class="step-status {status_cls}">{status_display}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ── Run pipeline ────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("⚠️ Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.session_state.start_time = time.time()
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input
    
    # Progress placeholder
    progress_placeholder = st.empty()
    
    # ── Step 1: Search ──
    with st.spinner("🔍 Search Agent is gathering information..."):
        progress_placeholder.info("**Step 1/4:** Search Agent analyzing web sources...")
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)
        progress_placeholder.success("✅ Step 1 complete: Search results gathered")
        time.sleep(0.3)  # visual feedback
    
    # ── Step 2: Reader ──
    with st.spinner("📄 Reader Agent is scraping top resources..."):
        progress_placeholder.info("**Step 2/4:** Reader Agent extracting content from sources...")
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)
        progress_placeholder.success("✅ Step 2 complete: Content scraped and extracted")
        time.sleep(0.3)
    
    # ── Step 3: Writer ──
    with st.spinner("✍️ Writer is drafting the report..."):
        progress_placeholder.info("**Step 3/4:** Writer Agent synthesizing research into report...")
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)
        progress_placeholder.success("✅ Step 3 complete: Report drafted")
        time.sleep(0.3)
    
    # ── Step 4: Critic ──
    with st.spinner("🧐 Critic is reviewing the report..."):
        progress_placeholder.info("**Step 4/4:** Critic Agent reviewing and scoring report...")
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)
        progress_placeholder.success("✅ All steps complete! Research pipeline finished.")
        time.sleep(0.5)
    
    st.session_state.running = False
    st.session_state.done = True
    progress_placeholder.empty()
    st.rerun()


# ── Results display ────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown("---")
    st.markdown("## 📊 Research Results")
    
    # Raw outputs in expanders
    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-title">
                    <span class="icon">🔍</span>
                    Search Agent Output
                </div>
                <div class="result-card-content">{r["search"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-title">
                    <span class="icon">📄</span>
                    Reader Agent Output
                </div>
                <div class="result-card-content">{r["reader"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="title">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Download
        col_dl1, col_dl2 = st.columns([1, 3])
        with col_dl1:
            st.download_button(
                label="⬇ Download Markdown",
                data=r["writer"],
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                key="download_report"
            )
        with col_dl2:
            st.download_button(
                label="📄 Download JSON",
                data=json.dumps(r, indent=2),
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_json"
            )
    
    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="title">🧐 Critic Feedback & Analysis</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <p>🧠 ResearchMind · Multi-Agent Research System</p>
    <div class="tech-stack">
        <span>LangChain</span>
        <span>Streamlit</span>
        <span>Python</span>
        <span>AI Agents</span>
    </div>
</div>
""", unsafe_allow_html=True)