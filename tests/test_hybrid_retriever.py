"""Tests for Hybrid Retriever, BM25, Cross-Encoder Reranker, and Context Compressor."""

import unittest
from src.chunking.compression import ContextCompressor
from src.embeddings.embedder import Embedder
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.reranker import Reranker
from src.vectordb.vector_store import VectorStore


class TestHybridRetriever(unittest.TestCase):
    """Test suite for sparse, hybrid, and reranked retrieval."""

    def test_bm25_exact_keyword_matching(self):
        """Verify BM25 accurately finds documents with specific acronyms/terms."""
        documents = [
            {"chunk_id": "c1", "chunk_text": "Photosynthesis is the process used by plants."},
            {"chunk_id": "c2", "chunk_text": "Error Code 403 indicates Forbidden access."},
            {"chunk_id": "c3", "chunk_text": "The quick brown fox jumps over the lazy dog."},
        ]
        bm25 = BM25Retriever()
        bm25.fit(documents)

        results = bm25.retrieve("Error Code 403", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["chunk_id"], "c2")
        self.assertGreater(results[0]["score"], 0.0)

    def test_reranker_reordering(self):
        """Verify Reranker scores and re-orders candidate documents."""
        reranker = Reranker(enabled=True)
        query = "database scaling"
        candidates = [
            {"chunk_id": "c1", "chunk_text": "General cooking recipes for dinner."},
            {"chunk_id": "c2", "chunk_text": "Relational database scaling and sharding strategies."},
        ]
        reranked = reranker.rerank(query=query, documents=candidates, top_k=2)
        self.assertEqual(len(reranked), 2)
        self.assertEqual(reranked[0]["chunk_id"], "c2")
        self.assertIn("rerank_score", reranked[0])

    def test_hybrid_retriever_rrf_fusion(self):
        """Verify HybridRetriever fuses dense and sparse results using RRF."""
        embedder = Embedder(dimension=8)
        vector_store = VectorStore(provider="in_memory")
        bm25 = BM25Retriever()

        docs = [
            {"chunk_id": "doc1", "chunk_text": "Retrieval Augmented Generation with LLMs."},
            {"chunk_id": "doc2", "chunk_text": "Transformer self-attention mechanism in deep learning."},
            {"chunk_id": "doc3", "chunk_text": "Financial quarterly earnings report Q3."},
        ]
        embeddings = embedder.embed_batch([d["chunk_text"] for d in docs])
        vector_store.add_documents(docs, embeddings)
        bm25.fit(docs)

        hybrid = HybridRetriever(
            vector_store=vector_store,
            embedder=embedder,
            bm25_retriever=bm25,
            reranker=Reranker(enabled=False),
        )

        results = hybrid.retrieve("Retrieval Augmented Generation", top_k=2)
        self.assertEqual(len(results), 2)
        self.assertIn("rrf_score", results[0])
        self.assertEqual(results[0]["chunk_id"], "doc1")

    def test_context_compressor(self):
        """Verify ContextCompressor prunes irrelevant sentences from chunks."""
        compressor = ContextCompressor(max_sentences_per_chunk=1)
        long_chunk = (
            "The sky is blue today. "
            "Python 3.12 introduces major performance improvements and type syntax. "
            "I like coffee in the morning."
        )
        query = "Python performance improvements"
        compressed = compressor.compress_chunk(query, long_chunk)
        self.assertIn("Python 3.12 introduces major performance improvements", compressed)
        self.assertNotIn("The sky is blue today", compressed)


if __name__ == "__main__":
    unittest.main()
