"""Structured output parsing."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field


class StructuredAnswer(BaseModel):
    answer: str
    cited_chunk_ids: list[str] = Field(default_factory=list)
    confidence: str = "medium"


class StructuredOutputParser:
    def parse(self, raw: str, available_chunk_ids: list[str]) -> StructuredAnswer:
        cited = [chunk_id for chunk_id in available_chunk_ids if chunk_id in raw]
        answer = re.sub(
            r"\s*\(?\s*(?:see\s+)?chunks?\s+[0-9a-f]{16,}(?:\s*,\s*[0-9a-f]{16,})*\s*[.)]*",
            "",
            raw,
            flags=re.IGNORECASE,
        )
        answer = re.sub(r"\[chunk_id=[^\]]+\]", "", answer, flags=re.IGNORECASE)
        return StructuredAnswer(answer=answer.strip(), cited_chunk_ids=cited)
