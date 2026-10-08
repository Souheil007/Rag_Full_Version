"""Unified retrieval facade supporting Dense, BM25, Hybrid (RRF), and Re-ranked search."""

from typing import Any, Literal
from src.chunking.compression import ContextCompressor
from src.embeddings.embedder import Embedder
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.reranker import Reranker
from src.utils.helpers import get_logger
from src.vectordb.vector_store import VectorStore

logger = get_logger(__name__)

RetrievalMode = Literal["dense", "bm25", "hybrid", "hybrid_rerank"]


class Retriever:
    """Unified retrieval engine coordinating Dense, BM25, Hybrid RRF, and Re-ranking."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: Embedder,
        bm25_retriever: BM25Retriever | None = None,
        reranker: Reranker | None = None,
        compressor: ContextCompressor | None = None,
        default_mode: RetrievalMode = "hybrid_rerank",
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> None:
        """Initialize unified retriever components and defaults.

        Args:
            vector_store: VectorStore instance for dense vector querying.
            embedder: Embedder instance for query text vectorization.
            bm25_retriever: Optional BM25Retriever instance for keyword search.
            reranker: Optional Reranker instance for cross-encoder scoring.
            compressor: Optional ContextCompressor for sentence pruning.
            default_mode: Default retrieval strategy ('dense', 'bm25', 'hybrid', 'hybrid_rerank').
            top_k: Default number of top documents to return.
            score_threshold: Minimum similarity cutoff for dense search.
        """
        self.vector_store = vector_store
        self.embedder = embedder
        self.bm25_retriever = bm25_retriever or BM25Retriever()
        self.reranker = reranker or Reranker(enabled=True)
        self.compressor = compressor or ContextCompressor()
        self.default_mode = default_mode
        self.top_k = top_k
        self.score_threshold = score_threshold

        # Internal hybrid engine
        self._hybrid_engine = HybridRetriever(
            vector_store=self.vector_store,
            embedder=self.embedder,
            bm25_retriever=self.bm25_retriever,
            reranker=self.reranker,
        )

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        mode: RetrievalMode | None = None,
        compress: bool = False,
    ) -> list[dict[str, Any]]:
        """Retrieve most relevant document chunks based on specified mode.

        Args:
            query: User search query string.
            top_k: Optional override for the number of results to fetch.
            mode: Search strategy ('dense', 'bm25', 'hybrid', 'hybrid_rerank').
            compress: Whether to prune irrelevant sentences from retrieved chunks.

        Returns:
            List of matching document chunks sorted by relevance score.
        """
        k = top_k or self.top_k
        search_mode = mode or self.default_mode

        if search_mode == "dense":
            query_vector = self.embedder.embed_text(query)
            results = self.vector_store.query(query_embedding=query_vector, top_k=k)
            results = [
                doc for doc in results if doc.get("score", 1.0) >= self.score_threshold
            ]
        elif search_mode == "bm25":
            results = self.bm25_retriever.retrieve(query=query, top_k=k)
        elif search_mode == "hybrid":
            self.reranker.enabled = False
            results = self._hybrid_engine.retrieve(query=query, top_k=k)
        elif search_mode == "hybrid_rerank":
            self.reranker.enabled = True
            results = self._hybrid_engine.retrieve(query=query, top_k=k)
        else:
            logger.warning(f"Unknown retrieval mode '{search_mode}'. Falling back to dense.")
            query_vector = self.embedder.embed_text(query)
            results = self.vector_store.query(query_embedding=query_vector, top_k=k)

        if compress:
            results = self.compressor.compress_documents(query=query, documents=results)

        logger.info(f"Retrieved {len(results)} chunks [mode={search_mode}, compress={compress}] for: '{query}'")
        return results
