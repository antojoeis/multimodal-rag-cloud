"""Append one JSON line per /ask request, for evaluating accuracy and latency.

Only text and stats are stored, never the image itself.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from app import config

logger = logging.getLogger(__name__)


def log_request(
    question: str,
    answer: str | None,
    model: str,
    latency_s: float | None,
    image_name: str | None = None,
    image_kb: float | None = None,
    error: str | None = None,
) -> None:
    if not config.REQUEST_LOG_PATH:
        return
    record = {
        "time": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "question": question,
        "answer": answer,
        "model": model,
        "latency_s": latency_s,
        "image_name": image_name,
        "image_kb": image_kb,
        "error": error,
    }
    try:
        path = Path(config.REQUEST_LOG_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        # Logging must never break the API.
        logger.exception("Could not write request log")
