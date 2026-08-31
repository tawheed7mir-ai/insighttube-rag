"""Metrics sink abstraction."""

from collections import Counter


class Metrics:
    def __init__(self) -> None:
        self.counters = Counter()

    def increment(self, name: str, value: int = 1) -> None:
        self.counters[name] += value
