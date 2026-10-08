"""Hybrid retriever combining Dense Vector and Sparse BM25 with Reciprocal Rank Fusion (RRF)."""

from typing import Any
from src.embeddings.embedder import Embedder
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.reranker import Reranker
from src.utils.helpers import get_logger
from src.vectordb.vector_store import VectorStore

logger = get_logger(__name__)


class HybridRetriever:
    """Combines Dense semantic search and BM25 sparse search with Reciprocal Rank Fusion."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: Embedder,
        bm25_retriever: BM25Retriever | None = None,
        reranker: Reranker | None = None,
        dense_weight: float = 0.5,
        sparse_weight: float = 0.5,
        rrf_k: int = 60,
    ) -> None:
        """Initialize HybridRetriever components and fusion parameters.

        Args:
            vector_store: VectorStore instance for dense search.
            embedder: Embedder instance for query vectorization.
            bm25_retriever: BM25Retriever instance for keyword search.
            reranker: Optional Reranker instance for cross-encoder scoring.
            dense_weight: Weight multiplier for dense ranks.
            sparse_weight: Weight multiplier for sparse BM25 ranks.
            rrf_k: Constant k for smoothing Reciprocal Rank Fusion formula.
        """
        self.vector_store = vector_store
        self.embedder = embedder
        self.bm25_retriever = bm25_retriever or BM25Retriever()
        self.reranker = reranker or Reranker(enabled=False)
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        self.rrf_k = rrf_k

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        candidate_multiplier: int = 4,
    ) -> list[dict[str, Any]]:
        """Retrieve documents using weighted RRF fusion over dense and sparse results.

        Args:
            query: User search query.
            top_k: Final number of ranked documents to return.
            candidate_multiplier: Factor to over-fetch candidates for fusion & reranking.

        Returns:
            List of ranked document dictionaries with fused scores.
        """
        candidates_to_fetch = top_k * candidate_multiplier

        # 1. Fetch Dense Candidates
        query_emb = self.embedder.embed_text(query)
        dense_results = self.vector_store.query(query_embedding=query_emb, top_k=candidates_to_fetch)

        # 2. Fetch Sparse BM25 Candidates
        sparse_results = self.bm25_retriever.retrieve(query=query, top_k=candidates_to_fetch)

        # 3. Reciprocal Rank Fusion (RRF)
        # RRF_Score(d) = sum( weight_m / (k + rank_m(d)) )
        fused_scores: dict[str, float] = {}
        doc_map: dict[str, dict[str, Any]] = {}

        for rank, doc in enumerate(dense_results, start=1):
            doc_id = doc.get("chunk_id", str(rank))
            doc_map[doc_id] = doc
            fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + (
                self.dense_weight / (self.rrf_k + rank)
            )

        for rank, doc in enumerate(sparse_results, start=1):
            doc_id = doc.get("chunk_id", str(rank))
            if doc_id not in doc_map:
                doc_map[doc_id] = doc
            fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + (
                self.sparse_weight / (self.rrf_k + rank)
            )

        # Build fused list
        fused_docs = []
        for doc_id, score in fused_scores.items():
            item = dict(doc_map[doc_id])
            item["rrf_score"] = round(score, 6)
            fused_docs.append(item)

        fused_docs.sort(key=lambda x: x["rrf_score"], reverse=True)

        # 4. Optional Re-ranking
        if self.reranker.enabled:
            return self.reranker.rerank(query=query, documents=fused_docs, top_k=top_k)

        return fused_docs[:top_k]
