"""Grounding validation."""

from __future__ import annotations

from app.domain import ScoredDocument


class GroundingValidator:
    def validate(self, answer: str, documents: list[ScoredDocument]) -> bool:
        if not documents:
            return False
        if "couldn't find enough information" in answer.lower():
            return False
        answer_terms = set(answer.lower().split())
        context_terms = set(" ".join(item.document.text for item in documents).lower().split())
        if not answer_terms:
            return False
        overlap = len(answer_terms.intersection(context_terms)) / max(1, len(answer_terms))
        return overlap >= 0.25
