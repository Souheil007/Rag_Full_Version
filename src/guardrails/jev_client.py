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

        If Jev is down, unresponsive, or unconfigured, bypasses Tier 2.

        Args:
            claim: Specific statement or proposition to verify.
            context: Retrieved reference text chunks.
            confidence_threshold: Minimum probability to accept as entailed.

        Returns:
            Dictionary containing entailment verdict, confidence, and latency.
        """
        start_time = time.perf_counter()

        # If no API key is provided, bypass Tier 2
        if not self.api_key:
            latency_ms = (time.perf_counter() - start_time) * 1000
            logger.info("Jev API key not configured; bypassing Tier 2 entailment check")
            return {
                "is_supported": True,
                "confidence": 1.0,
                "decision": "bypassed",
                "latency_ms": round(latency_ms, 2),
                "engine": "bypassed",
                "bypassed": True,
                "reason": "Missing JEV_API_KEY",
            }

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
                        "bypassed": False,
                    }

                latency_ms = (time.perf_counter() - start_time) * 1000
                logger.warning("Jev API returned HTTP %s (%s); bypassing Tier 2 check", resp.status_code, resp.text)
                return {
                    "is_supported": True,
                    "confidence": 1.0,
                    "decision": "bypassed",
                    "latency_ms": round(latency_ms, 2),
                    "engine": "bypassed",
                    "bypassed": True,
                    "reason": f"Jev HTTP {resp.status_code}",
                }

        except Exception as exc:
            latency_ms = (time.perf_counter() - start_time) * 1000
            logger.warning("Jev service unresponsive or timed out (%s); bypassing Tier 2 check", exc)
            return {
                "is_supported": True,
                "confidence": 1.0,
                "decision": "bypassed",
                "latency_ms": round(latency_ms, 2),
                "engine": "bypassed",
                "bypassed": True,
                "reason": f"Jev error/timeout: {exc}",
            }
