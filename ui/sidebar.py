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
        st.markdown('<div class="sidebar-header" style="margin-top:30px;">ℹ️ About</div>', unsafe_allow_html=True)
        st.caption(
            "EduPilot uses Google Gemini for chat and HuggingFace for lightning-fast local RAG retrieval."
        )

        st.markdown("**Models used:**")
        st.code("LLM:    gemini-1.5-flash\nEmbed:  all-MiniLM-L6-v2", language="text")

        st.markdown("**Quick start:**")
        with st.expander("Example questions"):
            st.markdown(
                "- Show CSE colleges under ₹2L in Tamil Nadu\n"
                "- Can I get NIT Trichy with JEE rank 45000 OBC?\n"
                "- When does VIT application close?\n"
                "- Best BITS campus for CS?\n"
                "- IIT cutoffs for SC category 2024"
            )

    return {
        "exam":       exam or None,
        "category":   category or None,
        "quota":      quota,
        "state":      state or None,
        "branch":     branch or None,
        "budget_max": budget_max,
    }
