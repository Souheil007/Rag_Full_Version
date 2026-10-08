"""Prompt templates and formatting utilities for RAG generation."""

from typing import Any

DEFAULT_RAG_SYSTEM_PROMPT = """You are a helpful and accurate AI assistant.
Answer the user question using ONLY the provided context. If the context does not contain enough information to answer, state clearly that you do not know."""


def format_rag_prompt(query: str, retrieved_docs: list[dict[str, Any]]) -> str:
    """Format user query and retrieved context documents into a structured prompt.

    Args:
        query: User input question.
        retrieved_docs: List of document chunks retrieved from the vector store.

    Returns:
        Structured prompt string ready for LLM consumption.
    """
    if not retrieved_docs:
        context_str = "No relevant context found."
    else:
        context_blocks = []
        for i, doc in enumerate(retrieved_docs, start=1):
            source = doc.get("metadata", {}).get("filename", "Unknown source")
            text = doc.get("chunk_text", "").strip()
            context_blocks.append(f"[{i}] (Source: {source})\n{text}")
        context_str = "\n\n".join(context_blocks)

    return f"""Context Information:
---------------------
{context_str}
---------------------

User Question: {query}

Answer:"""
