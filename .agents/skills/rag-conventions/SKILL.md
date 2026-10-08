---
name: rag-conventions
description: Enforces clean Python naming conventions, concise Google-style docstrings, and modular architecture for this RAG project.
---

# RAG Project Coding & Documentation Conventions

This skill provides guidelines and templates for developing modules in the RAG project.

## 1. Naming Conventions

| Entity | Convention | Example |
| :--- | :--- | :--- |
| **Directory / Module** | `snake_case` | `ingestion/`, `loader.py`, `vector_store.py` |
| **Class** | `PascalCase` | `TextChunker`, `ChromaVectorStore`, `GeminiClient` |
| **Function / Method** | `snake_case` | `load_pdf()`, `generate_response()`, `similarity_search()` |
| **Variable / Parameter** | `snake_case` | `chunk_size`, `query_text`, `embedding_model` |
| **Constant** | `UPPER_SNAKE_CASE` | `DEFAULT_TOP_K`, `CONFIG_PATH` |

## 2. Concise Google-Style Docstrings

Every module, class, and public function must include a concise Google-style docstring.
Keep explanations tight and focused:

### Module Header
```python
"""Data ingestion module for loading documents from various file types."""
```

### Class Header
```python
class TextChunker:
    """Splits raw text into manageable chunks for vector embedding."""
```

### Method / Function
```python
def retrieve_top_k(query: str, top_k: int = 5) -> list[dict]:
    """Retrieve top-k relevant chunks for a user query.

    Args:
        query: User search query.
        top_k: Number of relevant documents to return.

    Returns:
        List of document dictionaries containing text and metadata.
    """
```

## 3. Project Structure Reference

```
rag-project/
├── README.md
├── requirements.txt
├── .env
├── .gitignore
├── config.yaml
├── src/
│   ├── ingestion/
│   ├── chunking/
│   ├── embeddings/
│   ├── vectordb/
│   ├── retrieval/
│   ├── prompts/
│   ├── llm/
│   ├── api/
│   └── utils/
├── tests/
├── logs/
└── main.py
```
