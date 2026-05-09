# TASKS.md — AutoResearcher Root
> Master task list for the entire project.
> Check off items as they are completed. Keep this in sync with CONTEXT.md.

---

## How to Use This File

- `[ ]` = not started
- `[~]` = in progress
- `[x]` = completed
- Add new tasks as they emerge — do not delete completed ones

---

## Phase 0 — Project Setup

- [ ] Initialize Git repository
- [ ] Create full folder structure as defined in `AGENTS.md`
- [ ] Create `.env` and `.env.example`
- [ ] Set up `backend/` with FastAPI + uvicorn
- [ ] Set up `frontend/` with React + Vite + TypeScript
- [ ] Configure `docker-compose.yml` for backend + frontend
- [ ] Verify backend starts on `localhost:8000`
- [ ] Verify frontend starts on `localhost:5173`
- [ ] Write `README.md` with setup instructions

---

## Phase 1 — Paper Search (Day 1)

### arXiv Integration
- [ ] Implement `tools/search_tool.py` — `search_arxiv(query, max_results)`
- [ ] Parse arXiv XML response into `Paper` schema
- [ ] Add rate limiting / delay between requests
- [ ] Write unit tests for `search_arxiv`
- [ ] Test with query: "AI agents in software engineering"

### Semantic Scholar Integration (optional, post-MVP)
- [ ] Implement `search_semantic_scholar(query, max_results)`
- [ ] Handle API key from settings

### FastAPI Route
- [ ] Create `api/routers/search.py` — `POST /api/search`
- [ ] Validate request with Pydantic schema
- [ ] Return structured paper list response
- [ ] Test route via Swagger UI (`/docs`)

---

## Phase 2 — PDF Processing (Day 1)

- [ ] Implement `tools/pdf_tool.py` — `download_pdf(url, save_path)`
- [ ] Implement `extract_text_from_pdf(pdf_path)` using PyMuPDF
- [ ] Handle corrupt / empty PDFs gracefully
- [ ] Clean extracted text (remove headers, footers, reference noise)
- [ ] Write unit tests for PDF extraction
- [ ] Test with 3 real arXiv PDFs

---

## Phase 3 — Chunking + Embedding (Day 2)

- [ ] Implement `tools/chunking_tool.py` — `chunk_text(text, chunk_size, overlap)`
- [ ] Choose and test chunking strategy (recursive character splitter recommended)
- [ ] Implement `tools/embedding_tool.py` — `create_embeddings(chunks)`
- [ ] Initialize SentenceTransformers model (`all-MiniLM-L6-v2`)
- [ ] Benchmark embedding speed on 10-page PDF
- [ ] Write unit tests for chunking and embedding

---

## Phase 4 — FAISS Vector Store (Day 2)

- [ ] Implement `services/vector_store_service.py`
- [ ] `initialize_index(dimension)` — create FAISS index
- [ ] `add_chunks(chunks, embeddings, metadata)` — store with metadata
- [ ] `search(query_embedding, top_k)` — similarity search
- [ ] `save_index(path)` / `load_index(path)` — persistence
- [ ] Write integration tests for store + retrieval
- [ ] Test end-to-end: PDF → chunks → embeddings → FAISS → retrieve

---

## Phase 5 — RAG Retrieval (Day 3)

- [ ] Implement `agents/retrieval_agent.py`
- [ ] Embed user query at query time
- [ ] Retrieve top-k relevant chunks from FAISS
- [ ] Format retrieved chunks as context string
- [ ] Pass context to LLM for answer generation
- [ ] Write integration test for full RAG pipeline
- [ ] Test with 5 sample questions against indexed papers

---

## Phase 6 — Analysis + Summarization (Day 3)

- [ ] Implement `agents/analysis_agent.py`
- [ ] Summarize individual papers (title, methodology, datasets, limitations)
- [ ] Implement `agents/writer_agent.py`
- [ ] Generate structured summary report for a single paper
- [ ] Create `POST /api/summarize` route
- [ ] Test summary quality on 3 papers

---

## Phase 7 — Multi-Agent Workflow (Day 4)

- [ ] Implement `agents/planner_agent.py`
- [ ] Decompose user query into 3–5 search sub-topics
- [ ] Implement `services/orchestrator_service.py`
- [ ] Wire agents: Planner → Search → PDF → Embed → Retrieve → Analyze → Write
- [ ] Handle partial failures gracefully (one paper fails, rest continue)
- [ ] Create `POST /api/research` — full autonomous research endpoint
- [ ] Test full pipeline end-to-end with a real research topic

---

## Phase 8 — Insight Detection (Post-MVP)

- [ ] Implement `agents/insight_agent.py`
- [ ] Detect recurring themes across papers
- [ ] Identify contradictions between papers
- [ ] Identify research gaps (what topics are missing)
- [ ] Include insights section in final report

---

## Phase 9 — React Frontend (Day 4)

- [ ] Set up React Router with pages: Home, Research, Results
- [ ] Build `SearchBar` component — topic input + submit
- [ ] Build `ProgressTracker` component — show agent pipeline progress
- [ ] Build `PaperCard` component — display paper title, abstract, summary
- [ ] Build `ReportView` component — display final literature review
- [ ] Connect all components to backend via `services/apiService.ts`
- [ ] Handle loading, error, and empty states
- [ ] Test full user flow in browser

---

## Phase 10 — Deployment

- [ ] Finalize `Dockerfile` for backend
- [ ] Finalize `Dockerfile` for frontend
- [ ] Test `docker-compose up` builds and runs correctly
- [ ] Configure environment variables for production
- [ ] Deploy backend to Railway / Render
- [ ] Deploy frontend (Vercel or same platform)
- [ ] Smoke test production deployment with a real query
- [ ] Update `docs/DEPLOYMENT.md` with steps

---

## Backlog (Nice to Have)

- [ ] Export report as PDF
- [ ] Conversation history (ask follow-up questions)
- [ ] Paper comparison table (side-by-side methodology)
- [ ] Citation formatter (APA / MLA)
- [ ] Streaming responses from Writer Agent
- [ ] OpenAlex API integration
- [ ] User authentication
- [ ] Save and reload past research sessions
