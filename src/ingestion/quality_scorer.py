"""Document extraction quality scoring module to filter degraded inputs."""

import re
from typing import Any
from pydantic import BaseModel, Field
from src.utils.helpers import get_logger

logger = get_logger(__name__)

DEFAULT_QUALITY_THRESHOLD = 0.65


class QualityReport(BaseModel):
    """Evaluation report on extraction fidelity and digital text health."""

    score: float = Field(ge=0.0, le=1.0)
    is_acceptable: bool
    metrics: dict[str, float] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class ExtractionQualityScorer:
    """Computes confidence scores for extracted document streams."""

    def __init__(self, threshold: float = DEFAULT_QUALITY_THRESHOLD) -> None:
        """Initialize ExtractionQualityScorer with quality threshold.

        Args:
            threshold: Minimum acceptable score in [0.0, 1.0].
        """
        self.threshold = threshold

    def evaluate_text(self, text: str, metadata: dict[str, Any] | None = None) -> QualityReport:
        """Assess text quality and detect OCR distortion or corrupted digital streams.

        Args:
            text: Raw extracted document text.
            metadata: Optional parser metadata (e.g. OCR confidence).

        Returns:
            QualityReport containing aggregate score and sub-metrics.
        """
        if not text or not text.strip():
            return QualityReport(
                score=0.0,
                is_acceptable=False,
                metrics={"char_count": 0.0},
                warnings=["Empty document text extracted."],
            )

        total_chars = len(text)
        warnings: list[str] = []

        # 1. Replacement & Control character ratio
        replacement_chars = text.count("\ufffd") + sum(1 for c in text if ord(c) < 32 and c not in "\n\r\t")
        clean_char_ratio = max(0.0, 1.0 - (replacement_chars / max(total_chars, 1)))
        if clean_char_ratio < 0.95:
            warnings.append(f"High non-printable character ratio detected ({(1 - clean_char_ratio) * 100:.1f}%).")

        # 2. Word validity / alphanumeric coherence
        words = re.findall(r"\b\w+\b", text)
        if not words:
            return QualityReport(
                score=0.0,
                is_acceptable=False,
                metrics={"clean_char_ratio": clean_char_ratio, "word_count": 0.0},
                warnings=["No alphanumeric words found in document."],
            )

        valid_words = [w for w in words if re.search(r"[a-zA-Z0-9]", w)]
        word_validity_ratio = len(valid_words) / max(len(words), 1)

        # 3. Gibberish / Unusual symbol cluster detection
        symbols = len(re.findall(r"[^\w\s.,;:!?()'\"/\\-]", text))
        symbol_ratio = min(1.0, symbols / max(total_chars, 1))
        symbol_penalty = max(0.0, 1.0 - (symbol_ratio * 3.0))
        if symbol_ratio > 0.15:
            warnings.append(f"Excessive symbol noise detected ({symbol_ratio * 100:.1f}%).")

        # 4. Density / Line fragmentation
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        avg_line_len = total_chars / max(len(lines), 1)
        line_health = min(1.0, avg_line_len / 25.0)  # Penalize severely fractured lines (< 25 chars avg)
        if line_health < 0.5:
            warnings.append("Severely fragmented lines detected (possible raw OCR column wrap failure).")

        # Base score from word and line health
        base_score = 0.65 * word_validity_ratio + 0.35 * line_health

        # Multiplicative damping from corrupt characters and excessive symbol noise
        aggregate_score = base_score * (clean_char_ratio ** 2) * symbol_penalty
        score = round(max(0.0, min(1.0, aggregate_score)), 4)
        is_acceptable = score >= self.threshold

        if not is_acceptable and not warnings:
            warnings.append(f"Aggregate extraction score ({score}) below threshold ({self.threshold}).")

        return QualityReport(
            score=score,
            is_acceptable=is_acceptable,
            metrics={
                "clean_char_ratio": round(clean_char_ratio, 4),
                "word_validity_ratio": round(word_validity_ratio, 4),
                "symbol_penalty": round(symbol_penalty, 4),
                "line_health": round(line_health, 4),
                "total_chars": float(total_chars),
                "word_count": float(len(words)),
            },
            warnings=warnings,
        )
