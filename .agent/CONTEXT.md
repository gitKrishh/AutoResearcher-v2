# CONTEXT.md — AutoResearcher Root
> Live project memory and logbook.
> Update this file after every meaningful change.

---

## Project Status

**Phase:** Pre-development / Setup
**Last Updated:** <!-- update this every session -->
**Active Branch:** `main`

---

## Current Progress

```
[ ] Project scaffolded
[ ] Backend skeleton created
[ ] Frontend skeleton created
[ ] Environment variables configured
[ ] Docker setup complete
[ ] arXiv API connected
[ ] PDF extraction working
[ ] Chunking + embedding pipeline working
[ ] FAISS store initialized
[ ] RAG retrieval working
[ ] Basic question answering working
[ ] Paper summary generation working
[ ] Multi-agent workflow connected
[ ] Research gap detection working
[ ] Writer agent producing final report
[ ] Frontend connected to backend
[ ] End-to-end MVP working
[ ] Deployed
```

---

## Completed Phases

_Nothing completed yet. Update this as phases finish._

---

## Pending Tasks

> See `TASKS.md` for the full task breakdown.

### Immediate (Day 1)
- [ ] Initialize project folder structure
- [ ] Set up `backend/` with FastAPI skeleton
- [ ] Set up `frontend/` with React + Vite
- [ ] Configure `.env` and `core/config.py`
- [ ] Connect arXiv API and test paper search
- [ ] Implement PDF download + PyMuPDF extraction

### Next Up (Day 2)
- [ ] Implement text chunking
- [ ] Set up SentenceTransformers embeddings
- [ ] Initialize FAISS vector store
- [ ] Store and retrieve chunks from FAISS

### Later (Day 3–4)
- [ ] Build retrieval agent with RAG
- [ ] Build analysis + summarization agent
- [ ] Build writer agent
- [ ] Wire up multi-agent orchestration
- [ ] Build React UI
- [ ] Deploy with Docker

---

## Decisions Taken

| Date | Decision | Reason |
|------|----------|--------|
| —    | Use LangChain for agent framework | Avoid re-inventing orchestration; faster iteration |
| —    | Use FAISS over Pinecone/Chroma | No external infra dependency for MVP |
| —    | React.js (Vite + TypeScript) for frontend | More professional than Streamlit; better long-term |
| —    | OpenAI API as primary LLM | Reliability; Ollama as local fallback |
| —    | PyMuPDF as primary PDF parser | Speed + reliability over pdfplumber |

---

## Known Bugs / Issues

_None yet. Log bugs here as they are discovered._

| ID  | Description | Status | File |
|-----|-------------|--------|------|
| —   | —           | —      | —    |

---

## Implementation Notes

_Add technical notes here as the project evolves._

- arXiv API does not require an API key for basic search (rate limit: ~3 req/sec)
- Semantic Scholar API key recommended for higher rate limits
- FAISS index must be serialized to disk after each session (`faiss.write_index`)
- PDF downloads should be cached locally to avoid re-downloading

---

## Test Results

_Log test outcomes here after running the test suite._

| Date | Test Suite | Passed | Failed | Notes |
|------|-----------|--------|--------|-------|
| —    | —         | —      | —      | —     |

---

## Next Steps

1. Scaffold the full folder structure as defined in `AGENTS.md`
2. Start with `backend/app/tools/search_tool.py` — arXiv search function
3. Test the search tool in isolation before wiring agents
4. Follow the MVP scope strictly — do not expand scope until MVP is working
