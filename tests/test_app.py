"""Unit tests for RAG pipeline components and API endpoints."""

from src.chunking.chunker import TextChunker
from src.embeddings.embedder import Embedder
from src.prompts.prompt_templates import format_rag_prompt
from src.retrieval.retriever import Retriever
from src.vectordb.vector_store import VectorStore


def test_chunker_basic():
    """Verify that TextChunker divides text into appropriate chunks."""
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    sample_text = "This is a test document. " * 5
    chunks = chunker.split_text(sample_text)
    assert len(chunks) > 0
    assert all(len(c) <= 50 for c in chunks)


def test_prompt_formatting():
    """Verify that prompt template formats sources and query properly."""
    query = "What is RAG?"
    docs = [
        {
            "chunk_text": "RAG stands for Retrieval-Augmented Generation.",
            "metadata": {"filename": "intro.txt"},
        }
    ]
    prompt = format_rag_prompt(query, docs)
    assert "What is RAG?" in prompt
    assert "Retrieval-Augmented Generation" in prompt
    assert "intro.txt" in prompt


def test_vector_store_in_memory_flow():
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
    assert len(results) == 2
