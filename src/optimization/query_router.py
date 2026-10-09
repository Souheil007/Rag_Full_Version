"""Config-driven query complexity classifier and model router."""

import re
from typing import Any
from src.utils.helpers import get_logger

logger = get_logger(__name__)

# Heuristic patterns identifying complex reasoning / multi-document synthesis queries
COMPLEX_PATTERNS: list[str] = [
    r"\bcompare\b",
    r"\bcontrast\b",
    r"\bdifference\s+between\b",
    r"\bversus\b|\bvs\b",
    r"\bpros\s+and\s+cons\b",
    r"\btrade-?offs?\b",
    r"\bstep-?by-?step\b",
    r"\bexplain\s+why\b",
    r"\bsynthesize\b",
    r"\banalyze\b|\banalysis\b",
    r"\bevaluate\b",
    r"\bhow\s+does\b.*\brelate\b",
]


class QueryRouter:
    """Intelligently routes queries based on complexity when enabled."""

    def __init__(
        self,
        enabled: bool = False,
        default_model: str = "open-mistral-7b",
        fast_model: str = "open-mistral-7b",
        reasoning_model: str = "mistral-large-latest",
    ) -> None:
        """Initialize QueryRouter configuration.

        Args:
            enabled: Whether dynamic routing is enabled.
            default_model: Fallback/default model when routing is disabled.
            fast_model: Lightweight model for simple factoid queries.
            reasoning_model: Advanced model for complex synthesis queries.
        """
        self.enabled = enabled
        self.default_model = default_model
        self.fast_model = fast_model
        self.reasoning_model = reasoning_model
        self._compiled_patterns = [re.compile(p, re.IGNORECASE) for p in COMPLEX_PATTERNS]

    def is_complex_query(self, query: str) -> tuple[bool, str]:
        """Classify whether a query requires complex reasoning.

        Args:
            query: User input query.

        Returns:
            Tuple of (is_complex, reason).
        """
        stripped = query.strip()

        # Multi-question check
        if stripped.count("?") > 1:
            return True, "multi_question"

        # Regex heuristic patterns
        for pattern in self._compiled_patterns:
            if pattern.search(stripped):
                return True, f"pattern_match_{pattern.pattern}"

        # Length / multi-clause heuristic
        words = stripped.split()
        if len(words) >= 20:
            return True, "long_multi_clause"

        return False, "simple_factoid"

    def route(self, query: str) -> dict[str, Any]:
        """Determine target model and route metadata for a query.

        Args:
            query: User query string.

        Returns:
            Routing dictionary containing selected model, route type, and rationale.
        """
        if not self.enabled:
            return {
                "model": self.default_model,
                "route": "default",
                "reason": "router_disabled",
                "is_routed": False,
            }

        is_complex, reason = self.is_complex_query(query)
        selected_model = self.reasoning_model if is_complex else self.fast_model
        route_type = "complex" if is_complex else "simple"

        logger.info(f"Query routed to '{selected_model}' ({route_type}: {reason})")
        return {
            "model": selected_model,
            "route": route_type,
            "reason": reason,
            "is_routed": True,
        }
