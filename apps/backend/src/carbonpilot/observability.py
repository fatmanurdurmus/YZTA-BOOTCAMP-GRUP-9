"""Fail-open LangSmith tracing with an intentionally small, safe metadata surface."""

import logging
import time
from contextlib import contextmanager
from typing import Iterator

from carbonpilot.config import get_settings

logger = logging.getLogger(__name__)


def tracing_enabled() -> bool:
    settings = get_settings()
    return bool(settings.langsmith_tracing and settings.langsmith_api_key)


@contextmanager
def trace_operation(name: str, *, thread_id: str | None = None, retries: int | None = None) -> Iterator[None]:
    """Trace an operation without document text, credentials, or activity payloads."""
    started = time.monotonic()
    run = None
    if tracing_enabled():
        try:
            from langsmith import Client
            from langsmith.run_trees import RunTree

            settings = get_settings()
            run = RunTree(
                name=name,
                run_type="chain",
                inputs={"thread_id": thread_id, "retries": retries},
                project_name=settings.langsmith_project,
                ls_client=Client(api_key=settings.langsmith_api_key),
            )
            run.post()
        except Exception:
            logger.warning("LangSmith trace start failed; continuing without tracing", exc_info=True)
    try:
        yield
    except Exception as exc:
        if run is not None:
            try:
                run.end(error=str(type(exc).__name__))
                run.patch()
            except Exception:
                logger.warning("LangSmith trace error update failed", exc_info=True)
        raise
    else:
        if run is not None:
            try:
                run.end(outputs={"status": "completed", "latency_ms": round((time.monotonic() - started) * 1000, 2)})
                run.patch()
            except Exception:
                logger.warning("LangSmith trace update failed", exc_info=True)
