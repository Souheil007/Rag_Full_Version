"""Bounded vector-based semantic cache with LRU eviction and quality filtering."""

from collections import OrderedDict
import time
from typing import Any
from src.utils.helpers import get_logger

logger = get_logger(__name__)


def compute_cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Compute cosine similarity between two float vectors.

    Args:
        v1: First vector.
        v2: Second vector.

    Returns:
        Cosine similarity score between -1.0 and 1.0.
    """
    if len(v1) != len(v2) or not v1:
        return 0.0

    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = sum(a * a for a in v1) ** 0.5
    norm_b = sum(b * b for b in v2) ** 0.5

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class SemanticCache:
    """In-memory semantic vector cache with bounded LRU eviction and TTL."""

    def __init__(
        self,
        enabled: bool = True,
        similarity_threshold: float = 0.95,
        max_entries: int = 1000,
        ttl_seconds: int = 86400,
        cache_only_verified: bool = True,
    ) -> None:
        """Initialize semantic cache settings.

        Args:
            enabled: Whether caching is actively enabled.
            similarity_threshold: Minimum cosine similarity to treat as a hit.
            max_entries: Maximum number of cache entries to store before LRU eviction.
            ttl_seconds: Lifespan of a cache entry in seconds.
            cache_only_verified: Whether to reject unverified or fallback responses.
        """
        self.enabled = enabled
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self.cache_only_verified = cache_only_verified

        # OrderedDict stores: key -> {query, embedding, answer, sources, created_at, last_accessed_at, is_verified}
        self._cache: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._hits: int = 0
        self._misses: int = 0

    def lookup(
        self,
        query: str,
        query_embedding: list[float],
    ) -> dict[str, Any] | None:
        """Search cache for semantically matching responses.

        Args:
            query: User search query text.
            query_embedding: Dense embedding vector of the query.

        Returns:
            Matched response dictionary or None if cache miss or expired.
        """
        if not self.enabled or not query_embedding:
            return None

        clean_query = query.strip().lower()
        now = time.time()

        # 1. Exact match check (ultra-fast O(1))
        if clean_query in self._cache:
            entry = self._cache[clean_query]
            if now - entry["created_at"] <= self.ttl_seconds:
                entry["last_accessed_at"] = now
                self._cache.move_to_end(clean_query)
                self._hits += 1
                return {
                    "answer": entry["answer"],
                    "sources": entry["sources"],
                    "similarity": 1.0,
                    "cached_query": entry["query"],
                }
            else:
                del self._cache[clean_query]

        # 2. Vector similarity scan across cached embeddings
        best_match_key: str | None = None
        best_similarity: float = -1.0
        expired_keys: list[str] = []

        for key, entry in self._cache.items():
            if now - entry["created_at"] > self.ttl_seconds:
                expired_keys.append(key)
                continue

            sim = compute_cosine_similarity(query_embedding, entry["embedding"])
            if sim > best_similarity:
                best_similarity = sim
                best_match_key = key

        # Clean expired keys
        for exp_key in expired_keys:
            self._cache.pop(exp_key, None)

        # Check if best similarity crosses threshold
        if best_match_key and best_similarity >= self.similarity_threshold:
            hit_entry = self._cache[best_match_key]
            hit_entry["last_accessed_at"] = now
            self._cache.move_to_end(best_match_key)
            self._hits += 1
            return {
                "answer": hit_entry["answer"],
                "sources": hit_entry["sources"],
                "similarity": best_similarity,
                "cached_query": hit_entry["query"],
            }

        self._misses += 1
        return None

    def store(
        self,
        query: str,
        query_embedding: list[float],
        answer: str,
        sources: list[dict[str, Any]] | None = None,
        is_verified: bool = True,
        disallowed_phrases: list[str] | None = None,
    ) -> bool:
        """Store query and verified answer in cache with LRU eviction.

        Args:
            query: Original query text.
            query_embedding: Dense embedding vector.
            answer: Model generated answer.
            sources: List of source documents.
            is_verified: Whether the answer passed factual grounding guardrails.
            disallowed_phrases: Phrases indicating a fallback or refusal to suppress caching.

        Returns:
            True if stored successfully, False if rejected by quality policy.
        """
        if not self.enabled or not query.strip() or not answer.strip() or not query_embedding:
            return False

        # Quality gate: Reject unverified responses if configured
        if self.cache_only_verified and not is_verified:
            logger.info("Semantic cache skipped: answer is not verified by guardrails.")
            return False

        # Quality gate: Reject fallback and refusal answers to prevent cache poisoning
        disallowed = disallowed_phrases or [
            "cannot find sufficient factual backing",
            "insufficient factual backing",
            "i cannot answer",
            "i don't have enough information",
        ]
        lower_answer = answer.lower()
        if any(phrase.lower() in lower_answer for phrase in disallowed):
            logger.info("Semantic cache skipped: answer contains fallback or refusal phrase.")
            return False

        clean_query = query.strip().lower()

        # Enforce LRU capacity limit
        if clean_query not in self._cache and len(self._cache) >= self.max_entries:
            evicted_key, _ = self._cache.popitem(last=False)
            logger.debug(f"Semantic cache capacity reached ({self.max_entries}). Evicted LRU key: {evicted_key}")

        now = time.time()
        self._cache[clean_query] = {
            "query": query.strip(),
            "embedding": query_embedding,
            "answer": answer,
            "sources": sources or [],
            "created_at": now,
            "last_accessed_at": now,
            "is_verified": is_verified,
        }
        self._cache.move_to_end(clean_query)
        return True

    def clear(self) -> None:
        """Clear all entries in the cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def size(self) -> int:
        """Return the current number of cached entries."""
        return len(self._cache)

    def stats(self) -> dict[str, Any]:
        """Return hit, miss, and capacity statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total) if total > 0 else 0.0
        return {
            "size": len(self._cache),
            "max_entries": self.max_entries,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 4),
            "enabled": self.enabled,
        }
