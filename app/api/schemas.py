"""API schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    video_url: str
    title: str | None = None
    channel: str | None = None
    tenant_id: str | None = None
    user_id: str | None = None


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    video_id: str | None = None
    tenant_id: str | None = None
    user_id: str | None = None


class EvaluateRequest(BaseModel):
    dataset_path: str = "data/evaluation/golden.jsonl"


class ApiResponse(BaseModel):
    data: Any
