"""Multi-query expansion."""

from __future__ import annotations


class MultiQueryGenerator:
    def generate(self, question: str) -> list[str]:
        variants = [question]
        if "?" in question:
            variants.append(question.replace("?", ""))
        return list(dict.fromkeys(variants))
