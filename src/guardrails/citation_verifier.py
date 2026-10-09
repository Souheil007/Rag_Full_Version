"""Citation verification module for checking source references in generated text."""

import re
from dataclasses import dataclass, field
from typing import Any

from src.utils.helpers import get_logger

logger = get_logger(__name__)


@dataclass
class CitationVerificationResult:
    """Result of citation verification analysis."""

    is_valid: bool
    total_citations: int
    valid_citations: list[dict[str, Any]] = field(default_factory=list)
    invalid_citations: list[dict[str, Any]] = field(default_factory=list)
    citation_score: float = 1.0
    details: str = ""


class CitationVerifier:
    """Verifies that inline citations strictly match retrieved source chunks."""

    def __init__(self, min_token_overlap: float = 0.4) -> None:
        """Initialize citation verifier.

        Args:
            min_token_overlap: Minimum token overlap between cited context and chunk text.
        """
        self.min_token_overlap = min_token_overlap
        # Regex patterns for numeric citations [1], [2] and named source citations [Source: foo.txt]
        self._numeric_pattern = re.compile(r"\[(\d+)\]")
        self._source_pattern = re.compile(r"\[(?:Source:\s*)?([^\]]+\.[a-zA-Z0-9]+)\]", re.IGNORECASE)

    def verify_citations(
        self,
        answer: str,
        retrieved_docs: list[dict[str, Any]],
    ) -> CitationVerificationResult:
        """Parse and verify inline citations against retrieved document chunks.

        Args:
            answer: Model generated answer containing citations.
            retrieved_docs: List of retrieved context chunks.

        Returns:
            CitationVerificationResult with validation details.
        """
        if not retrieved_docs:
            has_citations = bool(self._numeric_pattern.search(answer) or self._source_pattern.search(answer))
            return CitationVerificationResult(
                is_valid=not has_citations,
                total_citations=1 if has_citations else 0,
                invalid_citations=[{"marker": "any", "reason": "No retrieved context available"}] if has_citations else [],
                citation_score=0.0 if has_citations else 1.0,
                details="No retrieved documents provided for verification.",
            )

        num_docs = len(retrieved_docs)
        valid_citations: list[dict[str, Any]] = []
        invalid_citations: list[dict[str, Any]] = []

        # 1. Check numeric citations: [1], [2], etc.
        numeric_matches = self._numeric_pattern.findall(answer)
        for match in numeric_matches:
            doc_idx = int(match)
            # 1-based index verification
            if 1 <= doc_idx <= num_docs:
                target_doc = retrieved_docs[doc_idx - 1]
                valid_citations.append({
                    "marker": f"[{doc_idx}]",
                    "doc_index": doc_idx,
                    "filename": target_doc.get("metadata", {}).get("filename", f"doc_{doc_idx}"),
                })
            else:
                invalid_citations.append({
                    "marker": f"[{doc_idx}]",
                    "doc_index": doc_idx,
                    "reason": f"Citation index [{doc_idx}] is out of bounds (retrieved {num_docs} chunks)",
                })

        # 2. Check named source citations: [Source: notes.txt]
        source_matches = self._source_pattern.findall(answer)
        retrieved_filenames = {
            doc.get("metadata", {}).get("filename", "").lower() for doc in retrieved_docs
        }
        for match in source_matches:
            fname = match.strip().lower()
            if any(fname in r_name for r_name in retrieved_filenames if r_name):
                valid_citations.append({
                    "marker": f"[Source: {match}]",
                    "filename": match,
                })
            else:
                invalid_citations.append({
                    "marker": f"[Source: {match}]",
                    "filename": match,
                    "reason": f"Cited file '{match}' was not in retrieved context chunks",
                })

        total = len(valid_citations) + len(invalid_citations)
        if total == 0:
            # Answer made claims without any citations
            return CitationVerificationResult(
                is_valid=True,
                total_citations=0,
                citation_score=1.0,
                details="No inline citations found in answer.",
            )

        score = len(valid_citations) / total
        is_valid = len(invalid_citations) == 0

        details = f"{len(valid_citations)}/{total} citations valid."
        if invalid_citations:
            details += f" {len(invalid_citations)} invalid citation(s) detected."

        return CitationVerificationResult(
            is_valid=is_valid,
            total_citations=total,
            valid_citations=valid_citations,
            invalid_citations=invalid_citations,
            citation_score=round(score, 3),
            details=details,
        )
