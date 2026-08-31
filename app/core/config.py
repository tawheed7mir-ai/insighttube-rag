"""Environment-driven configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class IngestionSettings:
    youtube_language: str = "en"
    chunk_size: int = 1500
    chunk_overlap: int = 300
    source_type: str = "youtube"
    metadata_version: str = "v1"

    @classmethod
    def from_env(cls) -> "IngestionSettings":
        return cls(
            youtube_language=os.getenv("YOUTUBE_LANGUAGE", "en"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1500")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "300")),
            source_type=os.getenv("SOURCE_TYPE", "youtube"),
            metadata_version=os.getenv("METADATA_VERSION", "v1"),
        )


@dataclass(frozen=True)
class RetrievalSettings:
    top_k: int = 10
    dense_top_k: int = 10
    sparse_top_k: int = 10
    mmr_fetch_k: int = 30
    mmr_lambda: float = 0.5
    rerank_top_k: int = 4
    context_max_chars: int = 6000
    min_score: float = 0.0
    enable_hybrid_search: bool = True
    enable_mmr: bool = True
    enable_reranker: bool = True
    enable_compression: bool = True
    enable_neighbor_expansion: bool = True
    enable_query_rewrite: bool = False
    enable_multi_query: bool = False

    @classmethod
    def from_env(cls) -> "RetrievalSettings":
        return cls(
            top_k=int(os.getenv("RETRIEVAL_TOP_K", "10")),
            dense_top_k=int(os.getenv("DENSE_TOP_K", "10")),
            sparse_top_k=int(os.getenv("SPARSE_TOP_K", "10")),
            mmr_fetch_k=int(os.getenv("MMR_FETCH_K", "30")),
            mmr_lambda=float(os.getenv("MMR_LAMBDA", "0.5")),
            rerank_top_k=int(os.getenv("RERANK_TOP_K", "4")),
            context_max_chars=int(os.getenv("CONTEXT_MAX_CHARS", "6000")),
            min_score=float(os.getenv("MIN_RETRIEVAL_SCORE", "0.0")),
            enable_hybrid_search=_env_bool("ENABLE_HYBRID_SEARCH", True),
            enable_mmr=_env_bool("ENABLE_MMR", True),
            enable_reranker=_env_bool("ENABLE_RERANKER", True),
            enable_compression=_env_bool("ENABLE_COMPRESSION", True),
            enable_neighbor_expansion=_env_bool("ENABLE_NEIGHBOR_EXPANSION", True),
            enable_query_rewrite=_env_bool("ENABLE_QUERY_REWRITE", False),
            enable_multi_query=_env_bool("ENABLE_MULTI_QUERY", False),
        )


@dataclass(frozen=True)
class AppSettings:
    environment: str = "development"
    data_dir: Path = Path("data")
    index_dir: Path = Path("data/indexes")
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_batch_size: int = 32
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    llm_provider: str = "groq"
    llm_model: str = "openai/gpt-oss-20b"
    llm_temperature: float = 0.0
    api_key: str | None = None
    rate_limit_per_minute: int = 60
    prompt_version: str = "rag-grounded-v1"
    ingestion: IngestionSettings = field(default_factory=IngestionSettings)
    retrieval: RetrievalSettings = field(default_factory=RetrievalSettings)

    @classmethod
    def from_env(cls) -> "AppSettings":
        data_dir = Path(os.getenv("DATA_DIR", "data"))
        return cls(
            environment=os.getenv("APP_ENV", "development"),
            data_dir=data_dir,
            index_dir=Path(os.getenv("INDEX_DIR", str(data_dir / "indexes"))),
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            embedding_batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE", "32")),
            reranker_model=os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
            llm_provider=os.getenv("LLM_PROVIDER", "groq"),
            llm_model=os.getenv("LLM_MODEL", "openai/gpt-oss-20b"),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
            api_key=os.getenv("APP_API_KEY"),
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
            prompt_version=os.getenv("PROMPT_VERSION", "rag-grounded-v1"),
            ingestion=IngestionSettings.from_env(),
            retrieval=RetrievalSettings.from_env(),
        )
