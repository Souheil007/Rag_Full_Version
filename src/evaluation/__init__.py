"""Evaluation package providing retrieval and generation quality scorecards."""

from src.evaluation.evaluator import RAGEvaluator
from src.evaluation.generation_metrics import GenerationEvaluator, compute_lexical_similarity
from src.evaluation.retrieval_metrics import (
    compute_hit_rate,
    compute_mrr,
    compute_precision_at_k,
    compute_recall_at_k,
    evaluate_retrieval_batch,
)

__all__ = [
    "RAGEvaluator",
    "GenerationEvaluator",
    "compute_precision_at_k",
    "compute_recall_at_k",
    "compute_hit_rate",
    "compute_mrr",
    "evaluate_retrieval_batch",
    "compute_lexical_similarity",
]
