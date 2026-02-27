"""
CollegeCompass AI — Streamlit sidebar with filter widgets.
render_sidebar() returns a dict of the student's selected filters.
"""

import streamlit as st

# ── Dropdown options ──────────────────────────────────────────

EXAMS = [
    "", "JEE Main", "JEE Advanced", "BITSAT", "VITEEE",
    "KCET", "MHT-CET", "TNEA", "COMEDK", "SRMJEEE",
    "WBJEE", "AP EAMCET", "TS EAMCET",
]

CATEGORIES = ["", "General", "OBC", "EWS", "SC", "ST", "PwD"]

QUOTAS = ["All_India", "Home_State", "Management", "NRI"]

BRANCHES = [
    "", "CSE", "ECE", "Mech", "Civil", "EE",
    "Chemical", "AI/ML", "IT", "Biotech",
]

STATES = [
    "", "Andhra Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
    "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
    "Uttarakhand", "West Bengal",
]


def render_sidebar() -> dict:
    """
    Render the sidebar filter panel.
    Returns a dict:
        {
            "exam":       str | None,
            "category":   str | None,
            "quota":      str,
            "state":      str | None,
            "branch":     str | None,
            "budget_max": int,
        }
    """
    with st.sidebar:

        st.markdown("## 🎓 CollegeCompass AI")
        st.markdown("*Your local admission counsellor*")
        st.divider()

        st.markdown("### 🔍 Student Profile")

        exam = st.selectbox(
            "Entrance Exam",
            EXAMS,
            help="Which exam did / will you appear for?",
        )

        category = st.selectbox(
            "Category",
            CATEGORIES,
            help="Your reservation category for cutoff comparison.",
        )

        quota = st.selectbox(
            "Quota",
            QUOTAS,
            index=0,
            help="All_India quota applies nationwide; Home_State gives state preference.",
        )

        st.divider()
        st.markdown("### 🗓️ Preferences")

        state = st.selectbox(
            "Preferred State",
            STATES,
            help="Filter colleges by state (leave blank for all India).",
        )

        branch = st.selectbox(
            "Preferred Branch",
            BRANCHES,
            help="Your target engineering branch.",
        )

        budget_max = st.slider(
            "Max Annual Tuition (₹)",
            min_value=50_000,
            max_value=2_000_000,
            value=500_000,
            step=25_000,
            format="₹%d",
            help="Colleges above this fee will be deprioritised.",
        )

        st.divider()
        st.markdown("### ℹ️ About")
        st.caption(
            "CollegeCompass AI runs 100% locally using Ollama + ChromaDB. "
            "No data leaves your device."
        )

        st.markdown("**Models used:**")
        st.code("LLM:    qwen2:0.5b\nEmbed:  nomic-embed-text", language="text")

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
