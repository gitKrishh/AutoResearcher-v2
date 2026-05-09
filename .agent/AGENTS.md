# AGENTS.md — AutoResearcher Root
> AI Operating Manual for the AutoResearcher project.
> Read this before touching any file in this repository.

---

## 1. Project Purpose

AutoResearcher is an **autonomous AI research assistant** — not a chatbot.

Given a research topic, it autonomously:
- Searches academic papers (arXiv, Semantic Scholar, OpenAlex)
- Downloads and processes PDFs
- Chunks and embeds documents into a vector store
- Retrieves contextually relevant sections via RAG
- Analyzes methodologies, extracts insights, detects research gaps
- Generates structured literature reviews with citations

**The system is agentic. Each agent has one responsibility. Do not mix concerns.**

---

## 2. Architecture Overview

```
User Query
    ↓
Planner Agent          ← breaks query into sub-topics
    ↓
Search Agent           ← fetches papers from academic APIs
    ↓
PDF Processing Agent   ← downloads, parses, cleans PDFs
    ↓
Embedding Agent        ← chunks text, generates embeddings, stores in FAISS
    ↓
Retrieval Agent        ← semantic search over vector store
    ↓
Analysis Agent         ← summarizes, compares, extracts methodologies
    ↓
Insight Agent          ← finds trends, contradictions, research gaps
    ↓
Writer Agent           ← generates final structured report
    ↓
Final Report           ← markdown/PDF with citations, summaries, gaps
```

**Framework philosophy:** Use established frameworks where possible. Prefer LangChain or LlamaIndex for orchestration logic over custom implementations. Avoid over-engineering.

---

## 3. Tech Stack

| Layer            | Technology                              |
|------------------|-----------------------------------------|
| Backend          | Python 3.11+, FastAPI                   |
| AI / LLM         | OpenAI API (primary), Ollama (fallback) |
| Embeddings       | SentenceTransformers (all-MiniLM-L6-v2) |
| Vector DB        | FAISS                                   |
| PDF Processing   | PyMuPDF (fitz), pdfplumber              |
| Agent Framework  | LangChain (preferred) or direct API     |
| Frontend         | React.js (Vite + TypeScript)            |
| API Layer        | FastAPI + Pydantic v2                   |
| Testing          | pytest (backend), Vitest (frontend)     |
| Containerization | Docker + docker-compose                 |
| Deployment       | Railway / Render                        |

---

## 4. Repository Folder Structure

```
AutoResearcher/
│
├── .agent/                    ← YOU ARE HERE (root AI context)
│   ├── AGENTS.md
│   ├── CONTEXT.md
│   ├── CODING_CONVENTIONS.md
│   ├── TASKS.md
│   └── PROMPTS.md
│
├── backend/
│   ├── .agent/                ← backend-specific AI context
│   ├── app/
│   │   ├── agents/            ← one file per agent
│   │   ├── api/               ← FastAPI routers
│   │   ├── core/              ← config, settings, constants
│   │   ├── services/          ← business logic (non-agent)
│   │   └── tools/             ← reusable tool functions
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── .agent/                ← frontend-specific AI context
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/          ← API call functions
│   │   └── types/
│   ├── public/
│   └── package.json
│
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── SYSTEM_DESIGN.md
│
├── scripts/
│   └── .agent/
├── tests/
│   └── .agent/
├── docker/
│
├── .env
├── .gitignore
├── docker-compose.yml
├── README.md
└── ARCHITECTURE.md
```

---

## 5. Agent Responsibilities

| Agent            | File                          | Single Responsibility                       |
|------------------|-------------------------------|---------------------------------------------|
| Planner Agent    | `agents/planner_agent.py`     | Decompose query into searchable sub-topics  |
| Search Agent     | `agents/search_agent.py`      | Fetch papers from arXiv, Semantic Scholar   |
| PDF Agent        | `agents/pdf_agent.py`         | Download, parse, clean, chunk PDFs          |
| Embedding Agent  | `agents/embedding_agent.py`   | Embed chunks and store in FAISS             |
| Retrieval Agent  | `agents/retrieval_agent.py`   | Semantic search and context retrieval       |
| Analysis Agent   | `agents/analysis_agent.py`    | Summarize and compare papers                |
| Insight Agent    | `agents/insight_agent.py`     | Extract gaps, trends, contradictions        |
| Writer Agent     | `agents/writer_agent.py`      | Compose final structured report             |

---

## 6. Workflow Rules

- **One agent = one job.** Never make an agent do two things.
- **Agents call tools.** Business logic lives in `tools/` and `services/`, not inside agents.
- **Use frameworks first.** Before writing custom orchestration, check if LangChain already has it.
- **No agent imports another agent directly.** Communication goes through the orchestrator or service layer.
- **All LLM calls are wrapped.** Never call `openai.chat.completions.create()` directly in agent files — use the `services/llm_service.py` wrapper.
- **Fail loudly.** Raise typed exceptions. Never silently swallow errors.

---

## 7. What NOT To Do

- ❌ Do NOT mix agent logic with API route logic
- ❌ Do NOT hardcode API keys anywhere — use `.env` and `core/config.py`
- ❌ Do NOT build 20 agents before the MVP works
- ❌ Do NOT store PDFs or embeddings in the repository
- ❌ Do NOT skip type hints on any function
- ❌ Do NOT return raw exceptions to the frontend — use structured error responses
- ❌ Do NOT write business logic inside FastAPI route handlers
- ❌ Do NOT use `print()` for logging — use the `logging` module

---

## 8. MVP Scope (Build First)

```
✅ Search papers via arXiv API
✅ Download and parse PDFs
✅ Chunk + embed documents into FAISS
✅ Ask questions about papers (RAG)
✅ Generate paper summary
```

**Do not add autonomous planning, multi-agent orchestration, or report export until MVP is working end-to-end.**

---

## 9. Testing Requirements

- Every agent must have a corresponding test file in `backend/tests/agents/`
- Every API route must have an integration test
- Use `pytest` fixtures for mocking LLM and API calls
- Minimum: happy path + one failure case per function
- Tests must pass before any feature is marked complete in `CONTEXT.md`

---

## 10. How to Update Context

After every meaningful change:
1. Update `CONTEXT.md` → mark completed tasks, log decisions
2. Update `TASKS.md` → check off done items, add new ones
3. If a new pattern is established → update `CODING_CONVENTIONS.md`

**Keep these files current. They are the project's memory.**
