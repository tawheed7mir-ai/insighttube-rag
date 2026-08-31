"""Regression helper placeholder."""

from __future__ import annotations


def compare_metric(current: float, baseline: float, tolerance: float = 0.02) -> bool:
    return current + tolerance >= baseline
