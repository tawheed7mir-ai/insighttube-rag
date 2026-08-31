"""Custom exceptions used across the RAG platform."""


class RagPlatformError(Exception):
    """Base class for application-specific failures."""


class TranscriptError(RagPlatformError):
    """Raised when transcript ingestion cannot complete."""


class TranscriptUnavailableError(TranscriptError):
    """Raised when a transcript is missing or disabled for a video."""


class EmbeddingError(RagPlatformError):
    """Raised when embedding generation fails."""


class IndexingError(RagPlatformError):
    """Raised when indexing or persistence fails."""


class RetrievalError(RagPlatformError):
    """Raised when retrieval fails."""


class RerankingError(RagPlatformError):
    """Raised when reranking fails."""


class LLMError(RagPlatformError):
    """Raised when the LLM provider fails."""


class ValidationError(RagPlatformError):
    """Raised when validated application data is malformed."""


class GroundingError(RagPlatformError):
    """Raised when answer grounding cannot be validated."""
