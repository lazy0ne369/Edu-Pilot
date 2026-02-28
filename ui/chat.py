"""
EduPilot — Chat UI helpers.
Optimised for a premium, centered AI assistant experience with integrated input.
"""

import streamlit as st
from langchain_core.messages import AIMessage


# ── Chat Bubbles & Scroll Logic Styling ───────────────────────
def inject_chat_css():
    st.markdown("""
    <style>
        /* Shared font and basic layout */
        .chat-view-root {
            max-width: 850px;
            margin: 0 auto;
            padding-top: 20px;
            /* Ensure footer can appear below */
            padding-bottom: 40px; 
        }

        /* ── Chat Animations ────────────────────────────────────────── */
        @keyframes chatFadeInSlideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Message Bubbles Styling */
        [data-testid="stChatMessage"] {
            border: none !important;
            background-color: transparent !important;
            margin-bottom: 2rem !important;
            animation: chatFadeInSlideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
        }
        
        /* User bubble (Right) */
        div[data-testid="stChatMessage"]:has(span[aria-label="👤"]) {
            display: flex;
            flex-direction: row-reverse;
            text-align: right;
        }
        div[data-testid="stChatMessage"]:has(span[aria-label="👤"]) .stMarkdown {
            background: linear-gradient(135deg, #111, #222) !important;
            color: #fff !important;
            padding: 14px 22px !important;
            border-radius: 20px 20px 4px 20px !important;
            max-width: 75%;
            font-size: 15px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        }
        div[data-testid="stChatMessage"]:has(span[aria-label="👤"]) .stMarkdown p {
            color: white !important;
        }

        /* Assistant bubble (Left) */
        div[data-testid="stChatMessage"]:has(span[aria-label="🎓"]) {
            display: flex;
            flex-direction: row;
            text-align: left;
        }
        div[data-testid="stChatMessage"]:has(span[aria-label="🎓"]) .stMarkdown {
            background-color: rgba(255, 255, 255, 0.8) !important;
            backdrop-filter: blur(10px) !important;
            color: #1a1a1a !important;
            padding: 18px 24px !important;
            border-radius: 20px 20px 20px 4px !important;
            max-width: 85%;
            border: 1px solid rgba(0,0,0,0.05);
            font-size: 15px;
            line-height: 1.6;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        }
        
        /* Chat Input Integration */
        [data-testid="stChatInput"] {
            position: relative !important;
            bottom: auto !important;
            left: auto !important;
            transform: none !important;
            max-width: 100% !important;
            margin: 40px 0 !important;
            padding: 0 !important;
            z-index: 100;
        }
        
        [data-testid="stChatInput"] > div {
            border: 1px solid rgba(0,0,0,0.08) !important;
            border-radius: 16px !important;
            background: rgba(255,255,255,0.85) !important;
            backdrop-filter: blur(10px) !important;
            box-shadow: 0 4px 24px rgba(0,0,0,0.04) !important;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        
        [data-testid="stChatInput"]:focus-within > div {
            border-color: #222 !important;
            box-shadow: 0 12px 32px rgba(0,0,0,0.1) !important;
            transform: translateY(-2px);
        }

        /* Responsive textarea */
        [data-testid="stChatInput"] textarea {
            font-size: 16px !important;
            padding: 18px 20px !important;
        }

        [data-testid="stChatMessageAvatar"] {
            display: none !important;
        }

        /* Enhanced Welcome Screen Typography */
        .chat-hero-title {
            font-size: 42px;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #111, #555, #111);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px;
            animation: chatFadeInSlideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .chat-hero-subtitle {
            color: #666;
            font-size: 18px;
            animation: chatFadeInSlideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.15s forwards;
            opacity: 0;
        }
    </style>
    """, unsafe_allow_html=True)


def render_welcome(filters: dict = None) -> None:
    inject_chat_css()
    st.markdown('<div class="chat-view-root">', unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; margin: 60px 0 50px 0;">
            <h2 class="chat-hero-title">How can I help you today?</h2>
            <p class="chat-hero-subtitle">Predict your college match with AI.</p>
        </div>
    """, unsafe_allow_html=True)

    chips = [
        "Best NITs for Computer Science?",
        "JoSAA registration guide 2025",
        "IIT Delhi vs IIT Bombay for EE",
        "Colleges with low fees in North India"
    ]
    cols = st.columns(2)
    for i, q in enumerate(chips):
        with cols[i % 2]:
            if st.button(q, key=f"chip_{i}", use_container_width=True):
                st.session_state["_injected_prompt"] = q
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def render_chat(messages: list[dict]) -> None:
    inject_chat_css()
    st.markdown('<div class="chat-view-root">', unsafe_allow_html=True)
    for msg in messages:
        avatar = "👤" if msg["role"] == "user" else "🎓"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
    st.markdown('</div>', unsafe_allow_html=True)


def render_stream(graph, input_msg: dict, config: dict) -> str:
    # Use a specific container for streaming to maintain root styles
    st.markdown('<div class="chat-view-root">', unsafe_allow_html=True)
    response_placeholder = st.empty()
    full_response = ""

    with st.spinner(" "):
        try:
            for state in graph.stream(input_msg, config, stream_mode="values"):
                messages = state.get("messages", [])
                if not messages: continue
                last_msg = messages[-1]

                if isinstance(last_msg, AIMessage):
                    content = last_msg.content
                    if isinstance(content, str) and content.strip():
                        full_response = content
                        # Render inside the styled root
                        response_placeholder.markdown(full_response + "▌")

            if full_response:
                response_placeholder.markdown(full_response)
            else:
                full_response = "Synthesizing response..."
                response_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"⚠️ **Error:** {str(e)}"
            response_placeholder.markdown(full_response)

    st.markdown('</div>', unsafe_allow_html=True)
    return full_response
