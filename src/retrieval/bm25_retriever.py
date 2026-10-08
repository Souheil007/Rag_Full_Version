"""BM25 sparse keyword retrieval engine for exact term and acronym search."""

import math
import re
from typing import Any
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class BM25Retriever:
    """Computes BM25 (Okapi) ranking scores for sparse keyword retrieval."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        """Initialize BM25 parameters.

        Args:
            k1: Term frequency saturation parameter.
            b: Document length normalization parameter.
        """
        self.k1 = k1
        self.b = b
        self.corpus: list[dict[str, Any]] = []
        self.doc_lengths: list[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: dict[str, int] = {}
        self.idf: dict[str, float] = {}

    def _tokenize(self, text: str) -> list[str]:
        """Convert raw text into lowercase alphanumeric tokens.

        Args:
            text: Input text string.

        Returns:
            List of normalized word tokens.
        """
        return re.findall(r"\b\w+\b", text.lower())

    def fit(self, documents: list[dict[str, Any]]) -> None:
        """Index a collection of documents for BM25 search.

        Args:
            documents: List of chunk dicts with 'chunk_id', 'chunk_text', and 'metadata'.
        """
        self.corpus = documents
        self.doc_lengths = []
        self.doc_freqs = {}
        total_len = 0
        num_docs = len(documents)

        if num_docs == 0:
            return

        for doc in documents:
            tokens = self._tokenize(doc.get("chunk_text", ""))
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_len += doc_len

            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1

        self.avg_doc_len = total_len / num_docs if num_docs > 0 else 0.0

        # Compute Robertson-Spärck Jones IDF
        self.idf = {}
        for token, freq in self.doc_freqs.items():
            self.idf[token] = math.log((num_docs - freq + 0.5) / (freq + 0.5) + 1.0)

        logger.info(f"Fitted BM25 index with {num_docs} chunks and {len(self.idf)} unique terms.")

    def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Retrieve top-k documents matching the query based on BM25 scores.

        Args:
            query: User search query string.
            top_k: Maximum number of ranked documents to return.

        Returns:
            List of matching document chunks with BM25 score and rank.
        """
        if not self.corpus or not query.strip():
            return []

        query_tokens = self._tokenize(query)
        scores: list[float] = [0.0] * len(self.corpus)

        for i, doc in enumerate(self.corpus):
            doc_tokens = self._tokenize(doc.get("chunk_text", ""))
            doc_len = self.doc_lengths[i]
            tf_dict: dict[str, int] = {}
            for t in doc_tokens:
                tf_dict[t] = tf_dict.get(t, 0) + 1

            for token in query_tokens:
                if token not in tf_dict:
                    continue
                tf = tf_dict[token]
                idf = self.idf.get(token, 0.0)
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                scores[i] += idf * (numerator / denominator)

        # Pair scores with documents and rank
        scored_docs = []
        for i, score in enumerate(scores):
            if score > 0.0:
                doc_copy = dict(self.corpus[i])
                doc_copy["score"] = round(score, 4)
                scored_docs.append(doc_copy)

        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]
