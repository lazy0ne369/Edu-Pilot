"""
EduPilot — LangGraph StateGraph.
LLM: upstage/solar-pro-3:free via OpenRouter (no tool calling needed)
RAG: Context retrieved from ChromaDB and injected directly into system prompt.

This is more reliable than tool calling — works with all models.
"""

import logging
from dotenv import load_dotenv
from typing import Annotated

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI

from agent.config import (
    LLM_MODEL,
    LLM_TEMPERATURE,
    MEMORY_K,
    LLM_API_KEY,
)
from agent.prompts import SYSTEM_PROMPT
from agent.retriever import get_retriever

load_dotenv()
log = logging.getLogger(__name__)

# Fallback models for when primary fails (Gemini)
FALLBACK_MODELS = [
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-2.0-flash",
]


# ── State ─────────────────────────────────────────────────────
class AgentState(TypedDict):
    messages:      Annotated[list[BaseMessage], add_messages]
    filters:       dict      # sidebar filters passed from app.py
    context:       str       # retrieved RAG context
    college_count: int       # number of colleges found matching filters


# ── LLM call (ChatGoogleGenerativeAI) ──────────────────────────────
def _call_llm(model: str, system: str, history: list[BaseMessage]) -> str:
    """Call the LLM with a given model and message history using LangChain."""
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=LLM_API_KEY,
        temperature=LLM_TEMPERATURE
    )
    
    messages = [SystemMessage(content=system)] + history
    response = llm.invoke(messages)
    return response.content



# ── RAG retrieval ─────────────────────────────────────────────
def _retrieve_context(query: str, filters: dict) -> tuple[str, int]:
    """Retrieve relevant college docs from ChromaDB and format as context."""
    try:
        retriever = get_retriever(
            state=filters.get("state"),
            exam=filters.get("exam"),
            budget_max=filters.get("budget_max"),
            branch=filters.get("branch"),
        )
        docs = retriever.invoke(query)
        if not docs:
            return "No specific college data found for this query.", 0
        
        # Sort docs by NIRF rank if available, otherwise keep semantic order
        docs = sorted(docs, key=lambda x: x.metadata.get("nirf_rank", 999))
        
        ctx = "\n\n---\n\n".join(
            f"**{doc.metadata.get('name', 'College')}**\n{doc.page_content}"
            for doc in docs
        )
        return ctx, len(docs)
    except Exception as e:
        log.warning("[EduPilot] Retrieval failed: %s", e)
        return "", 0


# ── Build graph ───────────────────────────────────────────────
def build_graph():

    def retrieve(state: AgentState) -> dict:
        """Retrieve context from ChromaDB for the latest user message."""
        messages = state["messages"]
        filters  = state.get("filters", {})
        query = next(
            (m.content for m in reversed(messages) if isinstance(m, HumanMessage)),
            ""
        )
        context, count = _retrieve_context(query, filters)
        return {"context": context, "college_count": count}

    def call_model(state: AgentState) -> dict:
        """Call the LLM with system prompt + retrieved context + conversation history."""
        messages = state["messages"]
        context  = state.get("context", "")
        filters  = state.get("filters", {})
        count    = state.get("college_count", 0)

        # Trim history
        trimmed  = messages[-(MEMORY_K * 2):] if len(messages) > MEMORY_K * 2 else messages

        # Build system prompt with injected RAG context
        filter_info = ""
        if any(filters.values()):
            parts = [f"{k}={v}" for k, v in filters.items() if v and k != "budget_max"]
            if filters.get("budget_max"):
                parts.append(f"budget=₹{filters['budget_max']:,}")
            filter_info = f"\nStudent profile: {', '.join(parts)}"

        system = SYSTEM_PROMPT + filter_info
        if count > 0:
            system += f"\n\nTotal matching colleges found: {count}."
            system += f"\n=== Retrieved College Data ===\n{context}\n=== End of Data ===\n\nStritly list ALL {count} matching colleges. DO NOT TRUNCATE or say 'some of the colleges'."
        else:
            system += "\n\nNo matching colleges found for this student profile and query. State that clearly and suggest adjusting filters."

        # We can just pass the trimmed LangChain messages directly
        history = list(trimmed)

        if not history:
            return {"messages": [AIMessage(content="Please ask a question about Indian college admissions.")]}

        # Try primary model then fallbacks
        models_to_try = [LLM_MODEL] + [m for m in FALLBACK_MODELS if m != LLM_MODEL]
        last_err = ""

        for model in models_to_try:
            try:
                content = _call_llm(model, system, history)
                return {"messages": [AIMessage(content=content)]}
            except Exception as e:
                last_err = str(e)
                log.warning("[EduPilot] Model %s failed: %s", model, e)
                continue

        # All models failed
        return {"messages": [AIMessage(content=_error_msg(last_err))]}

    graph = StateGraph(AgentState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("agent", call_model)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "agent")
    graph.add_edge("agent", END)
    return graph.compile(checkpointer=MemorySaver())


def _error_msg(err: str) -> str:
    e = err.lower()
    if "401" in e or "unauthorized" in e:
        return "⚠️ **Invalid API key.** Check your `.env` file for your Gemini key."
    if "429" in e or "rate limit" in e:
        return "⚠️ **Rate limit hit on Gemini.** Please wait a moment and try again."
    if "connection" in e or "timeout" in e:
        return "⚠️ **Connection error.** Check your internet and try again."
    return f"⚠️ All models temporarily unavailable on Gemini. Please try again in a moment.\n\n`{err}`"


# ── Singleton ─────────────────────────────────────────────────
GRAPH = build_graph()
