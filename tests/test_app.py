"""Unit tests for RAG pipeline components and API endpoints."""

import unittest
from src.chunking.chunker import TextChunker
from src.embeddings.embedder import Embedder
from src.prompts.prompt_templates import format_rag_prompt
from src.retrieval.retriever import Retriever
from src.vectordb.vector_store import VectorStore


class TestApp(unittest.TestCase):
    """Test cases for chunking, vector store, and prompt formatting."""

    def test_chunker_basic(self):
        """Verify that TextChunker divides text into appropriate chunks."""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        sample_text = "This is a test document. " * 5
        chunks = chunker.split_text(sample_text)
        self.assertGreater(len(chunks), 0)
        self.assertTrue(all(len(c) <= 50 for c in chunks))

    def test_prompt_formatting(self):
        """Verify that prompt template formats sources and query properly."""
        query = "What is RAG?"
        docs = [
            {
                "chunk_text": "RAG stands for Retrieval-Augmented Generation.",
                "metadata": {"filename": "intro.txt"},
            }
        ]
        prompt = format_rag_prompt(query, docs)
        self.assertIn("What is RAG?", prompt)
        self.assertIn("Retrieval-Augmented Generation", prompt)
        self.assertIn("intro.txt", prompt)

    def test_vector_store_in_memory_flow(self):
        """Verify end-to-end embedding, indexing, and retrieval flow."""
        embedder = Embedder(dimension=8)
        vector_store = VectorStore(provider="in_memory")

        chunks = [
            {"chunk_id": "c1", "chunk_text": "Machine learning basics.", "metadata": {}},
            {"chunk_id": "c2", "chunk_text": "Deep learning architectures.", "metadata": {}},
        ]
        embeddings = embedder.embed_batch([c["chunk_text"] for c in chunks])
        vector_store.add_documents(chunks, embeddings)

        retriever = Retriever(vector_store=vector_store, embedder=embedder, top_k=2)
        results = retriever.retrieve("learning")
        self.assertEqual(len(results), 2)

    def test_sentry_debug_endpoint(self):
        """Verify that /sentry-debug triggers ZeroDivisionError for Sentry verification."""
        try:
            from src.api.routes import create_app

            app = create_app()
            # Find route handler
            route_handler = next(
                (r.endpoint for r in app.routes if getattr(r, "path", None) == "/sentry-debug"),
                None,
            )
            self.assertIsNotNone(route_handler)
            with self.assertRaises(ZeroDivisionError):
                route_handler()
        except ImportError:
            self.skipTest("fastapi not installed in environment.")



if __name__ == "__main__":
    unittest.main()

