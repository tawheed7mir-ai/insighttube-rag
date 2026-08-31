"""Context compression."""

from __future__ import annotations

from app.domain import ScoredDocument


class ContextCompressor:
    def compress(self, query: str, documents: list[ScoredDocument], max_chars: int) -> list[ScoredDocument]:
        used = 0
        output: list[ScoredDocument] = []
        for item in documents:
            if used >= max_chars:
                break
            budget = max_chars - used
            text = item.document.text[:budget]
            item.document.text = text
            used += len(text)
            output.append(item)
        return output
