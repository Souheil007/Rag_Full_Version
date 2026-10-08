"""CLI script to run batch RAG evaluation over benchmark datasets and generate scorecards."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path when invoked directly as a script
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.evaluation.evaluator import RAGEvaluator
from src.llm.llm_client import LLMClient
from src.prompts.prompt_templates import DEFAULT_RAG_SYSTEM_PROMPT, format_rag_prompt
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.reranker import Reranker
from src.retrieval.retriever import Retriever
from src.utils.helpers import get_logger, load_config
from src.vectordb.vector_store import VectorStore
from src.embeddings.embedder import Embedder

logger = get_logger(__name__)


def run_evaluation(
    dataset_path: str = "data/eval/golden_dataset.json",
    output_report_path: str = "reports/evaluation_scorecard.md",
    top_k: int = 5,
    live_pipeline: bool = True,
) -> dict[str, Any]:
    """Execute evaluation over the golden dataset and save Markdown scorecard.

    Args:
        dataset_path: Path to benchmark golden dataset JSON.
        output_report_path: Path where Markdown scorecard will be saved.
        top_k: Number of retrieved chunks to evaluate per query.
        live_pipeline: Whether to execute live retrieval and LLM generation.

    Returns:
        Scorecard dictionary containing aggregate metrics.
    """
    cfg = load_config()
    model_name = cfg.get("llm", {}).get("model_name", "open-mistral-7b")

    llm_client = LLMClient(
        provider=cfg.get("llm", {}).get("provider", "mistral"),
        model_name=model_name,
    )
    evaluator = RAGEvaluator(llm_client=llm_client)

    cases = evaluator.load_golden_dataset(dataset_path)
    if not cases:
        logger.warning(f"No test cases loaded from {dataset_path}")
        return {}

    logger.info(f"Loaded {len(cases)} test cases from {dataset_path}")

    # Optionally execute live retrieval and generation
    if live_pipeline:
        embedder = Embedder(
            provider=cfg.get("embeddings", {}).get("provider", "sentence_transformers"),
            model_name=cfg.get("embeddings", {}).get("model_name", "all-MiniLM-L6-v2"),
        )
        vector_store = VectorStore(
            provider=cfg.get("vectordb", {}).get("provider", "chroma"),
            collection_name=cfg.get("vectordb", {}).get("collection_name", "rag_documents"),
            persist_directory=cfg.get("vectordb", {}).get("persist_directory", "./chroma_db"),
        )
        bm25_retriever = BM25Retriever()
        reranker = Reranker(enabled=True)
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder,
            bm25_retriever=bm25_retriever,
            reranker=reranker,
            default_mode="hybrid_rerank",
            top_k=top_k,
        )

        for case in cases:
            query = case.get("query", "")
            retrieved_docs = retriever.retrieve(query=query, top_k=top_k)
            case["retrieved_ids"] = [d.get("chunk_id", "") for d in retrieved_docs]
            case["context_chunks"] = [d.get("chunk_text", "") for d in retrieved_docs]

            prompt = format_rag_prompt(query, retrieved_docs)
            generated_answer = llm_client.generate(prompt, system_prompt=DEFAULT_RAG_SYSTEM_PROMPT)
            case["generated_answer"] = generated_answer

    scorecard = evaluator.evaluate_pipeline(cases, k=top_k)
    report_md = evaluator.generate_markdown_scorecard(scorecard)

    out_path = Path(output_report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    logger.info(f"Evaluation scorecard written to {output_report_path}")
    print("\n" + report_md + "\n")
    return scorecard


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAG benchmark evaluation")
    parser.add_argument("--dataset", default="data/eval/golden_dataset.json", help="Path to golden dataset")
    parser.add_argument("--output", default="reports/evaluation_scorecard.md", help="Path to output markdown report")
    parser.add_argument("--top-k", type=int, default=5, help="Cutoff K for retrieval metrics")
    parser.add_argument("--no-live", action="store_true", help="Evaluate existing dataset answers without querying live pipeline")

    args = parser.parse_args()
    run_evaluation(
        dataset_path=args.dataset,
        output_report_path=args.output,
        top_k=args.top_k,
        live_pipeline=not args.no_live,
    )
