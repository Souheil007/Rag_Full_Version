"""Unit tests for TableSanityChecker structural health, math reconciliation, and lexical grounding."""

import pytest
from src.ingestion.quality_scorer import TableSanityChecker, TableHealthReport


def test_table_sanity_checker_healthy_table():
    """Verify that a standard balanced table receives a high health score."""
    checker = TableSanityChecker(repair_threshold=0.70)
    headers = ["Metric", "2021", "2022", "2023"]
    rows = [
        ["Revenue", "$100M", "$120M", "$150M"],
        ["Operating Profit", "$20M", "$25M", "$35M"],
        ["Net Margin", "20%", "21%", "23%"],
    ]

    report = checker.evaluate_table(table_id="tbl_healthy", headers=headers, rows=rows)

    assert isinstance(report, TableHealthReport)
    assert report.health_score >= 0.90
    assert not report.needs_repair
    assert len(report.issues) == 0


def test_table_sanity_checker_detects_column_shift():
    """Verify that inverted/shifted tables (like Table 14 with boolean first col and long last col) are caught."""
    checker = TableSanityChecker(repair_threshold=0.70)
    headers = ["Question", "Respondent A", "Respondent B", "Respondent C"]
    rows = [
        ["No", "Yes", "No", "Are you a UK citizen?"],
        ["Yes", "No", "Yes", "Are you currently employed?"],
        ["No", "", "No Yes", "Do you have a driving licence?"],
    ]

    report = checker.evaluate_table(table_id="tbl_shifted_14", headers=headers, rows=rows)

    assert report.needs_repair is True
    assert report.health_score < 0.70
    assert any("alignment skew" in issue.lower() for issue in report.issues)
    assert report.metrics["is_column_shifted"] == 1.0


def test_table_sanity_checker_empty_and_jagged():
    """Verify that empty and jagged grids trigger repair flags."""
    checker = TableSanityChecker(repair_threshold=0.70)

    # Empty
    rep_empty = checker.evaluate_table(table_id="tbl_empty", headers=[], rows=[])
    assert rep_empty.needs_repair is True
    assert rep_empty.health_score == 0.0

    # Jagged & sparse
    headers = ["Col A", "Col B", "Col C", "Col D"]
    rows = [
        ["Val 1", "Val 2"],  # Missing cols
        ["", "", "", ""],    # Empty row
        ["Val 3", "Val 4", "Val 5", "Val 6"],
    ]
    rep_jagged = checker.evaluate_table(table_id="tbl_sparse", headers=headers, rows=rows)
    assert rep_jagged.needs_repair is True
    assert any("jagged" in issue.lower() or "empty cell" in issue.lower() for issue in rep_jagged.issues)


def test_accounting_number_parser():
    """Verify that accounting numbers, parentheses negative, commas, and footnotes parse properly."""
    parse = TableSanityChecker.parse_accounting_number

    assert parse("100") == 100.0
    assert parse("$250,000") == 250000.0
    assert parse("(150,000)") == -150000.0
    assert parse("(25.5)") == -25.5
    assert parse("-40") == -40.0
    assert parse("£35.91 1") == 35.91
    assert parse("14.8*") == 14.8
    assert parse("-") == 0.0
    assert parse("—") == 0.0
    assert parse("") is None
    assert parse("Non-numeric text") is None


def test_pure_total_math_reconciliation_pass():
    """Verify that a table with consistent row sums and accounting parentheses reconciles successfully."""
    checker = TableSanityChecker(repair_threshold=0.70)
    headers = ["Item", "2020", "2021"]
    rows = [
        ["Gross Revenue", "250,000", "300,000"],
        ["Operating Costs", "(150,000)", "(180,000)"],
        ["Other Income", "10,000", "20,000"],
        ["Total Net Income", "110,000", "140,000"],  # 250 - 150 + 10 = 110; 300 - 180 + 20 = 140
    ]

    report = checker.evaluate_table(table_id="tbl_math_pass", headers=headers, rows=rows)

    assert report.math_reconciled is True
    assert not report.needs_repair
    assert report.health_score >= 0.90
    assert len(report.issues) == 0


def test_pure_total_math_reconciliation_mismatch():
    """Verify that arithmetic discrepancy on pure total tables triggers repair flags."""
    checker = TableSanityChecker(repair_threshold=0.70)
    headers = ["Item", "Amount"]
    rows = [
        ["Consulting Fees", "100.00"],
        ["Software Licensing", "200.00"],
        ["Server Hosting", "50.00"],
        ["Total", "450.00"],  # 100 + 200 + 50 = 350 != 450 (Mismatch!)
    ]

    report = checker.evaluate_table(table_id="tbl_math_fail", headers=headers, rows=rows)

    assert report.math_reconciled is False
    assert report.needs_repair is True
    assert any("math reconciliation failed" in issue.lower() for issue in report.issues)
    assert report.health_score <= 0.50


def test_nested_subtotal_table_bypasses_math_check():
    """Verify that multi-tier tables with subtotals are intentionally bypassed to prevent false alarms."""
    checker = TableSanityChecker(repair_threshold=0.70)
    headers = ["Item", "Amount"]
    rows = [
        ["Current Assets Cash", "50"],
        ["Current Assets Receivables", "50"],
        ["Subtotal Current Assets", "100"],
        ["Non-Current Property", "200"],
        ["Subtotal Non-Current", "200"],
        ["Total Assets", "300"],
    ]

    report = checker.evaluate_table(table_id="tbl_nested_subtotal", headers=headers, rows=rows)

    # Should cleanly bypass arithmetic summing
    assert report.math_reconciled is None
    assert not report.needs_repair
    assert not any("math reconciliation failed" in issue.lower() for issue in report.issues)


def test_verbatim_grounding_pass():
    """Verify that extracted numbers present on the source page receive 100% grounding."""
    checker = TableSanityChecker(repair_threshold=0.70)
    headers = ["Region", "Sales", "Margin"]
    rows = [
        ["Americas", "$500M", "22%"],
        ["Europe", "$350M", "19%"],
    ]
    raw_page_text = "Financial Highlights: Americas recorded $500M with margin 22%. Europe achieved $350M and 19%."

    report = checker.evaluate_table(
        table_id="tbl_grounded",
        headers=headers,
        rows=rows,
        raw_page_text=raw_page_text,
    )

    assert report.grounding_ratio == 1.0
    assert not report.needs_repair
    assert len(report.issues) == 0


def test_verbatim_grounding_fail_on_hallucinated_digits():
    """Verify that hallucinated or dropped numbers trigger verbatim grounding repair flags."""
    checker = TableSanityChecker(repair_threshold=0.70)
    headers = ["Asset", "Value"]
    rows = [
        ["Real Estate", "999,999"],
        ["Equities", "888,888"],
        ["Bonds", "777,777"],
    ]
    # Source page has completely different numbers
    raw_page_text = "Audited figures: Real Estate 123456, Equities 234567, Bonds 345678."

    report = checker.evaluate_table(
        table_id="tbl_unreferenced",
        headers=headers,
        rows=rows,
        raw_page_text=raw_page_text,
    )

    assert report.grounding_ratio < 0.85
    assert report.needs_repair is True
    assert any("grounding" in issue.lower() for issue in report.issues)
