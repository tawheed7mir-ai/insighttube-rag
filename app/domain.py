"""Shared contracts between indexing, retrieval, and generation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ScoredDocument(BaseModel):
    document: Document
    score: float
    source: str = "unknown"
    rerank_score: Optional[float] = None


class Citation(BaseModel):
    chunk_id: str
    video_id: str
    start_timestamp: str
    end_timestamp: str
    url: str
    text: str
    score: float | None = None


class RetrievalTrace(BaseModel):
    query: str
    rewritten_query: str | None = None
    queries: List[str] = Field(default_factory=list)
    dense_results: List[str] = Field(default_factory=list)
    sparse_results: List[str] = Field(default_factory=list)
    fused_results: List[str] = Field(default_factory=list)
    mmr_results: List[str] = Field(default_factory=list)
    reranked_results: List[str] = Field(default_factory=list)
    final_chunk_ids: List[str] = Field(default_factory=list)
    latency_ms: Dict[str, float] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class Answer(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    grounded: bool = False
    retrieval_metadata: Dict[str, Any] = Field(default_factory=dict)
    request_id: str
