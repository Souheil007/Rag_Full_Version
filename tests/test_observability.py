"""Unit tests for distributed tracing, metrics collector, and observability."""

import os
import unittest
from src.observability.metrics_collector import MetricsCollector
from src.observability.span_exporter import SpanExporter
from src.observability.tracer import Tracer


class TestObservability(unittest.TestCase):
    """Test suite for distributed tracing and operational metrics."""

    def test_tracer_span_lifecycle(self):
        """Verify tracer records nested spans, status, and duration."""
        tracer = Tracer()
        with tracer.trace("test_query_pipeline") as root:
            with root.span("retrieval_step") as s1:
                s1.set_attribute("chunk_count", 5)
                self.assertEqual(s1.name, "retrieval_step")
            with root.span("llm_step") as s2:
                s2.set_attribute("model", "gemini-2.0-flash")

        summary = root.get_summary()
        self.assertEqual(summary["status"], "OK")
        self.assertTrue(summary["total_duration_ms"] >= 0.0)
        self.assertEqual(len(summary["spans"]), 3)  # root + 2 children

    def test_metrics_collector_percentiles_and_cost(self):
        """Verify MetricsCollector computes P50, P95, error rate, and dollar cost."""
        metrics = MetricsCollector()
        # Record sample latencies: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 ms
        for lat in range(10, 110, 10):
            metrics.record_query(
                duration_ms=float(lat),
                is_error=(lat == 100),
                input_tokens=1000,
                output_tokens=200,
                model_name="gemini-2.0-flash",
            )

        snapshot = metrics.get_metrics_snapshot()
        self.assertEqual(snapshot["total_requests"], 10)
        self.assertEqual(snapshot["total_errors"], 1)
        self.assertEqual(snapshot["error_rate"], 0.10)
        self.assertEqual(snapshot["p50_latency_ms"], 60.0)
        self.assertTrue(snapshot["total_cost_usd"] > 0.0)

    def test_span_exporter_jsonl(self):
        """Verify SpanExporter writes valid JSONL telemetry records."""
        test_log_path = "logs/test_traces.jsonl"
        exporter = SpanExporter(log_path=test_log_path)
        sample_trace = {
            "trace_id": "test-123",
            "total_duration_ms": 45.2,
            "status": "OK",
            "spans": [],
        }
        exporter.export(sample_trace)

        self.assertTrue(os.path.exists(test_log_path))
        with open(test_log_path, "r", encoding="utf-8") as f:
            line = f.readline()
            self.assertIn("test-123", line)

        # Cleanup
        if os.path.exists(test_log_path):
            os.remove(test_log_path)

    def test_sentry_monitor_disabled_by_default(self):
        """Verify SentryMonitor handles missing DSN gracefully without crashing."""
        from src.observability.sentry_monitor import SentryMonitor

        sentry = SentryMonitor(dsn="")
        self.assertFalse(sentry.enabled)
        # Verify capture calls return None when disabled
        self.assertIsNone(sentry.capture_exception(ValueError("Test error")))
        self.assertIsNone(sentry.capture_message("Test message"))


if __name__ == "__main__":
    unittest.main()

