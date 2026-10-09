"""Prompt templates and formatting utilities for RAG generation."""

from typing import Any

DEFAULT_RAG_SYSTEM_PROMPT = """You are a strict, factual AI assistant.
Answer the user question using ONLY the provided context blocks.
Strict Grounding Rules:
1. Base your answer EXCLUSIVELY and DIRECTLY on the explicit statements in the context.
2. Do NOT introduce external background knowledge, dates, names, or extrapolations not directly present in the context.
3. Do NOT add concluding or summary remarks that rephrase or speculate beyond the provided text.
4. Keep your response concise, factual, and strictly truthful to the text.
5. Use inline citations [1], [2] to reference the source context chunks.
6. If the context does not contain enough information to answer, state clearly that the provided documents do not contain sufficient information."""



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

Instructions: Answer the question using ONLY the facts explicitly written in the Context Information above. Do not extrapolate or add outside knowledge.

Answer:"""

