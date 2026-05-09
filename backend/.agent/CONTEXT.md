# CONTEXT.md — AutoResearcher Backend
> Live memory and logbook for the `backend/` service.
> Update after every meaningful backend change.
> For project-wide progress, also update root `/.agent/CONTEXT.md`.

---

## Service Status

**Phase:** Pre-development
**Last Updated:** <!-- fill in each session -->
**Python Version:** 3.11+
**FastAPI Version:** 0.111+

---

## Environment Setup Status

```
[ ] Python virtual environment created (`python -m venv .venv`)
[ ] requirements.txt installed
[ ] requirements-dev.txt installed
[ ] .env file configured with all required keys
[ ] Backend starts with `uvicorn app.main:app --reload`
[ ] /api/health returns 200
[ ] Swagger UI accessible at /docs
```

---

## Current Progress

### Phase 1 — Project Skeleton
```
[ ] app/main.py created with FastAPI init + CORS + lifespan
[ ] app/core/config.py with pydantic-settings
[ ] app/core/exceptions.py with all custom exception types
[ ] app/core/schemas.py with base Pydantic models
[ ] app/core/logging.py configured
[ ] app/core/prompts.py with all prompt templates
[ ] app/api/deps.py with shared DI functions
[ ] GET /api/health route working
[ ] Dockerfile written
```

### Phase 2 — Search Tool + Agent
```
[ ] tools/search_tool.py — search_arxiv() implemented
[ ] arXiv XML response parsed into Paper schema
[ ] Rate limiting handled (3 req/sec max)
[ ] agents/search_agent.py — SearchAgent class
[ ] POST /api/search route working
[ ] Unit tests passing for search_tool
[ ] Integration test passing for /api/search
```

### Phase 3 — PDF Processing
```
[ ] tools/pdf_tool.py — download_pdf() implemented
[ ] tools/pdf_tool.py — extract_text_from_pdf() implemented
[ ] Text cleaning (remove headers/footers/noise)
[ ] Corrupt/empty PDF handling
[ ] agents/pdf_agent.py — PDFAgent class
[ ] Unit tests passing for pdf_tool
[ ] Tested with 3 real arXiv PDFs
```

### Phase 4 — Chunking + Embedding + FAISS
```
[ ] tools/chunking_tool.py — chunk_text() implemented
[ ] tools/embedding_tool.py — create_embeddings() implemented
[ ] SentenceTransformers model loaded and tested
[ ] services/vector_store_service.py — FAISS index created
[ ] add_chunks() working with metadata storage
[ ] search() returning top-k chunks correctly
[ ] Index save/load working (vector_store/)
[ ] agents/embedding_agent.py — EmbeddingAgent class
[ ] Integration test: PDF → chunks → embed → FAISS → retrieve
```

### Phase 5 — RAG Retrieval
```
[ ] agents/retrieval_agent.py — RetrievalAgent class
[ ] Query embedding + similarity search working
[ ] Context formatting for LLM prompt
[ ] End-to-end RAG: question → retrieve → answer
[ ] POST /api/research basic version working
[ ] Integration test passing
```

### Phase 6 — Analysis + Writer Agents
```
[ ] agents/analysis_agent.py — AnalysisAgent class
[ ] Paper summarization working (LLM call)
[ ] Paper comparison working (multi-paper LLM call)
[ ] agents/writer_agent.py — WriterAgent class
[ ] Literature review generation working
[ ] FinalReport schema fully populated
[ ] POST /api/research full pipeline working
```

### Phase 7 — Multi-Agent Orchestration
```
[ ] agents/planner_agent.py — PlannerAgent class
[ ] agents/insight_agent.py — InsightAgent class
[ ] services/orchestrator_service.py — full pipeline wired
[ ] Partial failure handling (one PDF fails, pipeline continues)
[ ] End-to-end test with real topic
```

---

## Decisions Taken

| Date | Decision | Reason |
|------|----------|--------|
| — | Use `httpx` (async) not `requests` | Backend is fully async; requests is sync-only |
| — | Use `faiss.IndexFlatIP` with normalized vectors | Best cosine similarity without extra infra |
| — | LangChain for agent framework internals | Avoid re-implementing chains and memory |
| — | `gpt-4o-mini` for light tasks, `gpt-4o` for heavy | Cost optimization without quality loss |
| — | Load FAISS index at startup via `lifespan` | Avoid re-loading on every request |
| — | PyMuPDF over pdfplumber as primary | ~10x faster on large PDFs |

---

## Known Bugs / Issues

| ID   | Description | Status | File | Notes |
|------|-------------|--------|------|-------|
| —    | —           | —      | —    | —     |

---

## Implementation Notes

> Add technical notes here as you discover them during development.

### arXiv API
- Base URL: `http://export.arxiv.org/api/query`
- Parameters: `search_query`, `max_results`, `start`
- Returns Atom XML — parse with `feedparser` or `xml.etree`
- No API key required; rate limit ~3 req/sec
- PDF URL format: `https://arxiv.org/pdf/{arxiv_id}.pdf`

### FAISS
- Dimension must match embedding model output: `384` for `all-MiniLM-L6-v2`
- Normalize vectors before `IndexFlatIP` for cosine similarity: `faiss.normalize_L2(vectors)`
- Metadata not stored in FAISS — maintain a parallel `metadata.json` keyed by chunk index
- Rebuild index from scratch if paper set changes significantly

### SentenceTransformers
- First load downloads model (~90MB) — cache in `.cache/` or Docker layer
- Batch embed for performance: `model.encode(chunks, batch_size=32)`
- Output is numpy array — convert to `float32` before FAISS insert

### LangChain Usage
- Use `RecursiveCharacterTextSplitter` for chunking (already tested)
- Use `LLMChain` or `RunnableSequence` for agent prompt pipelines
- Do NOT use LangChain agents directly — manage orchestration in `orchestrator_service.py`

---

## Environment Variables Required

```env
# LLM
OPENAI_API_KEY=sk-...

# Academic APIs
SEMANTIC_SCHOLAR_API_KEY=         # optional, higher rate limits
OPENALEX_API_KEY=                  # optional

# App Config
ENVIRONMENT=development            # development | production
LOG_LEVEL=INFO
MAX_PAPERS_PER_SEARCH=10
CHUNK_SIZE=512
CHUNK_OVERLAP=64
FAISS_INDEX_PATH=vector_store/index
PDF_CACHE_DIR=data/pdfs
DEFAULT_LLM_MODEL=gpt-4o-mini
HEAVY_LLM_MODEL=gpt-4o
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Server
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173
```

---

## Performance Benchmarks

> Fill in as you measure during development.

| Operation | Input Size | Time | Notes |
|-----------|-----------|------|-------|
| arXiv search | 10 results | — | — |
| PDF download | avg ~2MB | — | — |
| PDF text extraction | 10 pages | — | — |
| Chunking | 10k tokens | — | — |
| Embedding (batch) | 50 chunks | — | — |
| FAISS search | 1000 vectors | — | — |
| LLM summarize | 1 paper | — | — |
| Full pipeline | 5 papers | — | — |

---

## Test Results

| Date | Suite | Passed | Failed | Notes |
|------|-------|--------|--------|-------|
| —    | —     | —      | —      | —     |

---

## Next Steps

1. Create `app/main.py` — FastAPI init with CORS, lifespan, router registration
2. Create `app/core/config.py` — Settings from `.env`
3. Create `app/core/exceptions.py` — All custom exception types
4. Create `app/tools/search_tool.py` — `search_arxiv()` function first
5. Test `search_arxiv()` in isolation with a real query before building the agent
