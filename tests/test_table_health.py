"""Unit tests for TableSanityChecker structural health and alignment diagnostics."""

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
