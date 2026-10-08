"""Text embeddings generator supporting local and cloud providers."""

from typing import Any
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class Embedder:
    """Generates vector representations of text queries and documents."""

    def __init__(
        self,
        provider: str = "sentence_transformers",
        model_name: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
    ) -> None:
        """Initialize Embedder with provider and model settings.

        Args:
            provider: Embedding provider name ('sentence_transformers', 'openai', 'gemini').
            model_name: Pretrained model identifier.
            dimension: Expected vector dimension.
        """
        self.provider = provider
        self.model_name = model_name
        self.dimension = dimension
        self._model = None

    def _init_model(self) -> None:
        """Lazily initialize the embedding model instance."""
        if self._model is not None:
            return

        if self.provider == "sentence_transformers":
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded SentenceTransformer model: {self.model_name}")
            except ImportError:
                logger.warning("sentence-transformers not installed. Using dummy embeddings.")
                self._model = None
        else:
            logger.info(f"Initialized API provider for embeddings: {self.provider}")

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding vector for a single text string.

        Args:
            text: Text to vectorize.

        Returns:
            List of float values representing the embedding vector.
        """
        self._init_model()
        if self._model is not None and hasattr(self._model, "encode"):
            vector = self._model.encode(text).tolist()
            return vector
        # Fallback dummy vector for scaffolding / testing
        return [0.0] * self.dimension

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a batch of text strings.

        Args:
            texts: List of text strings to vectorize.

        Returns:
            List of embedding vectors.
        """
        if not texts:
            return []

        self._init_model()
        if self._model is not None and hasattr(self._model, "encode"):
            vectors = self._model.encode(texts).tolist()
            return vectors
        # Fallback dummy vectors
        return [[0.0] * self.dimension for _ in texts]
