"""Unit and integration tests for structured block chunking, table parsing, and hit collapsing."""

import pytest
from src.ingestion.doc_tree import BlockType, DocumentNode, DocumentTree
from src.ingestion.quality_scorer import ExtractionQualityScorer
from src.chunking.table_parser import NormalizedTable, TableParser
from src.chunking.table_serializer import TableSerializer
from src.chunking.block_chunker import BlockChunker
from src.retrieval.hit_collapser import HitCollapser


def test_doc_tree_hierarchy_and_prose_link() -> None:
    """Test DocumentTree builds section hierarchy and links preceding prose to tables."""
    blocks = [
        {"id": "sec_1", "type": "section", "content": "1. Financial Review", "level": 1},
        {"id": "p_1", "type": "paragraph", "content": "The following table illustrates Q3 profits.", "level": 0},
        {
            "id": "t_1",
            "type": "table",
            "content": "| Metric | Value |\n|---|---|\n| Revenue | $50M |",
            "level": 0,
            "table_metadata": {"caption": "Table 1: Profits", "headers": ["Metric", "Value"], "rows": [["Revenue", "$50M"]]},
        },
    ]

    tree = DocumentTree.from_blocks(blocks, doc_id="report_2025", title="Annual Report")
    table_node = tree.get_node("t_1")

    assert table_node is not None
    assert table_node.preceding_prose_id == "p_1"
    assert table_node.section_path == ["Annual Report", "1. Financial Review"]


def test_extraction_quality_scorer() -> None:
    """Test ExtractionQualityScorer detects clean text vs corrupted streams."""
    scorer = ExtractionQualityScorer(threshold=0.65)

    clean_text = (
        "Operating revenue increased by 14% across all business segments in 2025. "
        "The consolidated financial statements show solid earnings growth."
    )
    clean_report = scorer.evaluate_text(clean_text)
    assert clean_report.is_acceptable is True
    assert clean_report.score >= 0.75

    corrupted_text = "\ufffd\ufffd\ufffd 1234 %%%% ^^^^ #### \x00\x01\x02 a b c"
    corrupted_report = scorer.evaluate_text(corrupted_text)
    assert corrupted_report.is_acceptable is False
    assert corrupted_report.score < 0.65
    assert len(corrupted_report.warnings) > 0


def test_table_parser_fill_down_headers() -> None:
    """Test forward-fill normalizer merges multi-tier hierarchical headers."""
    raw_headers = [
        ["2025 Financials", "", "2026 Forecast", ""],
        ["Revenue", "Net Margin", "Revenue", "Net Margin"],
    ]
    normalized = TableParser.fill_down_headers(raw_headers)

    assert normalized == [
        "2025 Financials > Revenue",
        "2025 Financials > Net Margin",
        "2026 Forecast > Revenue",
        "2026 Forecast > Net Margin",
    ]


def test_table_parser_headerless_stitcher() -> None:
    """Test table stitcher connects pages when page 2 has no header."""
    table_blocks = [
        {
            "id": "tbl_p1",
            "caption": "Quarterly Ledger",
            "headers": ["Quarter", "Revenue"],
            "rows": [["Q1", "$10M"], ["Q2", "$12M"]],
            "page": 1,
            "bbox": [0.1, 0.2, 0.9, 0.88],  # Reaches bottom margin
        },
        {
            "id": "tbl_p2",
            "caption": "",
            "headers": [],  # Header omitted on page 2!
            "rows": [["Q3", "$14M"], ["Q4", "$16M"]],
            "page": 2,
            "bbox": [0.1, 0.05, 0.9, 0.35],  # Starts near top margin
        },
    ]

    stitched = TableParser.stitch_multipage_tables(table_blocks)
    assert len(stitched) == 1
    assert len(stitched[0].rows) == 4
    assert stitched[0].page_numbers == [1, 2]
    assert stitched[0].headers == ["Quarter", "Revenue"]


def test_table_serializer_dual_formats() -> None:
    """Test TableSerializer generates KV sentences for vector embedding and Markdown for generation."""
    table = NormalizedTable(
        table_id="tbl_pricing",
        caption="Subscription Tiers",
        headers=["Tier", "Monthly Price", "SLA"],
        rows=[
            ["Basic", "$10", "99.0%"],
            ["Enterprise", "$500", "99.99%"],
        ],
        units={"Monthly Price": "USD"},
    )

    kv_text = TableSerializer.to_kv_sentences(table, section_path=["Product", "Pricing"])
    assert "Section: Product > Pricing" in kv_text
    assert "Table Title: Subscription Tiers" in kv_text
    assert "Row 1: Tier: Basic; Monthly Price: $10 USD; SLA: 99.0%" in kv_text
    assert "Row 2: Tier: Enterprise; Monthly Price: $500 USD; SLA: 99.99%" in kv_text

    md_text = TableSerializer.to_markdown(table)
    assert "| Tier | Monthly Price | SLA |" in md_text
    assert "| Basic | $10 | 99.0% |" in md_text


def test_block_chunker_atomic_vs_row_group() -> None:
    """Test BlockChunker keeps small tables atomic and chunks large tables with replicated headers."""
    chunker = BlockChunker(max_atomic_rows=5, row_group_size=4, row_overlap=1)

    # 1. Small Table (3 rows)
    small_node = DocumentNode(
        id="t_small",
        node_type=BlockType.TABLE,
        content="",
        section_path=["Test"],
        table_metadata={
            "caption": "Small",
            "headers": ["A", "B"],
            "rows": [["1", "2"], ["3", "4"], ["5", "6"]],
        },
    )
    small_chunks = chunker.chunk_table_node(small_node)
    assert len(small_chunks) == 1
    assert small_chunks[0].metadata["is_atomic"] is True

    # 2. Large Table (10 rows > max_atomic_rows=5)
    large_node = DocumentNode(
        id="t_large",
        node_type=BlockType.TABLE,
        content="",
        section_path=["Test"],
        table_metadata={
            "caption": "Large",
            "headers": ["A", "B"],
            "rows": [[str(i), str(i * 2)] for i in range(10)],
        },
    )
    large_chunks = chunker.chunk_table_node(large_node)
    assert len(large_chunks) > 1
    for chunk in large_chunks:
        assert chunk.metadata["is_atomic"] is False
        assert "A" in chunk.content_for_embedding
        assert "| A | B |" in chunk.content_for_generation


def test_hit_collapser_deduplication_and_budgeting() -> None:
    """Test HitCollapser collapses multiple sibling row hits from the same table and injects preceding prose."""
    table = NormalizedTable(
        table_id="tbl_fin",
        caption="Consolidated Financials",
        headers=["Item", "Value"],
        rows=[[f"Item {i}", f"${i}M"] for i in range(20)],
    )
    table_registry = {"tbl_fin": table}

    # Two hits from the same table
    hits = [
        {
            "id": "c1",
            "metadata": {
                "table_id": "tbl_fin",
                "row_range": [2, 5],
                "preceding_prose_id": "p_intro",
                "section_path": ["Report", "Finances"],
            },
        },
        {
            "id": "c2",
            "metadata": {
                "table_id": "tbl_fin",
                "row_range": [4, 8],
                "preceding_prose_id": "p_intro",
                "section_path": ["Report", "Finances"],
            },
        },
    ]

    doc_tree = DocumentTree(doc_id="report", title="Report")
    intro_node = DocumentNode(
        id="p_intro",
        node_type=BlockType.PARAGRAPH,
        content="The financials below represent Q1 audited totals.",
    )
    doc_tree.add_node(intro_node)

    collapser = HitCollapser(table_token_budget=1000)
    collapsed = collapser.collapse_hits(hits, doc_tree=doc_tree, table_registry=table_registry)

    # Must collapse sibling hits to 1 source table entry
    assert len(collapsed.deduplicated_sources) == 1
    assert "Consolidated Financials" in collapsed.formatted_prompt_context
    assert "The financials below represent Q1 audited totals." in collapsed.formatted_prompt_context
    # Table should not be repeated twice
    assert collapsed.formatted_prompt_context.count("### Table: Consolidated Financials") == 1
