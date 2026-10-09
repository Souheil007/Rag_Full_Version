"""FastAPI REST API endpoints with distributed tracing and operational metrics."""

from typing import Any, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.chunking.chunker import TextChunker
from src.embeddings.embedder import Embedder
from src.guardrails.citation_verifier import CitationVerifier
from src.guardrails.fallback_handler import DEFAULT_FALLBACK_MESSAGE, FallbackHandler
from src.guardrails.hallucination_detector import HallucinationDetector
from src.guardrails.jev_client import JevClient
from src.ingestion.loader import DocumentLoader
from src.llm.llm_client import LLMClient
from src.observability.metrics_collector import MetricsCollector
from src.observability.sentry_monitor import SentryMonitor
from src.observability.span_exporter import SpanExporter
from src.observability.tracer import Tracer
from src.optimization.profiler import PipelineProfiler
from src.optimization.query_router import QueryRouter
from src.optimization.semantic_cache import SemanticCache
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
    guardrail_status: str | None = Field(default="approved", description="Guardrail outcome: 'approved' or 'fallback_triggered'.")
    citation_score: float | None = Field(default=1.0, description="Verified citations score (0.0 to 1.0).")
    grounding_score: float | None = Field(default=1.0, description="Entailment grounding score from Jev (0.0 to 1.0).")
    claims: list[dict[str, Any]] | None = Field(default=None, description="Detailed statements evaluated by Jev.")
    profiling: dict[str, Any] | None = Field(default=None, description="Granular latency and cost profiling breakdown.")




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

    # Pre-warm models at server startup to prevent cold-start latency on first query
    embedder._init_model()
    reranker._init_model()

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

    # Initialize Guardrails Components
    guardrails_cfg = cfg.get("guardrails", {})
    guardrails_enabled = guardrails_cfg.get("enabled", True)
    jev_cfg = guardrails_cfg.get("jev", {})
    fallback_cfg = guardrails_cfg.get("fallback", {})

    jev_client = JevClient(
        api_base=jev_cfg.get("api_base", "https://api.typesafe.ai/v1"),
        model_name=jev_cfg.get("model", "typesafe/jev"),
        timeout_seconds=jev_cfg.get("timeout_seconds", 3.0),
    )
    citation_verifier = CitationVerifier()
    hallucination_detector = HallucinationDetector(
        jev_client=jev_client,
        confidence_threshold=jev_cfg.get("confidence_threshold", 0.85),
    )
    fallback_handler = FallbackHandler(
        fallback_message=fallback_cfg.get("fallback_message", DEFAULT_FALLBACK_MESSAGE),
        strict_mode=fallback_cfg.get("strict_mode", True),
    )

    # Optimization Components (Plan 4)
    opt_cfg = cfg.get("optimization", {})
    cache_cfg = opt_cfg.get("semantic_cache", {})
    router_cfg = opt_cfg.get("query_router", {})

    semantic_cache = SemanticCache(
        enabled=cache_cfg.get("enabled", True),
        similarity_threshold=cache_cfg.get("similarity_threshold", 0.95),
        max_entries=cache_cfg.get("max_entries", 1000),
        ttl_seconds=cache_cfg.get("ttl_seconds", 86400),
        cache_only_verified=cache_cfg.get("cache_only_verified", True),
    )
    query_router = QueryRouter(
        enabled=router_cfg.get("enabled", False),
        default_model=router_cfg.get("default_model", model_name),
        fast_model=router_cfg.get("fast_model", model_name),
        reasoning_model=router_cfg.get("reasoning_model", "mistral-large-latest"),
    )
    profiler = PipelineProfiler(metrics_collector=metrics)

    @app.get("/health")
    def health_check() -> dict[str, str]:
        """Health check endpoint to verify server status."""
        return {"status": "ok", "app": cfg.get("app", {}).get("name", "RAG")}

    @app.get("/metrics")
    def get_metrics() -> dict[str, Any]:
        """Retrieve operational latency percentiles, error rates, and token costs."""
        snapshot = metrics.get_metrics_snapshot()
        snapshot["cache"] = semantic_cache.stats()
        return snapshot

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
        """Execute RAG query wrapped in distributed tracing, caching, and metrics tracking."""
        # Check semantic cache if enabled
        query_embedding: list[float] = []
        if semantic_cache.enabled:
            query_embedding = embedder.embed_text(req.query)
            cached_result = semantic_cache.lookup(req.query, query_embedding)
            if cached_result is not None:
                with tracer.trace("rag_query_pipeline") as root_trace:
                    root_trace.root_span.set_input({
                        "query": req.query,
                        "search_type": req.search_type,
                        "top_k": req.top_k,
                        "cache_hit": True,
                    })
                    with root_trace.span("semantic_cache_lookup") as s_c:
                        s_c.set_output({
                            "status": "hit",
                            "similarity": cached_result.get("similarity", 1.0),
                            "cached_query": cached_result.get("cached_query", req.query),
                        })
                    root_trace.root_span.set_output({
                        "answer": cached_result["answer"],
                        "sources_count": len(cached_result["sources"]),
                    })
                summary = root_trace.get_summary()
                exporter.export(summary)

                profiling_info = profiler.profile_trace(
                    trace_summary=summary,
                    model_name="semantic_cache",
                    input_tokens=0,
                    output_tokens=0,
                    cache_hit=True,
                )
                metrics.record_query(
                    duration_ms=summary["total_duration_ms"],
                    is_error=False,
                    cache_hit=True,
                    input_tokens=0,
                    output_tokens=0,
                    model_name="semantic_cache",
                )
                return QueryResponse(
                    query=req.query,
                    search_type=req.search_type,
                    answer=cached_result["answer"],
                    sources=cached_result["sources"],
                    trace_id=summary["trace_id"],
                    latency_ms=summary["total_duration_ms"],
                    estimated_cost_usd=0.0,
                    guardrail_status="approved",
                    citation_score=1.0,
                    grounding_score=1.0,
                    profiling=profiling_info,
                )

        # Cache miss: Route query
        route_decision = query_router.route(req.query)
        active_model = route_decision["model"]

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
                    "chunks": [d.get("chunk_text", "") for d in retrieved_docs],
                })

            # 2. Prompt Formatting Span
            with root_trace.span("prompt_formatting") as s_fmt:
                s_fmt.set_input({"query": req.query, "chunks_retrieved": len(retrieved_docs)})
                prompt = format_rag_prompt(req.query, retrieved_docs)
                s_fmt.set_output({"prompt_length": len(prompt)})

            # 3. LLM Generation Span
            with root_trace.span("llm_generation") as s_llm:
                s_llm.set_input({"prompt": prompt, "model": active_model})
                generated_answer = llm_client.generate(
                    prompt,
                    system_prompt=DEFAULT_RAG_SYSTEM_PROMPT,
                    model_name=active_model,
                )
                s_llm.set_attribute("model", active_model)
                s_llm.set_output({"answer": generated_answer})

            # 4. Guardrails Verification Span
            guardrail_decision = None
            evaluated_claims = None
            if guardrails_enabled:
                with root_trace.span("guardrail_verification") as s_guard:
                    s_guard.set_input({"raw_answer_length": len(generated_answer), "chunks_count": len(retrieved_docs)})
                    citation_res = citation_verifier.verify_citations(generated_answer, retrieved_docs)
                    grounding_res = hallucination_detector.verify_grounding(generated_answer, retrieved_docs)
                    guardrail_decision = fallback_handler.evaluate_and_enforce(
                        answer=generated_answer,
                        citation_result=citation_res,
                        grounding_result=grounding_res,
                    )
                    final_answer = guardrail_decision.final_answer
                    evaluated_claims = grounding_res.supported_claims + grounding_res.unsupported_claims
                    s_guard.set_attribute("action", guardrail_decision.action_taken)
                    s_guard.set_attribute("citation_score", guardrail_decision.citation_score)
                    s_guard.set_attribute("grounding_score", guardrail_decision.grounding_score)
                    s_guard.set_output({
                        "approved": guardrail_decision.approved,
                        "reasons": guardrail_decision.reasons,
                        "engine": grounding_res.engine,
                        "claims_count": len(evaluated_claims),
                    })
            else:
                final_answer = generated_answer

            root_trace.root_span.set_output({"answer": final_answer, "sources_count": len(retrieved_docs)})

        summary = root_trace.get_summary()
        exporter.export(summary)

        # Estimate tokens (approx 4 chars per token)
        input_tokens = len(prompt) // 4
        output_tokens = len(final_answer) // 4
        cost = metrics.estimate_cost(active_model, input_tokens, output_tokens)

        # Store in cache if verified and approved
        if semantic_cache.enabled:
            is_verified = (
                guardrail_decision.approved
                and guardrail_decision.action_taken != "fallback_triggered"
            ) if guardrail_decision else True
            if not query_embedding:
                query_embedding = embedder.embed_text(req.query)
            semantic_cache.store(
                query=req.query,
                query_embedding=query_embedding,
                answer=final_answer,
                sources=retrieved_docs,
                is_verified=is_verified,
                disallowed_phrases=[fallback_cfg.get("fallback_message", DEFAULT_FALLBACK_MESSAGE)],
            )

        # Record operational metrics
        metrics.record_query(
            duration_ms=summary["total_duration_ms"],
            is_error=False,
            cache_hit=False,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model_name=active_model,
        )

        profiling_info = profiler.profile_trace(
            trace_summary=summary,
            model_name=active_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_hit=False,
        )

        return QueryResponse(
            query=req.query,
            search_type=req.search_type,
            answer=final_answer,
            sources=retrieved_docs,
            trace_id=summary["trace_id"],
            latency_ms=summary["total_duration_ms"],
            estimated_cost_usd=cost,
            guardrail_status=guardrail_decision.action_taken if guardrail_decision else "disabled",
            citation_score=guardrail_decision.citation_score if guardrail_decision else 1.0,
            grounding_score=guardrail_decision.grounding_score if guardrail_decision else 1.0,
            claims=evaluated_claims,
            profiling=profiling_info,
        )




    @app.post("/evaluate", response_model=dict[str, Any])
    def run_benchmark_evaluation(dataset_path: str = "data/eval/golden_dataset.json") -> dict[str, Any]:
        """Run batch evaluation against a benchmark dataset and return metric scorecard."""
        from src.evaluation.evaluator import RAGEvaluator

        evaluator = RAGEvaluator(llm_client=llm_client)
        cases = evaluator.load_golden_dataset(dataset_path)
        if not cases:
            return {"status": "error", "message": f"Dataset not found at {dataset_path}"}

        for case in cases:
            q = case.get("query", "")
            docs = retriever.retrieve(query=q, top_k=5)
            case["retrieved_ids"] = [d.get("chunk_id", "") for d in docs]
            case["context_chunks"] = [d.get("chunk_text", "") for d in docs]
            p = format_rag_prompt(q, docs)
            case["generated_answer"] = llm_client.generate(p, system_prompt=DEFAULT_RAG_SYSTEM_PROMPT)

        scorecard = evaluator.evaluate_pipeline(cases, k=5)
        return scorecard

    return app
