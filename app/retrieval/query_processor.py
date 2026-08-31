"""Query validation and normalization."""

from __future__ import annotations

from app.core.security import defend_prompt_injection


class QueryProcessor:
    def process(self, question: str) -> str:
        cleaned = " ".join(question.strip().split())
        if not cleaned:
            raise ValueError("Question cannot be empty")
        if len(cleaned) > 2000:
            raise ValueError("Question is too long")
        return defend_prompt_injection(cleaned)
