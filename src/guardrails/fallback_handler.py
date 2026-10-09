"""Safe fallback handler when guardrails or grounding checks fail."""

from dataclasses import dataclass
from typing import Any

from src.guardrails.citation_verifier import CitationVerificationResult
from src.guardrails.hallucination_detector import GroundingResult
from src.utils.helpers import get_logger

logger = get_logger(__name__)

DEFAULT_FALLBACK_MESSAGE = (
    "I cannot find sufficient factual backing in the retrieved documents to answer "
    "this question reliably. Please refer directly to the source documents."
)


@dataclass
class GuardrailDecision:
    """Enforcement decision from the guardrail pipeline."""

    approved: bool
    final_answer: str
    action_taken: str  # "approved", "fallback_triggered", "partially_redacted"
    reasons: list[str]
    citation_score: float
    grounding_score: float


class FallbackHandler:
    """Evaluates guardrail check results and triggers safe fallback responses."""

    def __init__(
        self,
        fallback_message: str = DEFAULT_FALLBACK_MESSAGE,
        strict_mode: bool = True,
    ) -> None:
        """Initialize fallback handler.

        Args:
            fallback_message: Standard message returned upon guardrail rejection.
            strict_mode: If True, reject answers immediately if any hallucination is detected.
        """
        self.fallback_message = fallback_message
        self.strict_mode = strict_mode

    def evaluate_and_enforce(
        self,
        answer: str,
        citation_result: CitationVerificationResult | None = None,
        grounding_result: GroundingResult | None = None,
    ) -> GuardrailDecision:
        """Enforce guardrail policies across citation and hallucination checks.

        Args:
            answer: Raw generated response.
            citation_result: Result from CitationVerifier.
            grounding_result: Result from HallucinationDetector.

        Returns:
            GuardrailDecision with approval status and final response text.
        """
        reasons: list[str] = []

        citation_score = citation_result.citation_score if citation_result else 1.0
        grounding_score = grounding_result.grounding_score if grounding_result else 1.0

        if citation_result and not citation_result.is_valid:
            reasons.append(
                f"Citation verification failed: {len(citation_result.invalid_citations)} invalid citation(s) found."
            )

        if grounding_result and not grounding_result.is_grounded:
            reasons.append(
                f"Grounding check failed: score {grounding_result.grounding_score:.2f} with "
                f"{len(grounding_result.unsupported_claims)} ungrounded claim(s)."
            )

        # In strict mode, any violation triggers the fallback
        if reasons:
            logger.warning("Guardrail triggered fallback: %s", "; ".join(reasons))
            return GuardrailDecision(
                approved=False,
                final_answer=self.fallback_message,
                action_taken="fallback_triggered",
                reasons=reasons,
                citation_score=citation_score,
                grounding_score=grounding_score,
            )

        return GuardrailDecision(
            approved=True,
            final_answer=answer,
            action_taken="approved",
            reasons=[],
            citation_score=citation_score,
            grounding_score=grounding_score,
        )
