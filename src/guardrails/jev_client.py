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
        model_name: str = "jev-1.13.0",
        timeout_seconds: float = 3.0,
    ) -> None:
        """Initialize Jev client.

        Args:
            api_key: API key for TypeSafe AI or OpenRouter.
            api_base: Base URL for decision endpoint.
            model_name: Identifier for the Jev model (e.g. 'jev-1.13.0').
            timeout_seconds: Request timeout in seconds.
        """
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("JEV_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.api_base = api_base.rstrip("/")
        self.model_name = model_name or "jev-1.13.0"
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
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            # Resolve the correct API endpoint
            if "openrouter.ai" in self.api_base:
                url = f"{self.api_base}/alpha/decisions" if not self.api_base.endswith("/decisions") else self.api_base
                payload = {
                    "model": self.model_name if "typesafe/" in self.model_name else f"typesafe/{self.model_name}",
                    "state": f"Context Reference:\n{context}",
                    "question": f"Is the following statement strictly entailed and supported by the context reference?\nStatement: '{claim}'",
                    "choices": ["supported", "unsupported"],
                }
            else:
                # Native TypeSafe AI SystemOne API (POST /v1/systemone)
                url = self.api_base if self.api_base.endswith("/systemone") else f"{self.api_base}/systemone"
                payload = {
                    "model": self.model_name,
                    "state": f"Context Reference:\n{context}",
                    "questions": {
                        "is_entailed": {
                            "type": "noul",
                            "instructions": (
                                "Is the following statement strictly entailed and supported by the context reference?\n"
                                f"Statement: '{claim}'"
                            ),
                        }
                    },
                }

            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.post(url, json=payload, headers=headers)

                if resp.status_code == 200:
                    data = resp.json()
                    confidence = 0.0

                    # 1. Parse native TypeSafe SystemOne response format
                    if "answers" in data and "is_entailed" in data["answers"]:
                        ans = data["answers"]["is_entailed"]
                        if ans.get("type") == "noul":
                            confidence = float(ans.get("noul", 0.0))
                        else:
                            confidence = float(ans.get("confidence", 0.0))
                    # 2. Parse OpenRouter / decision choice format
                    elif "choice" in data or "decision" in data:
                        choice = data.get("choice") or data.get("decision")
                        raw_conf = float(data.get("confidence", 0.0))
                        confidence = raw_conf if choice == "supported" else 0.0

                    latency_ms = (time.perf_counter() - start_time) * 1000
                    is_supported = confidence >= confidence_threshold

                    return {
                        "is_supported": is_supported,
                        "confidence": round(confidence, 3),
                        "decision": "supported" if is_supported else "unsupported",
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
