"""Evaluation runner."""

from __future__ import annotations

from pathlib import Path

from app.evaluation.datasets import load_jsonl
from app.evaluation.retrieval_metrics import mrr, recall_at_k
from app.services.rag_service import RagService


class Evaluator:
    def __init__(self, service: RagService) -> None:
        self.service = service

    def run(self, dataset_path: Path) -> dict:
        rows = load_jsonl(dataset_path)
        scores = []
        for row in rows:
            result = self.service.query(row["question"], video_id=row.get("video_id"))
            retrieved = result.get("retrieval_metadata", {}).get("final_chunk_ids", [])
            relevant = set(row.get("relevant_chunk_ids", []))
            scores.append({"recall@5": recall_at_k(relevant, retrieved, 5), "mrr": mrr(relevant, retrieved)})
        if not scores:
            return {"count": 0, "recall@5": 0.0, "mrr": 0.0}
        return {"count": len(scores), "recall@5": sum(s["recall@5"] for s in scores) / len(scores), "mrr": sum(s["mrr"] for s in scores) / len(scores)}
