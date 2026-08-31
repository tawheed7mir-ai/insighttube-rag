# Architecture

The system is split into ingestion, indexing, retrieval, generation, evaluation, observability, API, UI, and service layers. The service layer composes interfaces so Chroma can become Qdrant/pgvector and local LLM output can become Groq or another provider without rewriting business logic.
