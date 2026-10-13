"""End-to-end integration test validating Docling layout conversion and structured chunking."""

from pathlib import Path
import pytest
from src.ingestion.layout_parser import LayoutParser
from src.chunking.block_chunker import BlockChunker
from src.retrieval.hit_collapser import HitCollapser


def test_docling_e2e_pipeline(tmp_path: Path) -> None:
    """Validate full end-to-end pipeline: Docling -> DocumentTree -> BlockChunker -> HitCollapser."""
    # 1. Create a sample technical document
    doc_path = tmp_path / "system_manual.md"
    content = """# Data Platform Manual
This manual documents the production architecture and database tiers.

## 1. Storage Topology
The cluster is split into transactional and analytical database instances.
The hardware allocation is outlined in the following specification table:

| Instance ID | Engine | vCPU | RAM | Tier |
|---|---|---|---|---|
| db-tx-01 | PostgreSQL | 16 | 64GB | Primary |
| db-tx-02 | PostgreSQL | 16 | 64GB | Replica |
| db-an-01 | ClickHouse | 32 | 128GB | Analytics |
| db-an-02 | ClickHouse | 32 | 128GB | Analytics |

```yaml
cluster:
  name: prod-data
  region: us-east-1
```

## 2. Retention Policy
All audit logs are retained for a minimum of 7 years in immutable cloud object storage.
"""
    doc_path.write_text(content, encoding="utf-8")

    # 2. Ingest via Docling LayoutParser
    parser = LayoutParser(quality_threshold=0.60)
    tree, quality_report = parser.parse_file(str(doc_path))

    assert tree is not None
    assert quality_report.is_acceptable is True
    assert tree.root.metadata["parser_engine"] in ("docling", "docling_ast")

    # 3. Verify DocumentTree structural items
    walked = tree.walk()
    assert len(walked) >= 5

    # 4. Generate block-type chunks with dual serialization
    chunker = BlockChunker(max_atomic_rows=10, row_group_size=5)
    chunks = chunker.chunk_tree(tree)
    assert len(chunks) >= 3

    # Check table chunk dual format
    table_chunks = [c for c in chunks if c.block_type.value == "table"]
    assert len(table_chunks) == 1
    t_chunk = table_chunks[0]

    # Content for embedding should be structured Key-Value sentences
    assert "Instance ID: db-tx-01" in t_chunk.content_for_embedding
    assert "Engine: PostgreSQL" in t_chunk.content_for_embedding
    # Content for generation should be pristine Markdown pipe table
    assert "| Instance ID | Engine | vCPU | RAM | Tier |" in t_chunk.content_for_generation

    # 5. Verify hit collapser
    collapser = HitCollapser()
    mock_hits = [
        {
            "id": t_chunk.chunk_id,
            "content": t_chunk.content_for_embedding,
            "content_for_generation": t_chunk.content_for_generation,
            "metadata": t_chunk.metadata,
        }
    ]
    collapsed = collapser.collapse_hits(mock_hits, doc_tree=tree)
    assert len(collapsed.deduplicated_sources) == 1
    assert "PostgreSQL" in collapsed.formatted_prompt_context
