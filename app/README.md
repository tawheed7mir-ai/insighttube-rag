# App package layout

This package is organized around the runtime responsibilities of the RAG system.

## Active runtime modules

- `api/` — API request schemas, dependencies, and routes
- `core/` — configuration, security, settings, and shared utilities
- `services/` — service layer, orchestration, and app-level facades
- `ingestion/` — transcript extraction, cleaning, normalization, and chunking
- `indexing/` — embedding generation and local index storage
- `retrieval/` — dense, sparse, hybrid, reranking, and context assembly
- `generation/` — prompt construction and response generation

## Keep-out / optional modules

The following folders are research or extension areas and are not required for a minimal Streamlit resume deployment:

- `evaluation/`
- `observability/`

These can be archived or moved to a separate `extras/` folder later if you want the project to look even cleaner on GitHub.

## Recommended mental model

Think of the app as:

- `api` = interface
- `services` = orchestration
- `ingestion` + `indexing` + `retrieval` + `generation` = pipeline
- `core` = shared infrastructure
