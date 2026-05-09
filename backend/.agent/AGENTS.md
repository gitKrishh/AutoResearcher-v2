# AGENTS.md — AutoResearcher Backend
> AI Operating Manual for the `backend/` service.
> Read this before writing or modifying any backend code.
> For project-wide rules, see root `/.agent/AGENTS.md`.

---

## 1. Service Purpose

The backend is the **core engine** of AutoResearcher.

It is responsible for:
- Exposing a REST API consumed by the React frontend
- Orchestrating all AI agents in sequence
- Processing PDFs and managing the FAISS vector store
- Making all LLM and embedding calls
- Handling all external API integrations (arXiv, Semantic Scholar)

The backend is **stateless per request** except for the FAISS index, which is persisted to disk.

---

## 2. Tech Stack (Backend Only)

| Concern              | Technology                                   |
|----------------------|----------------------------------------------|
| Framework            | FastAPI                                       |
| Runtime              | Python 3.11+                                 |
| ASGI Server          | Uvicorn                                      |
| LLM                  | OpenAI API (`gpt-4o` default, `gpt-4o-mini` for light tasks) |
| Agent Framework      | LangChain (use existing chains/tools first)  |
| Embeddings           | SentenceTransformers `all-MiniLM-L6-v2`      |
| Vector Store         | FAISS (local, persisted to `vector_store/`)  |
| PDF Parsing          | PyMuPDF (`fitz`) — primary                   |
| HTTP Client          | `httpx` (async)                              |
| Validation           | Pydantic v2                                  |
| Settings             | `pydantic-settings`                          |
| Testing              | `pytest` + `pytest-asyncio` + `httpx`        |
| Linting/Formatting   | Ruff + Black + mypy                          |

---

## 3. Folder Structure

```
backend/
│
├── .agent/                          ← YOU ARE HERE
│   ├── AGENTS.md
│   ├── CONTEXT.md
│   └── CODING_CONVENTIONS.md
│
├── app/
│   ├── main.py                      ← FastAPI app init, middleware, router registration
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                  ← shared FastAPI dependencies (DI)
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── search.py            ← POST /api/search
│   │       ├── research.py          ← POST /api/research (full pipeline)
│   │       ├── papers.py            ← GET  /api/papers/{id}
│   │       └── health.py            ← GET  /api/health
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner_agent.py
│   │   ├── search_agent.py
│   │   ├── pdf_agent.py
│   │   ├── embedding_agent.py
│   │   ├── retrieval_agent.py
│   │   ├── analysis_agent.py
│   │   ├── insight_agent.py
│   │   └── writer_agent.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                ← pydantic-settings Settings class
│   │   ├── exceptions.py            ← all custom exception types
│   │   ├── schemas.py               ← shared Pydantic request/response models
│   │   ├── prompts.py               ← all LLM prompt templates (from PROMPTS.md)
│   │   └── logging.py               ← logging configuration
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py           ← all LLM calls go through here
│   │   ├── vector_store_service.py  ← FAISS index management
│   │   └── orchestrator_service.py  ← wires agents together
│   │
│   └── tools/
│       ├── __init__.py
│       ├── search_tool.py           ← arXiv / Semantic Scholar fetch
│       ├── pdf_tool.py              ← download + extract PDF text
│       ├── chunking_tool.py         ← text splitting
│       └── embedding_tool.py        ← generate embeddings
│
├── tests/
│   ├── conftest.py
│   ├── agents/
│   │   ├── test_planner_agent.py
│   │   ├── test_search_agent.py
│   │   └── ...
│   ├── api/
│   │   ├── test_search_routes.py
│   │   └── test_research_routes.py
│   └── tools/
│       ├── test_search_tool.py
│       ├── test_pdf_tool.py
│       └── test_embedding_tool.py
│
├── vector_store/                    ← FAISS index files (gitignored)
├── data/
│   └── pdfs/                        ← downloaded PDFs (gitignored)
│
├── requirements.txt
├── requirements-dev.txt
└── Dockerfile
```

---

## 4. Layer Responsibilities

### `api/routers/`
- **Only** handle HTTP request/response
- Validate input with Pydantic schemas
- Call one service function
- Return structured response
- No business logic — ever

### `services/`
- Contain all business logic
- Orchestrate agents and tools
- Manage state (FAISS index, session context)
- Called by routers and other services

### `agents/`
- Each agent has a single well-defined job
- Agents call tools and services — never other agents directly
- Every agent is a class with a `run()` method
- No raw API calls inside agent files

### `tools/`
- Pure utility functions (or near-pure)
- No LLM calls inside tools
- Reusable across multiple agents
- Should be independently testable

### `core/`
- Configuration, constants, exceptions, schemas
- No logic — only definitions
- The entire app depends on `core/`, nothing in `core/` depends on the app

---

## 5. Agent Definitions (Backend Scope)

### PlannerAgent
- **Input:** raw user query string
- **Output:** `list[str]` — 3–5 search sub-topics
- **LLM call:** yes (`PLANNER_DECOMPOSE_QUERY` prompt)
- **Tools used:** none

### SearchAgent
- **Input:** list of sub-topics, `max_results_per_topic: int`
- **Output:** `list[Paper]`
- **LLM call:** optional (for relevance filtering)
- **Tools used:** `search_tool.search_arxiv()`

### PDFAgent
- **Input:** `list[Paper]` (with PDF URLs)
- **Output:** `list[ProcessedPaper]` (with extracted text)
- **LLM call:** no
- **Tools used:** `pdf_tool.download_pdf()`, `pdf_tool.extract_text()`

### EmbeddingAgent
- **Input:** `list[ProcessedPaper]`
- **Output:** stored in FAISS (side effect), returns `list[str]` chunk IDs
- **LLM call:** no (embedding model only)
- **Tools used:** `chunking_tool.chunk_text()`, `embedding_tool.create_embeddings()`
- **Service used:** `vector_store_service.add_chunks()`

### RetrievalAgent
- **Input:** query string, `top_k: int`
- **Output:** `list[Chunk]` — relevant text chunks with metadata
- **LLM call:** no (embedding only)
- **Tools used:** `embedding_tool.embed_query()`
- **Service used:** `vector_store_service.search()`

### AnalysisAgent
- **Input:** `list[ProcessedPaper]`
- **Output:** `list[PaperAnalysis]`
- **LLM call:** yes (`ANALYSIS_SUMMARIZE_PAPER`, `ANALYSIS_COMPARE_PAPERS`)
- **Tools used:** none

### InsightAgent
- **Input:** `list[PaperAnalysis]`, original topic
- **Output:** `InsightReport`
- **LLM call:** yes (`INSIGHT_FIND_GAPS`)
- **Tools used:** none

### WriterAgent
- **Input:** `list[PaperAnalysis]`, `InsightReport`, original topic
- **Output:** `FinalReport` (markdown string + structured metadata)
- **LLM call:** yes (`WRITER_LITERATURE_REVIEW`)
- **Tools used:** none

---

## 6. API Routes Reference

| Method | Path                  | Handler                         | Description                    |
|--------|-----------------------|---------------------------------|--------------------------------|
| GET    | `/api/health`         | `health.health_check`           | Service health check           |
| POST   | `/api/search`         | `search.search_papers`          | Search papers only (no RAG)    |
| POST   | `/api/research`       | `research.run_research`         | Full autonomous pipeline       |
| GET    | `/api/papers/{id}`    | `papers.get_paper`              | Get a single processed paper   |

All routes are prefixed with `/api`. CORS is enabled for `localhost:5173` in development.

---

## 7. Pydantic Schemas (Key Models)

```python
# Defined in core/schemas.py

class SearchRequest(BaseModel):
    query: str
    max_results: int = 10

class Paper(BaseModel):
    id: str
    title: str
    abstract: str
    authors: list[str]
    pdf_url: str
    published: str
    source: str  # "arxiv" | "semantic_scholar"

class ResearchRequest(BaseModel):
    topic: str
    max_papers: int = 10
    include_insights: bool = True

class FinalReport(BaseModel):
    topic: str
    paper_count: int
    papers: list[PaperAnalysis]
    literature_review: str
    insights: InsightReport | None
    generated_at: str

class APIResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: APIError | None = None
```

---

## 8. LLM Service Rules

All LLM calls must go through `services/llm_service.py`. Never call OpenAI directly from agents.

```python
# services/llm_service.py
class LLMService:
    async def complete(self, prompt: str, model: str = "gpt-4o-mini") -> str: ...
    async def complete_json(self, prompt: str, model: str = "gpt-4o-mini") -> dict: ...
```

- Use `gpt-4o-mini` for: planning, filtering, short summaries
- Use `gpt-4o` for: full paper analysis, literature review writing
- Always set `temperature=0` for JSON-output tasks
- Always validate JSON responses before returning — catch `json.JSONDecodeError`

---

## 9. FAISS Index Management

- Index lives at `vector_store/index.faiss` and `vector_store/metadata.json`
- Load index on app startup (`lifespan` event in `main.py`)
- Save index after every `add_chunks()` call
- Metadata JSON maps chunk IDs to paper metadata (title, authors, page)
- Index dimension: `384` (for `all-MiniLM-L6-v2`)
- Use `faiss.IndexFlatIP` (inner product) with normalized embeddings

---

## 10. Error Handling Rules

Define all exceptions in `core/exceptions.py`:

```python
class AutoResearcherError(Exception): ...      # base
class SearchError(AutoResearcherError): ...
class PDFDownloadError(AutoResearcherError): ...
class PDFParseError(AutoResearcherError): ...
class EmbeddingError(AutoResearcherError): ...
class RetrievalError(AutoResearcherError): ...
class LLMError(AutoResearcherError): ...
class VectorStoreError(AutoResearcherError): ...
```

FastAPI exception handlers in `main.py` catch these and return structured responses.
Never let internal exceptions propagate as 500s with stack traces to the frontend.

---

## 11. What NOT To Do (Backend)

- ❌ Never put logic inside route handlers — only in services
- ❌ Never call `openai` directly inside agent files
- ❌ Never hardcode model names in agents — use `core/config.py`
- ❌ Never store PDFs or FAISS index in Git
- ❌ Never skip `await` on async functions
- ❌ Never use `requests` — use `httpx` (async)
- ❌ Never return Python exceptions directly as API responses
- ❌ Never skip type hints on any function signature

---

## 12. Testing Requirements

- `tests/conftest.py` must have fixtures for: mock LLM responses, mock arXiv API, sample PDF path, initialized FAISS index
- Every agent: minimum 2 tests (happy path + failure handling)
- Every route: minimum 2 tests (valid request + invalid input)
- Every tool function: minimum 1 test
- Run with: `pytest backend/tests/ -v`
- All tests must pass before updating `CONTEXT.md` to mark a phase complete
