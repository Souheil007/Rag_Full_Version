"""Block-type chunking engine preserving document hierarchy and table schemas."""

from typing import Any
from pydantic import BaseModel, Field
from src.ingestion.doc_tree import BlockType, DocumentNode, DocumentTree
from src.chunking.table_parser import NormalizedTable, TableParser
from src.chunking.table_serializer import TableSerializer
from src.utils.helpers import get_logger

logger = get_logger(__name__)

DEFAULT_ROW_GROUP_SIZE = 15
DEFAULT_ROW_OVERLAP = 2
DEFAULT_MAX_ATOMIC_ROWS = 25
DEFAULT_PROSE_CHUNK_SIZE = 500


class ChunkPayload(BaseModel):
    """Processed chunk containing dual representations and provenance metadata."""

    chunk_id: str
    block_type: BlockType
    content_for_embedding: str
    content_for_generation: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class BlockChunker:
    """Splits DocumentTree nodes into typed, schema-preserving chunks."""

    def __init__(
        self,
        max_atomic_rows: int = DEFAULT_MAX_ATOMIC_ROWS,
        row_group_size: int = DEFAULT_ROW_GROUP_SIZE,
        row_overlap: int = DEFAULT_ROW_OVERLAP,
        prose_chunk_size: int = DEFAULT_PROSE_CHUNK_SIZE,
    ) -> None:
        """Initialize BlockChunker with table and prose chunking parameters.

        Args:
            max_atomic_rows: Maximum rows to keep a table atomic in a single chunk.
            row_group_size: Number of rows per sub-chunk for oversized tables.
            row_overlap: Number of overlapping rows between consecutive table sub-chunks.
            prose_chunk_size: Character budget per prose paragraph chunk.
        """
        self.max_atomic_rows = max_atomic_rows
        self.row_group_size = row_group_size
        self.row_overlap = row_overlap
        self.prose_chunk_size = prose_chunk_size

    def chunk_table_node(self, node: DocumentNode) -> list[ChunkPayload]:
        """Convert a table DocumentNode into atomic or row-grouped ChunkPayloads.

        Args:
            node: DocumentNode of type BlockType.TABLE.

        Returns:
            List of generated ChunkPayload objects.
        """
        table_meta = node.table_metadata or {}
        raw_headers = table_meta.get("headers", [])
        raw_rows = table_meta.get("rows", [])
        caption = table_meta.get("caption") or node.metadata.get("caption", "")

        # If table headers/rows were not pre-parsed, parse from Markdown content
        if not raw_headers and node.content:
            headers, rows = TableParser.parse_markdown_table(node.content)
        else:
            headers = TableParser.fill_down_headers(raw_headers) if raw_headers and isinstance(raw_headers[0], list) else raw_headers
            rows = raw_rows

        norm_table = NormalizedTable(
            table_id=node.id,
            caption=caption,
            headers=headers,
            rows=rows,
            page_numbers=[node.metadata.get("page", 1)],
            units=table_meta.get("units", {}),
        )

        total_rows = len(norm_table.rows)
        chunks: list[ChunkPayload] = []

        # Case 1: Small Table - Keep Atomic
        if total_rows <= self.max_atomic_rows:
            embed_text = TableSerializer.to_kv_sentences(
                norm_table,
                section_path=node.section_path,
            )
            gen_text = TableSerializer.to_markdown(norm_table)

            chunks.append(
                ChunkPayload(
                    chunk_id=f"{node.id}_atomic",
                    block_type=BlockType.TABLE,
                    content_for_embedding=embed_text,
                    content_for_generation=gen_text,
                    metadata={
                        "table_id": norm_table.table_id,
                        "is_atomic": True,
                        "row_range": [0, total_rows],
                        "total_rows": total_rows,
                        "section_path": node.section_path,
                        "preceding_prose_id": node.preceding_prose_id,
                        "page_numbers": norm_table.page_numbers,
                    },
                )
            )
            return chunks

        # Case 2: Large Table - Row Grouping with Replicated Headers
        start = 0
        chunk_idx = 0
        step = max(1, self.row_group_size - self.row_overlap)

        while start < total_rows:
            end = min(total_rows, start + self.row_group_size)
            row_slice = (start, end)

            embed_text = TableSerializer.to_kv_sentences(
                norm_table,
                row_slice=row_slice,
                section_path=node.section_path,
            )
            gen_text = TableSerializer.to_markdown(
                norm_table,
                row_slice=row_slice,
            )

            chunks.append(
                ChunkPayload(
                    chunk_id=f"{node.id}_part_{chunk_idx}",
                    block_type=BlockType.TABLE,
                    content_for_embedding=embed_text,
                    content_for_generation=gen_text,
                    metadata={
                        "table_id": norm_table.table_id,
                        "is_atomic": False,
                        "row_range": [start, end],
                        "total_rows": total_rows,
                        "section_path": node.section_path,
                        "preceding_prose_id": node.preceding_prose_id,
                        "page_numbers": norm_table.page_numbers,
                    },
                )
            )

            chunk_idx += 1
            start += step

        return chunks

    def chunk_prose_node(self, node: DocumentNode) -> list[ChunkPayload]:
        """Split a paragraph or text node with breadcrumb prefixes.

        Args:
            node: DocumentNode of type BlockType.PARAGRAPH, CODE, etc.

        Returns:
            List of generated ChunkPayload objects.
        """
        text = node.content.strip()
        if not text:
            return []

        section_prefix = f"[{' > '.join(node.section_path)}]\n" if node.section_path else ""

        # If fits within prose size budget
        if len(text) <= self.prose_chunk_size:
            return [
                ChunkPayload(
                    chunk_id=node.id,
                    block_type=node.node_type,
                    content_for_embedding=section_prefix + text,
                    content_for_generation=text,
                    metadata={
                        "section_path": node.section_path,
                        "parent_id": node.parent_id,
                        "level": node.level,
                        "page": node.metadata.get("page", 1),
                    },
                )
            ]

        # Otherwise split into sentence/paragraph segments
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: list[ChunkPayload] = []

        for p_idx, p in enumerate(paragraphs):
            chunks.append(
                ChunkPayload(
                    chunk_id=f"{node.id}_p_{p_idx}",
                    block_type=node.node_type,
                    content_for_embedding=section_prefix + p,
                    content_for_generation=p,
                    metadata={
                        "section_path": node.section_path,
                        "parent_id": node.parent_id,
                        "level": node.level,
                        "page": node.metadata.get("page", 1),
                    },
                )
            )

        return chunks

    def chunk_tree(self, tree: DocumentTree) -> list[ChunkPayload]:
        """Traverse the entire DocumentTree and generate block-typed chunks.

        Args:
            tree: DocumentTree to chunk.

        Returns:
            Comprehensive list of all generated ChunkPayload objects.
        """
        all_chunks: list[ChunkPayload] = []
        nodes = tree.walk()

        for node in nodes:
            if node.node_type in (BlockType.ROOT, BlockType.SECTION, BlockType.HEADER_FOOTER):
                continue
            elif node.node_type == BlockType.TABLE:
                all_chunks.extend(self.chunk_table_node(node))
            else:
                all_chunks.extend(self.chunk_prose_node(node))

        return all_chunks
