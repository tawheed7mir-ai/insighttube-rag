"""BM25 sparse index for transcript chunks."""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from app.domain import Document, ScoredDocument

TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


class BM25Index:
    def __init__(self, path: Path, k1: float = 1.5, b: float = 0.75) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.k1 = k1
        self.b = b
        self.documents: dict[str, Document] = {}
        self.term_freqs: dict[str, Counter[str]] = {}
        self.doc_freqs: Counter[str] = Counter()
        self.avg_doc_len = 0.0
        self._load()

    def upsert(self, documents: list[Document]) -> None:
        for document in documents:
            old = self.term_freqs.get(document.id)
            if old:
                for term in old:
                    self.doc_freqs[term] -= 1
            terms = Counter(tokenize(document.text))
            self.documents[document.id] = document
            self.term_freqs[document.id] = terms
            for term in terms:
                self.doc_freqs[term] += 1
        self._recompute_avg_len()
        self._persist()

    def search(self, query: str, top_k: int, filters: dict[str, Any] | None = None) -> list[ScoredDocument]:
        query_terms = tokenize(query)
        scores: list[ScoredDocument] = []
        doc_count = max(1, len(self.documents))
        for doc_id, document in self.documents.items():
            if not _matches(document.metadata, filters):
                continue
            score = 0.0
            freqs = self.term_freqs[doc_id]
            doc_len = sum(freqs.values()) or 1
            for term in query_terms:
                tf = freqs.get(term, 0)
                if not tf:
                    continue
                df = self.doc_freqs.get(term, 0)
                idf = math.log(1 + (doc_count - df + 0.5) / (df + 0.5))
                denom = tf + self.k1 * (1 - self.b + self.b * doc_len / (self.avg_doc_len or 1))
                score += idf * (tf * (self.k1 + 1)) / denom
            if score > 0:
                scores.append(ScoredDocument(document=document, score=score, source="sparse"))
        return sorted(scores, key=lambda item: item.score, reverse=True)[:top_k]

    def _recompute_avg_len(self) -> None:
        if not self.term_freqs:
            self.avg_doc_len = 0.0
            return
        self.avg_doc_len = sum(sum(freqs.values()) for freqs in self.term_freqs.values()) / len(self.term_freqs)

    def _persist(self) -> None:
        payload = {
            "documents": [_dump(doc) for doc in self.documents.values()],
            "k1": self.k1,
            "b": self.b,
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self.path.exists():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.k1 = payload.get("k1", self.k1)
        self.b = payload.get("b", self.b)
        self.documents = {}
        self.term_freqs = {}
        self.doc_freqs = Counter()
        for raw_doc in payload.get("documents", []):
            self.upsert([Document(**raw_doc)])


def _matches(metadata: dict[str, Any], filters: dict[str, Any] | None) -> bool:
    if not filters:
        return True
    return all(value is None or metadata.get(key) == value for key, value in filters.items())


def _dump(model: Document) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
