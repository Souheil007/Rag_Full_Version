"""CLI inspection tool to test Docling ingestion and block-type chunking on real PDFs."""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestion.layout_parser import LayoutParser
from src.ingestion.doc_tree import BlockType
from src.ingestion.quality_scorer import TableSanityChecker
from src.chunking.block_chunker import BlockChunker
from src.chunking.table_repairer import TableRepairer
from src.retrieval.hit_collapser import HitCollapser


def inspect_pdf(file_path: str, query: str | None = None) -> None:
    """Inspect Docling parsing and chunking on a local PDF document.

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

    # 2. Document Tree Structure & Table Sanity Check
    print("\n" + "=" * 80)
    print("🌳 Step 2: Extracted Document AST Tree & Table Health Scoring")
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

    table_checker = TableSanityChecker(repair_threshold=0.70)
    table_repairer = TableRepairer(provider="mistral")
    table_health_reports = {}
    table_repair_results = {}

    if tables:
        print("\n📊 Detected Tables, Health Diagnostic & Alignment Check:")
        for idx, t in enumerate(tables, 1):
            t_meta = t.table_metadata or {}
            headers = t_meta.get("headers", [])
            rows = t_meta.get("rows", [])
            total_rows = t_meta.get("total_rows", len(rows))
            caption = t_meta.get("caption") or t.metadata.get("caption", "Untitled Table")
            prose_link = f"(Linked to prose: {t.preceding_prose_id})" if t.preceding_prose_id else "(No preceding prose)"

            page_num = t.metadata.get("page", 1)
            # Run automated table sanity check with verbatim grounding and pure totals
            h_report = table_checker.evaluate_table(
                table_id=t.id,
                headers=headers,
                rows=rows,
                pdf_path=str(path),
                page_number=page_num,
            )
            table_health_reports[t.id] = h_report

            if h_report.needs_repair:
                status_symbol = "⚠️ REPAIR REQUIRED"
                # Route to TableRepairer
                repair_res = table_repairer.repair_table_node(t, pdf_path=str(path), health_report=h_report)
                table_repair_results[t.id] = repair_res

                if repair_res.repaired:
                    status_symbol = "✨ REPAIRED (Mistral OCR)"
                    # Update table in place
                    t.content = repair_res.new_markdown or t.content
                    t.table_metadata["headers"] = repair_res.new_headers
                    t.table_metadata["rows"] = repair_res.new_rows
                else:
                    status_symbol = f"⚠️ REPAIR SKIPPED ({repair_res.method})"
            else:
                status_symbol = "✅ Healthy"

            math_info = "N/A (Bypassed)" if h_report.math_reconciled is None else ("✅ Match" if h_report.math_reconciled else "❌ Mismatch")
            print(f"  • Table {idx}: '{caption}' | Health: {h_report.health_score:.2f} [{status_symbol}]")
            print(f"    - ID: `{t.id}` | Prose: {prose_link} | Page: {page_num}")
            print(f"    - Lexical Grounding: {h_report.grounding_ratio * 100:.1f}% | Pure Math: {math_info}")
            print(f"    - Columns ({len(headers)}): {headers}")
            print(f"    - Total Rows: {total_rows}")
            if h_report.issues:
                for issue in h_report.issues:
                    print(f"      🚩 Issue: {issue}")
            if t.id in table_repair_results:
                r_info = table_repair_results[t.id]
                print(f"      🔧 Repair Detail: [{r_info.method}] {r_info.reason}")

    # 3. Block-Type Chunking
    print("\n" + "=" * 80)
    print("✂️ Step 3: Block-Type Chunking Engine & Relationships")
    print("=" * 80)

    chunker = BlockChunker(max_atomic_rows=25, row_group_size=12, row_overlap=2)
    chunks = chunker.chunk_tree(tree)
    print(f"Total Chunks Generated: {len(chunks)}")

    table_chunks = [c for c in chunks if c.block_type == BlockType.TABLE]
    prose_chunks = [c for c in chunks if c.block_type != BlockType.TABLE]
    print(f"• Table Chunks: {len(table_chunks)} (Atomic or Row-Grouped with Replicated Schemas)")
    print(f"• Prose Chunks: {len(prose_chunks)}")

    print("\n🔗 Chunk Provenance & Relations Summary:")
    for idx, c in enumerate(chunks, 1):
        rel_info = []
        if c.block_type == BlockType.TABLE:
            t_id = c.metadata.get("table_id")
            rel_info.append(f"TableID: {t_id}")
            if c.metadata.get("preceding_prose_id"):
                rel_info.append(f"Linked Intro Prose: `{c.metadata['preceding_prose_id']}`")
            if c.metadata.get("is_atomic"):
                rel_info.append("Mode: Atomic (Full Table)")
            else:
                rel_info.append(f"Rows: {c.metadata.get('row_range')}")
        else:
            if c.metadata.get("parent_id"):
                rel_info.append(f"Parent: `{c.metadata['parent_id']}`")
            page = c.metadata.get("page")
            if page:
                rel_info.append(f"Page: {page}")

        sec_str = " > ".join(c.metadata.get("section_path", []))
        print(f"  [{idx:02d}] ID: {c.chunk_id:<20} | Type: {c.block_type.value:<10} | Section: {sec_str} | {' | '.join(rel_info)}")

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

    # 5. Save detailed markdown report to file
    report_dir = Path("reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"inspection_{path.stem}.md"

    report_lines = [
        f"# Ingestion & Chunking Inspection: {path.name}",
        f"- **File Path**: `{path.resolve()}`",
        f"- **Engine**: `{tree.root.metadata.get('parser_engine', 'docling')}`",
        f"- **Quality Score ($Q_{{score}}$)**: **{report.score:.3f} / 1.0** ({'Acceptable' if report.is_acceptable else 'Degraded'})",
        f"- **Structural Blocks**: {len(sections)} sections, {len(tables)} tables, {len(paragraphs)} paragraphs",
        f"- **Total Chunks Generated**: {len(chunks)} ({len(table_chunks)} table chunks, {len(prose_chunks)} prose chunks)",
        "",
        "## 1. Detected Sections",
    ]
    for s in sections:
        report_lines.append(f"{'  ' * s.level}- [H{s.level}] {s.content}")

    report_lines.extend(["", "## 2. Extracted & Normalized Tables (with Health Diagnostics)"])
    for idx, t in enumerate(tables, 1):
        t_meta = t.table_metadata or {}
        headers = t_meta.get("headers", [])
        total_rows = t_meta.get("total_rows", len(t_meta.get("rows", [])))
        caption = t_meta.get("caption") or t.metadata.get("caption", "Untitled Table")
        prose_link = f"(Linked to prose: `{t.preceding_prose_id}`)" if t.preceding_prose_id else "(No preceding prose)"
        h_rep = table_health_reports.get(t.id)

        report_lines.append(f"### Table {idx}: {caption}")
        report_lines.append(f"- **Table ID**: `{t.id}`")
        if h_rep:
            math_diag = "Bypassed (Nested/None)" if h_rep.math_reconciled is None else ("✅ Reconciled" if h_rep.math_reconciled else "❌ Mismatch")
            health_str = (
                f"**{h_rep.health_score:.2f} / 1.0** ({'⚠️ REPAIR REQUIRED' if h_rep.needs_repair else '✅ Healthy'}) "
                f"| Grounding: **{h_rep.grounding_ratio * 100:.1f}%** | Math: **{math_diag}**"
            )
            report_lines.append(f"- **Structural Health**: {health_str}")
            if h_rep.issues:
                for issue in h_rep.issues:
                    report_lines.append(f"  - 🚩 *{issue}*")
        if t.id in table_repair_results:
            rep = table_repair_results[t.id]
            rep_status = "✨ REPAIRED" if rep.repaired else f"⚠️ SKIPPED / FAILED ({rep.method})"
            report_lines.append(f"- **VLM Repair**: {rep_status} — {rep.reason}")
        report_lines.append(f"- **Section Path**: `{' > '.join(t.section_path)}`")
        report_lines.append(f"- **Prose Link**: {prose_link}")
        report_lines.append(f"- **Rows**: {total_rows} | **Columns** ({len(headers)}): `{headers}`")
        report_lines.append("\n**Markdown Preview:**\n")
        report_lines.append(t.content[:500] + ("\n..." if len(t.content) > 500 else ""))
        report_lines.append("")

    report_lines.extend(["", "## 3. All Generated Chunks & Relational Provenance"])
    report_lines.append("| # | Chunk ID | Block Type | Section Path | Relational Links / Metadata |")
    report_lines.append("| :--- | :--- | :--- | :--- | :--- |")

    for idx, c in enumerate(chunks, 1):
        sec = " > ".join(c.metadata.get("section_path", [])) or "Root"
        rels = []
        if c.block_type == BlockType.TABLE:
            if c.metadata.get("table_id"):
                rels.append(f"Table: `{c.metadata['table_id']}`")
            if c.metadata.get("preceding_prose_id"):
                rels.append(f"Intro Prose: `{c.metadata['preceding_prose_id']}`")
            if c.metadata.get("is_atomic"):
                rels.append("Atomic (Full)")
            else:
                rels.append(f"Rows: {c.metadata.get('row_range')}")
        else:
            if c.metadata.get("parent_id"):
                rels.append(f"Parent: `{c.metadata['parent_id']}`")
            if c.metadata.get("page"):
                rels.append(f"Page: {c.metadata['page']}")

        rel_str = ", ".join(rels) if rels else "-"
        report_lines.append(f"| {idx} | `{c.chunk_id}` | `{c.block_type.value}` | {sec} | {rel_str} |")

    report_lines.extend(["", "## 4. Chunk Content & Dual Representation Details"])
    for idx, c in enumerate(chunks, 1):
        report_lines.append(f"### Chunk {idx}: `{c.chunk_id}` ({c.block_type.value})")
        report_lines.append(f"- **Section**: `{' > '.join(c.metadata.get('section_path', []))}`")
        report_lines.append(f"- **Metadata**: `{c.metadata}`")
        report_lines.append("\n#### [A] Content for Vector Embedding (KV / Semantic Linearization):\n")
        report_lines.append("```text")
        report_lines.append(c.content_for_embedding[:800] + ("\n... [truncated]" if len(c.content_for_embedding) > 800 else ""))
        report_lines.append("```")
        report_lines.append("\n#### [B] Content for LLM Context Generation:\n")
        if c.block_type == BlockType.TABLE:
            report_lines.append(c.content_for_generation)
        else:
            report_lines.append(f"> {c.content_for_generation}")
        report_lines.append("\n---\n")

    report_file.write_text("\n".join(report_lines), encoding="utf-8")

    print("\n" + "=" * 80)
    print(f"💾 Full Inspection Report Saved To: {report_file.resolve()}")
    print("🎉 Chunking & Ingestion Inspection Finished Successfully!")
    print("=" * 80)


if __name__ == "__main__":
    cli_parser = argparse.ArgumentParser(description="Test Docling ingestion and block chunking on a PDF.")
    cli_parser.add_argument("file_path", help="Path to PDF or document file to test (e.g. data/sample.pdf)")
    cli_parser.add_argument("--query", "-q", help="Optional test question to simulate retrieval and hit collapse", default=None)
    args = cli_parser.parse_args()

    inspect_pdf(args.file_path, query=args.query)
