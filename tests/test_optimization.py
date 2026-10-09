"""Unit and integration tests for Plan 4 cost and latency optimizations."""

import time
import pytest
from fastapi.testclient import TestClient
from src.api.routes import create_app
from src.observability.metrics_collector import MetricsCollector
from src.optimization.profiler import PipelineProfiler
from src.optimization.query_router import QueryRouter
from src.optimization.semantic_cache import (
    SemanticCache,
    compute_cosine_similarity,
)


# ============================================================================
# 1. Unit Tests: Cosine Similarity & Semantic Cache
# ============================================================================


def test_cosine_similarity() -> None:
    """Verify vector cosine similarity calculation edge cases and accuracy."""
    # Orthogonal vectors
    assert compute_cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0
    # Identical vectors
    assert pytest.approx(compute_cosine_similarity([1.0, 2.0], [1.0, 2.0]), 0.001) == 1.0
    # Zero / empty vectors
    assert compute_cosine_similarity([], []) == 0.0
    assert compute_cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_semantic_cache_hit_and_miss() -> None:
    """Verify semantic cache hit on similarity threshold and miss when dissimilar."""
    cache = SemanticCache(enabled=True, similarity_threshold=0.90, max_entries=10)

    # Store first item
    v1 = [1.0, 0.0, 0.0]
    stored = cache.store(
        query="What is RAG?",
        query_embedding=v1,
        answer="Retrieval-Augmented Generation.",
        sources=[{"doc_id": "1"}],
        is_verified=True,
    )
    assert stored is True
    assert cache.size() == 1

    # Exact query hit
    hit = cache.lookup("What is RAG?", v1)
    assert hit is not None
    assert hit["answer"] == "Retrieval-Augmented Generation."
    assert hit["similarity"] == 1.0

    # Semantically close query (similarity ~ 0.99)
    v_close = [0.99, 0.05, 0.0]
    hit_close = cache.lookup("Explain RAG to me", v_close)
    assert hit_close is not None
    assert hit_close["similarity"] > 0.90

    # Distant query (dissimilar vector)
    v_distant = [0.0, 1.0, 0.0]
    miss = cache.lookup("What is chocolate?", v_distant)
    assert miss is None


def test_semantic_cache_lru_eviction() -> None:
    """Verify least recently used entry is evicted when exceeding max_entries."""
    cache = SemanticCache(enabled=True, similarity_threshold=0.90, max_entries=2)

    cache.store("q1", [1.0, 0.0], "a1", is_verified=True)
    cache.store("q2", [0.0, 1.0], "a2", is_verified=True)
    assert cache.size() == 2

    # Access q1 to make q2 the least recently used
    cache.lookup("q1", [1.0, 0.0])

    # Insert q3, which should evict q2
    cache.store("q3", [0.5, 0.5], "a3", is_verified=True)
    assert cache.size() == 2

    # q1 and q3 remain; q2 was evicted
    assert cache.lookup("q1", [1.0, 0.0]) is not None
    assert cache.lookup("q2", [0.0, 1.0]) is None
    assert cache.lookup("q3", [0.5, 0.5]) is not None


def test_semantic_cache_ttl_expiration() -> None:
    """Verify expired cache entries are discarded."""
    cache = SemanticCache(enabled=True, similarity_threshold=0.90, max_entries=10, ttl_seconds=1)

    cache.store("expiring query", [1.0, 0.0], "temporary answer", is_verified=True)
    assert cache.lookup("expiring query", [1.0, 0.0]) is not None

    # Wait for TTL to expire
    time.sleep(1.1)
    assert cache.lookup("expiring query", [1.0, 0.0]) is None


def test_semantic_cache_quality_filters() -> None:
    """Verify unverified or fallback responses are rejected by the quality gate."""
    cache = SemanticCache(enabled=True, cache_only_verified=True)

    # 1. Unverified response
    res1 = cache.store("q", [1.0, 0.0], "some answer", is_verified=False)
    assert res1 is False
    assert cache.size() == 0

    # 2. Refusal / Fallback response
    res2 = cache.store(
        "q",
        [1.0, 0.0],
        "I cannot find sufficient factual backing in the retrieved documents to answer this reliably.",
        is_verified=True,
    )
    assert res2 is False
    assert cache.size() == 0


def test_semantic_cache_stats() -> None:
    """Verify stats reporting hit rate and sizing."""
    cache = SemanticCache(enabled=True, similarity_threshold=0.90, max_entries=5)
    cache.store("q1", [1.0, 0.0], "a1", is_verified=True)

    _ = cache.lookup("q1", [1.0, 0.0])  # Hit
    _ = cache.lookup("unknown", [0.0, 1.0])  # Miss

    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 0.5
    assert stats["size"] == 1


# ============================================================================
# 2. Unit Tests: Query Router
# ============================================================================


def test_query_router_disabled() -> None:
    """Verify query router uses default model when disabled."""
    router = QueryRouter(
        enabled=False,
        default_model="open-mistral-7b",
        fast_model="open-mistral-7b",
        reasoning_model="mistral-large-latest",
    )
    decision = router.route("Compare dense retrieval vs BM25 in detail?")
    assert decision["is_routed"] is False
    assert decision["model"] == "open-mistral-7b"
    assert decision["route"] == "default"


def test_query_router_enabled_classification() -> None:
    """Verify query router chooses appropriate models for simple vs complex queries."""
    router = QueryRouter(
        enabled=True,
        default_model="open-mistral-7b",
        fast_model="open-mistral-7b",
        reasoning_model="mistral-large-latest",
    )

    # Simple factoid query
    simple_res = router.route("What is chunk size?")
    assert simple_res["is_routed"] is True
    assert simple_res["route"] == "simple"
    assert simple_res["model"] == "open-mistral-7b"

    # Comparison / reasoning query
    complex_res = router.route("Compare dense and sparse search and list the trade-offs")
    assert complex_res["is_routed"] is True
    assert complex_res["route"] == "complex"
    assert complex_res["model"] == "mistral-large-latest"

    # Multi-question query
    multi_res = router.route("What is RAG? Why use embeddings?")
    assert multi_res["is_routed"] is True
    assert multi_res["route"] == "complex"
    assert multi_res["model"] == "mistral-large-latest"


# ============================================================================
# 3. Unit Tests: Pipeline Profiler
# ============================================================================


def test_pipeline_profiler() -> None:
    """Verify stage duration extraction and cost calculation in profiler."""
    metrics = MetricsCollector()
    profiler = PipelineProfiler(metrics_collector=metrics)

    fake_trace_summary = {
        "trace_id": "trace-test-123",
        "total_duration_ms": 150.0,
        "spans": [
            {"name": "rag_query_pipeline", "duration_ms": 150.0},
            {"name": "retrieval", "duration_ms": 40.0},
            {"name": "prompt_formatting", "duration_ms": 5.0},
            {"name": "llm_generation", "duration_ms": 90.0},
            {"name": "guardrail_verification", "duration_ms": 15.0},
        ],
    }

    # Non-cached execution
    profile = profiler.profile_trace(
        trace_summary=fake_trace_summary,
        model_name="open-mistral-7b",
        input_tokens=1000,
        output_tokens=200,
        cache_hit=False,
    )
    assert profile["retrieval_ms"] == 40.0
    assert profile["prompt_formatting_ms"] == 5.0
    assert profile["generation_ms"] == 90.0
    assert profile["guardrail_ms"] == 15.0
    assert profile["total_latency_ms"] == 150.0
    assert profile["cache_hit"] is False
    assert profile["estimated_cost_usd"] > 0.0

    # Cached execution ($0 cost)
    cached_profile = profiler.profile_trace(
        trace_summary=fake_trace_summary,
        model_name="open-mistral-7b",
        input_tokens=0,
        output_tokens=0,
        cache_hit=True,
    )
    assert cached_profile["cache_hit"] is True
    assert cached_profile["estimated_cost_usd"] == 0.0
    assert cached_profile["model"] == "semantic_cache"


# ============================================================================
# 4. Integration Tests: API /query with Semantic Cache & Profiling
# ============================================================================


def test_api_query_caching_and_profiling() -> None:
    """Verify first API query misses cache and second query hits cache with $0 spend."""
    test_cfg = {
        "app": {"name": "Test RAG", "version": "1.0.0"},
        "llm": {"provider": "gemini", "model_name": "gemini-2.0-flash"},
        "guardrails": {"enabled": False},
        "optimization": {
            "semantic_cache": {
                "enabled": True,
                "similarity_threshold": 0.95,
                "max_entries": 100,
                "ttl_seconds": 3600,
                "cache_only_verified": False,
            },
            "query_router": {
                "enabled": False,
                "default_model": "open-mistral-7b",
            },
        },
    }

    app = create_app(test_cfg)
    client = TestClient(app)

    # Query 1: Initial call (Cache Miss)
    resp1 = client.post("/query", json={"query": "What is semantic caching?"})
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert "profiling" in data1
    assert data1["profiling"]["cache_hit"] is False
    assert "total_latency_ms" in data1["profiling"]

    # Query 2: Identical call (Cache Hit)
    resp2 = client.post("/query", json={"query": "What is semantic caching?"})
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["answer"] == data1["answer"]
    assert data2["estimated_cost_usd"] == 0.0
    assert data2["profiling"]["cache_hit"] is True
    assert data2["profiling"]["estimated_cost_usd"] == 0.0
    assert data2["profiling"]["model"] == "semantic_cache"

    # Query metrics endpoint to verify cache telemetry
    metrics_resp = client.get("/metrics")
    assert metrics_resp.status_code == 200
    metrics_data = metrics_resp.json()
    assert "cache" in metrics_data
    assert metrics_data["cache"]["hits"] >= 1
    assert metrics_data["cache"]["size"] >= 1
