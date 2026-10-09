"""Client for the Jev discriminative decision model."""

import os
import time
from typing import Any
import httpx

from src.utils.helpers import get_logger

logger = get_logger(__name__)


class JevClient:
    """Client for Jev discriminative decision model (TypeSafe AI / OpenRouter)."""

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str = "https://api.typesafe.ai/v1",
        model_name: str = "typesafe/jev",
        timeout_seconds: float = 3.0,
    ) -> None:
        """Initialize Jev client.

        Args:
            api_key: API key for TypeSafe AI or OpenRouter.
            api_base: Base URL for decision endpoint.
            model_name: Identifier for the Jev model.
            timeout_seconds: Request timeout in seconds.
        """
        self.api_key = api_key or os.getenv("JEV_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.api_base = api_base.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def check_entailment(
        self,
        claim: str,
        context: str,
        confidence_threshold: float = 0.85,
    ) -> dict[str, Any]:
        """Verify whether a factual assertion is entailed by the retrieved context.

        Args:
            claim: Specific statement or proposition to verify.
            context: Retrieved reference text chunks.
            confidence_threshold: Minimum probability to accept as entailed.

        Returns:
            Dictionary containing entailment verdict, confidence, and latency.
        """
        start_time = time.perf_counter()

        # Offline / deterministic fallback when no API key is provided
        if not self.api_key:
            return self._heuristic_entailment_fallback(claim, context, start_time)

        try:
            # TypeSafe / OpenRouter Decision API structure
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model_name,
                "state": f"Context Reference:\n{context}",
                "question": f"Is the following statement strictly entailed and supported by the context reference?\nStatement: '{claim}'",
                "choices": ["supported", "unsupported"],
            }

            with httpx.Client(timeout=self.timeout_seconds) as client:
                url = f"{self.api_base}/decide" if not self.api_base.endswith("/decide") else self.api_base
                resp = client.post(url, json=payload, headers=headers)

                if resp.status_code == 200:
                    data = resp.json()
                    decision = data.get("choice", "unsupported")
                    confidence = float(data.get("confidence", 0.0))
                    latency_ms = (time.perf_counter() - start_time) * 1000

                    is_supported = decision == "supported" and confidence >= confidence_threshold
                    return {
                        "is_supported": is_supported,
                        "confidence": confidence,
                        "decision": decision,
                        "latency_ms": round(latency_ms, 2),
                        "engine": "jev",
                    }

                logger.warning("Jev API returned HTTP %s: %s", resp.status_code, resp.text)
                return self._heuristic_entailment_fallback(claim, context, start_time)

        except Exception as exc:
            logger.warning("Jev API call failed (%s); falling back to heuristic", exc)
            return self._heuristic_entailment_fallback(claim, context, start_time)

    def _heuristic_entailment_fallback(
        self,
        claim: str,
        context: str,
        start_time: float,
    ) -> dict[str, Any]:
        """Perform token overlap heuristic entailment check when API is unavailable.

        Args:
            claim: Statement to verify.
            context: Context text to check against.
            start_time: Perf counter start timestamp.

        Returns:
            Entailment result dictionary.
        """
        latency_ms = (time.perf_counter() - start_time) * 1000
        claim_clean = claim.lower().strip()
        context_clean = context.lower().strip()

        # Check exact or strong substring match
        if claim_clean in context_clean:
            return {
                "is_supported": True,
                "confidence": 1.0,
                "decision": "supported",
                "latency_ms": round(latency_ms, 2),
                "engine": "heuristic_fallback",
            }

        # Token set overlap check for non-stop words
        claim_tokens = {w for w in claim_clean.split() if len(w) > 3}
        if not claim_tokens:
            return {
                "is_supported": True,
                "confidence": 0.9,
                "decision": "supported",
                "latency_ms": round(latency_ms, 2),
                "engine": "heuristic_fallback",
            }

        context_tokens = set(context_clean.split())
        overlap = claim_tokens.intersection(context_tokens)
        ratio = len(overlap) / len(claim_tokens)

        is_supported = ratio >= 0.70
        confidence = round(ratio, 3)

        return {
            "is_supported": is_supported,
            "confidence": confidence,
            "decision": "supported" if is_supported else "unsupported",
            "latency_ms": round(latency_ms, 2),
            "engine": "heuristic_fallback",
        }
