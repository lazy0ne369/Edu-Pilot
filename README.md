# 🎓 EduPilot AI
**Local Indian college admission counsellor powered by RAG + Ollama**

## Overview
EduPilot AI helps Indian engineering students find colleges
based on JEE rank, budget, state, branch, and category.
100% local — no API keys, no internet required after setup.

## Prerequisites
1. Python 3.10+
2. Ollama installed: https://ollama.com/download
3. Pull required models:
   ```
   ollama pull qwen2:0.5b
   ollama pull nomic-embed-text
   ```

## Installation
```bash
git clone <repo>  &&  cd college_compass

# Create a Python 3.13 virtual environment (required — ChromaDB is not yet Python 3.14 compatible)
python3.13 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python data/generate_data.py          # generates colleges.json
python -m agent.ingest                # embeds into ChromaDB (one-time)
```

## Running
```bash
source .venv/bin/activate             # activate venv (if not already active)
streamlit run app.py
# Open browser: http://localhost:8501
```

## Architecture
```
Streamlit (app.py)
  └─▶ LangGraph Agent (agent/graph.py)
        ├─▶ search_colleges  ──▶ ChromaDB (k=3 cosine)
        ├─▶ check_eligibility ─▶ ChromaDB (cutoff lookup)
        └─▶ get_deadlines    ──▶ ChromaDB (cycle data)
                                     └─▶ Ollama qwen2:0.5b
```

## Project Structure
```
college_compass/
├── app.py                   # Streamlit entrypoint
├── requirements.txt
├── data/
│   ├── generate_data.py     # generates colleges.json
│   └── colleges.json        # synthetic 50-college dataset
├── agent/
│   ├── config.py            # tunable constants
│   ├── prompts.py           # SYSTEM_PROMPT
│   ├── graph.py             # LangGraph StateGraph
│   ├── tools.py             # search_colleges, check_eligibility, get_deadlines
│   ├── retriever.py         # ChromaDB retriever factory
│   └── ingest.py            # data ingestion + ensure_ingested()
└── ui/
    ├── sidebar.py           # filter widgets
    ├── chat.py              # chat renderer + streaming
    └── cards.py             # college recommendation cards
```

## FAQ
```
Q: 'Connection refused :11434' → Make sure Ollama is running: ollama serve
Q: 'Collection not found'      → Run python -m agent.ingest first
Q: Slow responses              → qwen2:0.5b is CPU — 15-45s is normal
Q: Empty chat responses        → Lower SCORE_THRESHOLD in config.py (try 0.5)
Q: Duplicate colleges after re-ingest → ingest.py is idempotent — safe to re-run
```

## Sample Queries
- `Show me CSE colleges under ₹2L in Tamil Nadu`
- `Can I get NIT Trichy with JEE rank 45000 OBC?`
- `When does VIT Vellore application close?`
- `List IITs for AI/ML with JEE Advanced`
- `Cheapest government colleges in Maharashtra for Mech`
