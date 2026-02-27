"""
EduPilot — Data ingestion into ChromaDB.
Embeddings: OllamaEmbeddings (mxbai-embed-large) — stable.
LLM: Solar Pro 3 via OpenRouter.

Public API:
    ingest()          — Full ingest: load JSON → embed → store (idempotent)
    ensure_ingested() — Calls ingest() only if collection is empty/missing
"""

import json
import sys
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

from agent.config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    DATA_PATH,
    EMBED_MODEL,
    OLLAMA_BASE_URL,
)


def _load_colleges(data_path: str = DATA_PATH) -> list[dict]:
    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(
            f"College data not found at {path!r}. Run: python data/generate_data.py"
        )
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _college_to_document(college: dict) -> Document:
    cutoffs_text = ""
    for exam, categories in college.get("cutoffs", {}).items():
        for category, quotas in categories.items():
            for quota, rank in quotas.items():
                cutoffs_text += f"{exam} {category} {quota} closing rank {rank}. "

    scholarships_text = ""
    for schol in college.get("scholarships", []):
        scholarships_text += (
            f"Scholarship: {schol['percent']}% for rank < {schol['rank_below']}. "
        )

    branches_text = ", ".join(college.get("branches", []))

    page_content = (
        f"{college['name']} is a {college['type']} college in "
        f"{college['city']}, {college['state']}. "
        f"NIRF rank: {college['nirf_rank']}. "
        f"Annual tuition fee: ₹{college['tuition_fee']:,}. "
        f"Average package: {college['avg_package']} LPA. "
        f"Highest package: {college['highest_package']} LPA. "
        f"Branches: {branches_text}. "
        f"Accepted exams: {', '.join(college.get('exams', []))}. "
        f"Admission status: {college['status']}. "
        f"Application deadline: {college.get('deadline', 'N/A')}. "
        f"{cutoffs_text}"
        f"{scholarships_text}"
        f"{college.get('description', '')}"
    )

    metadata = {
        "name":            college["name"],
        "state":           college["state"],
        "city":            college.get("city", ""),
        "type":            college["type"],
        "nirf_rank":       int(college["nirf_rank"]),
        "tuition_fee":     int(college["tuition_fee"]),
        "avg_package":     str(college["avg_package"]),
        "highest_package": str(college.get("highest_package", "N/A")),
        "status":          college["status"],
        "deadline":        college.get("deadline", "N/A"),
        "branches":        ", ".join(college.get("branches", [])),
        "exams":           ", ".join(college.get("exams", [])),
    }

    return Document(page_content=page_content, metadata=metadata)


def ingest(data_path: str = DATA_PATH) -> int:
    """
    Load college data, embed with nomic-embed-text (Ollama), store in ChromaDB.
    Idempotent — deletes and recreates the collection on every call.
    """
    print("Loading college data …")
    colleges  = _load_colleges(data_path)
    documents = [_college_to_document(c) for c in colleges]

    print(f"Embedding {len(documents)} colleges with {EMBED_MODEL} …")
    embeddings = OllamaEmbeddings(
        model=EMBED_MODEL,
        base_url=OLLAMA_BASE_URL,
    )

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Removed existing collection.")
    except Exception:
        pass

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
    )

    print(f"✅  Ingested {len(documents)} documents into '{COLLECTION_NAME}'.")
    return len(documents)


def ensure_ingested(data_path: str = DATA_PATH) -> None:
    """No-op if collection exists; otherwise ingests."""
    try:
        client     = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_collection(COLLECTION_NAME)
        if collection.count() > 0:
            print(f"[ingest] {collection.count()} docs in '{COLLECTION_NAME}' — skipping.")
            return
    except Exception:
        pass
    print("[ingest] Collection empty or missing — starting ingest …")
    ingest(data_path)


if __name__ == "__main__":
    n = ingest()
    sys.exit(0 if n > 0 else 1)
