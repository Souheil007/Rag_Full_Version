"""Generation quality evaluators using LLM-as-a-Judge and lexical metrics."""

import json
import re
from typing import Any
from src.llm.llm_client import LLMClient
from src.utils.helpers import get_logger

logger = get_logger(__name__)


def compute_lexical_similarity(response: str, reference: str) -> float:
    """Calculate word-level Jaccard similarity score between response and reference.

    Args:
        response: Generated answer string.
        reference: Ground truth reference answer.

    Returns:
        Similarity score between 0.0 and 1.0.
    """
    if not response or not reference:
        return 0.0

    words_resp = set(re.findall(r"\w+", response.lower()))
    words_ref = set(re.findall(r"\w+", reference.lower()))

    if not words_resp or not words_ref:
        return 0.0

    intersection = words_resp.intersection(words_ref)
    union = words_resp.union(words_ref)
    return round(len(intersection) / len(union), 4)


class GenerationEvaluator:
    """LLM-as-a-Judge and heuristic evaluator for RAG response quality."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        """Initialize GenerationEvaluator with an optional LLM client.

        Args:
            llm_client: Optional LLMClient instance for judge calls.
        """
        self.llm_client = llm_client

    def evaluate_faithfulness(
        self,
        answer: str,
        context_chunks: list[str],
    ) -> dict[str, Any]:
        """Assess whether claims in the generated answer are grounded in context.

        Args:
            answer: Generated response string to evaluate.
            context_chunks: List of context text strings provided to LLM.

        Returns:
            Dictionary containing 'score' (0.0 - 1.0), 'reason', and 'verdict'.
        """
        if not answer or not context_chunks:
            return {"score": 0.0, "reason": "Empty answer or context", "verdict": "FAIL"}

        context_text = "\n\n".join(context_chunks)

        if self.llm_client is None:
            # Heuristic fallback when LLM judge client is uninitialized
            overlap = compute_lexical_similarity(answer, context_text)
            score = round(min(1.0, overlap * 2.5), 2)
            return {
                "score": score,
                "reason": "Lexical overlap fallback (LLM judge unavailable)",
                "verdict": "PASS" if score >= 0.5 else "FAIL",
            }

        prompt = f"""You are an expert AI Evaluator judging Groundedness / Faithfulness.
Task: Determine if the candidate answer is strictly supported by the provided context.

[Context]
{context_text}

[Candidate Answer]
{answer}

Respond ONLY in valid JSON with these keys:
"score": float between 0.0 and 1.0 (1.0 = fully grounded, 0.0 = completely hallucinated)
"reason": concise explanation
"verdict": "PASS" or "FAIL"
"""
        try:
            raw_response = self.llm_client.generate(prompt)
            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return {
                    "score": float(data.get("score", 0.0)),
                    "reason": str(data.get("reason", "")),
                    "verdict": str(data.get("verdict", "FAIL")).upper(),
                }
        except Exception as exc:
            logger.warning(f"Faithfulness LLM evaluation failed ({exc}). Using fallback.")

        overlap = compute_lexical_similarity(answer, context_text)
        return {
            "score": round(min(1.0, overlap * 2.0), 2),
            "reason": "Lexical fallback due to API evaluation error",
            "verdict": "PASS" if overlap >= 0.2 else "FAIL",
        }

    def evaluate_answer_relevance(
        self,
        query: str,
        answer: str,
    ) -> dict[str, Any]:
        """Assess whether the generated answer directly addresses the user query.

        Args:
            query: User input query string.
            answer: Generated response string to evaluate.

        Returns:
            Dictionary containing 'score' (0.0 - 1.0), 'reason', and 'verdict'.
        """
        if not query or not answer:
            return {"score": 0.0, "reason": "Empty query or answer", "verdict": "FAIL"}

        if self.llm_client is None:
            overlap = compute_lexical_similarity(query, answer)
            score = round(min(1.0, overlap * 3.0), 2)
            return {
                "score": score,
                "reason": "Lexical overlap fallback (LLM judge unavailable)",
                "verdict": "PASS" if score >= 0.3 else "FAIL",
            }

        prompt = f"""You are an expert AI Evaluator judging Answer Relevance.
Task: Determine if the candidate answer directly addresses the user query without off-topic ramble.

[User Query]
{query}

[Candidate Answer]
{answer}

Respond ONLY in valid JSON with these keys:
"score": float between 0.0 and 1.0 (1.0 = directly relevant, 0.0 = completely off-topic)
"reason": concise explanation
"verdict": "PASS" or "FAIL"
"""
        try:
            raw_response = self.llm_client.generate(prompt)
            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return {
                    "score": float(data.get("score", 0.0)),
                    "reason": str(data.get("reason", "")),
                    "verdict": str(data.get("verdict", "FAIL")).upper(),
                }
        except Exception as exc:
            logger.warning(f"Answer relevance LLM evaluation failed ({exc}). Using fallback.")

        overlap = compute_lexical_similarity(query, answer)
        return {
            "score": round(min(1.0, overlap * 2.5), 2),
            "reason": "Lexical fallback due to API evaluation error",
            "verdict": "PASS" if overlap >= 0.2 else "FAIL",
        }
