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
    grounding_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    math_reconciled: bool | None = None
    metrics: dict[str, float] = Field(default_factory=dict)
    issues: list[str] = Field(default_factory=list)


class TableSanityChecker:
    """Diagnoses structural table anomalies including column skew, empty cell voids, dropped bands, and math mismatches."""

    def __init__(self, repair_threshold: float = 0.70) -> None:
        """Initialize TableSanityChecker with repair threshold.

        Args:
            repair_threshold: Minimum acceptable health score in [0.0, 1.0].
        """
        self.repair_threshold = repair_threshold

    @staticmethod
    def parse_accounting_number(val: str) -> float | None:
        """Parse float from string supporting parentheses, currency, and footnote tags.

        Args:
            val: String cell value.

        Returns:
            Parsed float value or None if non-numeric.
        """
        if not val:
            return None
        stripped = val.strip()
        if not stripped or stripped in ("-", "—", "N/A", "None", ""):
            return 0.0

        # Strip currency symbols
        cleaned = re.sub(r"[$£€¥]", "", stripped).strip()

        # Check for accounting parentheses e.g. (150,000) or (150)
        is_negative = False
        paren_match = re.match(r"^\((.+)\)$", cleaned)
        if paren_match:
            is_negative = True
            cleaned = paren_match.group(1).strip()
        elif cleaned.startswith("-"):
            is_negative = True
            cleaned = cleaned[1:].strip()

        # Detach trailing footnote markers e.g. "35.91 1" or "35.91*"
        cleaned = re.sub(r"\s+[\d*†‡]+$", "", cleaned)
        cleaned = cleaned.replace(",", "")

        # Extract number
        num_match = re.search(r"^[-+]?\d+(?:\.\d+)?", cleaned)
        if not num_match:
            return None

        try:
            val_f = float(num_match.group(0))
            return -val_f if is_negative else val_f
        except ValueError:
            return None

    def check_pure_total_math(
        self,
        headers: list[str],
        rows: list[list[str]],
        tolerance: float = 2.0,
    ) -> tuple[bool | None, list[str]]:
        """Verify column sums on simple tables with an unambiguous single Total row.

        Args:
            headers: List of column headers.
            rows: Matrix of table data rows.
            tolerance: Maximum allowable difference for published rounding.

        Returns:
            Tuple of (math_reconciled status, list of issues).
            Status is None when table has no total or has nested subtotals (bypassed).
        """
        if len(rows) < 3:
            return None, []

        total_keywords = ("total", "sum", "overall", "total income", "total costs", "total assets", "grand total")
        subtotal_keywords = ("subtotal", "sub-total", "interim total", "income subtotal", "costs subtotal", "sub total")

        # Check if any intermediate row contains subtotal keywords (nested tiers - intentionally bypassed)
        for r in rows[:-2]:
            label = " ".join(r).lower()
            if any(sub_kw in label for sub_kw in subtotal_keywords):
                # Bypassed: nested multi-tier table
                return None, []

        # Find total row at bottom
        total_row_idx = None
        for idx in (len(rows) - 1, len(rows) - 2):
            label = " ".join(rows[idx]).lower()
            if any(re.search(rf"\b{kw}\b", label) for kw in total_keywords):
                total_row_idx = idx
                break

        if total_row_idx is None:
            return None, []

        total_row = rows[total_row_idx]
        item_rows = rows[:total_row_idx]
        issues: list[str] = []
        verified_columns = 0
        math_matches = 0

        num_cols = len(headers)
        for col_idx in range(num_cols):
            # Parse total cell
            if col_idx >= len(total_row):
                continue
            total_val = self.parse_accounting_number(total_row[col_idx])
            if total_val is None:
                continue

            # Parse item values
            col_vals: list[float] = []
            for r in item_rows:
                if col_idx < len(r):
                    val = self.parse_accounting_number(r[col_idx])
                    if val is not None:
                        col_vals.append(val)

            if len(col_vals) >= 2:
                verified_columns += 1
                computed_sum = sum(col_vals)
                col_name = headers[col_idx] if col_idx < len(headers) else f"Col {col_idx+1}"
                diff = abs(computed_sum - total_val)
                if diff > tolerance:
                    issues.append(
                        f"Math reconciliation failed: Column '{col_name}' sum ({computed_sum:.2f}) "
                        f"!= extracted total ({total_val:.2f}) [diff: {diff:.2f} > tolerance {tolerance}]."
                    )
                else:
                    math_matches += 1

        if verified_columns == 0:
            return None, []

        reconciled = (math_matches == verified_columns)
        return reconciled, issues

    def check_verbatim_grounding(
        self,
        rows: list[list[str]],
        pdf_path: str | None = None,
        page_number: int | None = None,
        raw_page_text: str | None = None,
    ) -> tuple[float, list[str]]:
        """Verify whether extracted numbers and entities appear verbatim on the PDF page.

        Args:
            rows: Extracted table rows.
            pdf_path: Path to target PDF document.
            page_number: Source page number (1-indexed).
            raw_page_text: Optional pre-extracted text from the page.

        Returns:
            Tuple of (grounding_ratio, list of diagnostic issues).
        """
        page_text = raw_page_text or ""
        if not page_text and pdf_path and page_number:
            try:
                import pypdfium2 as pdfium

                pdf = pdfium.PdfDocument(str(pdf_path))
                if 0 <= (page_number - 1) < len(pdf):
                    page = pdf[page_number - 1]
                    textpage = page.get_textpage()
                    page_text = textpage.get_text_range()
            except Exception:
                try:
                    import pypdf

                    reader = pypdf.PdfReader(str(pdf_path))
                    if 0 <= (page_number - 1) < len(reader.pages):
                        page_text = reader.pages[page_number - 1].extract_text() or ""
                except Exception:
                    page_text = ""

        if not page_text:
            return 1.0, []

        # Build comprehensive token set from page text
        # Include original tokens, punctuation-stripped tokens, and comma-removed numbers
        page_raw_tokens = set(re.findall(r"\b[\w.,%-]+(?:\.\w+)?\b", page_text.lower()))
        normalized_tokens = set()
        for tok in page_raw_tokens:
            normalized_tokens.add(tok)
            normalized_tokens.add(tok.replace(",", ""))
            normalized_tokens.add(tok.replace("%", ""))
            normalized_tokens.add(tok.strip("()[]{}'\""))

        total_checked = 0
        grounded_count = 0
        issues: list[str] = []

        for row_idx, r in enumerate(rows, start=1):
            for cell in r:
                clean_cell = cell.strip()
                if not clean_cell or clean_cell in ("-", "—", "N/A", "None"):
                    continue

                cell_tokens = re.findall(r"\b[\w.,%-]+(?:\.\w+)?\b", clean_cell.lower())
                for tok in cell_tokens:
                    cleaned_tok = tok.replace(",", "").replace("%", "").strip("()[]{}'\"")
                    # Check digits or significant non-stopword tokens (len >= 4)
                    is_numeric = bool(re.search(r"\d", cleaned_tok))
                    if is_numeric or len(cleaned_tok) >= 4:
                        total_checked += 1
                        if (
                            tok in normalized_tokens
                            or cleaned_tok in normalized_tokens
                            or cleaned_tok in page_text.lower()
                        ):
                            grounded_count += 1
                        else:
                            if len(issues) < 5:  # Cap at 5 sample issues to avoid bloat
                                issues.append(
                                    f"Verbatim Grounding: Token '{tok}' from row {row_idx} not found on source page."
                                )

        if total_checked == 0:
            return 1.0, []

        ratio = round(grounded_count / total_checked, 4)
        if ratio < 0.85:
            issues.insert(0, f"Low verbatim grounding ratio ({ratio * 100:.1f}% < 85.0%). Possible OCR hallucination.")

        return ratio, issues

    def evaluate_table(
        self,
        table_id: str,
        headers: list[str],
        rows: list[list[str]],
        pdf_path: str | None = None,
        page_number: int | None = None,
        raw_page_text: str | None = None,
        warnings_from_parser: list[str] | None = None,
    ) -> TableHealthReport:
        """Evaluate structural health, alignment skew, verbatim grounding, and pure totals.

        Args:
            table_id: Unique identifier of the table.
            headers: List of column header strings.
            rows: Matrix of row string cells.
            pdf_path: Optional path to target PDF document for lexical grounding.
            page_number: Optional source page number (1-indexed).
            raw_page_text: Optional pre-extracted text from the source page.
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
        col_avg_lens: list[float] = []
        for col_idx in range(num_cols):
            lens = [len(r[col_idx].strip()) for r in rows if col_idx < len(r)]
            col_avg_lens.append(sum(lens) / max(len(lens), 1))

        is_column_shifted = False
        if num_cols >= 2:
            last_col_len = col_avg_lens[-1]
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

        # 4. Verbatim Source Grounding Check
        grounding_ratio, grounding_issues = self.check_verbatim_grounding(
            rows=rows,
            pdf_path=pdf_path,
            page_number=page_number,
            raw_page_text=raw_page_text,
        )
        if grounding_issues:
            issues.extend(grounding_issues)

        # 5. Pure Total Math Reconciliation Check
        math_reconciled, math_issues = self.check_pure_total_math(headers=headers, rows=rows)
        if math_issues:
            issues.extend(math_issues)

        # Compute aggregate health score
        col_shift_penalty = 0.50 if is_column_shifted else 1.0
        empty_penalty = max(0.0, 1.0 - (empty_cell_ratio * 1.5))
        jagged_penalty = max(0.0, 1.0 - (jagged_rows / max(num_rows, 1)))
        grounding_penalty = min(1.0, grounding_ratio / 0.85) if grounding_ratio < 0.85 else 1.0
        math_penalty = 0.50 if math_reconciled is False else 1.0

        score = round(col_shift_penalty * empty_penalty * jagged_penalty * grounding_penalty * math_penalty, 4)
        needs_repair = (
            (score < self.repair_threshold)
            or is_column_shifted
            or (grounding_ratio < 0.85)
            or (math_reconciled is False)
        )

        return TableHealthReport(
            table_id=table_id,
            health_score=score,
            needs_repair=needs_repair,
            grounding_ratio=grounding_ratio,
            math_reconciled=math_reconciled,
            metrics={
                "empty_cell_ratio": round(empty_cell_ratio, 4),
                "is_column_shifted": 1.0 if is_column_shifted else 0.0,
                "first_col_avg_len": round(col_avg_lens[0], 2) if col_avg_lens else 0.0,
                "last_col_avg_len": round(col_avg_lens[-1], 2) if col_avg_lens else 0.0,
                "grounding_ratio": round(grounding_ratio, 4),
                "math_reconciled": 1.0 if math_reconciled is True else (0.0 if math_reconciled is False else -1.0),
            },
            issues=issues,
        )

