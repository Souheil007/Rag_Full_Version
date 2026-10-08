"""Span exporter supporting local JSONL logs, Langfuse tracing, and Sentry error monitoring."""

import json
import os
from pathlib import Path
from typing import Any
from src.observability.sentry_monitor import SentryMonitor
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class SpanExporter:
    """Exports trace spans to local JSONL, Langfuse observability, and Sentry error monitoring."""

    def __init__(self, log_path: str = "logs/traces.jsonl") -> None:
        """Initialize SpanExporter and auto-detect Langfuse and Sentry credentials.

        Args:
            log_path: Path to the JSONL trace log file.
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._langfuse = self._init_langfuse()
        self._sentry = SentryMonitor()

    def _init_langfuse(self) -> Any | None:
        """Lazily initialize Langfuse client if credentials are configured.

        Returns:
            Langfuse client instance or None if not configured.
        """
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if not public_key or not secret_key:
            logger.info("Langfuse credentials not set. Tracing to local JSONL only.")
            return None

        try:
            from langfuse import Langfuse

            client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host,
            )
            logger.info(f"Langfuse observability client initialized → {host}")
            return client
        except ImportError:
            logger.warning("langfuse package not installed. Run: pip install langfuse")
            return None
        except Exception as exc:
            logger.warning(f"Langfuse initialization failed: {exc}")
            return None

    def export(self, trace_summary: dict[str, Any]) -> None:
        """Export trace to local JSONL, Langfuse, and Sentry.

        Args:
            trace_summary: Trace summary dictionary from TraceContext.get_summary().
        """
        self._export_local(trace_summary)
        if self._langfuse:
            self._export_langfuse(trace_summary)
        if self._sentry.enabled:
            self._export_sentry(trace_summary)

    def _export_local(self, trace_summary: dict[str, Any]) -> None:
        """Append trace summary to local JSONL file.

        Args:
            trace_summary: Trace dictionary to persist.
        """
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(trace_summary) + "\n")
        except Exception as exc:
            logger.error(f"Failed to write local trace log: {exc}")

    def _export_langfuse(self, trace_summary: dict[str, Any]) -> None:
        """Send trace and child spans to Langfuse observability platform.

        Args:
            trace_summary: Trace dictionary containing spans and metadata.
        """
        try:
            trace = self._langfuse.trace(
                id=trace_summary.get("trace_id"),
                name=trace_summary.get("spans", [{}])[0].get("name", "rag_pipeline"),
                metadata={
                    "total_duration_ms": trace_summary.get("total_duration_ms"),
                    "status": trace_summary.get("status"),
                },
            )

            # Export each child span as a Langfuse generation or span
            for span in trace_summary.get("spans", [])[1:]:  # Skip root span
                trace.span(
                    name=span["name"],
                    start_time=None,
                    end_time=None,
                    metadata=span.get("attributes", {}),
                    status_message=span.get("status"),
                    level="ERROR" if span.get("status") == "ERROR" else "DEFAULT",
                )

            self._langfuse.flush()
            logger.info(f"Trace {trace_summary.get('trace_id')} exported to Langfuse.")
        except Exception as exc:
            logger.error(f"Failed to export trace to Langfuse: {exc}")

    def _export_sentry(self, trace_summary: dict[str, Any]) -> None:
        """Report trace errors to Sentry monitoring.

        Args:
            trace_summary: Trace dictionary containing spans and status.
        """
        if trace_summary.get("status") != "ERROR":
            return

        for span in trace_summary.get("spans", []):
            if span.get("status") == "ERROR" and span.get("error"):
                self._sentry.capture_message(
                    message=f"Span Error [{span.get('name')}]: {span.get('error')}",
                    level="error",
                )

