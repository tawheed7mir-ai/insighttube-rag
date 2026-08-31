"""FastAPI dependencies."""

from functools import lru_cache

from app.core.config import AppSettings
from app.services.rag_service import RagService


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings.from_env()


@lru_cache(maxsize=1)
def get_rag_service() -> RagService:
    return RagService(get_settings())
