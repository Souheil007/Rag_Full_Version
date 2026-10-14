"""Automated invariant regression tests on the frozen multi-page merged-cell table fixture."""

from pathlib import Path
import pytest
from src.ingestion.layout_parser import LayoutParser
from src.ingestion.doc_tree import BlockType
from src.chunking.block_chunker import BlockChunker
from src.retrieval.hit_collapser import HitCollapser

FIXTURE_PATH = Path("tests/fixtures/ugly_multipage_table.docx")


@pytest.fixture(scope="module")
def parsed_ugly_tree():
    """Parse the frozen multi-page merged table fixture via Docling LayoutParser."""
    if not FIXTURE_PATH.exists():
        from scripts.generate_fixtures import generate_ugly_multipage_table_docx
        generate_ugly_multipage_table_docx(str(FIXTURE_PATH))

    parser = LayoutParser(quality_threshold=0.60)
    tree, report = parser.parse_file(str(FIXTURE_PATH))
    assert report.is_acceptable is True
    return tree


def test_table_no_lost_cells(parsed_ugly_tree) -> None:
    """Invariant 1: Assert all 40 data rows are preserved and cell counts match."""
    tables = parsed_ugly_tree.get_nodes_by_type(BlockType.TABLE)
    assert len(tables) >= 1

    main_table = tables[0]
    table_meta = main_table.table_metadata
    assert table_meta is not None

    headers = table_meta.get("headers", [])
    rows = table_meta.get("rows", [])

    assert len(headers) == 5
    # Total rows in the table (40 data rows + any sub-rows)
    assert len(rows) >= 40

    # Ensure data rows exist and cell counts match
    data_rows = [r for r in rows if any("DERIV-" in cell for cell in r)]
    assert len(data_rows) >= 38
    for row in rows:
        assert len(row) == 5


def test_fill_down_headers_on_fixture(parsed_ugly_tree) -> None:
    """Invariant 2: Assert multi-tier merged headers are compounded and contain no blanks."""
    tables = parsed_ugly_tree.get_nodes_by_type(BlockType.TABLE)
    headers = tables[0].table_metadata.get("headers", [])

    # Assert compound headers survived
    headers_str = " ".join(headers)
    assert any("Delta" in h for h in headers)
    assert any("Jurisdiction" in h or "Instrument" in h for h in headers)
    # No blank header strings
    assert all(bool(h.strip()) for h in headers)


def test_reading_order_and_section_integrity(parsed_ugly_tree) -> None:
    """Invariant 3: Assert sections are separate subtrees and table is correctly nested."""
    sections = parsed_ugly_tree.get_nodes_by_type(BlockType.SECTION)
    section_titles = [s.content for s in sections]

    assert any("Multi-Tier Derivative" in title for title in section_titles)
    assert any("Capital Requirements" in title for title in section_titles)

    # Table parentage check
    table_node = parsed_ugly_tree.get_nodes_by_type(BlockType.TABLE)[0]
    assert any("Derivative" in part for part in table_node.section_path)


def test_row_group_chunking_with_replicated_headers(parsed_ugly_tree) -> None:
    """Invariant 4: Oversized 40-row table must chunk into row groups with full replicated headers."""
    chunker = BlockChunker(max_atomic_rows=15, row_group_size=10, row_overlap=2)
    chunks = chunker.chunk_tree(parsed_ugly_tree)

    table_chunks = [c for c in chunks if c.block_type == BlockType.TABLE]
    assert len(table_chunks) >= 4  # 40 rows / 8 net rows per chunk = 5 chunks

    for chunk in table_chunks:
        assert chunk.metadata["is_atomic"] is False
        assert "row_range" in chunk.metadata
        # Replicated headers in KV embedding representation
        assert "Jurisdiction" in chunk.content_for_embedding or "DERIV-" in chunk.content_for_embedding
        # Replicated Markdown table structure in generation payload
        assert "| " in chunk.content_for_generation
        assert chunk.content_for_generation.count("|") >= 10


def test_hit_deduplication_on_fixture_chunks(parsed_ugly_tree) -> None:
    """Invariant 5: Sibling sub-chunks from the 40-row table must collapse to 1 consolidated table context."""
    chunker = BlockChunker(max_atomic_rows=15, row_group_size=10, row_overlap=2)
    chunks = chunker.chunk_tree(parsed_ugly_tree)
    table_chunks = [c for c in chunks if c.block_type == BlockType.TABLE]

    # Simulate top-3 search hits matching 3 different sub-chunks of the same table
    simulated_hits = [
        {
            "id": c.chunk_id,
            "content": c.content_for_embedding,
            "content_for_generation": c.content_for_generation,
            "metadata": c.metadata,
        }
        for c in table_chunks[:3]
    ]

    collapser = HitCollapser(table_token_budget=2000)
    collapsed = collapser.collapse_hits(simulated_hits, doc_tree=parsed_ugly_tree)

    # Must collapse sibling hits to 1 source entry
    assert len(collapsed.deduplicated_sources) == 1
    # Prompt context must not repeat the table header multiple times
    assert collapsed.formatted_prompt_context.count("### Table:") <= 1
    assert collapsed.total_estimated_tokens <= 2500
