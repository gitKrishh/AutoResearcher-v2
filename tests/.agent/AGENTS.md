# AGENTS.md — AutoResearcher Tests
> AI Operating Manual for the root-level `tests/` directory.
> Read this before writing or modifying any test at the project level.
> For backend-specific tests, also see `backend/.agent/AGENTS.md`.
> For project-wide rules, see root `/.agent/AGENTS.md`.

---

## 1. Purpose of This Directory

The root `tests/` directory holds **cross-service and end-to-end (E2E) tests** that validate the system as a whole — not individual units or backend logic in isolation.

This directory tests:
- Full pipeline integration (backend + FAISS + LLM working together)
- API contract compliance (does the backend response match what the frontend expects)
- E2E user flows (submit topic → receive full report)
- External API integration checks (arXiv, Semantic Scholar — real calls)
- Performance benchmarks and regression checks

**Service-level unit and integration tests live inside each service:**
- Backend unit/integration tests → `backend/tests/`
- Frontend component tests → colocated in `frontend/src/`

---

## 2. Folder Structure

```
tests/
│
├── .agent/                         ← YOU ARE HERE
│   └── AGENTS.md
│
├── e2e/
│   ├── test_full_pipeline.py       ← topic → final report (real backend)
│   ├── test_search_to_embed.py     ← search → PDF → FAISS store
│   └── test_rag_retrieval.py       ← embed papers → query → answer
│
├── integration/
│   ├── test_api_contracts.py       ← verify API responses match TypeScript types
│   ├── test_arxiv_live.py          ← real arXiv API call (marked slow)
│   └── test_vector_store_flow.py   ← chunk → embed → store → retrieve round-trip
│
├── performance/
│   ├── test_pipeline_latency.py    ← measure full pipeline duration
│   └── test_embedding_throughput.py ← measure embedding speed at scale
│
├── fixtures/
│   ├── sample_papers.json          ← mock paper data shared across tests
│   ├── sample_report.json          ← mock FinalReport for contract tests
│   └── sample_pdfs/                ← small test PDFs (< 5 pages)
│       └── test_paper.pdf
│
└── conftest.py                     ← shared fixtures for all test modules here
```

---

## 3. Test Categories

### `e2e/` — End-to-End Tests
Test the full system from a user-facing input to a final output.
These run against a **live local backend** (requires the backend to be running).

- Slow by nature — acceptable
- Require real API keys (OpenAI, optionally arXiv)
- Marked with `@pytest.mark.e2e`
- Not run in standard CI — only on explicit trigger or pre-deploy

### `integration/` — Cross-Service Integration Tests
Test that multiple components work correctly together, but with mocked external services where possible.

- API contract tests ensure backend responses conform to the shape the frontend TypeScript types expect
- Vector store flow tests run the full chunk → embed → FAISS → retrieve loop
- Marked with `@pytest.mark.integration`
- Run in CI on every push to `main`

### `performance/` — Performance Benchmarks
Measure latency and throughput at key pipeline bottlenecks.
These are not pass/fail tests — they report metrics and flag regressions.

- Marked with `@pytest.mark.performance`
- Run manually or on scheduled CI jobs
- Results logged to stdout and optionally to a JSON file for tracking over time

---

## 4. Pytest Markers

Defined in `pytest.ini` (project root):

```ini
[pytest]
markers =
    e2e: end-to-end tests requiring live backend and real API keys
    integration: cross-service integration tests
    performance: performance benchmarks (not pass/fail)
    slow: tests that take more than 10 seconds
    live_api: tests that make real external API calls (arXiv, Semantic Scholar)
```

Run subsets:
```bash
# All tests except slow/e2e
pytest tests/ -m "not e2e and not slow"

# Only integration tests
pytest tests/integration/ -m integration

# Everything including e2e (pre-deploy check)
pytest tests/ --run-e2e
```

---

## 5. E2E Test Pattern

```python
# tests/e2e/test_full_pipeline.py
"""
E2E test: full research pipeline.
Requires: backend running on localhost:8000, valid OPENAI_API_KEY in .env
"""
import pytest
import httpx

BASE_URL = "http://localhost:8000/api"


@pytest.mark.e2e
@pytest.mark.slow
async def test_full_research_pipeline_returns_report():
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(
            f"{BASE_URL}/research",
            json={"topic": "AI agents in software engineering", "max_papers": 3},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    report = body["data"]
    assert report["topic"] == "AI agents in software engineering"
    assert report["paper_count"] >= 1
    assert len(report["literature_review"]) > 200
    assert isinstance(report["papers"], list)
    assert len(report["papers"]) >= 1
```

---

## 6. API Contract Test Pattern

API contract tests verify that backend responses match the TypeScript type definitions in `frontend/src/types/`.
They act as a bridge between backend and frontend — catching schema drift early.

```python
# tests/integration/test_api_contracts.py
"""
Contract tests: verify backend API responses conform to the expected shape
that the frontend TypeScript types describe.
"""
import pytest
from pydantic import BaseModel, ValidationError
from typing import Any


# Mirror frontend TypeScript types as Pydantic models
class PaperContract(BaseModel):
    id: str
    title: str
    abstract: str
    authors: list[str]
    pdf_url: str
    published: str
    source: str  # "arxiv" | "semantic_scholar"


class APIResponseContract(BaseModel):
    success: bool
    data: Any = None
    error: dict | None = None


@pytest.mark.integration
async def test_search_response_matches_frontend_contract(async_client):
    response = await async_client.post(
        "/api/search",
        json={"query": "transformer models", "max_results": 2},
    )
    assert response.status_code == 200

    body = APIResponseContract(**response.json())
    assert body.success is True

    papers = [PaperContract(**p) for p in body.data]
    assert len(papers) >= 1
```

---

## 7. Shared Fixtures (`conftest.py`)

```python
# tests/conftest.py
import json
import pytest
from pathlib import Path
from httpx import AsyncClient, ASGITransport

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_papers() -> list[dict]:
    return json.loads((FIXTURES_DIR / "sample_papers.json").read_text())


@pytest.fixture(scope="session")
def sample_report() -> dict:
    return json.loads((FIXTURES_DIR / "sample_report.json").read_text())


@pytest.fixture(scope="session")
def sample_pdf_path() -> Path:
    return FIXTURES_DIR / "sample_pdfs" / "test_paper.pdf"


@pytest.fixture
async def live_client():
    """HTTP client pointing at the live local backend."""
    async with AsyncClient(base_url="http://localhost:8000", timeout=120.0) as client:
        yield client
```

---

## 8. Performance Test Pattern

```python
# tests/performance/test_pipeline_latency.py
"""
Performance benchmark: measure full pipeline latency.
Not a pass/fail test — logs timings and flags if regression threshold exceeded.
"""
import time
import pytest
import httpx

LATENCY_THRESHOLD_SECONDS = 120  # fail if full pipeline exceeds this


@pytest.mark.performance
@pytest.mark.slow
async def test_full_pipeline_completes_within_threshold():
    async with httpx.AsyncClient(timeout=180.0) as client:
        start = time.perf_counter()
        response = await client.post(
            "http://localhost:8000/api/research",
            json={"topic": "LLM reasoning", "max_papers": 3},
        )
        elapsed = time.perf_counter() - start

    print(f"\n[PERF] Full pipeline: {elapsed:.2f}s")
    assert response.status_code == 200
    assert elapsed < LATENCY_THRESHOLD_SECONDS, (
        f"Pipeline exceeded threshold: {elapsed:.2f}s > {LATENCY_THRESHOLD_SECONDS}s"
    )
```

---

## 9. Test Data (Fixtures)

Keep fixture files small and deterministic:

- `fixtures/sample_papers.json` — 3–5 realistic paper objects matching the `Paper` schema
- `fixtures/sample_report.json` — 1 complete `FinalReport` for contract testing
- `fixtures/sample_pdfs/test_paper.pdf` — a real short academic PDF (< 5 pages) for PDF parsing tests

**Never use real personal data in fixtures. Never commit API keys.**

---

## 10. Running Tests

```bash
# Fast tests only (unit + integration, no live API, no e2e)
pytest tests/ -m "not e2e and not live_api and not slow" -v

# Integration only
pytest tests/integration/ -v

# Full suite (pre-deploy)
pytest tests/ -v

# With coverage report
pytest tests/ --cov=backend/app --cov-report=term-missing
```

---

## 11. What NOT To Do

- ❌ Do not put backend unit tests here — they go in `backend/tests/`
- ❌ Do not put frontend component tests here — they are colocated in `frontend/src/`
- ❌ Do not commit tests that make real API calls without marking them `@pytest.mark.live_api`
- ❌ Do not write tests that depend on a specific paper being returned by arXiv — results change
- ❌ Do not hardcode sleep/wait times — use proper async patterns
- ❌ Do not let performance tests fail CI — they are informational only
