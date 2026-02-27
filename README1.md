# 🎓 EduPilot AI

**A fully local Indian college admission counsellor — powered by RAG, LangGraph, ChromaDB, Ollama, and Streamlit.**

> 100% offline after setup. No API keys. No cloud. No subscription. Just your laptop.

---

## Table of Contents

1. [What Is This?](#1-what-is-this)
2. [How It Works — Big Picture](#2-how-it-works--big-picture)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Component Deep-Dive](#5-component-deep-dive)
   - 5.1 [Data Layer — `data/`](#51-data-layer--data)
   - 5.2 [Config — `agent/config.py`](#52-config--agentconfigpy)
   - 5.3 [System Prompt — `agent/prompts.py`](#53-system-prompt--agentpromptspy)
   - 5.4 [Ingest — `agent/ingest.py`](#54-ingest--agentingestpy)
   - 5.5 [Retriever — `agent/retriever.py`](#55-retriever--agentretrieverpy)
   - 5.6 [Tools — `agent/tools.py`](#56-tools--agenttoolspy)
   - 5.7 [Graph — `agent/graph.py`](#57-graph--agentgraphpy)
   - 5.8 [UI — `ui/`](#58-ui--ui)
   - 5.9 [Entry Point — `app.py`](#59-entry-point--apppy)
6. [The 10-Table RAG Schema](#6-the-10-table-rag-schema)
7. [Prerequisites](#7-prerequisites)
8. [Installation](#8-installation)
9. [Running the App](#9-running-the-app)
10. [The TODO Checklist — Step by Step](#10-the-todo-checklist--step-by-step)
11. [Example Queries & What Happens](#11-example-queries--what-happens)
12. [Configuration Reference](#12-configuration-reference)
13. [Architecture Diagram](#13-architecture-diagram)
14. [FAQ & Troubleshooting](#14-faq--troubleshooting)

---

## 1. What Is This?

EduPilot AI is a **Retrieval-Augmented Generation (RAG)** chatbot that acts as a personal Indian college admission counsellor. A student types natural language questions — their JEE rank, budget, preferred state, branch, category — and the agent searches a local vector database of 30 real-world colleges, retrieves the most relevant records, and generates a grounded, structured response via a local LLM.

**Target users:** Indian engineering students preparing for JEE / BITSAT / state entrance exams.

**What it can answer:**
- "What colleges can I get with JEE rank 45000, General, ₹2L budget in South India?"
- "Am I eligible for NIT Trichy CSE with OBC rank 12000?"
- "When is the VITEEE application deadline?"
- "Which college gives the best placements under ₹1.5L fees?"

**What makes it different from ChatGPT:**
- Answers are grounded in a structured local database — not hallucinated
- Every recommendation comes with real cutoff numbers, fees, and placement data
- Fully offline — your data never leaves your laptop

---

## 2. How It Works — Big Picture

Here is the end-to-end flow every time a student sends a message:

```
Student types query
        │
        ▼
[Streamlit chat_input]          ← app.py
        │
        ▼
[Sidebar filters appended]      ← exam, category, budget, state, branch
        │
        ▼
[LangGraph StateGraph]          ← agent/graph.py
        │
   ┌────▼────┐
   │  Agent  │  ← ChatOllama (qwen2:0.5b) + SYSTEM_PROMPT
   │  Node   │    decides: do I need a tool? which one?
   └────┬────┘
        │ tool_calls? YES
        ▼
   ┌─────────────┐
   │  ToolNode   │  picks ONE of 3 tools based on intent
   └──┬──┬──┬───┘
      │  │  │
      │  │  └─── get_deadlines      → ChromaDB (admission cycle dates)
      │  └─────── check_eligibility  → ChromaDB (cutoff lookup by rank)
      └────────── search_colleges    → ChromaDB (semantic college search)
                        │
                        ▼
                  [ChromaDB k=3]     ← cosine similarity, threshold=0.7
                        │
                        ▼
              [Top 3 college chunks]
                        │
                        ▼
   ┌────▼────┐
   │  Agent  │  ← LLM reads chunks + formats structured response
   │  Node   │
   └────┬────┘
        │ no more tool_calls
        ▼
[st.write_stream()]              ← tokens stream live to browser
        │
        ▼
  Chat bubble rendered           ← ui/chat.py
```

The agent loop can cycle multiple times if the LLM decides it needs more tool calls before it has enough information to respond.

---

## 3. Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Frontend | Streamlit | 1.37.1 | Chat UI, sidebar filters, streaming |
| Agent Framework | LangGraph | 0.2.14 | State machine, tool routing, memory |
| LLM Wrapper | LangChain + Ollama | 0.2.16 / 0.1.3 | Bind tools, invoke LLM |
| Local LLM | Ollama qwen2:0.5b | latest | Inference, token generation |
| Embedder | nomic-embed-text via Ollama | latest | Embed college docs + queries |
| Vector Store | ChromaDB | 0.5.5 | Cosine similarity search, metadata filters |
| Memory | LangGraph MemorySaver | built-in | Per-session conversation history |
| Data | JSON + Python | — | Synthetic 30-college dataset |
| Config | python-dotenv | 1.0.1 | Override defaults via .env |

**Why these choices:**
- **qwen2:0.5b** — smallest Ollama model that still understands tool calling; runs on CPU in 15–45s
- **nomic-embed-text** — high quality, free, runs locally, great for semantic search
- **ChromaDB** — zero-config local vector DB, persists to disk, supports metadata filters
- **LangGraph** — replaces the deprecated `ConversationChain`; explicit state + tool routing
- **Streamlit** — single-file Python UI, no React, no Node.js needed

---

## 4. Project Structure

```
college_compass/
│
├── app.py                  ← ONLY file you run: streamlit run app.py
├── requirements.txt        ← All pinned exact versions
├── .env.example            ← Copy to .env to override any config
├── README.md               ← This file
│
├── data/
│   ├── generate_data.py    ← Run once: creates colleges.json (30 records)
│   └── colleges.json       ← Output: synthetic college dataset (auto-generated)
│
├── agent/                  ← All backend/AI logic lives here
│   ├── __init__.py
│   ├── config.py           ← Single source of truth for ALL constants
│   ├── prompts.py          ← SYSTEM_PROMPT (the agent's personality + rules)
│   ├── ingest.py           ← JSON → embeddings → ChromaDB (run once, idempotent)
│   ├── retriever.py        ← ChromaDB retriever with metadata filter support
│   ├── tools.py            ← 3 LangGraph @tool functions the agent can call
│   └── graph.py            ← LangGraph StateGraph definition + GRAPH singleton
│
└── ui/                     ← All Streamlit UI components
    ├── __init__.py
    ├── sidebar.py          ← Filter widgets (exam, category, budget, state, branch)
    ├── chat.py             ← Chat bubble renderer + streaming
    └── cards.py            ← College recommendation card renderer
```

**Key rule:** `app.py` contains **zero business logic**. It only imports and wires together modules from `agent/` and `ui/`. All logic lives in those modules.

---

## 5. Component Deep-Dive

### 5.1 Data Layer — `data/`

#### `data/generate_data.py`

This script generates the synthetic college dataset. It models the full **10-table schema** (see Section 6) and outputs a single denormalised `colleges.json` — a list of 30 rich college objects, each containing all relevant fields from all 10 tables.

**College mix:**
- 7 IITs (IIT Madras, Delhi, Bombay, Kharagpur, Roorkee, Hyderabad, Guwahati)
- 8 NITs (Trichy, Surathkal, Warangal, Calicut, Rourkela, Jaipur, Durgapur, Silchar)
- 3 BITS campuses (Pilani, Goa, Hyderabad)
- 12 private/deemed universities (VIT, SRM, Manipal, Amrita, etc.)

**For each college, the script generates:**
- Basic info: name, state, NIRF rank, tuition fee, average/highest placement
- Accepted entrance exams and whether JEE is accepted
- Scholarship slabs by rank range (private colleges: min 3 slabs)
- Programs offered (CSE, ECE, Mech, Civil, IT, AI/ML, EEE) with seat counts
- Cutoff data per program × exam × quota × category (2024 data)
- Admission cycle status (Open / Closed / Upcoming) with dates
- Website URL (synthetic: `https://[shortname].ac.in`)

**Sample IIT cutoff ranges (General, All India, CSE):**
- IITs: closing rank 100–2000
- NITs: closing rank 8,000–35,000
- Private (own exam score): varies by institution

**Run it:**
```bash
python data/generate_data.py
# Output: data/colleges.json
# Verify: python -c "import json; print(len(json.load(open('data/colleges.json'))))"
# Should print: 30
```

#### `data/colleges.json`

Auto-generated. Each record looks like this (abbreviated):

```json
{
  "id": 8,
  "name": "NIT Trichy",
  "state": "Tamil Nadu",
  "type": "NIT",
  "nirf_rank": 9,
  "tuition_fee": 170000,
  "avg_package": 14,
  "highest_package": 45,
  "accepts_jee": true,
  "exams": ["JEE Main"],
  "programs": ["CSE", "ECE", "Mech", "Civil", "EEE"],
  "cutoffs": {
    "CSE": {
      "General": {"All_India": 8500, "Home_State": 12000},
      "OBC":     {"All_India": 11900},
      "SC":      {"All_India": 21250}
    }
  },
  "scholarships": [],
  "admission_status": "Open",
  "application_deadline": "2025-03-01",
  "website": "https://nitt.ac.in"
}
```

---

### 5.2 Config — `agent/config.py`

**Single source of truth for every magic number and path in the project.** Nothing is hardcoded anywhere else.

```python
OLLAMA_BASE_URL  = "http://localhost:11434"   # Where Ollama is running
LLM_MODEL        = "qwen2:0.5b"               # Local LLM for generation
EMBED_MODEL      = "nomic-embed-text"         # Local model for embeddings
CHROMA_DIR       = Path(...) / "chroma_db"    # Where vector DB is persisted
COLLECTION       = "college_compass"          # ChromaDB collection name
RETRIEVAL_K      = 3                          # Return top-3 matches
SCORE_THRESHOLD  = 0.7                        # Min cosine similarity to include
LLM_TEMPERATURE  = 0.3                        # Low = more factual, less creative
MEMORY_K         = 10                         # Keep last 10 turns in context
CHUNK_SIZE       = 600                        # Characters per text chunk
CHUNK_OVERLAP    = 80                         # Overlap between chunks
```

All values can be overridden by creating a `.env` file (copy from `.env.example`). The config uses `python-dotenv` to load it automatically.

**Uses `pathlib.Path` throughout** — no hardcoded Windows `C:\` paths or Unix `/home/` paths. Works on Windows, Mac, and Linux.

---

### 5.3 System Prompt — `agent/prompts.py`

The `SYSTEM_PROMPT` constant defines the agent's **identity, rules, and output format**. It is prepended to every LLM call so the model always knows its role.

**Key rules enforced by the prompt:**
1. Answer ONLY from retrieved context — if context is empty, say so honestly
2. Always give concrete numbers (fees in ₹, packages in LPA, ranks)
3. Format every college recommendation consistently with emoji headers
4. Mention the student's category and quota in reasoning
5. Never mention other AI products by name
6. Ask for missing info (rank/budget/category) before recommending
7. Always end recommendations with a 2024 data disclaimer

**Why this matters:** Without the system prompt, `qwen2:0.5b` would hallucinate college data. The prompt grounds it — "answer only from the context below" — making it a RAG agent rather than a free-form chatbot.

---

### 5.4 Ingest — `agent/ingest.py`

This is the **one-time setup script** that converts `colleges.json` into vector embeddings stored in ChromaDB.

**What it does, step by step:**

1. **Load JSON** — reads all 30 college records from `data/colleges.json`
2. **rich_text_summary()** — converts each college dict into a natural language paragraph:
   ```
   "NIT Trichy is a NIT college in Tamil Nadu, ranked 9 by NIRF.
   Annual tuition is ₹1,70,000. Accepts JEE Main. CSE cutoff (General,
   All India): 8500. Average placement: 14 LPA, highest: 45 LPA.
   Scholarships: none (government fee waivers apply). Status: Open."
   ```
3. **Chunk** — splits each summary into chunks of 600 chars with 80-char overlap (using LangChain's `RecursiveCharacterTextSplitter`)
4. **Embed** — sends each chunk to `OllamaEmbeddings(nomic-embed-text)` running locally
5. **Persist** — stores vectors + metadata in ChromaDB collection `"college_compass"`

**Metadata stored per chunk** (used for filters):
```python
{
  "state":       "Tamil Nadu",
  "exam_list":   "JEE Main",
  "fee_range":   "100000-200000",
  "nirf_rank":   9,
  "branch_list": "CSE,ECE,Mech,Civil,EEE",
  "name":        "NIT Trichy",
  "type":        "NIT",
  "status":      "Open",
  "tuition_fee": 170000,
  "avg_package": 14
}
```

**Idempotency:** Before ingesting, the script checks if the collection already has 30+ documents. If yes, it prints `"Already ingested. Skipping."` and exits. Safe to run multiple times.

```bash
python -m agent.ingest
# First run: "✓ Ingested 30 colleges (N chunks) into 'college_compass'"
# Second run: "✓ Already ingested (N docs). Skipping."
```

---

### 5.5 Retriever — `agent/retriever.py`

`get_retriever()` returns a configured LangChain retriever backed by ChromaDB.

**Signature:**
```python
def get_retriever(
    state: str = None,
    exam: str = None,
    budget_max: int = None,
    branch: str = None,
) -> VectorStoreRetriever:
```

**How metadata filtering works:**

When sidebar filters are set, the retriever adds ChromaDB `$where` clauses so only matching colleges are even considered for similarity search:

```python
# Example: student sets state=Tamil Nadu, budget=200000
where = {
  "$and": [
    {"state":       {"$eq": "Tamil Nadu"}},
    {"tuition_fee": {"$lte": 200000}}
  ]
}
```

Filters are only applied when the parameter is not `None`. If no filters are set, all 30 colleges are searched.

**Retrieval settings:**
- `k=3` — return top 3 most similar chunks
- `score_threshold=0.7` — ignore chunks below 70% cosine similarity
- Distance metric: cosine (set at collection creation time)

---

### 5.6 Tools — `agent/tools.py`

The agent has **3 tools** it can call. LangGraph reads each tool's docstring to decide which one to invoke based on the student's query intent.

#### Tool 1: `search_colleges`

```python
@tool
def search_colleges(query, state, exam, budget_max, branch) -> str:
```

**When the agent calls this:** General college recommendations, finding options, fee/placement comparisons.

**What it does:** Passes all sidebar filters to `get_retriever()`, invokes with the query, formats the top-3 results with college name, state, type, NIRF rank, fees, placement, and admission status.

**Example trigger query:** *"Best CSE colleges in South India under ₹2L fees"*

---

#### Tool 2: `check_eligibility`

```python
@tool
def check_eligibility(rank, exam, category, quota, branch) -> str:
```

**When the agent calls this:** Any rank-based eligibility question, cutoff comparison, "Can I get into X?" queries.

**What it does:**
1. Constructs a semantic query: `"JEE Main General All_India closing rank 45000 cutoff eligibility CSE"`
2. Retrieves top-3 colleges with matching exam/branch
3. Extracts closing rank from the chunk text using regex
4. Compares student's rank against cutoff:
   - 🟢 **DREAM** — rank ≤ cutoff × 0.7 (comfortably within)
   - 🟡 **SAFE** — rank ≤ cutoff (within cutoff)
   - 🟠 **BORDERLINE** — rank ≤ cutoff × 1.15 (slightly above)
   - 🔴 **UNLIKELY** — rank > cutoff × 1.15

**Example trigger query:** *"Can I get NIT Trichy CSE with OBC rank 12000?"*

---

#### Tool 3: `get_deadlines`

```python
@tool
def get_deadlines(college_name, exam) -> str:
```

**When the agent calls this:** Any question about dates, deadlines, application status, open/closed status.

**What it does:** Queries ChromaDB for admission cycle information — `application_deadline`, `exam_date`, `counselling_date`, and `status` (Open/Closed/Upcoming).

**Example trigger query:** *"When is the VITEEE application deadline?"*

---

### 5.7 Graph — `agent/graph.py`

This is the brain of the application — a **LangGraph StateGraph** that defines the agent loop.

#### State Schema

```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

`add_messages` is a LangGraph reducer — it appends new messages to the list rather than replacing it, giving the agent full conversation history.

#### Nodes

**`call_model` node:**
- Takes the current message history
- Truncates to last `MEMORY_K * 2` messages to bound context window
- Prepends `SYSTEM_PROMPT` as a `SystemMessage`
- Calls `ChatOllama` with tools bound
- Returns the LLM response (may contain `tool_calls`)

**`tools` node (ToolNode):**
- A prebuilt LangGraph node that executes whichever tool the LLM requested
- Passes tool results back as `ToolMessage` objects
- The agent then gets another turn to read the results and respond

#### Routing

```python
def should_continue(state) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"    # LLM wants to call a tool → go to ToolNode
    return END            # LLM is done → return response to user
```

#### Graph Edges

```
[entry] → agent → should_continue → tools → agent → should_continue → END
```

The loop repeats until `should_continue` returns `END` (no more tool calls).

#### Memory

```python
memory = MemorySaver()
graph.compile(checkpointer=memory)
```

`MemorySaver` stores the full conversation state keyed by `thread_id`. In `app.py`, the `thread_id` is `st.session_state.session_id` — a UUID generated once per browser session. This gives each student their own isolated conversation memory that persists across Streamlit reruns.

#### Singleton

```python
GRAPH = build_graph()
```

`GRAPH` is compiled **once at import time** and shared across all Streamlit interactions. This avoids rebuilding the graph on every user message.

---

### 5.8 UI — `ui/`

#### `ui/sidebar.py` — `render_sidebar()`

Renders the left sidebar with filter widgets and returns a dict:

```python
{
  "exam":       "JEE Main",       # st.selectbox
  "category":   "OBC",            # st.selectbox
  "quota":      "All_India",       # st.selectbox
  "state":      "Tamil Nadu",     # st.selectbox
  "branch":     "CSE",            # st.selectbox
  "budget_max": 200000            # st.slider (₹50k–₹10L, step ₹50k)
}
```

These filters are stored in `st.session_state.filters` and appended to every query as a `[Student profile: ...]` context block before sending to the agent.

#### `ui/chat.py` — `render_chat()` and `render_stream()`

**`render_chat(messages)`** — Replays the full conversation history as chat bubbles. Each message is rendered with `st.chat_message()` using appropriate avatars (👤 for user, 🎓 for assistant).

**`render_stream(graph, input_msg, config)`** — Streams the agent's response token by token:
1. Calls `GRAPH.stream(input_msg, config, stream_mode="messages")`
2. Filters for `AIMessageChunk` tokens
3. Uses `st.write_stream()` to display tokens live as they arrive
4. Returns the full assembled response string for history storage

This is why you see the response appearing word-by-word rather than all at once.

#### `ui/cards.py` — `render_card()`

Renders a structured college recommendation card using Streamlit columns and metric widgets:

```
┌──────────────────────────────────────────────────────┐
│  🎓 NIT Trichy  •  Tamil Nadu  •  NIT  •  NIRF #9   │
│  ┌──────────┬──────────────┬─────────────────────┐   │
│  │ ₹1,70,000│   14 LPA    │  45 LPA             │   │
│  │  /year   │  avg pkg    │  highest pkg         │   │
│  └──────────┴──────────────┴─────────────────────┘   │
│  Status: Open  •  Admission: LIKELY                   │
└──────────────────────────────────────────────────────┘
```

---

### 5.9 Entry Point — `app.py`

`app.py` is the **only file Streamlit runs directly**. It contains zero business logic — it only wires modules together.

**What it does on startup:**
1. `st.set_page_config()` — must be the very first Streamlit call
2. `@st.cache_resource` wraps `ensure_ingested()` — runs once per server session, not once per user interaction
3. `init_session()` — creates `session_id`, `messages`, and `filters` in `st.session_state` if they don't exist

**On each user message:**
1. Appends sidebar filter context to the query
2. Displays the user's original message (without injected context)
3. Calls `render_stream(GRAPH, input_msg, config)` to get streaming response
4. Appends response to `st.session_state.messages`
5. Calls `st.rerun()` to refresh the UI

**Why `st.rerun()`?** Streamlit re-executes the entire script top-to-bottom on every interaction. Calling `st.rerun()` after appending the assistant message ensures the new message is immediately visible in the chat history on the next render cycle.

---

## 6. The 10-Table RAG Schema

The data model covers every aspect of Indian college admissions. All 10 tables are denormalised into each college's JSON record for efficient RAG retrieval.

| Table | Fields | Purpose |
|---|---|---|
| **1. Colleges** | id, name, state, nirf_rank, tuition_fee, avg_package, highest_package | Core college identity |
| **2. Entrance Exams** | exam_id, exam_name, conducted_by, mode, application_deadline | JEE/BITSAT/VITEEE etc. |
| **3. College_Exam_Map** | college_id, exam_id, accepts_jee, scholarship_based_on_exam | Which college accepts which exam |
| **4. Scholarship_Slabs** | college_id, rank_range, scholarship_percent | Fee waivers by rank (private colleges) |
| **5. Quota_Types** | quota_id, quota_name | All_India / Home_State / Management / Minority / NRI |
| **6. Reservations** | category_name, percentage, applicable_exam | OBC 27%, EWS 10%, SC 15%, ST 7.5%, PwD 5% |
| **7. Programs** | program_id, college_id, branch_name, seats_total | CSE/ECE/Mech/Civil/IT/AI-ML/EEE |
| **8. Cutoffs** | program_id, exam_id, quota_type, category, closing_rank, year | 2024 closing ranks by category |
| **9. Admission_Cycles** | college_id, application_open/deadline, exam_date, counselling_date, status | Live cycle data |
| **10. College_Metadata** | college_id, website_url | Official website |

**Embedding strategy:** Each college is converted to a single natural language paragraph summarising all 10 tables, then chunked and embedded. This means a query like *"Tamil Nadu NIT with good placements under 2L"* semantically matches the right college even without exact keyword matches.

---

## 7. Prerequisites

Before installing the project, make sure these are in place:

### Python 3.10+
```bash
python --version
# Must show 3.10.x or higher
```

### Ollama
Download and install from https://ollama.com/download (Windows / Mac / Linux installers available).

### Pull Required Models (one-time, needs internet)
```bash
ollama pull qwen2:0.5b        # ~350MB — the LLM for generation
ollama pull nomic-embed-text  # ~270MB — the embedding model
```

### Start Ollama
```bash
ollama serve
# Keep this running in a separate terminal while using the app
```

Verify it's running: open http://localhost:11434 — you should see `Ollama is running`.

```bash
# Verify both models are available
ollama list
# Should show both qwen2:0.5b and nomic-embed-text
```

---

## 8. Installation

```bash
# 1. Navigate into the project folder
cd college_compass

# 2. (Recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# or
source venv/bin/activate       # Mac / Linux

# 3. Install all dependencies (exact pinned versions)
pip install -r requirements.txt

# 4. Generate the synthetic college dataset
python data/generate_data.py
# Output: data/colleges.json (30 colleges)

# 5. Embed the data into ChromaDB (one-time, takes 2–5 minutes)
python -m agent.ingest
# Output: chroma_db/ folder created with vector embeddings
# You should see: ✓ Ingested 30 colleges into 'college_compass'
```

**Optional — override config:**
```bash
# Copy the example env file
copy .env.example .env         # Windows
# or
cp .env.example .env           # Mac / Linux

# Edit .env to change any defaults (model, paths, thresholds)
```

---

## 9. Running the App

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

The app will:
1. Check if data is already ingested (no-op if `chroma_db/` exists with 30+ docs)
2. Render the sidebar with filter widgets
3. Show a welcome screen with example queries
4. Accept your first chat message

**To stop the app:** Press `Ctrl+C` in the terminal.

---

## 10. The TODO Checklist — Step by Step

Execute these in order. Each step has a verifiable acceptance criterion — do not proceed to the next step until the current one passes.

| Step | Task | Acceptance Criterion |
|---|---|---|
| 01 | `pip install -r requirements.txt` | Completes with no errors |
| 02 | Start Ollama: `ollama serve` | `http://localhost:11434` shows "Ollama is running" |
| 03 | Pull models: `ollama pull qwen2:0.5b && ollama pull nomic-embed-text` | `ollama list` shows both |
| 04 | `python data/generate_data.py` | `colleges.json` has exactly 30 records |
| 05 | Check config: `python -c "from agent.config import RETRIEVAL_K, LLM_MODEL; print(RETRIEVAL_K, LLM_MODEL)"` | Prints `3 qwen2:0.5b` |
| 06 | `python -m agent.ingest` | Prints "Ingested 30 colleges"; `chroma_db/` folder exists |
| 07 | Test retriever: `python -c "from agent.retriever import get_retriever; docs = get_retriever().invoke('CSE South India'); print(len(docs))"` | Prints `3` |
| 08 | Test prompts: `python -c "from agent.prompts import SYSTEM_PROMPT; print(len(SYSTEM_PROMPT))"` | Prints a number > 500 |
| 09 | Test tools: `python -c "from agent.tools import search_colleges; print(search_colleges.invoke({'query': 'NIT CSE placements'})[:200])"` | Prints college info, no errors |
| 10 | Test graph: `python -c "from agent.graph import GRAPH; print(type(GRAPH).__name__)"` | Prints `CompiledStateGraph` |
| 11 | `streamlit run app.py` | Browser opens at :8501, sidebar + chat input visible |
| 12 | Type: *"My JEE rank is 45000 General, budget 2L, want CSE in South India"* | Response mentions 2–3 specific colleges with fees, packages, eligibility |
| 13 | Type: *"Can I get into NIT Trichy CSE with this rank?"* | Agent remembers rank from previous turn, gives a verdict |
| 14 | Type: *"When is the VITEEE application deadline?"* | Agent returns a date or Open/Closed/Upcoming status |

**Final sanity check — verify no deprecated or cloud imports:**
```bash
grep -r "openai\|anthropic\|fastapi\|ConversationChain\|langchain.llms" . --include="*.py"
# Must return zero output (0 matches)
```

---

## 11. Example Queries & What Happens

| Query | Agent Intent | Tools Called | Expected Response |
|---|---|---|---|
| "My JEE rank is 45000, category General, budget ₹2L, want CSE in South India" | College search + eligibility | `search_colleges` + `check_eligibility` | 3 NIT/private colleges with fees, packages, 🟡/🟠 eligibility |
| "Can I get into NIT Trichy with OBC rank 12000?" | Cutoff lookup | `check_eligibility` | Cutoff comparison → 🟡 SAFE or 🟠 BORDERLINE verdict |
| "When is the VITEEE application deadline?" | Deadline lookup | `get_deadlines` | Application deadline date + status |
| "Best placements under ₹1.5L fees" | Budget-filtered search | `search_colleges` (budget filter) | Top 3 colleges sorted by avg_package, all under ₹1.5L |
| "I'm EWS, home state Maharashtra, JEE rank 80000" | Home state quota + EWS | `search_colleges` + `check_eligibility` | Maharashtra colleges, Home State quota, EWS cutoff comparison |
| "Compare BITS Pilani vs NIT Trichy for ECE" | Parallel comparison | `search_colleges` (×2) | Side-by-side fees, cutoffs, placements, scholarships |

---

## 12. Configuration Reference

All values live in `agent/config.py` and can be overridden in `.env`:

| Variable | Default | What to change it to |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Change if Ollama runs on different port |
| `LLM_MODEL` | `qwen2:0.5b` | `qwen2:1.5b` or `llama3.2:1b` for better quality |
| `EMBED_MODEL` | `nomic-embed-text` | `mxbai-embed-large` for higher quality embeddings |
| `RETRIEVAL_K` | `3` | Increase to `5` for more context (slower) |
| `SCORE_THRESHOLD` | `0.7` | Lower to `0.5` if getting empty responses |
| `LLM_TEMPERATURE` | `0.3` | Raise to `0.7` for more varied/creative answers |
| `MEMORY_K` | `10` | Raise to keep more turns in context |
| `CHROMA_DIR` | `./chroma_db` | Absolute path if you want DB elsewhere |

---

## 13. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Streamlit :8501                              │
│                                                                     │
│   ┌─────────────┐    ┌──────────────────────────────────────────┐  │
│   │  ui/sidebar │    │              ui/chat.py                  │  │
│   │             │    │                                          │  │
│   │ exam        │    │  👤 Student: My JEE rank is 45000...     │  │
│   │ category    │    │                                          │  │
│   │ budget ₹    │    │  🎓 Agent: 🎓 NIT Trichy (NIRF #9)      │  │
│   │ state       │    │     • Tuition: ₹1,70,000/year           │  │
│   │ branch      │    │     • Avg Package: 14 LPA               │  │
│   │             │    │     • Eligibility: 🟡 SAFE — cutoff 8500│  │
│   └──────┬──────┘    └──────────────────────────────────────────┘  │
│          │ filters                          ▲                       │
└──────────┼──────────────────────────────────┼───────────────────────┘
           │                                  │ streamed tokens
           ▼                                  │
┌──────────────────────────────────────────────────────────────────────┐
│                    agent/graph.py — LangGraph                        │
│                                                                      │
│  ┌──────────────────────┐        ┌──────────────────────────────┐   │
│  │   call_model node    │        │        ToolNode               │   │
│  │                      │◄───────│                              │   │
│  │  SystemMessage +     │        │  search_colleges()           │   │
│  │  conversation history│────────►  check_eligibility()         │   │
│  │                      │        │  get_deadlines()             │   │
│  │  ChatOllama          │        └──────────┬───────────────────┘   │
│  │  qwen2:0.5b          │                   │                       │
│  └──────────────────────┘                   │                       │
│                                             │                       │
│            MemorySaver (keyed by session_id)│                       │
└─────────────────────────────────────────────┼───────────────────────┘
                                              │ retriever.invoke(query)
                                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    ChromaDB  ./chroma_db/                            │
│                                                                      │
│  Collection: "college_compass"                                       │
│  30 colleges × multiple chunks                                       │
│  Cosine similarity, k=3, threshold=0.7                               │
│                                                                      │
│  Metadata filters: state | exam | tuition_fee | branch_list          │
└───────────────────────────────────────┬──────────────────────────────┘
                                        │ embed query
                                        ▼
                              Ollama :11434
                         ┌────────────────────────┐
                         │  nomic-embed-text       │ ← embeddings
                         │  qwen2:0.5b             │ ← generation
                         └────────────────────────┘
```

---

## 14. FAQ & Troubleshooting

**Q: `Connection refused` at port 11434**
Ollama is not running. Open a new terminal and run:
```bash
ollama serve
```
Keep that terminal open while using the app.

---

**Q: `Collection 'college_compass' not found` or ChromaDB error**
You haven't ingested the data yet. Run:
```bash
python -m agent.ingest
```

---

**Q: Responses are slow (15–45 seconds)**
This is normal for `qwen2:0.5b` on CPU. If you have an NVIDIA or Apple Silicon GPU, Ollama uses it automatically — responses drop to 3–8 seconds. No configuration needed.

---

**Q: Empty or irrelevant responses / agent says "I don't have enough data"**
Two possible fixes:
1. Lower `SCORE_THRESHOLD` in `.env` (try `0.5`)
2. Re-run ingest if ChromaDB seems corrupted: `python -m agent.ingest`

---

**Q: `ModuleNotFoundError: No module named 'agent'`**
You're running commands from inside a subfolder. Always run from the project root:
```bash
cd college_compass          # ← must be here
python -m agent.ingest      # ← then run commands
streamlit run app.py
```

---

**Q: Duplicate data after re-running ingest**
`ingest.py` is idempotent — it checks if 30+ docs already exist before embedding. It is safe to run multiple times. If you want to force a fresh ingest, delete the `chroma_db/` folder first:
```bash
rmdir /s /q chroma_db       # Windows
# or
rm -rf chroma_db            # Mac / Linux
python -m agent.ingest
```

---

**Q: The agent doesn't remember my rank from the previous message**
Each browser tab gets its own `session_id`. If you opened a new tab or refreshed with `Clear` button, history resets. In the same session, memory persists for up to `MEMORY_K=10` turns.

---

**Q: How do I use a better / faster model?**
```bash
ollama pull llama3.2:1b     # Better quality, ~1GB
```
Then update `.env`:
```
LLM_MODEL=llama3.2:1b
```
Restart the Streamlit app.

---

**Q: Can I add more colleges?**
Yes. Edit `data/generate_data.py` to add more records, then:
```bash
python data/generate_data.py
rm -rf chroma_db
python -m agent.ingest
```
The agent will automatically use the new data.

---

*Built with LangGraph · ChromaDB · Ollama · Streamlit — 100% local, 100% free.*
