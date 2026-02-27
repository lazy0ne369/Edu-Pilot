"""
CollegeCompass AI — Streamlit entrypoint.
Run: streamlit run app.py

This file ONLY wires ui/ and agent/ modules together.
Zero business logic lives here.
"""

import uuid
import streamlit as st
from langchain_core.messages import HumanMessage

# ── Page config — must be first Streamlit call ────────────────
st.set_page_config(
    page_title="CollegeCompass AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────
from agent.ingest import ensure_ingested
from agent.graph import GRAPH
from ui.sidebar import render_sidebar
from ui.chat import render_chat, render_stream, render_welcome


# ── One-time data ingestion ───────────────────────────────────
@st.cache_resource(show_spinner="Checking college database...")
def init_database():
    """Run ingestion once per Streamlit server session (cached by cache_resource)."""
    ensure_ingested()
    return True


# ── Session state initialisation ─────────────────────────────
def init_session():
    """Initialise session state keys on first load."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "filters" not in st.session_state:
        st.session_state.filters = {}


# ── Main ──────────────────────────────────────────────────────
def main():
    init_database()
    init_session()

    # Sidebar filters
    filters = render_sidebar()
    st.session_state.filters = filters

    # Header
    st.title("🎓 CollegeCompass AI")
    st.caption(
        f"Indian college admission counsellor · "
        f"Session: `{st.session_state.session_id[:8]}…` · "
        f"Filters: {', '.join(f'{k}={v}' for k,v in filters.items() if v and k != 'budget_max') or 'none'} · "
        f"Budget: ₹{filters.get('budget_max',0):,}/yr"
    )

    # Clear history button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🗑️ Clear", help="Clear chat history"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

    st.divider()

    # Welcome screen (no messages yet) — passes filters for dynamic suggestions
    if not st.session_state.messages:
        render_welcome(filters=filters)

    # Handle prompt injected by clicking a suggestion button
    if "_injected_prompt" in st.session_state:
        injected = st.session_state.pop("_injected_prompt")
        st.session_state.messages.append({"role": "user", "content": injected})

    # Chat history
    render_chat(st.session_state.messages)


    # Chat input
    if prompt := st.chat_input(
        "Ask me anything — rank, fees, cutoffs, scholarships, deadlines..."
    ):
        # Append filters context to the query if filters are set
        enriched_prompt = prompt
        f = st.session_state.filters
        filter_parts = []
        if f.get("exam"):       filter_parts.append(f"Exam: {f['exam']}")
        if f.get("category"):   filter_parts.append(f"Category: {f['category']}")
        if f.get("quota"):      filter_parts.append(f"Quota: {f['quota']}")
        if f.get("state"):      filter_parts.append(f"Preferred state: {f['state']}")
        if f.get("branch"):     filter_parts.append(f"Preferred branch: {f['branch']}")
        if f.get("budget_max"): filter_parts.append(f"Budget: ₹{f['budget_max']:,}/year")

        if filter_parts:
            enriched_prompt = (
                f"{prompt}\n\n[Student profile: {' | '.join(filter_parts)}]"
            )

        # Display user message (original, without filter injection)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Stream agent response
        config = {"configurable": {"thread_id": st.session_state.session_id}}
        input_msg = {
            "messages": [HumanMessage(content=enriched_prompt)],
            "filters":  st.session_state.filters,
            "context":  "",
        }

        with st.chat_message("assistant", avatar="🎓"):
            response = render_stream(GRAPH, input_msg, config)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


if __name__ == "__main__":
    main()
