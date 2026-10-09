"""Statement-level hallucination detection and entailment verification."""

import re
import time
from dataclasses import dataclass, field
from typing import Any

from src.guardrails.jev_client import JevClient
from src.utils.helpers import get_logger

logger = get_logger(__name__)


@dataclass
class GroundingResult:
    """Result of factual grounding and hallucination detection."""

    is_grounded: bool
    grounding_score: float
    total_claims: int
    supported_claims: list[dict[str, Any]] = field(default_factory=list)
    unsupported_claims: list[dict[str, Any]] = field(default_factory=list)
    latency_ms: float = 0.0
    engine: str = "jev"
    details: str = ""


class HallucinationDetector:
    """Detects hallucinations by verifying statement-level entailment against context."""

    def __init__(
        self,
        jev_client: JevClient | None = None,
        confidence_threshold: float = 0.85,
        min_grounding_score: float = 0.80,
    ) -> None:
        """Initialize hallucination detector.

        Args:
            jev_client: Jev decision client instance.
            confidence_threshold: Minimum confidence per claim for entailment.
            min_grounding_score: Minimum ratio of supported claims to pass check.
        """
        self.jev_client = jev_client or JevClient()
        self.confidence_threshold = confidence_threshold
        self.min_grounding_score = min_grounding_score

    def extract_claims(self, text: str) -> list[str]:
        """Extract atomic factual claims and sentences from generated response.

        Args:
            text: Raw generated answer text.

        Returns:
            List of distinct statements to verify.
        """
        # Split on sentence boundaries
        raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        claims = []

        ignore_prefixes = (
            "here is",
            "based on",
            "according to",
            "in summary",
            "to summarize",
            "sure",
            "i hope",
            "please note",
            "as mentioned",
        )

        for s in raw_sentences:
            s_clean = s.strip()
            # Filter out empty or very short non-informative phrases
            if len(s_clean.split()) < 4:
                continue

            # Strip citation markers like [1], [Source: ...] for clean claim analysis
            cleaned_claim = re.sub(r"\[\d+\]", "", s_clean)
            cleaned_claim = re.sub(r"\[Source:[^\]]+\]", "", cleaned_claim, flags=re.IGNORECASE).strip()

            if cleaned_claim.lower().startswith(ignore_prefixes):
                # Still check if it contains a substantive subordinate clause
                parts = cleaned_claim.split(",", 1)
                if len(parts) > 1 and len(parts[1].strip().split()) >= 4:
                    cleaned_claim = parts[1].strip()

            if len(cleaned_claim.split()) >= 4:
                claims.append(cleaned_claim)

        return claims

    def verify_grounding(
        self,
        answer: str,
        retrieved_docs: list[dict[str, Any]],
    ) -> GroundingResult:
        """Verify whether generated statements are strictly grounded in retrieved chunks.

        Args:
            answer: Generated answer to verify.
            retrieved_docs: Context chunks retrieved for the query.

        Returns:
            GroundingResult with verification metrics and unsupported claims.
        """
        start_time = time.perf_counter()

        if not retrieved_docs:
            return GroundingResult(
                is_grounded=False,
                grounding_score=0.0,
                total_claims=1,
                unsupported_claims=[{"claim": answer, "reason": "No context available"}],
                details="No retrieved context chunks provided for grounding verification.",
            )

        combined_context = "\n".join(
            doc.get("chunk_text", "") for doc in retrieved_docs
        )

        claims = self.extract_claims(answer)
        if not claims:
            # Trivial or empty answer
            return GroundingResult(
                is_grounded=True,
                grounding_score=1.0,
                total_claims=0,
                details="No substantive factual claims found in answer.",
            )

        supported_claims: list[dict[str, Any]] = []
        unsupported_claims: list[dict[str, Any]] = []
        engine_used = "jev"

        for claim in claims:
            verdict = self.jev_client.check_entailment(
                claim=claim,
                context=combined_context,
                confidence_threshold=self.confidence_threshold,
            )
            engine_used = verdict.get("engine", "jev")

            record = {
                "claim": claim,
                "confidence": verdict.get("confidence", 0.0),
                "decision": verdict.get("decision", "unsupported"),
            }

            if verdict.get("is_supported", False):
                supported_claims.append(record)
            else:
                unsupported_claims.append(record)

        total = len(claims)
        score = len(supported_claims) / total if total > 0 else 1.0
        is_grounded = score >= self.min_grounding_score and len(unsupported_claims) == 0

        latency_ms = (time.perf_counter() - start_time) * 1000

        details = f"{len(supported_claims)}/{total} claims supported by context."
        if unsupported_claims:
            details += f" {len(unsupported_claims)} potentially hallucinated statement(s) detected."

        return GroundingResult(
            is_grounded=is_grounded,
            grounding_score=round(score, 3),
            total_claims=total,
            supported_claims=supported_claims,
            unsupported_claims=unsupported_claims,
            latency_ms=round(latency_ms, 2),
            engine=engine_used,
            details=details,
        )
