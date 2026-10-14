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


class TableHealthReport(BaseModel):
    """Health diagnostic report for a parsed table."""

    table_id: str
    health_score: float = Field(ge=0.0, le=1.0)
    needs_repair: bool
    metrics: dict[str, float] = Field(default_factory=dict)
    issues: list[str] = Field(default_factory=list)


class TableSanityChecker:
    """Diagnoses structural table anomalies including column skew, empty cell voids, and dropped bands."""

    def __init__(self, repair_threshold: float = 0.70) -> None:
        """Initialize TableSanityChecker with repair threshold.

        Args:
            repair_threshold: Minimum acceptable health score in [0.0, 1.0].
        """
        self.repair_threshold = repair_threshold

    def evaluate_table(
        self,
        table_id: str,
        headers: list[str],
        rows: list[list[str]],
        warnings_from_parser: list[str] | None = None,
    ) -> TableHealthReport:
        """Evaluate structural health and detect column shifts or alignment skew.

        Args:
            table_id: Unique identifier of the table.
            headers: List of column header strings.
            rows: Matrix of row string cells.
            warnings_from_parser: Optional parser/OCR level warnings.

        Returns:
            TableHealthReport with diagnostic health score and repair flag.
        """
        issues: list[str] = []
        if warnings_from_parser:
            issues.extend(warnings_from_parser)

        num_cols = len(headers)
        num_rows = len(rows)

        if num_cols == 0 or num_rows == 0:
            return TableHealthReport(
                table_id=table_id,
                health_score=0.0,
                needs_repair=True,
                metrics={"empty_table": 1.0},
                issues=["Table has 0 columns or 0 data rows."],
            )

        # 1. Null / Empty Cell Ratio
        total_cells = num_cols * num_rows
        empty_cells = 0
        for r in rows:
            for c_idx in range(num_cols):
                cell_val = r[c_idx].strip() if c_idx < len(r) else ""
                if not cell_val:
                    empty_cells += 1

        empty_cell_ratio = empty_cells / max(total_cells, 1)
        if empty_cell_ratio > 0.25:
            issues.append(f"High empty cell ratio detected ({empty_cell_ratio * 100:.1f}%).")

        # 2. Length Skew / Column Inversion Anomaly Detection
        # Check if rightmost column has long descriptive text (e.g. questions) while leftmost has short booleans
        col_avg_lens: list[float] = []
        for col_idx in range(num_cols):
            lens = [len(r[col_idx].strip()) for r in rows if col_idx < len(r)]
            col_avg_lens.append(sum(lens) / max(len(lens), 1))

        # Check for reversed/shifted layout: first col has tiny tokens (len <= 4) and last col has long sentences (len >= 20)
        is_column_shifted = False
        if num_cols >= 2:
            first_col_len = col_avg_lens[0]
            last_col_len = col_avg_lens[-1]
            first_col_header_len = len(headers[0].strip()) if headers else 0

            # If the first column header implies a question/name but data is tiny (e.g. Yes/No), and last column has long text
            first_col_tokens = [r[0].strip().lower() for r in rows if len(r) > 0]
            boolean_like_count = sum(1 for tok in first_col_tokens if tok in ("yes", "no", "true", "false", "1", "0", "x", "✓", "✗"))
            if boolean_like_count / max(len(first_col_tokens), 1) >= 0.60 and last_col_len > 15.0:
                is_column_shifted = True
                issues.append(
                    f"Column alignment skew detected: Column 1 consists of short boolean answers "
                    f"while Column {num_cols} contains long descriptive text (avg len: {last_col_len:.1f})."
                )

        # 3. Jagged Row Lengths
        jagged_rows = sum(1 for r in rows if len(r) != num_cols)
        if jagged_rows > 0:
            issues.append(f"{jagged_rows} rows have mismatching column counts (jagged grid).")

        # Compute aggregate health score
        col_shift_penalty = 0.50 if is_column_shifted else 1.0
        empty_penalty = max(0.0, 1.0 - (empty_cell_ratio * 1.5))
        jagged_penalty = max(0.0, 1.0 - (jagged_rows / max(num_rows, 1)))

        score = round(col_shift_penalty * empty_penalty * jagged_penalty, 4)
        needs_repair = (score < self.repair_threshold) or is_column_shifted

        return TableHealthReport(
            table_id=table_id,
            health_score=score,
            needs_repair=needs_repair,
            metrics={
                "empty_cell_ratio": round(empty_cell_ratio, 4),
                "is_column_shifted": 1.0 if is_column_shifted else 0.0,
                "first_col_avg_len": round(col_avg_lens[0], 2) if col_avg_lens else 0.0,
                "last_col_avg_len": round(col_avg_lens[-1], 2) if col_avg_lens else 0.0,
            },
            issues=issues,
        )

