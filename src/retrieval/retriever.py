"""Retrieval module combining embedding generation and vector search."""

from typing import Any
from src.embeddings.embedder import Embedder
from src.utils.helpers import get_logger
from src.vectordb.vector_store import VectorStore

logger = get_logger(__name__)


class Retriever:
    """Coordinates query vectorization and semantic search against vector store."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: Embedder,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> None:
        """Initialize Retriever with store, embedder, and search parameters.

        Args:
            vector_store: Instantiated VectorStore.
            embedder: Instantiated Embedder.
            top_k: Number of chunks to retrieve.
            score_threshold: Minimum similarity score cutoff.
        """
        self.vector_store = vector_store
        self.embedder = embedder
        self.top_k = top_k
        self.score_threshold = score_threshold

    def retrieve(self, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        """Retrieve most relevant document chunks for a query string.

        Args:
            query: User search query text.
            top_k: Optional override for the number of results to fetch.

        Returns:
            List of matching document chunks sorted by relevance.
        """
        k = top_k or self.top_k
        query_vector = self.embedder.embed_text(query)
        results = self.vector_store.query(query_embedding=query_vector, top_k=k)

        filtered_results = [
            doc for doc in results if doc.get("score", 1.0) >= self.score_threshold
        ]
        logger.info(f"Retrieved {len(filtered_results)} relevant chunks for query: '{query}'")
        return filtered_results
