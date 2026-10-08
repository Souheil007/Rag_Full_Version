"""FastAPI REST API endpoints for document indexing and querying."""

from typing import Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.chunking.chunker import TextChunker
from src.embeddings.embedder import Embedder
from src.ingestion.loader import DocumentLoader
from src.llm.llm_client import LLMClient
from src.prompts.prompt_templates import (
    DEFAULT_RAG_SYSTEM_PROMPT,
    format_rag_prompt,
)
from src.retrieval.retriever import Retriever
from src.utils.helpers import get_logger, load_config
from src.vectordb.vector_store import VectorStore

logger = get_logger(__name__)


class QueryRequest(BaseModel):
    """Payload model for user query requests."""

    query: str = Field(..., description="The query/question to search and answer.")
    top_k: int | None = Field(default=5, description="Number of context chunks to retrieve.")


class QueryResponse(BaseModel):
    """Response model for query answers and retrieved citations."""

    query: str
    answer: str
    sources: list[dict[str, Any]]


class IndexDirectoryRequest(BaseModel):
    """Payload model for indexing a directory of documents."""

    dir_path: str = Field(default="data", description="Path to directory containing files.")


def create_app(config: dict[str, Any] | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        config: Optional configuration dictionary.

    Returns:
        Configured FastAPI app instance.
    """
    cfg = config or load_config()

    app = FastAPI(
        title=cfg.get("app", {}).get("name", "RAG Full Version"),
        version=cfg.get("app", {}).get("version", "1.0.0"),
    )

    # Initialize RAG Pipeline components
    loader = DocumentLoader(
        supported_extensions=cfg.get("ingestion", {}).get("supported_extensions")
    )
    chunker = TextChunker(
        chunk_size=cfg.get("chunking", {}).get("chunk_size", 500),
        chunk_overlap=cfg.get("chunking", {}).get("chunk_overlap", 50),
    )
    embedder = Embedder(
        provider=cfg.get("embeddings", {}).get("provider", "sentence_transformers"),
        model_name=cfg.get("embeddings", {}).get("model_name", "all-MiniLM-L6-v2"),
        dimension=cfg.get("embeddings", {}).get("dimension", 384),
    )
    vector_store = VectorStore(
        provider=cfg.get("vectordb", {}).get("provider", "chroma"),
        collection_name=cfg.get("vectordb", {}).get("collection_name", "rag_documents"),
        persist_directory=cfg.get("vectordb", {}).get("persist_directory", "./chroma_db"),
    )
    retriever = Retriever(
        vector_store=vector_store,
        embedder=embedder,
        top_k=cfg.get("retrieval", {}).get("top_k", 5),
        score_threshold=cfg.get("retrieval", {}).get("score_threshold", 0.0),
    )
    llm_client = LLMClient(
        provider=cfg.get("llm", {}).get("provider", "gemini"),
        model_name=cfg.get("llm", {}).get("model_name", "gemini-1.5-flash"),
        temperature=cfg.get("llm", {}).get("temperature", 0.2),
        max_output_tokens=cfg.get("llm", {}).get("max_output_tokens", 1024),
    )

    @app.get("/health")
    def health_check() -> dict[str, str]:
        """Health check endpoint to verify server status."""
        return {"status": "ok", "app": cfg.get("app", {}).get("name", "RAG")}

    @app.post("/index", response_model=dict[str, Any])
    def index_directory(req: IndexDirectoryRequest) -> dict[str, Any]:
        """Load, chunk, embed, and store documents from a directory."""
        docs = loader.load_directory(req.dir_path)
        if not docs:
            raise HTTPException(
                status_code=404,
                detail=f"No valid documents found in {req.dir_path}",
            )

        chunks = chunker.chunk_documents(docs)
        texts = [c["chunk_text"] for c in chunks]
        embeddings = embedder.embed_batch(texts)
        vector_store.add_documents(chunks, embeddings)

        return {
            "status": "success",
            "indexed_documents": len(docs),
            "indexed_chunks": len(chunks),
        }

    @app.post("/query", response_model=QueryResponse)
    def query_rag(req: QueryRequest) -> QueryResponse:
        """Retrieve relevant context and generate answer for query."""
        retrieved_docs = retriever.retrieve(req.query, top_k=req.top_k)
        prompt = format_rag_prompt(req.query, retrieved_docs)
        answer = llm_client.generate(prompt, system_prompt=DEFAULT_RAG_SYSTEM_PROMPT)

        return QueryResponse(
            query=req.query,
            answer=answer,
            sources=retrieved_docs,
        )

    return app
