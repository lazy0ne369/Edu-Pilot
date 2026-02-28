"""
EduPilot — Refined Website Layout.
Features: Compact Footer, Optimized Navigation and Premium Chat Page.
"""

import uuid
import streamlit as st
import pandas as pd
import numpy as np
from langchain_core.messages import HumanMessage
from agent.config import DATA_PATH
import hashlib
from pathlib import Path

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="EduPilot | Premium Admissions Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session State Initialisation ─────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "filters" not in st.session_state:
    st.session_state.filters = {}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = "Aditya Kumar"
if "saved_colleges" not in st.session_state:
    st.session_state.saved_colleges = ["IIT Bombay", "NIT Trichy", "BITS Pilani"]

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    /* ── Animations ───────────────────────────────────────────── */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes floating {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    /* ── Global Styles & Color Grading ───────────────────────── */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        /* Premium Soft Mesh Gradient / Color Grading Effect */
        background: linear-gradient(-45deg, #fdfbfb, #ebedee, #fdfcfb, #e2d1c3);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #111;
    }

    [data-testid="stHeader"] {
        display: none !important;
    }
    
    .st-emotion-cache-18ni77z { padding-top: 0px !important; }

    /* Fixed Premium Header with Glassmorphism */
    .header-anchor {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 75px;
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(20px) saturate(200%);
        border-bottom: 1px solid rgba(0,0,0,0.05);
        z-index: 999999;
        display: flex;
        align-items: center;
        padding: 0 5%;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.03);
    }

    .main .block-container {
        padding-top: 85px !important;
        padding-bottom: 40px !important;
    }

    /* Navigation button overrides */
    div[data-testid="stColumn"] button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        color: #555 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        padding: 8px 16px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        border-radius: 12px !important;
    }
    div[data-testid="stColumn"] button[kind="secondary"]:hover {
        color: #000 !important;
        background: rgba(0,0,0,0.04) !important;
        transform: translateY(-1px);
    }
    
    div[data-testid="stColumn"] button[kind="primary"] {
        background: linear-gradient(135deg, #111 0%, #333 100%) !important;
        color: #fff !important;
        border-radius: 20px !important;
        padding: 8px 24px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div[data-testid="stColumn"] button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2) !important;
    }

    /* ── Typography & Layout Animations ───────────────────────── */
    .hero-title {
        font-size: 64px;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #111, #444, #111);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        color: #555;
        font-size: 20px;
        margin-bottom: 50px;
        animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) 0.15s forwards;
        opacity: 0;
    }

    /* Home Search Bar */
    .home-search-wrap {
        max-width: 60% !important;
        margin: 0 auto !important;
        animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) 0.3s forwards;
        opacity: 0;
    }
    
    [data-testid="stTextInput"] input {
        height: 60px !important;
        border-radius: 18px !important;
        border: 2px solid transparent !important;
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.06) !important;
        padding-left: 24px !important;
        font-size: 17px !important;
        font-weight: 500 !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #222 !important;
        box-shadow: 0 16px 48px rgba(0,0,0,0.12) !important;
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 1) !important;
    }

    /* Hero Image */
    .hero-image {
        height: 480px;
        width: 100%;
        max-width: 90%;
        margin: 80px auto;
        background-image: url('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1600&q=80');
        background-size: cover;
        background-position: center;
        border-radius: 28px;
        box-shadow: 0 30px 60px rgba(0,0,0,0.15);
        animation: fadeInUp 1.2s cubic-bezier(0.16, 1, 0.3, 1) 0.45s forwards;
        opacity: 0;
        transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .hero-image:hover {
        transform: scale(1.02);
    }

    /* Vision Section */
    .vision-section {
        padding: 60px 0;
        text-align: center;
        max-width: 700px;
        margin: 0 auto;
        animation: fadeInUp 1.2s cubic-bezier(0.16, 1, 0.3, 1) 0.6s forwards;
        opacity: 0;
    }

    /* Footer Redesign */
    .premium-footer {
        background-color: #0f0f0f;
        color: #888;
        padding: 50px 5%;
        border-top: 1px solid #222;
        margin-top: 100px;
        width: 100%;
        font-size: 14px;
        box-shadow: inset 0 20px 40px rgba(0,0,0,0.2);
    }
    .footer-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
    }
    .footer-left {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .footer-right {
        display: flex;
        gap: 30px;
        align-items: center;
    }
    .footer-logo {
        color: #fff;
        font-weight: 800;
        font-size: 20px;
        letter-spacing: -0.01em;
    }
    .footer-tagline {
        color: #777;
        font-size: 13px;
    }
    .footer-links {
        display: flex;
        gap: 24px;
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .footer-links a {
        color: #888;
        text-decoration: none;
        transition: color 0.3s ease;
        font-weight: 500;
    }
    .footer-links a:hover {
        color: #fff;
    }

    @media (max-width: 768px) {
        .footer-content {
            flex-direction: column;
            text-align: center;
            gap: 30px;
        }
        .footer-right {
            flex-direction: column;
            gap: 15px;
        }
        .footer-links {
            justify-content: center;
        }
        .hero-title { font-size: 42px; }
        .hero-image { height: 300px; }
        .home-search-wrap { max-width: 90% !important; }
    }
</style>
""", unsafe_allow_html=True)

# ── Navigation Router ─────────────────────────────────────────
def go_to(page):
    st.session_state.page = page
    st.rerun()

# ── Optimized Header ──────────────────────────────────────────
st.markdown('<div class="header-anchor"></div>', unsafe_allow_html=True)
header_container = st.container()
with header_container:
    h_col_logo, h_col_nav, h_col_auth = st.columns([1.5, 3, 1.5])
    with h_col_logo:
        st.markdown('<div style="padding-top:12px; font-weight:800; font-size:22px; cursor:pointer;" onclick="window.parent.postMessage({type: \'streamlit:setComponentValue\', value: \'home\'}, \'*\')">✦ EduPilot</div>', unsafe_allow_html=True)
        if st.button(" ", key="logo_home_btn", help="Go to Home"): go_to("home")
    with h_col_nav:
        n1, n2, n3 = st.columns(3)
        with n1:
            if st.button("Home", key="l_home"): go_to("home")
        with n2:
            if st.button("Agent", key="l_agent"): go_to("agent")
        with n3:
            if st.button("Dashboard", key="l_dash"): go_to("dashboard")
    with h_col_auth:
        if not st.session_state.logged_in:
            if st.button("Login / Sign Up", key="h_auth", type="primary"):
                st.session_state.logged_in = True
                st.rerun()
        else:
            if st.button("Logout", key="h_logout", type="secondary"):
                st.session_state.logged_in = False
                go_to("home")

# ── Logic ─────────────────────────────────────────────────────
from agent.ingest import ensure_ingested
from agent.graph import GRAPH
from ui.sidebar import render_sidebar
from ui.chat import render_chat, render_stream, render_welcome

@st.cache_resource
def init_db(data_hash: str):
    ensure_ingested()
    return True

def get_data_hash():
    p = Path(DATA_PATH)
    return hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else "none"

# ── Home Page ─────────────────────────────────────────────────
def render_home_page():
    st.markdown('<div style="text-align: center; margin-top: 80px;">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Elevate Your Future.</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Personalised admissions guidance powered by AI.</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="home-search-wrap">', unsafe_allow_html=True)
    search_input = st.text_input("Search colleges...", placeholder="Find colleges by name, city, or courses...", label_visibility="collapsed", key="search_h")
    if search_input:
        st.session_state["_injected_prompt"] = f"Tell me about colleges related to: {search_input}"
        go_to("agent")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="hero-image"></div>', unsafe_allow_html=True)

    st.markdown('<div class="vision-section">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-weight: 800; font-size: 32px; margin-bottom: 20px;">Our Vision</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #444; line-height: 1.7; font-size: 17px;">Helping students make smarter college decisions through transparent, AI-powered insights while keeping data 100% private.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Agent Page ────────────────────────────────────────────────
def render_agent_page():
    filters = render_sidebar()
    st.session_state.filters = filters
    
    if not st.session_state.messages:
        render_welcome(filters=filters)

    if "_injected_prompt" in st.session_state:
        injected = st.session_state.pop("_injected_prompt")
        st.session_state.messages.append({"role": "user", "content": injected})

    render_chat(st.session_state.messages)

    if prompt := st.chat_input("Ask about ranks, fees, or specific colleges..."):
        f = st.session_state.filters
        filter_parts = [f"{k}: {v}" for k, v in f.items() if v and k != "budget_max"]
        if f.get("budget_max"): filter_parts.append(f"Budget: ₹{f['budget_max']:,}")
        enriched_prompt = f"{prompt}\n\n[Profile: {' | '.join(filter_parts)}]" if filter_parts else prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        config = {"configurable": {"thread_id": st.session_state.session_id}}
        input_msg = {"messages": [HumanMessage(content=enriched_prompt)], "filters": f, "context": ""}
        with st.chat_message("assistant", avatar="🎓"):
            response = render_stream(GRAPH, input_msg, config)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# ── Dashboard Page ────────────────────────────────────────────
def render_dashboard_page():
    if not st.session_state.logged_in:
        st.warning("Authorize to access Dashboard.")
        render_home_page()
        return
    st.markdown(f"## Account Summary")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div style="background:#f9f9f9; padding:20px; border-radius:12px; margin-bottom:20px;"><h3>👤 Profile</h3><p>Aditya Kumar<br>aditya@example.com</p></div>', unsafe_allow_html=True)
        st.markdown('### 🔖 Shortlist')
        for clg in st.session_state.saved_colleges:
            r1, r2 = st.columns([4, 1])
            with r1: st.info(clg)
            with r2: 
                if st.button("✕", key=f"d_{clg}"):
                    st.session_state.saved_colleges.remove(clg)
                    st.rerun()

# ── Main ──────────────────────────────────────────────────────
def main():
    init_db(get_data_hash())
    
    if st.session_state.page == "home":
        render_home_page()
    elif st.session_state.page == "agent":
        render_agent_page()
    elif st.session_state.page == "dashboard":
        render_dashboard_page()

    # Redesigned Footer
    st.markdown("""
    <div class="premium-footer">
        <div class="footer-content">
            <div class="footer-left">
                <div class="footer-logo">✦ EduPilot</div>
                <div class="footer-tagline">100% Local AI. 0% Data Shared.</div>
            </div>
            <div class="footer-right">
                <ul class="footer-links">
                    <li><a href="#">Privacy Policy</a></li>
                    <li><a href="#">Terms</a></li>
                    <li><a href="#">Contact</a></li>
                </ul>
                <div style="color: #444;">© 2025 EduPilot</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
