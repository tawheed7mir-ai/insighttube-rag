"""Structured logging setup.

Phase 1 keeps logging vendor-neutral and standard-library based. The log shape
is stable enough for local debugging and can later be routed into OpenTelemetry
or a managed logging backend.
"""

from __future__ import annotations

import logging
import os


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

