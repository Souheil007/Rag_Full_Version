"""Operational metrics collector for latency percentiles, error rates, and token cost."""

import statistics
import time
from typing import Any

# Pricing per 1M tokens (USD)
MODEL_PRICING_PER_1M: dict[str, dict[str, float]] = {
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
}


class MetricsCollector:
    """Collects and computes real-time operational metrics across queries."""

    def __init__(self) -> None:
        """Initialize in-memory metrics storage."""
        self.latencies_ms: list[float] = []
        self.total_requests: int = 0
        self.total_errors: int = 0
        self.cache_hits: int = 0
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self.total_cost_usd: float = 0.0
        self.start_time: float = time.time()

    def record_query(
        self,
        duration_ms: float,
        is_error: bool = False,
        cache_hit: bool = False,
        input_tokens: int = 0,
        output_tokens: int = 0,
        model_name: str = "gemini-2.0-flash",
    ) -> None:
        """Record telemetry for a single query execution.

        Args:
            duration_ms: Total latency in milliseconds.
            is_error: Whether the query encountered an unhandled error.
            cache_hit: Whether the query was served from cache.
            input_tokens: Number of prompt/context tokens.
            output_tokens: Number of generated response tokens.
            model_name: Model identifier used for generation.
        """
        self.total_requests += 1
        self.latencies_ms.append(duration_ms)

        if is_error:
            self.total_errors += 1
        if cache_hit:
            self.cache_hits += 1

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        # Compute cost
        cost = self.estimate_cost(model_name, input_tokens, output_tokens)
        self.total_cost_usd += cost

    def estimate_cost(
        self, model_name: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate estimated cost in USD for token consumption.

        Args:
            model_name: Model identifier.
            input_tokens: Prompt token count.
            output_tokens: Completion token count.

        Returns:
            Calculated cost in USD.
        """
        rates = MODEL_PRICING_PER_1M.get(
            model_name, {"input": 0.10, "output": 0.40}
        )
        cost = (input_tokens / 1_000_000.0) * rates["input"] + (
            output_tokens / 1_000_000.0
        ) * rates["output"]
        return round(cost, 7)

    def get_metrics_snapshot(self) -> dict[str, Any]:
        """Compute aggregated operational metrics and latency percentiles.

        Returns:
            Snapshot dictionary containing counts, error rate, P50, P95, and cost.
        """
        if not self.latencies_ms:
            return {
                "total_requests": 0,
                "error_rate": 0.0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "total_cost_usd": 0.0,
            }

        sorted_latencies = sorted(self.latencies_ms)
        n = len(sorted_latencies)
        p50 = sorted_latencies[int(n * 0.5)]
        p95 = sorted_latencies[min(int(n * 0.95), n - 1)]

        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": round(self.total_errors / self.total_requests, 4),
            "cache_hits": self.cache_hits,
            "cache_hit_ratio": round(self.cache_hits / max(self.total_requests, 1), 4),
            "p50_latency_ms": round(p50, 2),
            "p95_latency_ms": round(p95, 2),
            "avg_latency_ms": round(statistics.mean(self.latencies_ms), 2),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost_usd": round(self.total_cost_usd, 6),
        }
