"""Unit tests for TableRepairer module."""

from unittest.mock import MagicMock, patch
from src.ingestion.doc_tree import DocumentNode, BlockType
from src.ingestion.quality_scorer import TableHealthReport
from src.chunking.table_repairer import TableRepairer, RepairResult


def test_table_repairer_skips_healthy_table():
    """Verify that healthy tables are not routed to VLM/OCR."""
    repairer = TableRepairer(provider="mistral")
    node = DocumentNode(
        id="tbl_healthy",
        node_type=BlockType.TABLE,
        content="| A | B |\n|---|---|\n| 1 | 2 |",
        table_metadata={"headers": ["A", "B"], "rows": [["1", "2"]]},
    )
    health = TableHealthReport(table_id="tbl_healthy", health_score=0.95, needs_repair=False)

    res = repairer.repair_table_node(node, health_report=health)

    assert isinstance(res, RepairResult)
    assert not res.repaired
    assert res.method == "healthy"


def test_table_repairer_explicitly_flags_when_api_key_missing():
    """Verify that when API key is missing, repair is skipped and explicitly flagged without heuristic fallback."""
    repairer = TableRepairer(provider="mistral")

    node = DocumentNode(
        id="tbl_damaged",
        node_type=BlockType.TABLE,
        content="| Question | Resp A |\n| No | Are you a citizen? |",
        table_metadata={"headers": ["Question", "Resp A"], "rows": [["No", "Are you a citizen?"]]},
    )
    health = TableHealthReport(table_id="tbl_damaged", health_score=0.45, needs_repair=True)

    with patch.object(repairer, "is_api_available", return_value=False):
        res = repairer.repair_table_node(node, health_report=health)

    assert not res.repaired
    assert res.method == "skipped_no_key"
    assert "Skipping VLM repair" in res.reason


def test_table_repairer_successful_mistral_vlm():
    """Verify that successful Pixtral VLM response updates table markdown and grid."""
    repairer = TableRepairer(provider="mistral")

    node = DocumentNode(
        id="tbl_damaged",
        node_type=BlockType.TABLE,
        content="| Broken | Grid |",
        table_metadata={"headers": ["Broken", "Grid"], "rows": [["X", "Y"]]},
        metadata={"page": 5, "caption": "Table 14"},
    )
    health = TableHealthReport(table_id="tbl_damaged", health_score=0.40, needs_repair=True)

    mock_choice = MagicMock()
    mock_choice.message.content = "| Question | Respondent A |\n|---|---|\n| Are you a citizen? | Yes |"

    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.complete.return_value = mock_resp

    mock_pil = MagicMock()
    mock_pil.save = MagicMock()

    mock_page = MagicMock()
    mock_page.render.return_value.to_pil.return_value = mock_pil

    mock_pdf = MagicMock()
    mock_pdf.__len__.return_value = 10
    mock_pdf.__getitem__.return_value = mock_page

    with patch.dict("os.environ", {"MISTRAL_API_KEY": "valid_key"}):
        with patch("mistralai.client.Mistral", return_value=mock_client):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pypdfium2.PdfDocument", return_value=mock_pdf):
                    res = repairer.repair_table_node(node, pdf_path="dummy.pdf", health_report=health)

    assert res.repaired is True
    assert res.method == "pixtral_vlm"
    assert res.new_headers == ["Question", "Respondent A"]
    assert res.new_rows == [["Are you a citizen?", "Yes"]]
