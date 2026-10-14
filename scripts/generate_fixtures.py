"""Fixture generator producing complex multi-page tables with merged cells."""

from pathlib import Path
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


def generate_ugly_multipage_table_docx(output_path: str = "tests/fixtures/ugly_multipage_table.docx") -> str:
    """Generate a realistic complex DOCX document with multi-page merged-cell tables.

    Args:
        output_path: Destination file path for generated DOCX fixture.

    Returns:
        Absolute path to generated fixture file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    doc = docx.Document()

    # Document Header
    title = doc.add_heading("Global Hedging & Risk Ledger", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    intro = doc.add_paragraph(
        "This regulatory document outlines the consolidated multi-tier hedging positions across "
        "foreign currency, interest rate, and commodity derivatives. As detailed in the ledger table below, "
        "tier-1 exposures require daily mark-to-market reconciliations with central counterparty clearinghouses."
    )

    doc.add_heading("1. Multi-Tier Derivative Exposure Ledger", level=1)
    doc.add_paragraph(
        "Note on Table 1.1: Multi-page table continuations carry forward positions across risk domains. "
        "Parent groupings in column 1 define contractual settlement jurisdictions."
    )

    # 40-row table spanning multiple pages with multi-tier merged headers
    num_rows = 42
    num_cols = 5
    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.style = "Table Grid"

    # Multi-tier Merged Header (Row 0 & Row 1)
    # Merge row 0 cells 0-1 into "Risk Jurisdiction & Instrument"
    table.cell(0, 0).text = "Risk Jurisdiction & Instrument"
    table.cell(0, 0).merge(table.cell(0, 1))

    # Merge row 0 cells 2-3 into "2025 Delta Exposure (USD Millions)"
    table.cell(0, 2).text = "2025 Delta Exposure (USD Millions)"
    table.cell(0, 2).merge(table.cell(0, 3))

    table.cell(0, 4).text = "Regulatory Tier"

    # Row 1 sub-headers (underlying sub-cells)
    sub_headers = ["Jurisdiction", "Instrument Code", "Q1 Delta", "Q2 Delta", "Tier Classification"]
    for c_idx, sub in enumerate(sub_headers):
        table.cell(1, c_idx).text = sub

    # Populate rows with merged spans in column 0
    jurisdictions = ["North America (CFTC)", "European Union (ESMA)", "Asia-Pacific (JFSA)", "Emerging Markets"]
    row_idx = 2

    for j_idx, jur in enumerate(jurisdictions):
        jur_start_row = row_idx
        # 10 rows per jurisdiction
        for item_idx in range(10):
            if row_idx >= num_rows:
                break
            code = f"DERIV-{jur[:3].upper()}-{item_idx + 1:03d}"
            q1_val = f"${(item_idx + 1) * 3.75:.2f}M"
            q2_val = f"${(item_idx + 1) * 4.10:.2f}M"
            tier = "Tier 1 (High)" if item_idx < 4 else ("Tier 2 (Med)" if item_idx < 8 else "Tier 3 (Standard)")

            table.cell(row_idx, 0).text = jur
            table.cell(row_idx, 1).text = code
            table.cell(row_idx, 2).text = q1_val
            table.cell(row_idx, 3).text = q2_val
            table.cell(row_idx, 4).text = tier
            row_idx += 1

        # Simulate page break after row 21 (mid-table)
        if j_idx == 1:
            doc.add_page_break()

    # Trailing section after table
    doc.add_heading("2. Capital Requirements & Buffer Standards", level=1)
    doc.add_paragraph(
        "All positions categorized as Tier 1 (High) require an additional 250 basis points of CET1 capital "
        "to satisfy systemic risk buffer mandates established under Basel III guidelines."
    )

    doc.save(str(path))
    return str(path.resolve())


if __name__ == "__main__":
    out_file = generate_ugly_multipage_table_docx()
    print(f"Generated fixture: {out_file}")
