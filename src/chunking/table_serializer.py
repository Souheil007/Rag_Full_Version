"""Dual-format serialization for tabular chunks: Key-Value for embeddings and Markdown for LLMs."""

from src.chunking.table_parser import NormalizedTable
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class TableSerializer:
    """Serializes NormalizedTable instances into dense-embedding and generation formats."""

    @staticmethod
    def to_kv_sentences(
        table: NormalizedTable,
        row_slice: tuple[int, int] | None = None,
        section_path: list[str] | None = None,
    ) -> str:
        """Linearize table rows into key-value sentences optimized for dense vector embedding.

        Args:
            table: NormalizedTable instance.
            row_slice: Optional (start_idx, end_idx) zero-indexed row slice tuple.
            section_path: Optional hierarchical breadcrumb list of section titles.

        Returns:
            Natural text string representation with structured KV rows.
        """
        lines: list[str] = []

        # Breadcrumbs & Context Prefix
        if section_path:
            lines.append(f"Section: {' > '.join(section_path)}")
        if table.caption:
            lines.append(f"Table Title: {table.caption}")

        start, end = row_slice if row_slice else (0, len(table.rows))
        target_rows = table.rows[start:end]

        for i, row in enumerate(target_rows, start=start + 1):
            row_parts: list[str] = []
            for col_idx, header in enumerate(table.headers):
                val = row[col_idx] if col_idx < len(row) else ""
                if val:
                    unit = table.units.get(header, "")
                    val_str = f"{val} {unit}".strip() if unit else val
                    row_parts.append(f"{header}: {val_str}")

            if row_parts:
                lines.append(f"Row {i}: {'; '.join(row_parts)}")

        return "\n".join(lines)

    @staticmethod
    def to_markdown(
        table: NormalizedTable,
        row_slice: tuple[int, int] | None = None,
        include_caption: bool = True,
    ) -> str:
        """Serialize table into standard Markdown pipe table format for LLM generation.

        Args:
            table: NormalizedTable instance.
            row_slice: Optional (start_idx, end_idx) zero-indexed row slice tuple.
            include_caption: Whether to prepend the table caption if present.

        Returns:
            Markdown pipe table string.
        """
        if not table.headers:
            return ""

        lines: list[str] = []
        if include_caption and table.caption:
            lines.append(f"**{table.caption}**\n")

        headers = table.headers
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        start, end = row_slice if row_slice else (0, len(table.rows))
        target_rows = table.rows[start:end]

        for row in target_rows:
            padded_row = [row[i] if i < len(row) else "" for i in range(len(headers))]
            escaped_cells = [c.replace("|", "\\|").replace("\n", " ") for c in padded_row]
            lines.append("| " + " | ".join(escaped_cells) + " |")

        return "\n".join(lines)

    @staticmethod
    def to_dict_rows(
        table: NormalizedTable,
        row_slice: tuple[int, int] | None = None,
    ) -> list[dict[str, str]]:
        """Convert rows to a list of header-value dictionaries.

        Args:
            table: NormalizedTable instance.
            row_slice: Optional (start_idx, end_idx) slice tuple.

        Returns:
            List of dictionaries mapping column headers to cell string values.
        """
        start, end = row_slice if row_slice else (0, len(table.rows))
        target_rows = table.rows[start:end]

        result: list[dict[str, str]] = []
        for row in target_rows:
            row_dict = {}
            for col_idx, header in enumerate(table.headers):
                row_dict[header] = row[col_idx] if col_idx < len(row) else ""
            result.append(row_dict)

        return result
