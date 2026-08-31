"""LLM provider abstraction."""

from __future__ import annotations

from typing import Protocol

from app.core.config import AppSettings


class LLMProvider(Protocol):
    def generate(self, prompt: str) -> str: ...


class LocalExtractiveLLM:
    """Deterministic fallback that returns evidence snippets from context."""

    def generate(self, prompt: str) -> str:
        lines = [line.strip() for line in prompt.splitlines() if line.strip()]
        evidence = [line for line in lines if not line.startswith(("TRANSCRIPT", "QUESTION", "Return", "You answer", "Ignore")) and "=" not in line]
        if not evidence:
            return "I couldn't find enough information in the indexed transcript to answer that."
        return " ".join(evidence[:3])


class GroqLLMProvider:
    def __init__(self, settings: AppSettings) -> None:
        try:
            from langchain_groq import ChatGroq
        except Exception as exc:  # pragma: no cover - optional dependency path.
            raise RuntimeError("langchain-groq is not installed") from exc
        self.model = ChatGroq(model=settings.llm_model, temperature=settings.llm_temperature)

    def generate(self, prompt: str) -> str:
        response = self.model.invoke(prompt)
        return getattr(response, "content", str(response))


def build_llm_provider(settings: AppSettings) -> LLMProvider:
    if settings.llm_provider.lower() == "groq":
        try:
            return GroqLLMProvider(settings)
        except Exception:
            return LocalExtractiveLLM()
    return LocalExtractiveLLM()
