"""
LangGraph tool definitions for EduPilot.
Three tools: search_colleges, check_eligibility, get_deadlines.
Docstrings are read by LangGraph to decide which tool to invoke.
"""

from langchain_core.tools import tool

from agent.retriever import get_retriever


@tool
def search_colleges(
    query: str,
    state: str = None,
    exam: str = None,
    budget_max: int = None,
    branch: str = None,
) -> str:
    """Search the Indian college database for colleges matching a query.

    Use this tool for:
    - General college recommendations ("good CSE colleges in South India")
    - Finding colleges within a budget ("colleges under 2 lakh fees")
    - Exploring options by state, branch, or exam type
    - Any question asking "which colleges", "suggest colleges", "list colleges"

    Args:
        query:      Natural language search query
        state:      Indian state to filter by (e.g. 'Tamil Nadu', 'Karnataka')
        exam:       Entrance exam name (e.g. 'JEE Main', 'VITEEE', 'BITSAT')
        budget_max: Maximum annual tuition in INR (e.g. 200000 for ₹2L/year)
        branch:     Branch/specialisation (e.g. 'CSE', 'ECE', 'Mech', 'AI/ML')

    Returns:
        Top-3 college summaries with fees, rankings, placements and eligibility info.
    """
    retriever = get_retriever(
        state=state,
        exam=exam,
        budget_max=budget_max,
        branch=branch,
    )
    docs = retriever.invoke(query)
    if not docs:
        return (
            "No colleges found matching those filters. "
            "Try broadening your search — remove state/branch filters or increase budget."
        )
    parts = []
    for i, doc in enumerate(docs, 1):
        m = doc.metadata
        parts.append(
            f"[Result {i}]\n"
            f"College: {m.get('name', 'Unknown')}\n"
            f"State: {m.get('state', 'N/A')} | Type: {m.get('type', 'N/A')} | NIRF: #{m.get('nirf_rank', 'N/A')}\n"
            f"Tuition: ₹{int(m.get('tuition_fee','0')):,}/year | Avg Package: {m.get('avg_package','N/A')} LPA\n"
            f"Admission Status: {m.get('status', 'Unknown')}\n"
            f"---\n{doc.page_content}"
        )
    return "\n\n".join(parts)


@tool
def check_eligibility(
    rank: int,
    exam: str,
    category: str = "General",
    quota: str = "All_India",
    branch: str = "CSE",
) -> str:
    """Check if a student is eligible for colleges given their entrance exam rank.

    Use this tool for:
    - "Can I get into X college with rank Y?"
    - "What colleges can I get with JEE rank 45000?"
    - "Am I eligible for NIT Trichy with OBC rank 12000?"
    - Any question involving rank-based eligibility or cutoff comparison

    Args:
        rank:     Student's entrance exam rank (lower = better for JEE/BITSAT)
        exam:     Exam name (e.g. 'JEE Main', 'JEE Advanced', 'BITSAT', 'VITEEE')
        category: Reservation category ('General', 'OBC', 'EWS', 'SC', 'ST', 'PwD')
        quota:    Admission quota ('All_India', 'Home_State', 'Management')
        branch:   Preferred branch (default: 'CSE')

    Returns:
        Dream / Safe / Likely college tiers with specific cutoff comparison.
    """
    query = (
        f"{exam} rank {rank} {category} category {quota} quota "
        f"{branch} cutoff eligibility closing rank 2024"
    )
    retriever = get_retriever(exam=exam, branch=branch)
    docs = retriever.invoke(query)

    if not docs:
        return (
            f"No cutoff data found for {exam} {category} category. "
            "The database may not have this specific combination. "
            "Please check the official JoSAA/college website for accurate cutoffs."
        )

    results = []
    for doc in docs:
        m = doc.metadata
        college_name = m.get("name", "Unknown College")
        nirf = m.get("nirf_rank", "N/A")
        fee = int(m.get("tuition_fee", 0))
        avg_pkg = m.get("avg_package", "N/A")
        content = doc.page_content

        # Try to extract closing rank from content
        import re
        rank_match = re.search(r'closing rank.*?(\d{2,6})', content, re.IGNORECASE)
        cutoff_rank = int(rank_match.group(1)) if rank_match else None

        if cutoff_rank:
            if rank <= cutoff_rank * 0.7:
                tier = "🟢 DREAM — very likely"
            elif rank <= cutoff_rank:
                tier = "🟡 SAFE — within cutoff"
            elif rank <= cutoff_rank * 1.15:
                tier = "🟠 BORDERLINE — slightly above cutoff"
            else:
                tier = "🔴 UNLIKELY — above cutoff"
            eligibility_note = f"Your rank: {rank:,} | Cutoff ({category}, {quota}): ~{cutoff_rank:,} | {tier}"
        else:
            eligibility_note = f"Your rank: {rank:,} | Cutoff data not precise — check official site"

        results.append(
            f"College: {college_name} (NIRF #{nirf})\n"
            f"Tuition: ₹{fee:,}/year | Avg Package: {avg_pkg} LPA\n"
            f"Eligibility: {eligibility_note}\n"
            f"Detail: {content[:300]}..."
        )

    return "\n\n---\n\n".join(results)


@tool
def get_deadlines(
    college_name: str = None,
    exam: str = None,
) -> str:
    """Fetch application deadlines and admission cycle status for colleges or exams.

    Use this tool for:
    - "When does VIT application close?"
    - "Is VITEEE still open?"
    - "What are the upcoming admission deadlines?"
    - "When is NIT counselling?"
    - Any question about dates, deadlines, open/closed status

    Args:
        college_name: College name to look up (e.g. 'VIT Vellore', 'NIT Trichy')
        exam:         Exam name to look up deadlines for (e.g. 'VITEEE', 'JEE Main')

    Returns:
        Application deadlines, exam dates, counselling dates and current status.
    """
    target = college_name or exam or "admission deadline"
    query = f"admission deadline application date {target} status open closed upcoming 2025"

    retriever = get_retriever()
    docs = retriever.invoke(query)

    if not docs:
        return (
            "Deadline information not found in our database. "
            "For the most current dates, check the official college or exam website directly."
        )

    results = []
    for doc in docs:
        m = doc.metadata
        name = m.get("name", "Unknown")
        status = m.get("status", "Unknown")
        results.append(
            f"College: {name}\n"
            f"Admission Status: {status}\n"
            f"Info: {doc.page_content[:400]}..."
        )

    return "\n\n---\n\n".join(results)
