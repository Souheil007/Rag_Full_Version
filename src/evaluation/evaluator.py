"""Central RAG Evaluator for batch benchmark scorecards."""

import json
from pathlib import Path
from typing import Any
from src.evaluation.generation_metrics import GenerationEvaluator, compute_lexical_similarity
from src.evaluation.retrieval_metrics import evaluate_retrieval_batch
from src.llm.llm_client import LLMClient
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class RAGEvaluator:
    """Orchestrates end-to-end evaluation over benchmark datasets."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        """Initialize RAGEvaluator.

        Args:
            llm_client: Optional LLMClient instance for LLM-as-a-Judge evaluations.
        """
        self.gen_evaluator = GenerationEvaluator(llm_client=llm_client)

    def load_golden_dataset(self, dataset_path: str = "data/eval/golden_dataset.json") -> list[dict[str, Any]]:
        """Load evaluation dataset from JSON file.

        Args:
            dataset_path: Path to dataset JSON file.

        Returns:
            List of evaluation item dictionaries.
        """
        path = Path(dataset_path)
        if not path.exists():
            logger.warning(f"Golden dataset not found at {dataset_path}. Returning empty list.")
            return []

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as exc:
            logger.error(f"Failed to read golden dataset: {exc}")
            return []

    def evaluate_pipeline(
        self,
        eval_cases: list[dict[str, Any]],
        k: int = 5,
    ) -> dict[str, Any]:
        """Run batch evaluation over test cases and generate an evaluation scorecard.

        Args:
            eval_cases: List of test case dicts containing query, answers, retrieved_ids, etc.
            k: Cut-off rank for retrieval metrics.

        Returns:
            Scorecard dictionary containing aggregate retrieval and generation metrics.
        """
        if not eval_cases:
            return {"status": "empty", "total_cases": 0}

        retrieval_batch = []
        faithfulness_scores = []
        relevance_scores = []
        lexical_scores = []
        item_results = []

        for case in eval_cases:
            query = case.get("query", "")
            generated_answer = case.get("answer", case.get("generated_answer", ""))
            ground_truth_answer = case.get("ground_truth_answer", "")
            retrieved_ids = case.get("retrieved_ids", [])
            ground_truth_ids = case.get("ground_truth_ids", [])
            context_chunks = case.get("context_chunks", [])

            # 1. Retrieval Metrics Data
            retrieval_batch.append({
                "retrieved_ids": retrieved_ids,
                "ground_truth_ids": ground_truth_ids,
            })

            # 2. Generation Metrics
            faith_result = self.gen_evaluator.evaluate_faithfulness(generated_answer, context_chunks)
            rel_result = self.gen_evaluator.evaluate_answer_relevance(query, generated_answer)
            lexical_sim = compute_lexical_similarity(generated_answer, ground_truth_answer)

            faithfulness_scores.append(faith_result["score"])
            relevance_scores.append(rel_result["score"])
            lexical_scores.append(lexical_sim)

            item_results.append({
                "query": query,
                "faithfulness": faith_result,
                "relevance": rel_result,
                "lexical_similarity": lexical_sim,
            })

        # Calculate Aggregate Metrics
        retrieval_summary = evaluate_retrieval_batch(retrieval_batch, k=k)
        n = len(eval_cases)

        mean_faithfulness = round(sum(faithfulness_scores) / n, 4) if n > 0 else 0.0
        mean_relevance = round(sum(relevance_scores) / n, 4) if n > 0 else 0.0
        mean_lexical = round(sum(lexical_scores) / n, 4) if n > 0 else 0.0

        overall_score = round(
            (retrieval_summary["hit_rate"] + mean_faithfulness + mean_relevance) / 3.0,
            4,
        )

        return {
            "status": "success",
            "total_cases": n,
            "overall_rag_score": overall_score,
            "retrieval_metrics": retrieval_summary,
            "generation_metrics": {
                "mean_faithfulness": mean_faithfulness,
                "mean_answer_relevance": mean_relevance,
                "mean_lexical_similarity": mean_lexical,
            },
            "item_details": item_results,
        }

    def generate_markdown_scorecard(self, scorecard: dict[str, Any]) -> str:
        """Format evaluation scorecard into a clean Markdown report string.

        Args:
            scorecard: Scorecard dictionary output from evaluate_pipeline().

        Returns:
            Formatted Markdown report string.
        """
        ret = scorecard.get("retrieval_metrics", {})
        gen = scorecard.get("generation_metrics", {})

        return f"""# 📊 RAG Evaluation Scorecard

**Overall System Score:** `{scorecard.get('overall_rag_score', 0.0)} / 1.0`
**Total Evaluated Cases:** `{scorecard.get('total_cases', 0)}`

## 🔍 1. Retrieval Performance Metrics
| Metric | Score | Description |
| :--- | :---: | :--- |
| **Precision@K** | `{ret.get('precision_at_k', 0.0)}` | Ratio of retrieved chunks that are relevant |
| **Recall@K** | `{ret.get('recall_at_k', 0.0)}` | Ratio of total ground-truth facts retrieved |
| **Hit Rate@K** | `{ret.get('hit_rate', 0.0)}` | Binary presence of relevant item in top-K |
| **MRR** | `{ret.get('mrr', 0.0)}` | Mean Reciprocal Rank of first relevant item |

## 🤖 2. Generation Quality Metrics (LLM-as-a-Judge)
| Metric | Score | Description |
| :--- | :---: | :--- |
| **Faithfulness / Groundedness** | `{gen.get('mean_faithfulness', 0.0)}` | Extracted claim grounding in context |
| **Answer Relevance** | `{gen.get('mean_answer_relevance', 0.0)}` | Direct alignment with user query |
| **Lexical Match (Similarity)** | `{gen.get('mean_lexical_similarity', 0.0)}` | Word-level overlap with ground truth |
"""
