"""Retrieval hit deduplication, sibling table collapse, and context token budgeting."""

from typing import Any
from pydantic import BaseModel, Field
from src.chunking.table_parser import NormalizedTable
from src.chunking.table_serializer import TableSerializer
from src.ingestion.doc_tree import DocumentTree
from src.utils.helpers import get_logger

logger = get_logger(__name__)

DEFAULT_TABLE_TOKEN_BUDGET = 2500
DEFAULT_TOTAL_TOKEN_BUDGET = 4000
DEFAULT_ROW_EXPANSION_WINDOW = 2


class CollapsedContext(BaseModel):
    """Consolidated context payload formatted for LLM generation prompt."""

    formatted_prompt_context: str
    deduplicated_sources: list[dict[str, Any]] = Field(default_factory=list)
    total_estimated_tokens: int = 0


class HitCollapser:
    """Collapses sibling table hits, deduplicates chunks, and enforces token budgets."""

    def __init__(
        self,
        table_token_budget: int = DEFAULT_TABLE_TOKEN_BUDGET,
        total_token_budget: int = DEFAULT_TOTAL_TOKEN_BUDGET,
        row_expansion_window: int = DEFAULT_ROW_EXPANSION_WINDOW,
    ) -> None:
        """Initialize HitCollapser with token limits and expansion parameters.

        Args:
            table_token_budget: Maximum tokens allocated for tabular contexts.
            total_token_budget: Total maximum token budget for the LLM context.
            row_expansion_window: Number of neighboring rows to expand around matching slices.
        """
        self.table_token_budget = table_token_budget
        self.total_token_budget = total_token_budget
        self.row_expansion_window = row_expansion_window

    def collapse_hits(
        self,
        hits: list[dict[str, Any]],
        doc_tree: DocumentTree | None = None,
        table_registry: dict[str, NormalizedTable] | None = None,
    ) -> CollapsedContext:
        """Deduplicate candidate hits and merge sibling table row slices.

        Args:
            hits: List of retrieved hit dicts containing 'content', 'metadata', and optional 'score'.
            doc_tree: Optional DocumentTree to look up introductory prose and node parents.
            table_registry: Optional map from table_id to full NormalizedTable instances.

        Returns:
            CollapsedContext ready for direct injection into prompt templates.
        """
        registry = table_registry or {}
        table_hits: dict[str, list[dict[str, Any]]] = {}
        prose_hits: list[dict[str, Any]] = []
        seen_prose_ids: set[str] = set()

        # 1. Segregate hits into prose vs. tables
        for hit in hits:
            meta = hit.get("metadata", {})
            block_type = meta.get("block_type", "")
            table_id = meta.get("table_id")

            if table_id:
                table_hits.setdefault(table_id, []).append(hit)
            else:
                chunk_id = meta.get("chunk_id", hit.get("id", str(len(prose_hits))))
                if chunk_id not in seen_prose_ids:
                    seen_prose_ids.add(chunk_id)
                    prose_hits.append(hit)

        formatted_sections: list[str] = []
        dedup_sources: list[dict[str, Any]] = []
        current_tokens = 0

        # 2. Process and merge sibling table hits
        for table_id, sibling_chunks in table_hits.items():
            full_table = registry.get(table_id)
            first_meta = sibling_chunks[0].get("metadata", {})
            section_path = first_meta.get("section_path", [])
            preceding_prose_id = first_meta.get("preceding_prose_id")

            # Inject preceding introductory paragraph if available in doc_tree
            if preceding_prose_id and doc_tree:
                prose_node = doc_tree.get_node(preceding_prose_id)
                if prose_node and prose_node.id not in seen_prose_ids:
                    seen_prose_ids.add(prose_node.id)
                    prose_block = f"[Context: {prose_node.content.strip()}]"
                    formatted_sections.append(prose_block)
                    current_tokens += len(prose_block) // 4

            # If full table is registered, calculate merged row range
            if full_table:
                total_rows = len(full_table.rows)
                min_row = total_rows
                max_row = 0
                has_range = False

                for sc in sibling_chunks:
                    r_range = sc.get("metadata", {}).get("row_range")
                    if r_range:
                        has_range = True
                        min_row = min(min_row, r_range[0])
                        max_row = max(max_row, r_range[1])

                # Check if full table fits within budget or is small
                estimated_full_tokens = (len(full_table.headers) * total_rows * 6) // 4
                if not has_range or estimated_full_tokens <= (self.table_token_budget // 2):
                    table_md = TableSerializer.to_markdown(full_table)
                    row_slice_info = f"Full Table ({total_rows} rows)"
                else:
                    # Apply row expansion window
                    expanded_start = max(0, min_row - self.row_expansion_window)
                    expanded_end = min(total_rows, max_row + self.row_expansion_window)
                    table_md = TableSerializer.to_markdown(
                        full_table,
                        row_slice=(expanded_start, expanded_end),
                    )
                    row_slice_info = f"Rows {expanded_start + 1}-{expanded_end} of {total_rows}"

                header_prefix = f"### Table: {full_table.caption or table_id} ({row_slice_info})\n"
                if section_path:
                    header_prefix = f"[Path: {' > '.join(section_path)}]\n" + header_prefix

                block_str = header_prefix + table_md
                formatted_sections.append(block_str)
                current_tokens += len(block_str) // 4

                dedup_sources.append({
                    "table_id": table_id,
                    "caption": full_table.caption,
                    "rows_included": row_slice_info,
                    "section_path": section_path,
                })
            else:
                # Fallback: table not in registry, use generation content of first chunk
                for sc in sibling_chunks:
                    content = sc.get("content_for_generation") or sc.get("content", "")
                    formatted_sections.append(content)
                    current_tokens += len(content) // 4
                    dedup_sources.append(first_meta)

        # 3. Append prose hits respecting total token budget
        for ph in prose_hits:
            content = ph.get("content_for_generation") or ph.get("content", "")
            est_tokens = len(content) // 4
            if current_tokens + est_tokens > self.total_token_budget:
                logger.warning("Token budget reached; truncating remaining prose hits.")
                break

            formatted_sections.append(content)
            current_tokens += est_tokens
            dedup_sources.append(ph.get("metadata", {}))

        final_context = "\n\n---\n\n".join(formatted_sections)

        return CollapsedContext(
            formatted_prompt_context=final_context,
            deduplicated_sources=dedup_sources,
            total_estimated_tokens=current_tokens,
        )
