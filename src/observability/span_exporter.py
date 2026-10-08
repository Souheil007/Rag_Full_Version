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
        host = os.getenv("LANGFUSE_HOST", os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com"))

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
            trace_id = trace_summary.get("trace_id")
            spans = trace_summary.get("spans", [])
            root_span = spans[0] if spans else {}
            root_name = root_span.get("name", "rag_pipeline") if root_span else "rag_pipeline"
            root_input = root_span.get("input") or trace_summary.get("input")
            root_output = root_span.get("output") or trace_summary.get("output")
            root_duration_ms = root_span.get("duration_ms", trace_summary.get("total_duration_ms", 0.0))

            metadata = {
                "trace_id": trace_id,
                "total_duration_ms": trace_summary.get("total_duration_ms"),
                "status": trace_summary.get("status"),
            }

            if hasattr(self._langfuse, "start_observation"):
                # Langfuse SDK v4+ API
                root_obs = self._langfuse.start_observation(
                    name=root_name,
                    as_type="chain",
                    input=root_input,
                    output=root_output,
                    metadata=metadata,
                )
                if hasattr(root_obs, "set_trace_io"):
                    try:
                        import warnings
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", DeprecationWarning)
                            root_obs.set_trace_io(input=root_input, output=root_output)
                    except Exception:
                        pass

                child_spans = spans[1:] if len(spans) > 1 else []
                for span in child_spans:
                    span_name = span.get("name", "span")
                    span_input = span.get("input")
                    span_output = span.get("output")
                    span_attrs = dict(span.get("attributes", {}))
                    span_duration_ms = span.get("duration_ms", 0.0)
                    span_attrs["duration_ms"] = span_duration_ms

                    # Classify observation type according to Langfuse conventions
                    if "llm" in span_name.lower() or "generation" in span_name.lower() or "model" in span_attrs:
                        as_type = "generation"
                    elif "retriev" in span_name.lower():
                        as_type = "retriever"
                    else:
                        as_type = "span"

                    start_kwargs = {
                        "name": span_name,
                        "as_type": as_type,
                        "input": span_input,
                        "output": span_output,
                        "metadata": span_attrs,
                        "status_message": span.get("status"),
                    }
                    if as_type == "generation" and span_attrs.get("model"):
                        start_kwargs["model"] = span_attrs["model"]

                    if hasattr(root_obs, "start_observation"):
                        child = root_obs.start_observation(**start_kwargs)
                    else:
                        child = self._langfuse.start_observation(**start_kwargs)

                    if child and hasattr(child, "end"):
                        end_kwargs = {}
                        if hasattr(child, "_otel_span") and hasattr(child._otel_span, "start_time"):
                            duration_ns = int(span_duration_ms * 1_000_000)
                            end_kwargs["end_time"] = child._otel_span.start_time + duration_ns
                        child.end(**end_kwargs)

                if hasattr(root_obs, "end"):
                    end_kwargs = {}
                    if hasattr(root_obs, "_otel_span") and hasattr(root_obs._otel_span, "start_time"):
                        duration_ns = int(root_duration_ms * 1_000_000)
                        end_kwargs["end_time"] = root_obs._otel_span.start_time + duration_ns
                    root_obs.end(**end_kwargs)

            elif hasattr(self._langfuse, "trace"):
                # Langfuse SDK v2/v3 legacy API
                trace = self._langfuse.trace(
                    id=trace_id,
                    name=root_name,
                    input=root_input,
                    output=root_output,
                    metadata=metadata,
                )
                if hasattr(trace, "span"):
                    for span in spans[1:]:
                        trace.span(
                            name=span["name"],
                            input=span.get("input"),
                            output=span.get("output"),
                            metadata=span.get("attributes", {}),
                            status_message=span.get("status"),
                        )

            if hasattr(self._langfuse, "flush"):
                self._langfuse.flush()

            trace_url = ""
            if hasattr(self._langfuse, "get_trace_url"):
                try:
                    trace_url = self._langfuse.get_trace_url(trace_id=trace_id)
                except Exception:
                    pass

            if trace_url:
                logger.info(f"Trace {trace_id} exported to Langfuse → {trace_url}")
            else:
                logger.info(f"Trace {trace_id} exported to Langfuse.")
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

