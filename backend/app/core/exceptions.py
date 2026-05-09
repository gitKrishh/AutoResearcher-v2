"""Custom exception types for AutoResearcher.

All exceptions inherit from AutoResearcherError.
Used throughout the app for typed error handling.
Never raise generic Exception — always use these.
"""


class AutoResearcherError(Exception):
    """Base exception for all AutoResearcher errors."""


class SearchError(AutoResearcherError):
    """Raised when academic paper search fails (arXiv, Semantic Scholar)."""


class PDFDownloadError(AutoResearcherError):
    """Raised when PDF download fails (network error, invalid URL)."""


class PDFParseError(AutoResearcherError):
    """Raised when PDF text extraction fails (corrupt, empty, unreadable)."""


class EmbeddingError(AutoResearcherError):
    """Raised when embedding generation fails."""


class RetrievalError(AutoResearcherError):
    """Raised when vector store retrieval fails."""


class LLMError(AutoResearcherError):
    """Raised when an LLM call fails (API error, invalid response, timeout)."""


class VectorStoreError(AutoResearcherError):
    """Raised when FAISS vector store operations fail (index, search, save/load)."""
