"""Table parsing, fill-down header normalization, and multi-page stitching."""

import re
from typing import Any
from pydantic import BaseModel, Field
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class NormalizedTable(BaseModel):
    """Normalized structured table representation with unified column schemas."""

    table_id: str
    caption: str = ""
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    units: dict[str, str] = Field(default_factory=dict)
    page_numbers: list[int] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TableParser:
    """Parses raw table grids, fills down merged headers, and stitches multi-page tables."""

    @staticmethod
    def fill_down_headers(raw_header_rows: list[list[str]]) -> list[str]:
        """Normalize multi-tier headers by forward-filling merged column spans.

        Args:
            raw_header_rows: List of header rows, where sub-cells may be empty strings.

        Returns:
            List of normalized composite column header names.
        """
        if not raw_header_rows:
            return []

        if len(raw_header_rows) == 1:
            return [h.strip() for h in raw_header_rows[0]]

        num_cols = max(len(row) for row in raw_header_rows)
        # Pad shorter rows
        padded = [row + [""] * (num_cols - len(row)) for row in raw_header_rows]

        # 1. Forward-fill empty values across columns horizontally for merged header spans
        for row in padded:
            last_val = ""
            for col_idx in range(num_cols):
                val = row[col_idx].strip()
                if val:
                    last_val = val
                elif last_val:
                    row[col_idx] = last_val

        # 2. Combine hierarchical rows vertically into compound names
        compound_headers: list[str] = []
        for col_idx in range(num_cols):
            parts: list[str] = []
            for row in padded:
                cell_val = row[col_idx].strip()
                if cell_val and (not parts or parts[-1] != cell_val):
                    parts.append(cell_val)
            compound_name = " > ".join(parts) if parts else f"Column_{col_idx + 1}"
            compound_headers.append(compound_name)

        return compound_headers

    @staticmethod
    def parse_markdown_table(md_text: str) -> tuple[list[str], list[list[str]]]:
        """Extract headers and rows from a Markdown pipe table.

        Args:
            md_text: Raw Markdown table string.

        Returns:
            Tuple of (headers list, rows matrix).
        """
        lines = [line.strip() for line in md_text.splitlines() if line.strip() and "|" in line]
        if not lines:
            return [], []

        def _split_row(row_str: str) -> list[str]:
            raw_cells = row_str.strip("|").split("|")
            return [c.strip() for c in raw_cells]

        headers = _split_row(lines[0])
        rows: list[list[str]] = []

        start_idx = 1
        # Skip divider line if present (e.g. |---|---|)
        if len(lines) > 1 and re.match(r"^[\s|:-]+$", lines[1]):
            start_idx = 2

        for line in lines[start_idx:]:
            row_cells = _split_row(line)
            if any(cell for cell in row_cells):
                rows.append(row_cells)

        return headers, rows

    @classmethod
    def stitch_multipage_tables(cls, table_blocks: list[dict[str, Any]]) -> list[NormalizedTable]:
        """Stitch multi-page tables across page breaks using signature matching and geometry.

        Args:
            table_blocks: List of raw table block dicts with keys 'id', 'headers', 'rows', 'page', 'bbox', etc.

        Returns:
            List of continuous NormalizedTable instances.
        """
        if not table_blocks:
            return []

        stitched: list[NormalizedTable] = []
        current_table: NormalizedTable | None = None

        for block in table_blocks:
            block_id = block.get("id", "table")
            caption = block.get("caption", "")
            raw_headers = block.get("headers", [])
            headers = cls.fill_down_headers(raw_headers) if raw_headers and isinstance(raw_headers[0], list) else [h.strip() for h in raw_headers]
            rows = block.get("rows", [])
            page = block.get("page", 1)
            bbox = block.get("bbox", [0, 0, 1, 1])  # [x0, y0, x1, y1]

            if current_table is None:
                current_table = NormalizedTable(
                    table_id=block_id,
                    caption=caption,
                    headers=headers,
                    rows=list(rows),
                    page_numbers=[page],
                    metadata={"bbox": bbox},
                )
                continue

            # Check for multi-page continuation:
            # Rule A: Repeated Header Signature matching
            is_header_match = headers and (headers == current_table.headers)

            # Rule B: Headerless Spillover Fallback (Page N cutoff at bottom, Page N+1 starts at top)
            prev_page = current_table.page_numbers[-1]
            prev_bbox = current_table.metadata.get("bbox", [0, 0, 1, 1])
            is_adjacent_page = (page == prev_page + 1)
            is_geometry_cutoff = prev_bbox[3] >= 0.80 and bbox[1] <= 0.20
            is_col_count_match = len(rows[0]) == len(current_table.headers) if (rows and current_table.headers) else False

            is_continuation = is_adjacent_page and (
                is_header_match or (not headers and is_geometry_cutoff and is_col_count_match)
            )

            if is_continuation:
                logger.info("Stitching continued table from page %d to page %d for table %s", prev_page, page, current_table.table_id)
                current_table.rows.extend(rows)
                current_table.page_numbers.append(page)
                current_table.metadata["bbox"] = bbox
            else:
                stitched.append(current_table)
                current_table = NormalizedTable(
                    table_id=block_id,
                    caption=caption,
                    headers=headers,
                    rows=list(rows),
                    page_numbers=[page],
                    metadata={"bbox": bbox},
                )

        if current_table:
            stitched.append(current_table)

        return stitched

    @classmethod
    def from_docling_table(
        cls,
        table_item: Any,
        doc: Any = None,
        table_id: str = "table",
    ) -> NormalizedTable:
        """Construct a NormalizedTable directly from a Docling TableItem AST node.

        Preserves native row spans, column spans, bounding boxes, and caption without text guessing.

        Args:
            table_item: Docling TableItem instance.
            doc: Optional parent DoclingDocument to resolve captions.
            table_id: Unique identifier for the table.

        Returns:
            NormalizedTable instance with verified grid data.
        """
        caption = ""
        if hasattr(table_item, "caption_text") and callable(table_item.caption_text) and doc:
            try:
                caption = table_item.caption_text(doc) or ""
            except Exception:
                caption = ""

        # Extract page number and bbox from Docling provenance
        pages: list[int] = []
        bbox = [0.0, 0.0, 1.0, 1.0]
        if hasattr(table_item, "prov") and table_item.prov:
            for p in table_item.prov:
                if hasattr(p, "page_no"):
                    pages.append(int(p.page_no))
                if hasattr(p, "bbox") and p.bbox:
                    b = p.bbox
                    bbox = [
                        float(getattr(b, "l", 0.0)),
                        float(getattr(b, "t", 0.0)),
                        float(getattr(b, "r", 1.0)),
                        float(getattr(b, "b", 1.0)),
                    ]

        pages = sorted(list(set(pages))) or [1]

        # Extract headers and rows
        headers: list[str] = []
        rows: list[list[str]] = []

        if hasattr(table_item, "export_to_dataframe") and callable(table_item.export_to_dataframe):
            try:
                df = table_item.export_to_dataframe(doc) if doc else table_item.export_to_dataframe()
                headers = [str(c).strip() for c in df.columns]
                rows = [[str(cell).strip() if cell is not None else "" for cell in row] for row in df.values]
            except Exception as e:
                logger.debug("Failed export_to_dataframe on Docling table: %s", e)

        # Fallback to table_item.data.grid if export_to_dataframe was empty
        if not rows and hasattr(table_item, "data") and hasattr(table_item.data, "grid"):
            grid = table_item.data.grid
            if grid:
                headers = [getattr(cell, "text", "").strip() for cell in grid[0]]
                for r in grid[1:]:
                    rows.append([getattr(cell, "text", "").strip() for cell in r])

        return NormalizedTable(
            table_id=table_id,
            caption=caption,
            headers=headers,
            rows=rows,
            page_numbers=pages,
            metadata={"bbox": bbox, "origin": "docling"},
        )
