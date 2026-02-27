"""
CollegeCompass AI — Chat UI helpers.

Functions:
    render_welcome(filters)  — Dynamic suggestions based on active sidebar filters
    render_chat(messages)    — Render the chat message history
    render_stream(...)       — Stream agent tokens and return full response
"""

import streamlit as st
from langchain_core.messages import AIMessage


# ── Dynamic prompt suggestions ────────────────────────────────

def _build_suggestions(filters: dict) -> list[tuple[str, str]]:
    """
    Build a context-aware list of (icon, prompt) suggestions
    based on whatever filters the user has set in the sidebar.
    """
    exam      = filters.get("exam")
    category  = filters.get("category", "General")
    quota     = filters.get("quota", "All_India")
    state     = filters.get("state")
    branch    = filters.get("branch", "CSE")
    budget    = filters.get("budget_max", 500_000)

    budget_str = f"₹{budget // 100_000}L" if budget >= 100_000 else f"₹{budget:,}"
    branch_str = branch or "CSE"
    cat_str    = category or "General"
    state_str  = state or "India"
    exam_str   = exam or "JEE Main"
    quota_str  = quota.replace("_", " ")

    suggestions = []

    # ── Budget-aware suggestions ──────────────────────────────
    if budget:
        suggestions.append((
            "💰",
            f"Show me {branch_str} colleges under {budget_str} in {state_str}"
        ))
        suggestions.append((
            "🎓",
            f"Best {branch_str} colleges under {budget_str} for {cat_str} category ({quota_str} quota)"
        ))

    # ── Eligibility suggestions ───────────────────────────────
    if exam:
        suggestions.append((
            "🎯",
            f"What rank do I need for NIT Trichy with {exam} under {cat_str} category?"
        ))
        suggestions.append((
            "✅",
            f"Can I get into a top NIT with rank 45000 in {exam}?"
        ))
    else:
        suggestions.append((
            "🎯",
            f"Can I get NIT Trichy with JEE Main rank 45000 {cat_str}?"
        ))

    # ── State-aware suggestions ───────────────────────────────
    if state:
        suggestions.append(("🏫", f"Top government colleges in {state_str} for {branch_str}"))
        suggestions.append(("🏛️", f"Private colleges in {state_str} accepting {exam_str}"))
    else:
        suggestions.append(("🏫", "Top NITs for CSE — fees, packages and cutoffs"))

    # ── Deadline and scholarship suggestions ─────────────────
    suggestions.append(("📅", "Which college applications are still open in 2025?"))
    suggestions.append(("💸", f"Scholarships available for {cat_str} students under {budget_str}"))
    suggestions.append(("🏆", f"Best IITs for {branch_str} with JEE Advanced cutoffs"))

    # Return first 6 (fill grid)
    return suggestions[:6]


# ── Welcome screen ────────────────────────────────────────────

def render_welcome(filters: dict = None) -> None:
    """
    Display a branded welcome panel with context-aware example prompts.

    Args:
        filters: dict from render_sidebar() — used to personalise suggestions.
                 Falls back to generic suggestions if None or empty.
    """
    if filters is None:
        filters = {}

    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 1rem 1rem;">
            <h2 style="margin-bottom: 0.2rem;">👋 Welcome to CollegeCompass AI</h2>
            <p style="color: grey; font-size: 0.95rem;">
                Ask me anything about Indian engineering admissions —
                ranks, fees, cutoffs, scholarships, or deadlines.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Show personalisation banner if filters are active
    active = {k: v for k, v in filters.items() if v and k != "budget_max"}
    if active or filters.get("budget_max", 500_000) != 500_000:
        filter_tags = " · ".join(
            [f"**{k.replace('_',' ').title()}:** {v}" for k, v in active.items()]
            + ([f"**Budget:** ₹{filters['budget_max']//1000}K/yr"]
               if filters.get("budget_max") else [])
        )
        st.info(f"🎛️ Suggestions tailored to your profile — {filter_tags}", icon="✨")
    else:
        st.caption("💡 Set filters in the sidebar to get personalised suggestions.")

    st.markdown("**Try one of these:**")
    suggestions = _build_suggestions(filters)

    cols = st.columns(2)
    for i, (icon, prompt) in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(
                f"{icon} {prompt}",
                key=f"example_{i}",
                use_container_width=True,
            ):
                st.session_state["_injected_prompt"] = prompt
                st.rerun()

    st.divider()


# ── Chat history renderer ─────────────────────────────────────

def render_chat(messages: list[dict]) -> None:
    """
    Render all messages in the session history.

    Args:
        messages: List of {'role': 'user'|'assistant', 'content': str}
    """
    for msg in messages:
        avatar = "👤" if msg["role"] == "user" else "🎓"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])


# ── Streaming agent response ──────────────────────────────────

def render_stream(graph, input_msg: dict, config: dict) -> str:
    """
    Stream tokens from the LangGraph agent and render them live.

    Args:
        graph:     Compiled LangGraph graph (GRAPH singleton)
        input_msg: Dict with 'messages' key containing HumanMessage
        config:    LangGraph config with thread_id

    Returns:
        Full response string (stored in session messages).
    """
    response_placeholder = st.empty()
    full_response = ""

    # Show a spinner while the agent is thinking / calling tools
    with st.spinner("🔍 Searching college database…"):
        try:
            for state in graph.stream(input_msg, config, stream_mode="values"):
                messages = state.get("messages", [])
                if not messages:
                    continue

                last_msg = messages[-1]

                if isinstance(last_msg, AIMessage):
                    content = last_msg.content
                    if isinstance(content, str) and content.strip():
                        full_response = content
                        response_placeholder.markdown(full_response + "▌")

            if full_response:
                response_placeholder.markdown(full_response)
            else:
                full_response = (
                    "I couldn't generate a response. "
                    "Make sure Ollama is running (`ollama serve`) "
                    f"and the model is pulled (`ollama pull llama3.2:3b`)."
                )
                response_placeholder.warning(full_response)

        except Exception as e:
            error_msg = str(e)
            if "Connection refused" in error_msg or "11434" in error_msg:
                full_response = (
                    "⚠️ **Ollama is not running.**\n\n"
                    "Start it with: `ollama serve`\n\n"
                    "Then pull the model: `ollama pull llama3.2:3b`"
                )
            elif "does not support tools" in error_msg or "400" in error_msg:
                full_response = (
                    "⚠️ **Tool calling not supported by this model.**\n\n"
                    "Update `agent/config.py` and set:\n"
                    "```python\nLLM_MODEL = \"llama3.2:3b\"\n```\n"
                    "Then pull: `ollama pull llama3.2:3b`"
                )
            elif "Collection" in error_msg or "not found" in error_msg.lower():
                full_response = (
                    "⚠️ **College database not found.**\n\n"
                    "Run:\n"
                    "```\npython data/generate_data.py\npython -m agent.ingest\n```"
                )
            else:
                full_response = f"⚠️ **Error:** {error_msg}"

            response_placeholder.markdown(full_response)

    return full_response
