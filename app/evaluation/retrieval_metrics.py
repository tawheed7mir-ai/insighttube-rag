"""Retrieval metrics."""

from __future__ import annotations


def recall_at_k(relevant_ids: set[str], retrieved_ids: list[str], k: int) -> float:
    if not relevant_ids:
        return 0.0
    return len(relevant_ids.intersection(retrieved_ids[:k])) / len(relevant_ids)


def mrr(relevant_ids: set[str], retrieved_ids: list[str]) -> float:
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_ids:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(relevant_ids: set[str], retrieved_ids: list[str], k: int) -> float:
    dcg = sum((1.0 / __import__("math").log2(rank + 1)) for rank, doc_id in enumerate(retrieved_ids[:k], start=1) if doc_id in relevant_ids)
    ideal = sum(1.0 / __import__("math").log2(rank + 1) for rank in range(1, min(len(relevant_ids), k) + 1))
    return dcg / ideal if ideal else 0.0
