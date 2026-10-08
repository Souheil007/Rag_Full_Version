"""Cross-Encoder re-ranking module to score and reorder retrieved candidates."""

from typing import Any
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class Reranker:
    """Scores (query, candidate_chunk) pairs using a Cross-Encoder model."""

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        enabled: bool = True,
    ) -> None:
        """Initialize Reranker with model identifier.

        Args:
            model_name: HuggingFace cross-encoder model name.
            enabled: Boolean flag to enable or bypass reranking.
        """
        self.model_name = model_name
        self.enabled = enabled
        self._model = None

    def _init_model(self) -> None:
        """Lazily initialize the cross-encoder model."""
        if self._model is not None or not self.enabled:
            return

        try:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self.model_name)
            logger.info(f"Loaded CrossEncoder model: {self.model_name}")
        except Exception as exc:
            logger.warning(f"CrossEncoder model unavailable ({exc}). Using lexical overlap fallback.")
            self._model = "fallback"

    def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Re-score candidate documents and return the top-k highest scoring.

        Args:
            query: User search query.
            documents: List of candidate document dicts.
            top_k: Number of highest-ranked documents to return.

        Returns:
            Re-ordered list of document dicts with updated 'rerank_score'.
        """
        if not documents or not self.enabled:
            return documents[:top_k]

        self._init_model()

        # Transformer Cross-Encoder Scoring
        if self._model is not None and self._model != "fallback":
            pairs = [[query, doc.get("chunk_text", "")] for doc in documents]
            scores = self._model.predict(pairs)
            for doc, score in zip(documents, scores):
                doc["rerank_score"] = float(score)
            documents.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
            return documents[:top_k]

        # Lightweight Lexical Fallback Cross-Scorer
        query_terms = set(query.lower().split())
        for doc in documents:
            text = doc.get("chunk_text", "").lower()
            overlap = sum(1 for term in query_terms if term in text)
            length_penalty = len(text.split()) / 500.0
            doc["rerank_score"] = round(overlap - (length_penalty * 0.1), 4)

        documents.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        return documents[:top_k]
