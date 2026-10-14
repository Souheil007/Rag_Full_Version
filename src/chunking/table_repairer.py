"""Table repair module supporting Mistral OCR / VLM and graceful skip flagging."""

import os
import re
from typing import Any
from pathlib import Path
from pydantic import BaseModel, Field

from src.ingestion.doc_tree import DocumentNode
from src.ingestion.quality_scorer import TableHealthReport, TableSanityChecker
from src.chunking.table_parser import NormalizedTable, TableParser
from src.chunking.table_serializer import TableSerializer
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class RepairResult(BaseModel):
    """Result of table repair attempt."""

    table_id: str
    repaired: bool
    method: str = "none"  # "mistral_ocr", "vlm", "skipped_no_key", "failed"
    new_markdown: str | None = None
    new_headers: list[str] = Field(default_factory=list)
    new_rows: list[list[str]] = Field(default_factory=list)
    reason: str = ""


class TableRepairer:
    """Manages table repair via Mistral OCR, Vision LLMs, or flags unrepairable tables."""

    def __init__(self, provider: str = "mistral") -> None:
        """Initialize TableRepairer with preferred VLM/OCR provider.

        Args:
            provider: Repair provider name ('mistral', 'gemini').
        """
        self.provider = provider.lower()
        self.checker = TableSanityChecker(repair_threshold=0.70)

    def is_api_available(self) -> bool:
        """Check whether the required provider API key is present in environment."""
        if self.provider == "mistral":
            return bool(os.getenv("MISTRAL_API_KEY"))
        elif self.provider == "gemini":
            return bool(os.getenv("GEMINI_API_KEY"))
        return False

    def repair_table_node(
        self,
        node: DocumentNode,
        pdf_path: str | None = None,
        health_report: TableHealthReport | None = None,
    ) -> RepairResult:
        """Attempt to repair a damaged table node via Mistral OCR or flag if no key.

        Args:
            node: DocumentNode of type BlockType.TABLE.
            pdf_path: Path to source PDF for page rendering if needed.
            health_report: Pre-computed health report.

        Returns:
            RepairResult with new table contents or explicit skipped flag.
        """
        table_meta = node.table_metadata or {}
        headers = table_meta.get("headers", [])
        rows = table_meta.get("rows", [])

        # 1. If health report not passed, compute it
        if health_report is None:
            health_report = self.checker.evaluate_table(node.id, headers, rows)

        if not health_report.needs_repair:
            return RepairResult(
                table_id=node.id,
                repaired=False,
                method="healthy",
                reason="Table already healthy; no repair required.",
            )

        # 2. Check API Key Availability - As requested, if no API key is present, DO NOT fall back to heuristics.
        # Instead, skip the repair and explicitly flag it.
        if not self.is_api_available():
            reason_msg = f"API key for {self.provider} not found or inactive. Skipping VLM repair."
            logger.warning("Table %s flagged for repair, but %s", node.id, reason_msg)
            return RepairResult(
                table_id=node.id,
                repaired=False,
                method="skipped_no_key",
                reason=reason_msg,
            )

        # 3. Attempt Mistral OCR / VLM repair
        if self.provider == "mistral":
            return self._repair_with_mistral_ocr(node, pdf_path, health_report)

        return RepairResult(
            table_id=node.id,
            repaired=False,
            method="unsupported_provider",
            reason=f"Provider '{self.provider}' repair handler not configured.",
        )

    def _repair_with_mistral_ocr(
        self,
        node: DocumentNode,
        pdf_path: str | None,
        health_report: TableHealthReport,
    ) -> RepairResult:
        """Execute repair via Mistral OCR API."""
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            return RepairResult(
                table_id=node.id,
                repaired=False,
                method="skipped_no_key",
                reason="MISTRAL_API_KEY missing from environment.",
            )

        try:
            from mistralai.client import Mistral

            client = Mistral(api_key=api_key)

            page_no = 1
            if node.metadata and "page" in node.metadata:
                page_no = int(node.metadata["page"])

            caption = node.metadata.get("caption") or (node.table_metadata or {}).get("caption", "")

            # If PDF path provided, render the specific page containing this table
            if pdf_path and Path(pdf_path).exists():
                import base64
                import io
                import pypdfium2 as pdfium

                pdf = pdfium.PdfDocument(str(pdf_path))
                target_page_idx = min(max(0, page_no - 1), len(pdf) - 1)
                page = pdf[target_page_idx]
                pil_image = page.render(scale=2).to_pil()

                buf = io.BytesIO()
                pil_image.save(buf, format="JPEG", quality=85)
                b64_image = base64.b64encode(buf.getvalue()).decode("utf-8")

                # Prompt Pixtral-12b-2409 to transcribe the exact visual table
                table_hint = f"titled '{caption}'" if caption else f"ID '{node.id}'"
                prompt_text = (
                    f"Carefully extract the table {table_hint} from this document page image. "
                    "Ensure that question/category text is in the correct column (usually column 1), "
                    "and that response answers (e.g. Yes/No/numbers) align with their respective respondent/year columns. "
                    "Output ONLY the markdown table, without commentary."
                )

                response = client.chat.complete(
                    model="pixtral-12b-2409",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{b64_image}"},
                        ],
                    }],
                )

                if response and response.choices:
                    raw_text = response.choices[0].message.content or ""
                    # Parse the Markdown table from Pixtral response
                    headers, rows = TableParser.parse_markdown_table(raw_text)
                    if headers and rows:
                        norm_table = NormalizedTable(
                            table_id=node.id,
                            caption=caption,
                            headers=headers,
                            rows=rows,
                            page_numbers=[page_no],
                        )
                        clean_md = TableSerializer.to_markdown(norm_table)
                        return RepairResult(
                            table_id=node.id,
                            repaired=True,
                            method="pixtral_vlm",
                            new_markdown=clean_md,
                            new_headers=headers,
                            new_rows=rows,
                            reason="Successfully repaired table using Mistral Pixtral VLM.",
                        )

            return RepairResult(
                table_id=node.id,
                repaired=False,
                method="failed",
                reason="Pixtral VLM returned empty or unparseable markdown grid.",
            )

        except Exception as exc:
            err_msg = str(exc)
            logger.warning("Mistral VLM call failed for %s: %s", node.id, err_msg)
            return RepairResult(
                table_id=node.id,
                repaired=False,
                method="failed",
                reason=f"Mistral VLM error: {err_msg}",
            )
