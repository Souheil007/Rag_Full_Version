"""CLI inspection tool to test Docling ingestion and block-type chunking on real PDFs."""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestion.layout_parser import LayoutParser
from src.ingestion.doc_tree import BlockType
from src.chunking.block_chunker import BlockChunker
from src.retrieval.hit_collapser import HitCollapser


def test_pdf(file_path: str, query: str | None = None) -> None:
    """Inspect and test Docling parsing and chunking on a local PDF document.

    Args:
        file_path: Relative or absolute path to target PDF document.
        query: Optional search query to test retrieval and hit collapsing.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"\n❌ Error: File not found at '{file_path}'")
        sys.exit(1)

    print("=" * 80)
    print(f"📄 Testing Document Ingestion: {path.name}")
    print("=" * 80)

    # 1. Parse with Docling
    print("\n⏳ Step 1: Converting document via Docling DocumentConverter...")
    parser = LayoutParser(quality_threshold=0.65)
    tree, report = parser.parse_file(str(path))

    print(f"✅ Conversion complete! Engine: {tree.root.metadata.get('parser_engine', 'docling')}")
    print(f"📊 Extraction Quality Score ($Q_{{score}}$): {report.score:.3f} / 1.0")
    print(f"   Status: {'Acceptable' if report.is_acceptable else 'Flagged as Degraded'}")
    if report.warnings:
        print("   ⚠️ Quality Warnings:")
        for w in report.warnings:
            print(f"      - {w}")

    # 2. Document Tree Structure
    print("\n" + "=" * 80)
    print("🌳 Step 2: Extracted Document AST Tree Hierarchy")
    print("=" * 80)

    sections = tree.get_nodes_by_type(BlockType.SECTION)
    tables = tree.get_nodes_by_type(BlockType.TABLE)
    paragraphs = tree.get_nodes_by_type(BlockType.PARAGRAPH)
    codes = tree.get_nodes_by_type(BlockType.CODE)

    print(f"• Sections Found:   {len(sections)}")
    print(f"• Tables Found:     {len(tables)}")
    print(f"• Paragraphs Found: {len(paragraphs)}")
    print(f"• Code Blocks:      {len(codes)}")

    if sections:
        print("\n📑 Detected Sections & Hierarchy:")
        for s in sections:
            indent = "  " * s.level
            print(f"{indent}└─ [H{s.level}] {s.content}")

    if tables:
        print("\n📊 Detected Tables & Normalization:")
        for idx, t in enumerate(tables, 1):
            t_meta = t.table_metadata or {}
            headers = t_meta.get("headers", [])
            total_rows = t_meta.get("total_rows", len(t_meta.get("rows", [])))
            caption = t_meta.get("caption") or t.metadata.get("caption", "Untitled Table")
            prose_link = f"(Linked to prose: {t.preceding_prose_id})" if t.preceding_prose_id else "(No preceding prose)"
            print(f"  • Table {idx}: '{caption}' {prose_link}")
            print(f"    - Columns ({len(headers)}): {headers}")
            print(f"    - Total Rows: {total_rows}")
            print(f"    - Section Path: {' > '.join(t.section_path)}")

    # 3. Block-Type Chunking
    print("\n" + "=" * 80)
    print("✂️ Step 3: Block-Type Chunking Engine")
    print("=" * 80)

    chunker = BlockChunker(max_atomic_rows=25, row_group_size=12, row_overlap=2)
    chunks = chunker.chunk_tree(tree)
    print(f"Total Chunks Generated: {len(chunks)}")

    table_chunks = [c for c in chunks if c.block_type == BlockType.TABLE]
    prose_chunks = [c for c in chunks if c.block_type != BlockType.TABLE]
    print(f"• Table Chunks: {len(table_chunks)} (Atomic or Row-Grouped with Replicated Schemas)")
    print(f"• Prose Chunks: {len(prose_chunks)}")

    # Display sample chunk dual representation
    if table_chunks:
        sample_tc = table_chunks[0]
        print("\n🔍 Sample Table Chunk (Dual Representation Inspection):")
        print("--- [A] For Dense Vector Embeddings (KV Linearized Sentences) ---")
        lines = sample_tc.content_for_embedding.splitlines()[:6]
        print("\n".join(lines) + ("\n... [truncated]" if len(lines) >= 6 else ""))

        print("\n--- [B] For LLM Generation (Pristine Markdown Table) ---")
        gen_lines = sample_tc.content_for_generation.splitlines()[:6]
        print("\n".join(gen_lines) + ("\n... [truncated]" if len(gen_lines) >= 6 else ""))

    # 4. Optional Query & Hit Collapse Simulation
    if query:
        print("\n" + "=" * 80)
        print(f"🔎 Step 4: Retrieval & Hit Collapse Test for Query: '{query}'")
        print("=" * 80)

        # Keyword matching simulation across chunks
        q_terms = [t.lower() for t in query.split() if len(t) > 2]
        scored_chunks = []
        for c in chunks:
            text_lower = c.content_for_embedding.lower()
            score = sum(1 for term in q_terms if term in text_lower)
            if score > 0:
                scored_chunks.append({
                    "id": c.chunk_id,
                    "content": c.content_for_embedding,
                    "content_for_generation": c.content_for_generation,
                    "metadata": c.metadata,
                    "score": score,
                })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        top_hits = scored_chunks[:4]

        if not top_hits:
            print("No matching chunks found for simulation.")
        else:
            collapser = HitCollapser(table_token_budget=2000)
            collapsed = collapser.collapse_hits(top_hits, doc_tree=tree)

            print(f"Retrieved Top Candidates: {len(top_hits)}")
            print(f"Deduplicated Sources: {len(collapsed.deduplicated_sources)}")
            print(f"Total Prompt Context Tokens (est.): {collapsed.total_estimated_tokens}")
            print("\n📝 Formatted LLM Prompt Context Preview:")
            print("-" * 50)
            print(collapsed.formatted_prompt_context[:800] + ("\n... [truncated]" if len(collapsed.formatted_prompt_context) > 800 else ""))

    print("\n" + "=" * 80)
    print("🎉 Chunking & Ingestion Inspection Finished Successfully!")
    print("=" * 80)


if __name__ == "__main__":
    cli_parser = argparse.ArgumentParser(description="Test Docling ingestion and block chunking on a PDF.")
    cli_parser.add_argument("file_path", help="Path to PDF or document file to test (e.g. data/sample.pdf)")
    cli_parser.add_argument("--query", "-q", help="Optional test question to simulate retrieval and hit collapse", default=None)
    args = cli_parser.parse_args()

    test_pdf(args.file_path, query=args.query)
