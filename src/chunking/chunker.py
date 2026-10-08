"""Text chunking module with recursive and fixed-size splitting."""

from typing import Any
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class TextChunker:
    """Splits text documents into smaller chunks for embeddings and retrieval."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        strategy: str = "recursive",
    ) -> None:
        """Initialize TextChunker with chunk size and strategy.

        Args:
            chunk_size: Maximum character length per text chunk.
            chunk_overlap: Number of overlapping characters between chunks.
            strategy: Chunking strategy ('recursive' or 'fixed').
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy

    def split_text(self, text: str) -> list[str]:
        """Split a raw string into text chunks.

        Args:
            text: Raw input text.

        Returns:
            List of text chunks.
        """
        if not text or not text.strip():
            return []

        chunks: list[str] = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end == text_len:
                break
            start += self.chunk_size - self.chunk_overlap

        return chunks

    def chunk_documents(self, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Split a list of ingested documents into chunked records.

        Args:
            documents: List of document dicts with 'content' and 'metadata'.

        Returns:
            List of chunk dicts with 'chunk_text', 'chunk_id', and 'metadata'.
        """
        chunked_results = []
        for doc_idx, doc in enumerate(documents):
            raw_text = doc.get("content", "")
            base_meta = doc.get("metadata", {})
            text_chunks = self.split_text(raw_text)

            for chunk_idx, text in enumerate(text_chunks):
                chunk_record = {
                    "chunk_id": f"doc_{doc_idx}_chunk_{chunk_idx}",
                    "chunk_text": text,
                    "metadata": {
                        **base_meta,
                        "chunk_index": chunk_idx,
                        "total_chunks": len(text_chunks),
                    },
                }
                chunked_results.append(chunk_record)

        logger.info(f"Chunked {len(documents)} documents into {len(chunked_results)} total chunks.")
        return chunked_results
