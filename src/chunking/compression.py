"""Contextual compression module to extract query-relevant sentences from chunks."""

import re
from typing import Any
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class ContextCompressor:
    """Extracts and prunes noisy sentences from retrieved chunks to reduce token waste."""

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        """Initialize ContextCompressor.

        Args:
            max_sentences_per_chunk: Maximum number of relevant sentences to retain per chunk.
        """
        self.max_sentences_per_chunk = max_sentences_per_chunk

    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into individual sentences.

        Args:
            text: Raw input string.

        Returns:
            List of sentence strings.
        """
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def compress_chunk(self, query: str, chunk_text: str) -> str:
        """Filter chunk text to only include sentences sharing terms with the query.

        Args:
            query: User search query.
            chunk_text: Retrieved chunk text.

        Returns:
            Pruned chunk text.
        """
        sentences = self._split_into_sentences(chunk_text)
        if len(sentences) <= self.max_sentences_per_chunk:
            return chunk_text

        query_terms = set(re.findall(r"\b\w+\b", query.lower()))
        scored_sentences = []

        for idx, sentence in enumerate(sentences):
            sentence_terms = set(re.findall(r"\b\w+\b", sentence.lower()))
            overlap = len(query_terms.intersection(sentence_terms))
            scored_sentences.append((overlap, idx, sentence))

        # Keep highest overlap, preserving original sentence order
        scored_sentences.sort(key=lambda x: (x[0], -x[1]), reverse=True)
        top_sentences = scored_sentences[: self.max_sentences_per_chunk]
        top_sentences.sort(key=lambda x: x[1])

        return " ".join(s[2] for s in top_sentences)

    def compress_documents(
        self, query: str, documents: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Prune noisy sentences across a list of retrieved documents.

        Args:
            query: User search query.
            documents: List of retrieved document dictionaries.

        Returns:
            List of documents with compressed 'chunk_text'.
        """
        compressed = []
        for doc in documents:
            doc_copy = dict(doc)
            original_text = doc.get("chunk_text", "")
            doc_copy["chunk_text"] = self.compress_chunk(query, original_text)
            doc_copy["original_len"] = len(original_text)
            doc_copy["compressed_len"] = len(doc_copy["chunk_text"])
            compressed.append(doc_copy)
        return compressed
