# Project Rules and Guidelines

## Naming Conventions
- **Modules & Packages**: `snake_case` (e.g., `vector_store.py`, `prompt_templates.py`)
- **Classes**: `PascalCase` (e.g., `DocumentLoader`, `VectorStore`, `LLMClient`)
- **Functions & Methods**: `snake_case` (e.g., `load_documents()`, `get_embeddings()`)
- **Variables & Attributes**: `snake_case` (e.g., `chunk_size`, `top_k`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_CHUNK_SIZE`, `SUPPORTED_EXTENSIONS`)

## Docstring Standards (Google Style - Concise)
All modules, classes, and public functions must have concise Google-style docstrings:
- Keep the summary to 1-2 clear lines.
- Only include `Args`, `Returns`, `Yields`, and `Raises` when necessary.
- Avoid redundant prose or overly verbose explanations.

Example:
```python
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split input text into overlapping fixed-size chunks.

    Args:
        text: Raw text string to split.
        chunk_size: Maximum character length per chunk.
        overlap: Overlap length between consecutive chunks.

    Returns:
        List of chunk strings.
    """
    pass
```

## Architecture Principles
- **Modularity**: Each component in `src/` has a single responsibility.
- **Config-Driven**: Use `config.yaml` and environment variables for parameters.
- **Type Annotations**: Use modern Python type hints (`str`, `list[dict]`, `Optional[T]`, etc.) on all function signatures.
