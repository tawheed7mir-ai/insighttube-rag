"""Validated transcript data structures.

These models are the contract between ingestion and the later indexing,
retrieval, citation, and evaluation phases. Keeping timestamps and source
metadata here prevents downstream code from guessing where evidence came from.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


def update_model(model: BaseModel, **updates: Any) -> BaseModel:
    """Return a copied Pydantic model across v1/v2 without deprecation warnings."""
    if hasattr(model, "model_copy"):
        return model.model_copy(update=updates)
    return model.copy(update=updates)


def stable_hash(value: str, length: int = 16) -> str:
    return sha256(value.encode("utf-8")).hexdigest()[:length]


def format_timestamp(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


class TranscriptSegment(BaseModel):
    text: str
    start: float = Field(ge=0)
    duration: float = Field(ge=0)
    end: float = Field(ge=0)
    speaker: Optional[str] = None

    @classmethod
    def from_api_snippet(cls, snippet: Any) -> "TranscriptSegment":
        if isinstance(snippet, dict):
            text = snippet.get("text", "")
            start = float(snippet.get("start", 0.0))
            duration = float(snippet.get("duration", 0.0))
        else:
            text = getattr(snippet, "text", "")
            start = float(getattr(snippet, "start", 0.0))
            duration = float(getattr(snippet, "duration", 0.0))
        return cls(text=text, start=start, duration=duration, end=start + duration)


class SourceMetadata(BaseModel):
    video_id: str
    source_url: str
    language: str
    source_type: str = "youtube"
    title: Optional[str] = None
    channel: Optional[str] = None
    speaker: Optional[str] = None
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    ingestion_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    version: str = "v1"


class TranscriptChunk(BaseModel):
    text: str
    video_id: str
    source_url: str
    chunk_id: str
    chunk_number: int
    start_time: float
    end_time: float
    start_timestamp: str
    end_timestamp: str
    language: str
    source_type: str
    content_hash: str
    version: str
    previous_chunk_id: Optional[str] = None
    next_chunk_id: Optional[str] = None
    title: Optional[str] = None
    channel: Optional[str] = None
    speaker: Optional[str] = None
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    segment_count: int = 0

    def to_document_metadata(self) -> Dict[str, Any]:
        if hasattr(self, "model_dump"):
            return self.model_dump(exclude={"text"})
        return self.dict(exclude={"text"})


class IngestionResult(BaseModel):
    metadata: SourceMetadata
    raw_segments: List[TranscriptSegment]
    cleaned_segments: List[TranscriptSegment]
    chunks: List[TranscriptChunk]

