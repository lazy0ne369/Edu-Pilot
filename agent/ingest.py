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
from langchain_huggingface import HuggingFaceEmbeddings

from agent.config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    DATA_PATH,
    EMBED_MODEL,
)


def _load_colleges(data_path: str = DATA_PATH) -> list[dict]:
    path = Path(data_path)
    if not path.exists():
        print(f"College data not found at {path!r}. Generating...")
        try:
            from data.generate_data import main as generate_data_main
            generate_data_main()
        except ImportError:
            import subprocess
            import sys
            script_path = str(Path(__file__).parent.parent / "data" / "generate_data.py")
            subprocess.run([sys.executable, script_path], check=True)
            
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


import hashlib

def _get_file_hash(data_path: str) -> str:
    """Calculate MD5 hash of the data file."""
    hasher = hashlib.md5()
    with open(data_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def ingest(data_path: str = DATA_PATH) -> int:
    """
    Load college data, embed with Google Gemini model, store in ChromaDB.
    Idempotent — deletes and recreates the collection on every call.
    """
    print("Loading college data …")
    colleges  = _load_colleges(data_path)
    documents = [_college_to_document(c) for c in colleges]

    print(f"Embedding {len(documents)} colleges with {EMBED_MODEL} …")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL
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

    # Save hash after successful ingestion
    hash_path = Path(CHROMA_PATH) / "ingest_hash.txt"
    hash_path.parent.mkdir(parents=True, exist_ok=True)
    hash_path.write_text(_get_file_hash(data_path))

    print(f"✅  Ingested {len(documents)} documents into '{COLLECTION_NAME}'.")
    return len(documents)


def ensure_ingested(data_path: str = DATA_PATH) -> None:
    """No-op if collection exists and matches file hash; otherwise ingests."""
    try:
        client     = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_collection(COLLECTION_NAME)
        
        hash_path = Path(CHROMA_PATH) / "ingest_hash.txt"
        current_hash = _get_file_hash(data_path)
        
        if collection.count() > 0 and hash_path.exists():
            stored_hash = hash_path.read_text().strip()
            if stored_hash == current_hash:
                print(f"[ingest] {collection.count()} docs in '{COLLECTION_NAME}' (hash match) — skipping.")
                return
            else:
                print("[ingest] Hash mismatch — data file updated.")
        elif collection.count() == 0:
            print("[ingest] Collection empty.")
        else:
            print("[ingest] Hash file missing.")
            
    except Exception as e:
        print(f"[ingest] Cache check failed: {e}")
    
    print("[ingest] Starting/Updating ingest …")
    ingest(data_path)


if __name__ == "__main__":
    n = ingest()
    sys.exit(0 if n > 0 else 1)
