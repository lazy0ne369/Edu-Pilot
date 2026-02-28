"""
EduPilot — Redesigned Sidebar.
Clean, minimal, and professional filter panel.
"""

import streamlit as st

# ── Dropdown options ──────────────────────────────────────────
EXAMS = ["", "JEE Main", "JEE Advanced", "BITSAT", "VITEEE", "KCET", "MHT-CET"]
CATEGORIES = ["", "General", "OBC", "EWS", "SC", "ST"]
QUOTAS = ["All_India", "Home_State", "Management"]
BRANCHES = ["", "CSE", "ECE", "Mech", "Civil", "EE", "AI/ML"]
STATES = ["", "Andhra Pradesh", "Delhi", "Gujarat", "Karnataka", "Maharashtra", "Tamil Nadu"]


def render_sidebar() -> dict:
    """
    Render a professional filter sidebar for students.
    """
    
    # Sidebar CSS for premium feel
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #eee;
        }
        [data-testid="stSidebar"] .stSelectbox label, 
        [data-testid="stSidebar"] .stSlider label {
            color: #666 !important;
            font-size: 14px !important;
            font-weight: 600 !important;
        }
        .sidebar-title {
            font-size: 18px;
            font-weight: 800;
            color: #0a0a0a;
            margin-bottom: 25px;
            margin-top: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="sidebar-title">Filters</div>', unsafe_allow_html=True)
        
        exam = st.selectbox("Entrance Exam", EXAMS)
        category = st.selectbox("Category", CATEGORIES)
        quota = st.selectbox("Quota", QUOTAS, index=0)
        
        st.divider()
        
        state = st.selectbox("Target State", STATES)
        branch = st.selectbox("Preferred Branch", BRANCHES)
        
        budget_max = st.slider(
            "Max Annual Fee (₹)",
            min_value=50_000,
            max_value=2_000_000,
            value=500_000,
            step=50_000,
            format="₹%d"
        )
        
        st.divider()
        st.caption("✦ EduPilot Agent Context")
        st.caption("Filters help the AI provide more relevant admissions advice.")

    return {
        "exam":       exam or None,
        "category":   category or None,
        "quota":      quota,
        "state":      state or None,
        "branch":     branch or None,
        "budget_max": budget_max,
    }
