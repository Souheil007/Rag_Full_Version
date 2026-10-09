"""Text chunking module with recursive and boundary-aware splitting."""

from typing import Any
from src.utils.helpers import get_logger

logger = get_logger(__name__)

DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", "? ", "! ", " ", ""]


class TextChunker:
    """Splits text documents into smaller chunks for embeddings and retrieval."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        strategy: str = "recursive",
        separators: list[str] | None = None,
    ) -> None:
        """Initialize TextChunker with chunk size and strategy.

        Args:
            chunk_size: Maximum character length per text chunk.
            chunk_overlap: Number of overlapping characters between chunks.
            strategy: Chunking strategy ('recursive' or 'fixed').
            separators: List of separator strings ordered by split priority.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        self.separators = separators or DEFAULT_SEPARATORS

    def _split_recursive(self, text: str, separators: list[str]) -> list[str]:
        """Split text recursively using hierarchical separators without breaking words.

        Args:
            text: Input text string.
            separators: Remaining separators to try.

        Returns:
            List of split chunks respecting chunk_size.
        """
        final_chunks: list[str] = []

        # Find the first valid separator present in the text
        separator = separators[-1]
        new_separators = []
        for i, s in enumerate(separators):
            if s == "" or s in text:
                separator = s
                new_separators = separators[i + 1:]
                break

        # Split text by chosen separator
        splits = text.split(separator) if separator else list(text)

        current_doc: list[str] = []
        total_len = 0

        for s in splits:
            s_len = len(s)

            # If adding this segment exceeds chunk_size and we already have content
            if total_len + s_len + (len(separator) if current_doc else 0) > self.chunk_size:
                if current_doc:
                    joined = separator.join(current_doc).strip()
                    if joined:
                        final_chunks.append(joined)

                    # Backtrack to satisfy overlap
                    while current_doc and total_len > self.chunk_overlap:
                        removed = current_doc.pop(0)
                        total_len -= len(removed) + (len(separator) if current_doc else 0)

                # If the single segment itself is larger than chunk_size, recurse with next separator
                if s_len > self.chunk_size:
                    if new_separators:
                        sub_chunks = self._split_recursive(s, new_separators)
                        final_chunks.extend(sub_chunks)
                    else:
                        # Fallback for unbreakable giant words
                        final_chunks.append(s[:self.chunk_size])
                    continue

            current_doc.append(s)
            total_len += s_len + (len(separator) if len(current_doc) > 1 else 0)

        if current_doc:
            joined = separator.join(current_doc).strip()
            if joined:
                final_chunks.append(joined)

        return final_chunks

    def split_text(self, text: str) -> list[str]:
        """Split a raw string into text chunks without cutting words or sentences.

        Args:
            text: Raw input text.

        Returns:
            List of clean text chunks.
        """
        if not text or not text.strip():
            return []

        if self.strategy == "fixed":
            # Word-boundary aware fixed chunking
            words = text.split()
            chunks = []
            curr: list[str] = []
            curr_len = 0
            for w in words:
                if curr_len + len(w) + 1 > self.chunk_size and curr:
                    chunks.append(" ".join(curr))
                    # Retain overlap words
                    curr = []
                    curr_len = 0
                curr.append(w)
                curr_len += len(w) + 1
            if curr:
                chunks.append(" ".join(curr))
            return chunks

        # Default: Hierarchical recursive chunking
        return self._split_recursive(text.strip(), self.separators)

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
