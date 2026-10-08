"""Lightweight distributed span tracer for tracking end-to-end RAG pipelines."""

import time
import uuid
from typing import Any


class Span:
    """Represents a single timed unit of work within a distributed trace."""

    def __init__(self, name: str, trace_id: str, parent_id: str | None = None) -> None:
        """Initialize span metadata.

        Args:
            name: Human-readable span operation name.
            trace_id: Global trace identifier linking all related spans.
            parent_id: Optional identifier of the parent enclosing span.
        """
        self.name = name
        self.trace_id = trace_id
        self.span_id = str(uuid.uuid4())[:8]
        self.parent_id = parent_id
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.duration_ms: float = 0.0
        self.attributes: dict[str, Any] = {}
        self.status: str = "UNSET"
        self.error: str | None = None

    def __enter__(self) -> "Span":
        """Start the span timer upon entering context block."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop the span timer and record exceptions if raised."""
        self.end_time = time.perf_counter()
        self.duration_ms = round((self.end_time - self.start_time) * 1000.0, 3)
        if exc_type is not None:
            self.status = "ERROR"
            self.error = str(exc_val)
        else:
            self.status = "OK"

    def set_attribute(self, key: str, value: Any) -> None:
        """Attach custom telemetry attribute to the span.

        Args:
            key: Attribute name.
            value: Attribute value (e.g. token counts, score, model name).
        """
        self.attributes[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Serialize span into standard dictionary format.

        Returns:
            Dictionary representation of the span.
        """
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "attributes": self.attributes,
            "error": self.error,
        }


class TraceContext:
    """Manages active spans within a single root trace execution."""

    def __init__(self, trace_id: str, name: str) -> None:
        """Initialize trace context.

        Args:
            trace_id: Global trace identifier.
            name: Root trace operation name.
        """
        self.trace_id = trace_id
        self.name = name
        self.root_span = Span(name=name, trace_id=trace_id)
        self.spans: list[Span] = []

    def __enter__(self) -> "TraceContext":
        """Enter root trace execution context."""
        self.root_span.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit root trace execution context."""
        self.root_span.__exit__(exc_type, exc_val, exc_tb)
        self.spans.append(self.root_span)

    def span(self, name: str) -> Span:
        """Create a child span linked to this trace.

        Args:
            name: Child span operation name.

        Returns:
            Context-managed Span instance.
        """
        child = Span(name=name, trace_id=self.trace_id, parent_id=self.root_span.span_id)
        self.spans.append(child)
        return child

    def get_summary(self) -> dict[str, Any]:
        """Aggregate total execution duration and child span details.

        Returns:
            Summary dictionary containing trace ID and breakdown.
        """
        return {
            "trace_id": self.trace_id,
            "total_duration_ms": self.root_span.duration_ms,
            "status": self.root_span.status,
            "spans": [s.to_dict() for s in self.spans],
        }


class Tracer:
    """Factory for creating and managing distributed traces."""

    def __init__(self) -> None:
        """Initialize Tracer."""
        pass

    def trace(self, name: str, trace_id: str | None = None) -> TraceContext:
        """Start a new root trace context.

        Args:
            name: Root trace operation name.
            trace_id: Optional user-provided trace ID.

        Returns:
            TraceContext instance.
        """
        tid = trace_id or str(uuid.uuid4())
        return TraceContext(trace_id=tid, name=name)
