"""Unit tests for RAG evaluation engine and metric scorecards."""

import unittest
from src.evaluation.evaluator import RAGEvaluator
from src.evaluation.generation_metrics import GenerationEvaluator, compute_lexical_similarity
from src.evaluation.retrieval_metrics import (
    compute_hit_rate,
    compute_mrr,
    compute_precision_at_k,
    compute_recall_at_k,
    evaluate_retrieval_batch,
)


class TestEvaluationEngine(unittest.TestCase):
    """Test suite for mathematical retrieval metrics and generation quality evaluators."""

    def test_precision_at_k(self):
        """Verify Precision@K calculation."""
        retrieved = ["doc1", "doc2", "doc3", "doc4"]
        ground_truth = ["doc2", "doc4"]
        # Top 2: ["doc1", "doc2"] -> 1 relevant / 2 = 0.5
        self.assertEqual(compute_precision_at_k(retrieved, ground_truth, k=2), 0.5)
        # Top 4: ["doc1", "doc2", "doc3", "doc4"] -> 2 relevant / 4 = 0.5
        self.assertEqual(compute_precision_at_k(retrieved, ground_truth, k=4), 0.5)

    def test_recall_at_k(self):
        """Verify Recall@K calculation."""
        retrieved = ["doc1", "doc2", "doc3"]
        ground_truth = ["doc2", "doc4"]
        # Top 3: ["doc1", "doc2", "doc3"] -> 1 retrieved / 2 ground truths = 0.5
        self.assertEqual(compute_recall_at_k(retrieved, ground_truth, k=3), 0.5)

    def test_hit_rate(self):
        """Verify Hit Rate@K calculation."""
        retrieved_hit = ["doc1", "doc2"]
        retrieved_miss = ["doc5", "doc6"]
        ground_truth = ["doc2"]

        self.assertEqual(compute_hit_rate(retrieved_hit, ground_truth, k=2), 1.0)
        self.assertEqual(compute_hit_rate(retrieved_miss, ground_truth, k=2), 0.0)

    def test_mrr(self):
        """Verify Mean Reciprocal Rank (MRR) calculation."""
        # 1st item match -> rank 1 -> 1.0
        self.assertEqual(compute_mrr(["doc1", "doc2"], ["doc1"]), 1.0)
        # 2nd item match -> rank 2 -> 0.5
        self.assertEqual(compute_mrr(["doc2", "doc1"], ["doc1"]), 0.5)
        # No match -> 0.0
        self.assertEqual(compute_mrr(["doc2", "doc3"], ["doc1"]), 0.0)

    def test_lexical_similarity(self):
        """Verify Jaccard word-level lexical similarity."""
        s1 = "Reciprocal Rank Fusion is a search algorithm."
        s2 = "Reciprocal Rank Fusion algorithm for search."
        sim = compute_lexical_similarity(s1, s2)
        self.assertTrue(sim > 0.5)

    def test_generation_evaluator_fallback(self):
        """Verify GenerationEvaluator fallback without an active LLM client."""
        evaluator = GenerationEvaluator(llm_client=None)
        answer = "Reciprocal Rank Fusion combines sparse and dense retrieval ranks."
        context = ["Reciprocal Rank Fusion combines ranks from multiple retrievers."]

        faith_res = evaluator.evaluate_faithfulness(answer, context)
        self.assertTrue(faith_res["score"] >= 0.0)
        self.assertIn("verdict", faith_res)

        rel_res = evaluator.evaluate_answer_relevance("What is RRF?", answer)
        self.assertTrue(rel_res["score"] >= 0.0)

    def test_rag_evaluator_batch_and_scorecard(self):
        """Verify RAGEvaluator batch processing and Markdown scorecard generation."""
        evaluator = RAGEvaluator(llm_client=None)
        sample_cases = [
            {
                "query": "What is RRF?",
                "generated_answer": "RRF stands for Reciprocal Rank Fusion.",
                "ground_truth_answer": "Reciprocal Rank Fusion (RRF) is a rank fusion algorithm.",
                "retrieved_ids": ["c1", "c2"],
                "ground_truth_ids": ["c1"],
                "context_chunks": ["RRF stands for Reciprocal Rank Fusion."],
            }
        ]

        scorecard = evaluator.evaluate_pipeline(sample_cases, k=2)
        self.assertEqual(scorecard["status"], "success")
        self.assertEqual(scorecard["total_cases"], 1)
        self.assertTrue("overall_rag_score" in scorecard)

        md_report = evaluator.generate_markdown_scorecard(scorecard)
        self.assertIn("RAG Evaluation Scorecard", md_report)
        self.assertIn("Precision@K", md_report)


if __name__ == "__main__":
    unittest.main()
