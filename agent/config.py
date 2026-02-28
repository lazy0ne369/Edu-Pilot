"""
EduPilot — Configuration constants.
LLM:        Solar Pro 3 via OpenRouter (OpenAI-compatible API)
Embeddings: mxbai-embed-large via Ollama (local, stable)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Gemini / LLM ──────────────────────────────────────────────
LLM_API_KEY      = os.environ.get("GOOGLE_API_KEY", "")

# Best performing Gemini models:
LLM_MODEL        = "gemini-1.5-flash"
LLM_TEMPERATURE  = 0.3

# ── Embeddings (HuggingFace — cloud-friendly, free, low memory) ─────────
EMBED_MODEL     = "all-MiniLM-L6-v2"

# ── ChromaDB ──────────────────────────────────────────────────
CHROMA_PATH     = "./chroma_db"
COLLECTION_NAME = "college_compass"

# ── Retriever ─────────────────────────────────────────────────
RETRIEVER_K      = 50
SCORE_THRESHOLD  = 0.1

# ── Conversation memory ───────────────────────────────────────
MEMORY_K        = 6

# ── Data ──────────────────────────────────────────────────────
DATA_PATH       = "./data/colleges.json"
