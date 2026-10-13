"""Layout-aware parser extracting structured document blocks, headings, and tables."""

import re
from pathlib import Path
from typing import Any
from src.ingestion.doc_tree import BlockType, DocumentNode, DocumentTree
from src.ingestion.quality_scorer import ExtractionQualityScorer, QualityReport
from src.chunking.table_parser import TableParser
from src.utils.helpers import get_logger
from docling.document_converter import DocumentConverter

logger = get_logger(__name__)

# Semantic Heading Patterns:
# Used as a secondary signal resolver when Docling's vision/layout model classifies small-font
# numbered headings (e.g. "1.2.3 Limitation of Liability") as generic body text.
# Docling's layout engine remains the primary authority on reading order, tables, and visual headers.
HEADING_PATTERNS = [
    (re.compile(r"^(#{1,6})\s+(.+)$"), "markdown"),
    (re.compile(r"^(\d+(\.\d+)*)\.?\s+([A-Z][\w\s,:-]{2,80})$"), "numbered"),
    (re.compile(r"^(Chapter|Section|Article|Appendix)\s+([0-9A-Z]+)[:.]?\s*(.*)$", re.IGNORECASE), "named"),
]

RUNNING_HEADER_FOOTER_PATTERNS = [
    re.compile(r"^(Page\s+\d+(\s+of\s+\d+)?|\d+\s*/\s*\d+|\b\d+\b)$", re.IGNORECASE),
    re.compile(r"^(Confidential|Internal Use Only|Draft|All Rights Reserved).*$", re.IGNORECASE),
]


class LayoutParser:
    """Parses native document streams directly using Docling into a structured DocumentTree."""

    def __init__(self, quality_threshold: float = 0.65) -> None:
        """Initialize LayoutParser with Docling DocumentConverter and quality threshold.

        Args:
            quality_threshold: Minimum acceptable extraction quality score.
        """
        self.quality_scorer = ExtractionQualityScorer(threshold=quality_threshold)
        self.converter = DocumentConverter()

    def is_running_header_or_footer(self, line: str) -> bool:
        """Check if a line matches common running header, footer, or page number patterns.

        Args:
            line: Text line string to inspect.

        Returns:
            True if the line is a detected header/footer artifact, otherwise False.
        """
        stripped = line.strip()
        if not stripped:
            return False
        return any(pat.match(stripped) for pat in RUNNING_HEADER_FOOTER_PATTERNS)

    def detect_heading(self, line: str) -> tuple[bool, int, str]:
        """Detect whether a line is a section heading and determine its hierarchy level.

        Args:
            line: Raw line string.

        Returns:
            Tuple of (is_heading, heading_level, clean_title).
        """
        stripped = line.strip()
        if not stripped or len(stripped) > 120:
            return False, 0, ""

        # 1. Markdown headings (# H1, ## H2, etc.)
        md_match = HEADING_PATTERNS[0][0].match(stripped)
        if md_match:
            level = len(md_match.group(1))
            title = md_match.group(2).strip()
            return True, level, title

        # 2. Numbered headings (1. Intro, 1.2 Sub-section, etc.)
        num_match = HEADING_PATTERNS[1][0].match(stripped)
        if num_match:
            numbering = num_match.group(1)
            title = num_match.group(3).strip()
            level = numbering.count(".") + 1
            return True, level, f"{numbering} {title}"

        # 3. Named sections (Chapter 1, Section 2)
        named_match = HEADING_PATTERNS[2][0].match(stripped)
        if named_match:
            prefix = named_match.group(1)
            num = named_match.group(2)
            rest = named_match.group(3).strip()
            title = f"{prefix} {num}: {rest}" if rest else f"{prefix} {num}"
            return True, 1 if prefix.lower() == "chapter" else 2, title

        # 4. Short ALL-CAPS headings (length between 4 and 60 chars)
        if stripped.isupper() and 4 <= len(stripped) <= 60 and not stripped.startswith("|"):
            words = stripped.split()
            if len(words) <= 8 and not re.search(r"[$%0-9]", stripped):
                return True, 1, stripped

        return False, 0, ""

    def parse_blocks(self, text: str, page_number: int = 1) -> list[dict[str, Any]]:
        """Extract typed document blocks from raw text.

        Args:
            text: Raw document text string.
            page_number: Source page number.

        Returns:
            List of raw block dictionaries ready for DocumentTree construction.
        """
        lines = text.splitlines()
        blocks: list[dict[str, Any]] = []

        i = 0
        block_counter = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                i += 1
                continue

            # Prune running headers and footers
            if self.is_running_header_or_footer(stripped):
                i += 1
                continue

            # 1. Check for Code Blocks (fenced)
            if stripped.startswith("```"):
                code_lines = [line]
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    code_lines.append(lines[i])
                    i += 1
                blocks.append({
                    "id": f"b_{block_counter}",
                    "type": BlockType.CODE.value,
                    "content": "\n".join(code_lines),
                    "level": 0,
                    "metadata": {"page": page_number},
                })
                block_counter += 1
                continue

            # 2. Check for Table Blocks (Markdown pipe table)
            if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2:
                table_lines = [line]
                i += 1
                while i < len(lines):
                    next_stripped = lines[i].strip()
                    if next_stripped.startswith("|") and next_stripped.endswith("|"):
                        table_lines.append(lines[i])
                        i += 1
                    else:
                        break

                table_content = "\n".join(table_lines)
                headers, rows = TableParser.parse_markdown_table(table_content)
                blocks.append({
                    "id": f"b_{block_counter}",
                    "type": BlockType.TABLE.value,
                    "content": table_content,
                    "level": 0,
                    "metadata": {"page": page_number},
                    "table_metadata": {
                        "headers": headers,
                        "rows": rows,
                        "total_rows": len(rows),
                    },
                })
                block_counter += 1
                continue

            # 3. Check for Headings
            is_head, level, title = self.detect_heading(line)
            if is_head:
                blocks.append({
                    "id": f"b_{block_counter}",
                    "type": BlockType.SECTION.value,
                    "content": title,
                    "level": level,
                    "metadata": {"page": page_number},
                })
                block_counter += 1
                i += 1
                continue

            # 4. Standard Paragraph Accumulation
            para_lines = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()
                if not next_stripped:
                    break
                if self.is_running_header_or_footer(next_stripped):
                    i += 1
                    continue
                if next_stripped.startswith("```") or (next_stripped.startswith("|") and next_stripped.endswith("|")):
                    break
                is_next_head, _, _ = self.detect_heading(next_line)
                if is_next_head:
                    break

                para_lines.append(next_line)
                i += 1

            blocks.append({
                "id": f"b_{block_counter}",
                "type": BlockType.PARAGRAPH.value,
                "content": "\n".join(para_lines).strip(),
                "level": 0,
                "metadata": {"page": page_number},
            })
            block_counter += 1

        return blocks

    def parse_document(
        self,
        text: str,
        doc_id: str = "doc_root",
        title: str = "Document",
        source_path: str = "",
    ) -> tuple[DocumentTree, QualityReport]:
        """Parse raw document text into an evaluated, linked DocumentTree.

        Args:
            text: Extracted document text.
            doc_id: Unique document identifier.
            title: Human-readable title.
            source_path: File system path if applicable.

        Returns:
            Tuple of (DocumentTree instance, QualityReport).
        """
        # Assess extraction quality
        quality_report = self.quality_scorer.evaluate_text(text)
        if not quality_report.is_acceptable:
            logger.warning(
                "Document %s failed quality threshold (score: %.3f): %s",
                doc_id,
                quality_report.score,
                quality_report.warnings,
            )

        blocks = self.parse_blocks(text)
        tree = DocumentTree.from_blocks(blocks, doc_id=doc_id, title=title)
        tree.root.metadata["quality_score"] = quality_report.score
        tree.root.metadata["is_acceptable"] = quality_report.is_acceptable
        tree.root.metadata["source_path"] = source_path

        return tree, quality_report

    @classmethod
    def _tree_from_docling_document(
        cls,
        docling_doc: Any,
        doc_id: str,
        title: str,
        source_path: str = "",
    ) -> DocumentTree:
        """Construct DocumentTree directly from DoclingDocument items without regex loss.

        Args:
            docling_doc: DoclingDocument instance.
            doc_id: Unique document identifier.
            title: Document title.
            source_path: Source file path.

        Returns:
            DocumentTree built from native Docling items.
        """
        blocks: list[dict[str, Any]] = []
        block_counter = 0

        # Check if docling_doc has iterate_items
        if hasattr(docling_doc, "iterate_items"):
            for entry in docling_doc.iterate_items():
                item = entry[0] if isinstance(entry, (tuple, list)) else entry
                type_name = type(item).__name__

                # Section Headers
                if "SectionHeader" in type_name or hasattr(item, "level"):
                    text = getattr(item, "text", "")
                    lvl = int(getattr(item, "level", 1))
                    blocks.append({
                        "id": f"b_{block_counter}",
                        "type": BlockType.SECTION.value,
                        "content": text.strip(),
                        "level": lvl,
                        "metadata": {"origin": "docling_ast"},
                    })
                    block_counter += 1

                # Tables
                elif "Table" in type_name:
                    norm_table = TableParser.from_docling_table(
                        item,
                        doc=docling_doc,
                        table_id=f"tbl_{block_counter}",
                    )
                    from src.chunking.table_serializer import TableSerializer

                    md_table = TableSerializer.to_markdown(norm_table)
                    blocks.append({
                        "id": f"b_{block_counter}",
                        "type": BlockType.TABLE.value,
                        "content": md_table,
                        "level": 0,
                        "table_metadata": {
                            "caption": norm_table.caption,
                            "headers": norm_table.headers,
                            "rows": norm_table.rows,
                            "total_rows": len(norm_table.rows),
                            "units": norm_table.units,
                        },
                        "metadata": {
                            "origin": "docling_ast",
                            "page": norm_table.page_numbers[0] if norm_table.page_numbers else 1,
                        },
                    })
                    block_counter += 1

                # Code Blocks
                elif "Code" in type_name:
                    text = getattr(item, "text", "")
                    blocks.append({
                        "id": f"b_{block_counter}",
                        "type": BlockType.CODE.value,
                        "content": text.strip(),
                        "level": 0,
                        "metadata": {"origin": "docling_ast"},
                    })
                    block_counter += 1

                # Regular Paragraphs or undetected headings
                elif hasattr(item, "text"):
                    text = getattr(item, "text", "").strip()
                    if text:
                        temp_parser = cls()
                        is_head, lvl, title_clean = temp_parser.detect_heading(text)
                        if is_head:
                            blocks.append({
                                "id": f"b_{block_counter}",
                                "type": BlockType.SECTION.value,
                                "content": title_clean,
                                "level": lvl,
                                "metadata": {"origin": "docling_ast"},
                            })
                        else:
                            blocks.append({
                                "id": f"b_{block_counter}",
                                "type": BlockType.PARAGRAPH.value,
                                "content": text,
                                "level": 0,
                                "metadata": {"origin": "docling_ast"},
                            })
                        block_counter += 1

        # Fallback to export_to_markdown if iterate_items was empty
        if not blocks and hasattr(docling_doc, "export_to_markdown"):
            md_text = docling_doc.export_to_markdown()
            temp_parser = LayoutParser()
            blocks = temp_parser.parse_blocks(md_text)

        tree = DocumentTree.from_blocks(blocks, doc_id=doc_id, title=title)
        tree.root.metadata["source_path"] = source_path
        tree.root.metadata["parser_engine"] = "docling_ast"
        return tree

    def parse_file(
        self,
        file_path: str,
        doc_id: str | None = None,
    ) -> tuple[DocumentTree, QualityReport]:
        """Parse local document file directly using Docling DocumentConverter.

        Args:
            file_path: Absolute or relative path to PDF, DOCX, HTML, or text document.
            doc_id: Optional unique identifier. Defaults to file stem.

        Returns:
            Tuple of (DocumentTree instance, QualityReport).
        """
        path = Path(file_path)
        actual_id = doc_id or path.stem

        logger.info("Executing Docling layout conversion on %s", path.name)
        result = self.converter.convert(str(path.resolve()))
        docling_doc = result.document

        # Direct AST mapping into DocumentTree
        tree = self._tree_from_docling_document(
            docling_doc=docling_doc,
            doc_id=actual_id,
            title=path.name,
            source_path=str(path.resolve()),
        )

        # Assess overall text health from Docling markdown export
        raw_text = docling_doc.export_to_markdown() if hasattr(docling_doc, "export_to_markdown") else ""
        quality_report = self.quality_scorer.evaluate_text(raw_text)
        tree.root.metadata["quality_score"] = quality_report.score
        tree.root.metadata["is_acceptable"] = quality_report.is_acceptable
        return tree, quality_report
