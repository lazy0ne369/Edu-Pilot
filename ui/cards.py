"""
CollegeCompass AI — College recommendation card renderer.

render_college_card(college_dict) renders a styled Streamlit card
for a single college. Called from external code when structured
college data is available; otherwise the markdown response suffices.
"""

import streamlit as st


def render_college_card(college: dict) -> None:
    """
    Render a styled card for a single college.

    Args:
        college: dict with keys:
            name, state, type, nirf_rank, tuition_fee,
            avg_package, status, deadline (all optional)
    """
    status = college.get("status", "Unknown")
    status_color = {
        "Open":     "#22c55e",   # green
        "Closed":   "#ef4444",   # red
        "Upcoming": "#f59e0b",   # amber
    }.get(status, "#6b7280")

    fee = college.get("tuition_fee", 0)
    fee_str = f"₹{int(fee):,}/yr" if fee else "N/A"

    pkg = college.get("avg_package", "N/A")
    pkg_str = f"{pkg} LPA" if pkg != "N/A" else "N/A"

    nirf = college.get("nirf_rank", "N/A")

    with st.container():
        st.markdown(
            f"""
            <div style="
                border: 1px solid #e5e7eb;
                border-left: 4px solid {status_color};
                border-radius: 8px;
                padding: 1rem 1.2rem;
                margin-bottom: 0.75rem;
                background: #fafafa;
            ">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong style="font-size: 1.05rem;">🎓 {college.get("name","Unknown")}</strong>
                        &nbsp;<span style="color:#6b7280; font-size:0.85rem;">
                            NIRF #{nirf} · {college.get("type","N/A")} · {college.get("state","N/A")}
                        </span>
                    </div>
                    <span style="
                        background:{status_color}20;
                        color:{status_color};
                        padding: 2px 10px;
                        border-radius: 99px;
                        font-size: 0.8rem;
                        font-weight: 600;
                    ">{status}</span>
                </div>
                <div style="
                    display:flex; gap:2rem; margin-top:0.6rem;
                    font-size: 0.9rem; color:#374151;
                ">
                    <div>💰 <strong>Tuition:</strong> {fee_str}</div>
                    <div>📦 <strong>Avg Package:</strong> {pkg_str}</div>
                    <div>📅 <strong>Deadline:</strong> {college.get("deadline","N/A")}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_college_cards(colleges: list[dict]) -> None:
    """Render multiple college cards in sequence."""
    for college in colleges:
        render_college_card(college)
