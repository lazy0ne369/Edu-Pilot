"""
CollegeCompass AI — Configuration constants.
LLM:        Llama 3.3 70B via OpenRouter (OpenAI-compatible API)
Embeddings: nomic-embed-text via Ollama (local, stable)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── OpenRouter / LLM ──────────────────────────────────────────
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Best available free model on OpenRouter right now (confirmed working):
LLM_MODEL        = "upstage/solar-pro-3:free"
LLM_TEMPERATURE  = 0.3

# ── Embeddings (Ollama — local, stable) ───────────────────────
EMBED_MODEL     = "mxbai-embed-large"
OLLAMA_BASE_URL = "http://localhost:11434"

# ── ChromaDB ──────────────────────────────────────────────────
CHROMA_PATH     = "./chroma_db"
COLLECTION_NAME = "college_compass"

# ── Retriever ─────────────────────────────────────────────────
RETRIEVER_K      = 3
SCORE_THRESHOLD  = 0.3

# ── Conversation memory ───────────────────────────────────────
MEMORY_K        = 6

# ── Data ──────────────────────────────────────────────────────
DATA_PATH       = "./data/colleges.json"
