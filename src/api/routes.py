"""FastAPI REST API endpoints with distributed tracing and operational metrics."""

from typing import Any, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.chunking.chunker import TextChunker
from src.embeddings.embedder import Embedder
from src.ingestion.loader import DocumentLoader
from src.llm.llm_client import LLMClient
from src.observability.metrics_collector import MetricsCollector
from src.observability.sentry_monitor import SentryMonitor
from src.observability.span_exporter import SpanExporter
from src.observability.tracer import Tracer
from src.prompts.prompt_templates import (
    DEFAULT_RAG_SYSTEM_PROMPT,
    format_rag_prompt,
)
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.reranker import Reranker
from src.retrieval.retriever import Retriever
from src.utils.helpers import get_logger, load_config
from src.vectordb.vector_store import VectorStore

logger = get_logger(__name__)


class QueryRequest(BaseModel):
    """Payload model for user query requests."""

    query: str = Field(..., description="The query/question to search and answer.")
    top_k: int | None = Field(default=5, description="Number of context chunks to retrieve.")
    search_type: Literal["dense", "bm25", "hybrid", "hybrid_rerank"] = Field(
        default="hybrid_rerank",
        description="Search strategy: 'dense', 'bm25', 'hybrid', or 'hybrid_rerank'.",
    )
    compress_context: bool = Field(
        default=False,
        description="Whether to prune noisy sentences from retrieved chunks.",
    )


class QueryResponse(BaseModel):
    """Response model for query answers, citations, and execution telemetry."""

    query: str
    search_type: str
    answer: str
    sources: list[dict[str, Any]]
    trace_id: str
    latency_ms: float
    estimated_cost_usd: float


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

    # Initialize Sentry before FastAPI application creation
    sentry_monitor = SentryMonitor()

    app = FastAPI(
        title=cfg.get("app", {}).get("name", "RAG Full Version"),
        version=cfg.get("app", {}).get("version", "1.0.0"),
    )

    # Observability & Metrics
    tracer = Tracer()
    metrics = MetricsCollector()
    exporter = SpanExporter()

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
    bm25_retriever = BM25Retriever()
    reranker = Reranker(enabled=True)

    # Unified Retriever Facade
    retriever = Retriever(
        vector_store=vector_store,
        embedder=embedder,
        bm25_retriever=bm25_retriever,
        reranker=reranker,
        default_mode=cfg.get("retrieval", {}).get("search_type", "hybrid_rerank"),
        top_k=cfg.get("retrieval", {}).get("top_k", 5),
        score_threshold=cfg.get("retrieval", {}).get("score_threshold", 0.0),
    )

    model_name = cfg.get("llm", {}).get("model_name", "gemini-2.0-flash")
    llm_client = LLMClient(
        provider=cfg.get("llm", {}).get("provider", "gemini"),
        model_name=model_name,
        temperature=cfg.get("llm", {}).get("temperature", 0.2),
        max_output_tokens=cfg.get("llm", {}).get("max_output_tokens", 1024),
    )

    @app.get("/health")
    def health_check() -> dict[str, str]:
        """Health check endpoint to verify server status."""
        return {"status": "ok", "app": cfg.get("app", {}).get("name", "RAG")}

    @app.get("/metrics")
    def get_metrics() -> dict[str, Any]:
        """Retrieve operational latency percentiles, error rates, and token costs."""
        return metrics.get_metrics_snapshot()

    @app.get("/sentry-debug")
    def trigger_sentry_error() -> None:
        """Trigger an intentional division-by-zero error to test Sentry integration."""
        _ = 1 / 0


    @app.post("/index", response_model=dict[str, Any])
    def index_directory(req: IndexDirectoryRequest) -> dict[str, Any]:
        """Load, chunk, embed, and index documents for dense and BM25 search."""
        docs = loader.load_directory(req.dir_path)
        if not docs:
            raise HTTPException(
                status_code=404,
                detail=f"No valid documents found in {req.dir_path}",
            )

        chunks = chunker.chunk_documents(docs)
        texts = [c["chunk_text"] for c in chunks]
        embeddings = embedder.embed_batch(texts)

        # Index in Vector Store and BM25 index
        vector_store.add_documents(chunks, embeddings)
        bm25_retriever.fit(chunks)

        return {
            "status": "success",
            "indexed_documents": len(docs),
            "indexed_chunks": len(chunks),
        }

    @app.post("/query", response_model=QueryResponse)
    def query_rag(req: QueryRequest) -> QueryResponse:
        """Execute RAG query wrapped in distributed tracing and metrics tracking."""
        with tracer.trace("rag_query_pipeline") as root_trace:
            root_trace.root_span.set_input({"query": req.query, "search_type": req.search_type, "top_k": req.top_k})

            # 1. Retrieval Span
            with root_trace.span("retrieval") as s_ret:
                s_ret.set_input({"query": req.query, "mode": req.search_type, "top_k": req.top_k})
                retrieved_docs = retriever.retrieve(
                    query=req.query,
                    top_k=req.top_k,
                    mode=req.search_type,
                    compress=req.compress_context,
                )
                s_ret.set_attribute("chunk_count", len(retrieved_docs))
                s_ret.set_attribute("mode", req.search_type)
                s_ret.set_output({
                    "count": len(retrieved_docs),
                    "chunks": [d.get("chunk_text", "")[:150] + "..." for d in retrieved_docs],
                })

            # 2. Prompt Formatting Span
            with root_trace.span("prompt_formatting") as s_fmt:
                s_fmt.set_input({"query": req.query, "chunks_retrieved": len(retrieved_docs)})
                prompt = format_rag_prompt(req.query, retrieved_docs)
                s_fmt.set_output({"prompt_length": len(prompt)})

            # 3. LLM Generation Span
            with root_trace.span("llm_generation") as s_llm:
                s_llm.set_input({"prompt": prompt, "model": model_name})
                answer = llm_client.generate(prompt, system_prompt=DEFAULT_RAG_SYSTEM_PROMPT)
                s_llm.set_attribute("model", model_name)
                s_llm.set_output({"answer": answer})

            root_trace.root_span.set_output({"answer": answer, "sources_count": len(retrieved_docs)})


        summary = root_trace.get_summary()
        exporter.export(summary)

        # Estimate tokens (approx 4 chars per token)
        input_tokens = len(prompt) // 4
        output_tokens = len(answer) // 4
        cost = metrics.estimate_cost(model_name, input_tokens, output_tokens)

        # Record operational metrics
        metrics.record_query(
            duration_ms=summary["total_duration_ms"],
            is_error=False,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model_name=model_name,
        )

        return QueryResponse(
            query=req.query,
            search_type=req.search_type,
            answer=answer,
            sources=retrieved_docs,
            trace_id=summary["trace_id"],
            latency_ms=summary["total_duration_ms"],
            estimated_cost_usd=cost,
        )

    return app
