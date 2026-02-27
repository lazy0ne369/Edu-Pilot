"""
EduPilot — Configuration constants.
LLM:        Solar Pro 3 via OpenRouter (OpenAI-compatible API)
Embeddings: mxbai-embed-large via Ollama (local, stable)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Gemini / LLM ──────────────────────────────────────────────
LLM_API_KEY      = os.environ.get("GEMINI_API_KEY", "")
LLM_BASE_URL     = "https://generativelanguage.googleapis.com/v1beta/openai"

# Best performing Gemini models (gemini-flash-latest is recommended):
LLM_MODEL        = "gemini-flash-latest"
LLM_TEMPERATURE  = 0.3

# ── Embeddings (Ollama — local, stable) ───────────────────────
EMBED_MODEL     = "mxbai-embed-large"
OLLAMA_BASE_URL = "http://localhost:11434"

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
