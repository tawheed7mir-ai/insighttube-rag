"""Generation metrics for local regression checks."""

from __future__ import annotations


def answer_relevance(answer: str, expected_terms: list[str]) -> float:
    if not expected_terms:
        return 0.0
    lowered = answer.lower()
    return sum(1 for term in expected_terms if term.lower() in lowered) / len(expected_terms)


def citation_correctness(cited_ids: list[str], expected_ids: set[str]) -> float:
    if not cited_ids:
        return 0.0
    return sum(1 for item in cited_ids if item in expected_ids) / len(cited_ids)
