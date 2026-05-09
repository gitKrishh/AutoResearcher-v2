# CODING_CONVENTIONS.md — AutoResearcher Backend
> Strict code style and engineering rules for the `backend/` service.
> These rules are specific to Python + FastAPI.
> Also follow root `/.agent/CODING_CONVENTIONS.md` for project-wide rules.

---

## 1. Python Version and Tooling

- Python **3.11+** required — use `match` statements, `tomllib`, and modern typing
- Formatter: **Black** (`line-length = 88`)
- Linter: **Ruff** (replaces flake8, isort, and more)
- Type checker: **mypy** (`strict = true`)
- Run before every commit:

```bash
black app/ tests/
ruff check app/ tests/ --fix
mypy app/
pytest tests/ -v
```

---

## 2. Typing Rules

**Every function must have complete type hints. No exceptions.**

```python
# ✅ Correct
async def fetch_papers(query: str, max_results: int = 10) -> list[Paper]:
    ...

# ✅ Correct — use built-in generics (Python 3.10+)
def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    ...

# ❌ Wrong — missing return type
async def fetch_papers(query: str, max_results: int = 10):
    ...

# ❌ Wrong — no type hints at all
def chunk_text(text, size, overlap):
    ...
```

- Use `str | None` instead of `Optional[str]` (Python 3.10+ union syntax)
- Use `list[str]` instead of `List[str]` (built-in generics)
- Use `TypedDict` or Pydantic models for structured dicts — avoid raw `dict`
- Never use `Any` except in test mocks — document why if you must

---

## 3. Async Rules

The backend is **fully async**. All I/O must be non-blocking.

```python
# ✅ Correct
import httpx

async def download_pdf(url: str, save_path: Path) -> Path:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        ...

# ❌ Wrong — synchronous in an async service
import requests

def download_pdf(url: str, save_path: Path) -> Path:
    response = requests.get(url)
    ...
```

- Use `httpx.AsyncClient` for all HTTP requests — never `requests`
- Use `asyncio.gather()` to run independent agent tasks concurrently
- CPU-bound tasks (PDF parsing, embeddings) run in `asyncio.to_thread()` to avoid blocking the event loop

```python
# ✅ Run CPU-bound work off the event loop
text = await asyncio.to_thread(extract_text_from_pdf, pdf_path)
embeddings = await asyncio.to_thread(model.encode, chunks)
```

---

## 4. FastAPI Conventions

### Route Handlers

```python
# ✅ Correct — thin handler, delegates to service
@router.post("/search", response_model=APIResponse[list[Paper]])
async def search_papers(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service),
) -> APIResponse[list[Paper]]:
    papers = await search_service.search(request.query, request.max_results)
    return APIResponse(success=True, data=papers)
```

- Route handlers must be **under 10 lines** of actual logic
- Always use `response_model=` to enforce output schema
- Always use `Depends()` for service injection — never instantiate services inside handlers
- Always use HTTP status codes explicitly for errors (`status_code=404`, `422`, etc.)

### Dependency Injection

```python
# api/deps.py
def get_llm_service() -> LLMService:
    return LLMService(settings.openai_api_key)

def get_vector_store() -> VectorStoreService:
    return VectorStoreService(settings.faiss_index_path)
```

- Every service is injectable via `Depends()`
- Services are instantiated once (use `@lru_cache` or FastAPI `lifespan` for singletons)

### Router Registration

```python
# app/main.py
app.include_router(health_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(research_router, prefix="/api")
app.include_router(papers_router, prefix="/api")
```

---

## 5. Pydantic v2 Rules

- All request and response models use `pydantic.BaseModel`
- Use `model_config = ConfigDict(...)` not class `Config` (Pydantic v2 style)
- Use `field_validator` and `model_validator` for validation logic
- Never bypass validation with `.model_construct()` unless you have a documented reason

```python
# ✅ Pydantic v2 style
from pydantic import BaseModel, ConfigDict, field_validator

class SearchRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str
    max_results: int = 10

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query must not be empty")
        return v

    @field_validator("max_results")
    @classmethod
    def max_results_in_range(cls, v: int) -> int:
        if not 1 <= v <= 50:
            raise ValueError("max_results must be between 1 and 50")
        return v
```

---

## 6. Agent Class Pattern

Every agent follows this exact structure:

```python
# agents/search_agent.py
import logging
from app.core.schemas import Paper, SearchAgentConfig
from app.core.exceptions import SearchError
from app.tools.search_tool import search_arxiv
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class SearchAgent:
    def __init__(self, llm_service: LLMService) -> None:
        self.llm = llm_service

    async def run(self, sub_topics: list[str], max_per_topic: int = 5) -> list[Paper]:
        logger.info("SearchAgent started for %d sub-topics", len(sub_topics))
        all_papers: list[Paper] = []

        for topic in sub_topics:
            try:
                papers = await search_arxiv(topic, max_per_topic)
                all_papers.extend(papers)
                logger.debug("Found %d papers for topic: %s", len(papers), topic)
            except SearchError:
                logger.warning("Search failed for topic: %s — skipping", topic)
                continue

        logger.info("SearchAgent complete — total papers: %d", len(all_papers))
        return all_papers
```

Rules:
- Class name = `{Name}Agent`
- Constructor takes only services/config — no logic
- Single public method: `run()` — always `async`
- Log `INFO` at start and end of `run()`
- Never raise from `run()` without logging first
- Return typed output — never raw `dict`

---

## 7. Tool Function Pattern

Tools are standalone async (or sync for CPU-bound) functions:

```python
# tools/search_tool.py
import logging
import httpx
from app.core.schemas import Paper
from app.core.exceptions import SearchError

logger = logging.getLogger(__name__)

async def search_arxiv(query: str, max_results: int = 10) -> list[Paper]:
    """Fetch papers from arXiv API for a given query."""
    if not query.strip():
        raise ValueError("Query must not be empty")

    url = "http://export.arxiv.org/api/query"
    params = {"search_query": f"all:{query}", "max_results": max_results}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise SearchError(f"arXiv request failed: {e}") from e

    return _parse_arxiv_response(response.text)


def _parse_arxiv_response(xml_text: str) -> list[Paper]:
    """Parse arXiv Atom XML into Paper objects."""
    ...
```

Rules:
- One function per responsibility
- Private helpers prefixed with `_`
- Always set `timeout` on HTTP calls
- Always `raise_for_status()` on responses
- Wrap external errors in domain exceptions (`SearchError`, not raw `httpx.HTTPError`)

---

## 8. Configuration Pattern

```python
# core/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # LLM
    openai_api_key: str
    default_llm_model: str = "gpt-4o-mini"
    heavy_llm_model: str = "gpt-4o"

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # Vector Store
    faiss_index_path: str = "vector_store/index"

    # PDF
    pdf_cache_dir: str = "data/pdfs"
    max_pdf_pages: int = 50

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Search
    max_papers_per_search: int = 10

    # Server
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

---

## 9. LLM Service Pattern

```python
# services/llm_service.py
import json
import logging
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.exceptions import LLMError

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, api_key: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)

    async def complete(self, prompt: str, model: str | None = None) -> str:
        model = model or settings.default_llm_model
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error("LLM call failed: %s", e, exc_info=True)
            raise LLMError(f"LLM call failed: {e}") from e

    async def complete_json(self, prompt: str, model: str | None = None) -> dict:
        model = model or settings.default_llm_model
        raw = await self.complete(prompt + "\nRespond with ONLY valid JSON.", model)
        try:
            return json.loads(raw.strip().removeprefix("```json").removesuffix("```"))
        except json.JSONDecodeError as e:
            logger.error("JSON parse failed. Raw output: %s", raw)
            raise LLMError(f"LLM returned invalid JSON: {e}") from e
```

---

## 10. Testing Conventions

### File Structure
```
tests/
├── conftest.py           ← shared fixtures
├── agents/
│   ├── test_search_agent.py
│   └── test_analysis_agent.py
├── api/
│   └── test_search_routes.py
└── tools/
    └── test_search_tool.py
```

### Fixtures (conftest.py)

```python
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import app

@pytest.fixture
def mock_llm_service():
    service = AsyncMock()
    service.complete_json.return_value = {"summary": "Test summary"}
    return service

@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
```

### Test Style

```python
# ✅ Correct naming
async def test_search_arxiv_returns_papers_on_valid_query():
    ...

async def test_search_arxiv_raises_search_error_on_network_failure():
    ...

async def test_post_search_returns_200_with_paper_list():
    ...

async def test_post_search_returns_422_on_empty_query():
    ...
```

- Use `pytest.mark.asyncio` or `asyncio_mode = "auto"` in `pytest.ini`
- Mock all external calls (OpenAI, arXiv, PDF download) — tests must run offline
- No `time.sleep()` in tests — mock time-dependent behavior
- Each test file must be runnable independently
