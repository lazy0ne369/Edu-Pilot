"""
EduPilot — ChromaDB retriever factory.
Embeddings: OllamaEmbeddings (mxbai-embed-large) — local, stable, already ingested.
LLM: Solar Pro 3 via OpenRouter.
"""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from agent.config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    EMBED_MODEL,
    RETRIEVER_K,
    SCORE_THRESHOLD,
)


def _build_where_filter(
    state: str = None,
    exam: str = None,
    budget_max: int = None,
    branch: str = None,
) -> dict | None:
    conditions = []
    if state:
        conditions.append({"state": {"$eq": state}})
    if exam:
        conditions.append({"exams": {"$contains": exam}})
    if budget_max:
        conditions.append({"tuition_fee": {"$lte": budget_max}})
    if branch:
        conditions.append({"branches": {"$contains": branch}})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def get_retriever(
    state: str = None,
    exam: str = None,
    budget_max: int = None,
    branch: str = None,
):
    """
    Return a similarity-score-threshold retriever backed by ChromaDB.
    Uses OllamaEmbeddings (nomic-embed-text) — unchanged from original.
    Only the chat LLM has been migrated to Gemini.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL
    )

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )

    where_filter = _build_where_filter(
        state=state,
        exam=exam,
        budget_max=budget_max,
        branch=branch,
    )

    retriever_kwargs: dict = {
        "k": RETRIEVER_K,
        "score_threshold": SCORE_THRESHOLD,
    }
    if where_filter:
        retriever_kwargs["filter"] = where_filter

    return vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs=retriever_kwargs,
    )
