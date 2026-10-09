"""Pipeline performance profiler extracting stage latencies and token spend."""

from typing import Any
from src.observability.metrics_collector import MetricsCollector


class PipelineProfiler:
    """Extracts granular per-stage latency and token cost for API responses."""

    def __init__(self, metrics_collector: MetricsCollector | None = None) -> None:
        """Initialize profiler with optional shared metrics collector.

        Args:
            metrics_collector: MetricsCollector instance for cost calculations.
        """
        self.metrics_collector = metrics_collector or MetricsCollector()

    def profile_trace(
        self,
        trace_summary: dict[str, Any],
        model_name: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cache_hit: bool = False,
    ) -> dict[str, Any]:
        """Extract stage-level breakdown and compute query cost.

        Args:
            trace_summary: Summary dictionary from TraceContext.get_summary().
            model_name: Identifier of model used for generation.
            input_tokens: Number of prompt/context tokens.
            output_tokens: Number of generated completion tokens.
            cache_hit: Whether the response was served from cache.

        Returns:
            Dictionary containing stage latencies, total time, and estimated cost.
        """
        spans = trace_summary.get("spans", [])

        # Map span durations by normalized name
        stage_durations: dict[str, float] = {
            "retrieval_ms": 0.0,
            "prompt_formatting_ms": 0.0,
            "generation_ms": 0.0,
            "guardrail_ms": 0.0,
        }

        for span in spans:
            name = span.get("name", "").lower()
            duration = float(span.get("duration_ms", 0.0))

            if "retrieval" in name or "retriever" in name:
                stage_durations["retrieval_ms"] += duration
            elif "prompt" in name:
                stage_durations["prompt_formatting_ms"] += duration
            elif "llm" in name or "generation" in name:
                stage_durations["generation_ms"] += duration
            elif "guardrail" in name:
                stage_durations["guardrail_ms"] += duration

        total_latency_ms = float(trace_summary.get("total_duration_ms", 0.0))

        # Cached queries incur zero LLM API cost
        if cache_hit:
            estimated_cost = 0.0
        else:
            estimated_cost = self.metrics_collector.estimate_cost(
                model_name, input_tokens, output_tokens
            )

        return {
            "retrieval_ms": round(stage_durations["retrieval_ms"], 2),
            "prompt_formatting_ms": round(stage_durations["prompt_formatting_ms"], 2),
            "generation_ms": round(stage_durations["generation_ms"], 2),
            "guardrail_ms": round(stage_durations["guardrail_ms"], 2),
            "total_latency_ms": round(total_latency_ms, 2),
            "cache_hit": cache_hit,
            "model": model_name if not cache_hit else "semantic_cache",
            "estimated_cost_usd": round(estimated_cost, 7),
        }
