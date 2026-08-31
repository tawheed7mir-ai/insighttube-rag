"""Configurable query rewriting."""

from __future__ import annotations


class QueryRewriter:
    def rewrite(self, question: str) -> str:
        # Local default keeps behavior deterministic. LLM-backed rewriting can be
        # swapped in later through this interface and evaluated before enabling.
        return question
