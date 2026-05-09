"""Pydantic schemas for request/response models.

All API request and response models are defined here.
These mirror the TypeScript types in the frontend.
"""

from pydantic import BaseModel, ConfigDict, field_validator


# ============================================================
# API Response Models
# ============================================================


class APIError(BaseModel):
    """Structured error response."""

    code: str
    message: str
    detail: str | None = None


class APIResponse(BaseModel):
    """Standard API response wrapper.

    All API responses follow this structure for consistency.
    """

    success: bool
    data: dict | list | None = None
    error: APIError | None = None
    meta: dict | None = None


# ============================================================
# Search Models
# ============================================================


class SearchRequest(BaseModel):
    """Request body for POST /api/search."""

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


# ============================================================
# Paper Models
# ============================================================


class Paper(BaseModel):
    """A single academic paper from search results."""

    id: str
    title: str
    abstract: str
    authors: list[str]
    pdf_url: str
    published: str
    source: str  # "arxiv" | "semantic_scholar"


class ProcessedPaper(Paper):
    """Paper with extracted full text from PDF."""

    full_text: str
    page_count: int
    text_length: int


class ChunkResult(BaseModel):
    """A text chunk returned from similarity search."""
    
    text: str
    score: float
    paper_id: str
    paper_title: str
    page_num: int | None = None


class PaperAnalysis(Paper):
    """Detailed LLM-generated analysis of a single paper."""

    summary: str
    methodology: str
    datasets: str
    key_findings: str
    limitations: str
    contribution: str


class InsightReport(BaseModel):
    """Structured insights generated from cross-paper analysis."""
    
    research_gaps: list[str]
    contradictions: list[str]
    trends: list[str]
    future_directions: list[str]


class FinalReport(BaseModel):
    """The final research output compiled by the WriterAgent."""
    
    topic: str
    paper_count: int
    papers: list[PaperAnalysis]
    literature_review: str
    insights: InsightReport | None
    generated_at: str


class ResearchRequest(BaseModel):
    """Request body for POST /api/research."""

    model_config = ConfigDict(str_strip_whitespace=True)

    topic: str
    max_papers: int = 10
    include_insights: bool = True

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Topic must not be empty")
        return v
