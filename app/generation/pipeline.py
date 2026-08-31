"""Generation pipeline."""

from __future__ import annotations

from app.domain import Answer, ScoredDocument
from app.generation.citations import CitationBuilder
from app.generation.context_builder import ContextBuilder
from app.generation.grounding import GroundingValidator
from app.generation.llm import LLMProvider
from app.generation.prompts import build_prompt
from app.generation.structured_output import StructuredOutputParser


class GenerationPipeline:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm
        self.context_builder = ContextBuilder()
        self.citations = CitationBuilder()
        self.grounding = GroundingValidator()
        self.parser = StructuredOutputParser()

    def generate(self, question: str, documents: list[ScoredDocument], request_id: str, retrieval_metadata: dict) -> Answer:
        if not documents:
            return Answer(
                answer="I couldn't find enough information in the indexed transcript to answer that.",
                citations=[],
                grounded=False,
                retrieval_metadata=retrieval_metadata,
                request_id=request_id,
            )
        context = self.context_builder.build(documents)
        raw = self.llm.generate(build_prompt(question, context))
        parsed = self.parser.parse(raw, [item.document.id for item in documents])
        grounded = self.grounding.validate(parsed.answer, documents)
        if not grounded:
            parsed.answer = "I couldn't find enough information in the indexed transcript to answer that."
        return Answer(
            answer=parsed.answer,
            citations=self.citations.build(documents),
            grounded=grounded,
            retrieval_metadata=retrieval_metadata,
            request_id=request_id,
        )
