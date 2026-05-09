# CODING_CONVENTIONS.md — AutoResearcher Root
> Strict code style and engineering standards for the entire project.
> Every contributor (human or AI) must follow these rules without exception.

---

## 1. Naming Conventions

### Python (Backend)

| Element          | Convention         | Example                          |
|------------------|--------------------|----------------------------------|
| Files            | `snake_case`       | `search_agent.py`                |
| Classes          | `PascalCase`       | `SearchAgent`, `PlannerAgent`    |
| Functions        | `snake_case`       | `fetch_papers()`, `extract_text()`|
| Variables        | `snake_case`       | `pdf_path`, `chunk_size`         |
| Constants        | `UPPER_SNAKE_CASE` | `MAX_CHUNKS`, `DEFAULT_MODEL`    |
| Type aliases     | `PascalCase`       | `PaperList`, `ChunkData`         |
| Private methods  | `_snake_case`      | `_clean_text()`, `_load_index()` |

### TypeScript / React (Frontend)

| Element          | Convention         | Example                          |
|------------------|--------------------|----------------------------------|
| Files (components)| `PascalCase.tsx`  | `SearchBar.tsx`, `ResultCard.tsx`|
| Files (hooks)    | `camelCase.ts`     | `useResearch.ts`, `usePapers.ts` |
| Files (services) | `camelCase.ts`     | `apiService.ts`, `searchService.ts`|
| Components       | `PascalCase`       | `ResearchPanel`, `PaperList`     |
| Functions        | `camelCase`        | `fetchPapers()`, `handleSubmit()`|
| Variables        | `camelCase`        | `paperList`, `isLoading`         |
| Constants        | `UPPER_SNAKE_CASE` | `API_BASE_URL`, `MAX_RESULTS`    |
| Types/Interfaces | `PascalCase`       | `Paper`, `SearchResult`          |

---

## 2. Folder Structure Rules

### Backend

```
backend/app/
├── agents/      ← one agent per file, nothing else
├── api/         ← FastAPI routers only, no logic
├── core/        ← config, settings, constants, exceptions
├── services/    ← all business logic and LLM calls
└── tools/       ← pure utility functions (search, PDF, embed)
```

- **Agents** must only call tools and services — no raw API calls inside agents
- **Routers** must only call services — no business logic in route handlers
- **Tools** must be pure functions — stateless, no side effects where possible

### Frontend

```
frontend/src/
├── components/  ← reusable UI components
├── pages/       ← page-level components (one per route)
├── hooks/       ← custom React hooks
├── services/    ← all fetch/axios API call functions
└── types/       ← shared TypeScript interfaces and types
```

- API calls only in `services/` — never fetch directly inside components
- Global state (if needed) via React Context or Zustand — not prop drilling

---

## 3. Formatting Standards

### Python

- Formatter: **Black** (line length: 88)
- Linter: **Ruff**
- Type checker: **mypy** (strict mode)
- All functions must have type hints — no exceptions

```python
# ✅ Correct
def fetch_papers(query: str, max_results: int = 10) -> list[dict]:
    ...

# ❌ Wrong
def fetch_papers(query, max_results=10):
    ...
```

### TypeScript / React

- Formatter: **Prettier** (single quotes, no semicolons, 2-space indent)
- Linter: **ESLint** with TypeScript rules
- No `any` type — use proper interfaces
- Prefer functional components with hooks — no class components

---

## 4. Architecture Patterns

### Backend — Layered Architecture

```
Router (API) → Service → Agent → Tool
```

- Routes call services
- Services orchestrate agents
- Agents call tools
- Tools are pure utility functions

### Frontend — Feature-Based

- One folder per major feature (research, results, history)
- Shared components in `components/common/`
- All API types mirrored from backend Pydantic models

### Agent Pattern

```python
class SearchAgent:
    def __init__(self, llm_service: LLMService, search_tool: SearchTool):
        self.llm = llm_service
        self.tool = search_tool

    async def run(self, query: str) -> list[Paper]:
        ...
```

- Agents are **classes**, not functions
- Dependencies injected via constructor
- `run()` is the single public entry point

---

## 5. Import Rules

### Python

- Standard library first
- Third-party second
- Local imports third
- Separate each group with a blank line
- No wildcard imports (`from module import *`)

```python
# ✅ Correct
import os
from pathlib import Path

import httpx
from pydantic import BaseModel

from app.core.config import settings
from app.tools.search_tool import fetch_papers
```

### TypeScript

- External packages first
- Internal absolute imports second
- Relative imports last

```typescript
// ✅ Correct
import { useState } from 'react'
import axios from 'axios'

import { Paper } from '@/types'
import { fetchPapers } from '@/services/apiService'

import SearchBar from './SearchBar'
```

---

## 6. Error Handling Rules

### Backend

- Define custom exceptions in `core/exceptions.py`
- Never raise generic `Exception` — always typed exceptions
- All FastAPI routes must have proper HTTP status codes
- Return structured error responses — never raw exception messages

```python
# core/exceptions.py
class PaperNotFoundError(Exception): ...
class PDFParseError(Exception): ...
class EmbeddingError(Exception): ...

# Usage
raise PDFParseError(f"Failed to parse PDF: {pdf_path}")
```

```python
# API error response format (always)
{
  "success": false,
  "error": {
    "code": "PDF_PARSE_ERROR",
    "message": "Failed to parse the requested PDF.",
    "detail": "..."
  }
}
```

### Frontend

- All API calls wrapped in try/catch
- User-facing errors shown via a toast or error component — never raw error strings
- Loading and error states always handled explicitly

---

## 7. API Response Format

All backend API responses follow this structure:

```json
// Success
{
  "success": true,
  "data": { ... },
  "meta": {
    "count": 10,
    "page": 1
  }
}

// Error
{
  "success": false,
  "error": {
    "code": "SEARCH_FAILED",
    "message": "Human-readable message",
    "detail": "Technical detail (dev only)"
  }
}
```

All response models defined as Pydantic `BaseModel` in `app/core/schemas.py`.

---

## 8. Testing Style

### Python (pytest)

- Test files mirror the source structure: `tests/agents/test_search_agent.py`
- Use fixtures for LLM mocks and API mocks
- Test function naming: `test_<function>_<scenario>`

```python
def test_fetch_papers_returns_list_on_valid_query():
    ...

def test_fetch_papers_raises_on_empty_query():
    ...
```

### TypeScript (Vitest)

- Test files colocated: `SearchBar.test.tsx` next to `SearchBar.tsx`
- Mock all API service calls
- Test user interactions, not implementation details

---

## 9. Environment and Configuration

- All secrets in `.env` — never hardcoded
- Loaded via `pydantic-settings` in `core/config.py`
- `.env` is gitignored — `.env.example` is committed with placeholder values

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    semantic_scholar_api_key: str = ""
    faiss_index_path: str = "vector_store/index"
    max_pdf_pages: int = 50
    chunk_size: int = 512
    chunk_overlap: int = 64

settings = Settings()
```

---

## 10. Logging

- Use Python's `logging` module — never `print()`
- Log level conventions:
  - `DEBUG` — detailed internal steps
  - `INFO` — agent started/completed, key milestones
  - `WARNING` — recoverable issues
  - `ERROR` — failures that stop a workflow

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Search agent started for query: %s", query)
logger.error("PDF parsing failed for: %s", pdf_url, exc_info=True)
```

---

## 11. Git Conventions

- Branch naming: `feature/`, `fix/`, `chore/`
- Commit messages: imperative present tense

```
✅ feat: add arXiv search tool
✅ fix: handle empty PDF text extraction
✅ chore: update FAISS index serialization
❌ added search feature
❌ fixed bug
```
