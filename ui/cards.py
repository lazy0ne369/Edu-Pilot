"""
EduPilot — College recommendation card renderer.
Redesigned with a premium white aesthetic.
"""

import streamlit as st


def render_college_card(college: dict) -> None:
    """
    Render a premium college card with type-specific accents.
    """
    ctype = college.get("type", "Private")
    
    # Task 6 accent colors
    accent_map = {
        "IIT": "#ef4444",
        "NIT": "#3b82f6",
        "Deemed": "#f59e0b",
        "Private": "#8b5cf6"
    }
    accent_color = accent_map.get(ctype, "#8b5cf6")

    fee = college.get("tuition_fee", 0)
    fee_str = f"₹{int(fee)//1000}K" if fee else "N/A"

    pkg = college.get("avg_package", "N/A")
    pkg_str = f"{pkg} LPA" if pkg != "N/A" else "N/A"
    
    status = college.get("status", "Unknown")
    
    nirf = college.get("nirf_rank", "N/A")

    st.markdown(
        f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 0;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border: 1px solid #f0f0f0;
            overflow: hidden;
            font-family: 'Inter', sans-serif;
        ">
            <!-- Top Accent Bar -->
            <div style="height: 4px; background: {accent_color}; width: 100%;"></div>
            
            <div style="padding: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                    <div>
                        <div style="font-size: 12px; font-weight: 600; color: {accent_color}; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.02em;">
                            {ctype} COLLEGE
                        </div>
                        <div style="font-size: 18px; font-weight: 700; color: #0a0a0a;">
                            {college.get("name","Unknown")}
                        </div>
                    </div>
                    <div style="background: #f3f4f6; color: #4b5563; padding: 4px 10px; border-radius: 99px; font-size: 12px; font-weight: 600;">
                        NIRF #{nirf}
                    </div>
                </div>
                
                <div style="color: #6b7280; font-size: 13px; margin-bottom: 20px;">
                    📍 {college.get("state","Unknown")}
                </div>

                <!-- Metric boxes row -->
                <div style="display: flex; gap: 12px; margin-bottom: 20px;">
                    <div style="flex: 1; background: #f8f8f8; padding: 10px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; color: #888; text-transform: uppercase;">Tuition</div>
                        <div style="font-size: 14px; font-weight: 700; color: #111;">{fee_str}</div>
                    </div>
                    <div style="flex: 1; background: #f8f8f8; padding: 10px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; color: #888; text-transform: uppercase;">Avg Pkg</div>
                        <div style="font-size: 14px; font-weight: 700; color: #111;">{pkg_str}</div>
                    </div>
                    <div style="flex: 1; background: #f8f8f8; padding: 10px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; color: #888; text-transform: uppercase;">Status</div>
                        <div style="font-size: 14px; font-weight: 700; color: #111;">{status}</div>
                    </div>
                </div>

                <div style="display: flex; justify-content: flex-end;">
                    <div style="font-size: 13px; font-weight: 600; color: #666; cursor: pointer; padding: 6px 12px; border: 1px solid #ddd; border-radius: 6px; transition: 0.3s;">
                        View Details
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_college_cards(colleges: list[dict]) -> None:
    """Render multiple premium college cards in sequence."""
    for college in colleges:
        render_college_card(college)
