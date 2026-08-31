"""Tracing abstraction."""

from contextlib import contextmanager
from time import perf_counter


@contextmanager
def span(name: str):
    start = perf_counter()
    try:
        yield
    finally:
        _ = {"span": name, "latency_ms": round((perf_counter() - start) * 1000, 3)}
