"""Context builder and source attribution."""

from __future__ import annotations

from app.domain import ScoredDocument


class ContextBuilder:
    def build(self, documents: list[ScoredDocument]) -> str:
        blocks = []
        for item in documents:
            metadata = item.document.metadata
            blocks.append(
                "\n".join(
                    [
                        f"[chunk_id={item.document.id}]",
                        f"time={metadata.get('start_timestamp')} to {metadata.get('end_timestamp')}",
                        f"url={metadata.get('source_url')}",
                        item.document.text,
                    ]
                )
            )
        return "\n\n---\n\n".join(blocks)
