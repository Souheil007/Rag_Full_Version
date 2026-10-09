"""Unit and integration tests for guardrails, citation verification, and Jev entailment."""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from src.api.routes import create_app
from src.guardrails.citation_verifier import CitationVerifier
from src.guardrails.fallback_handler import (
    DEFAULT_FALLBACK_MESSAGE,
    FallbackHandler,
)
from src.guardrails.hallucination_detector import HallucinationDetector
from src.guardrails.jev_client import JevClient


@pytest.fixture
def sample_retrieved_docs():
    """Sample retrieved documents for testing."""
    return [
        {
            "chunk_id": "doc1_chunk0",
            "chunk_text": "Photosynthesis is the biological process used by plants to convert light energy into chemical energy.",
            "metadata": {"filename": "biology.txt"},
        },
        {
            "chunk_id": "doc2_chunk0",
            "chunk_text": "Chlorophyll is the primary pigment responsible for absorbing light in green leaves.",
            "metadata": {"filename": "chlorophyll.pdf"},
        },
    ]


# ---------------------------------------------------------
# CitationVerifier Tests
# ---------------------------------------------------------

def test_citation_verifier_valid_numeric_citations(sample_retrieved_docs):
    """Verify that citations within doc bounds pass validation."""
    verifier = CitationVerifier()
    answer = "Photosynthesis converts light to chemical energy [1] using chlorophyll [2]."
    result = verifier.verify_citations(answer, sample_retrieved_docs)

    assert result.is_valid is True
    assert result.total_citations == 2
    assert result.citation_score == 1.0
    assert len(result.invalid_citations) == 0


def test_citation_verifier_out_of_bounds_citation(sample_retrieved_docs):
    """Verify that out-of-bounds citations are flagged as invalid."""
    verifier = CitationVerifier()
    answer = "Photosynthesis occurs in plants [1], and mitochondria power the cell [5]."
    result = verifier.verify_citations(answer, sample_retrieved_docs)

    assert result.is_valid is False
    assert result.total_citations == 2
    assert len(result.invalid_citations) == 1
    assert result.invalid_citations[0]["doc_index"] == 5
    assert result.citation_score == 0.5


def test_citation_verifier_named_source_citations(sample_retrieved_docs):
    """Verify source-based citation parsing and validation."""
    verifier = CitationVerifier()
    valid_answer = "Light is absorbed by chlorophyll [Source: chlorophyll.pdf]."
    res1 = verifier.verify_citations(valid_answer, sample_retrieved_docs)
    assert res1.is_valid is True

    invalid_answer = "Water is split during the process [Source: non_existent.pdf]."
    res2 = verifier.verify_citations(invalid_answer, sample_retrieved_docs)
    assert res2.is_valid is False
    assert len(res2.invalid_citations) == 1


def test_citation_verifier_no_citations(sample_retrieved_docs):
    """Verify answers without citations are handled gracefully."""
    verifier = CitationVerifier()
    answer = "Photosynthesis creates sugar and oxygen."
    result = verifier.verify_citations(answer, sample_retrieved_docs)

    assert result.is_valid is True
    assert result.total_citations == 0
    assert result.citation_score == 1.0


# ---------------------------------------------------------
# JevClient Tests
# ---------------------------------------------------------

def test_jev_client_heuristic_fallback(sample_retrieved_docs):
    """Verify offline heuristic fallback when no API key is provided."""
    client = JevClient(api_key=None)
    context = sample_retrieved_docs[0]["chunk_text"]

    # Grounded claim
    claim_grounded = "Photosynthesis converts light energy into chemical energy."
    res_grounded = client.check_entailment(claim_grounded, context)
    assert res_grounded["is_supported"] is True
    assert res_grounded["engine"] == "heuristic_fallback"

    # Hallucinated / unrelated claim
    claim_unrelated = "Quantum computers operate at absolute zero using superconducting qubits."
    res_unrelated = client.check_entailment(claim_unrelated, context)
    assert res_unrelated["is_supported"] is False
    assert res_unrelated["decision"] == "unsupported"


@patch("src.guardrails.jev_client.httpx.Client")
def test_jev_client_mock_api_success(mock_httpx_cls, sample_retrieved_docs):
    """Verify successful response parsing from Jev decision API."""
    mock_post = MagicMock()
    mock_post.status_code = 200
    mock_post.json.return_value = {
        "choice": "supported",
        "confidence": 0.96,
        "model": "typesafe/jev",
    }

    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_post
    mock_httpx_cls.return_value.__enter__.return_value = mock_client_instance

    client = JevClient(api_key="mock_key")
    res = client.check_entailment(
        claim="Chlorophyll absorbs light in green leaves.",
        context=sample_retrieved_docs[1]["chunk_text"],
        confidence_threshold=0.85,
    )

    assert res["is_supported"] is True
    assert res["confidence"] == 0.96
    assert res["engine"] == "jev"


# ---------------------------------------------------------
# HallucinationDetector Tests
# ---------------------------------------------------------

def test_hallucination_detector_grounded_answer(sample_retrieved_docs):
    """Verify that a grounded response passes hallucination verification."""
    detector = HallucinationDetector()
    answer = "Photosynthesis is the biological process converting light to chemical energy."
    result = detector.verify_grounding(answer, sample_retrieved_docs)

    assert result.is_grounded is True
    assert result.grounding_score >= 0.8
    assert len(result.unsupported_claims) == 0


def test_hallucination_detector_hallucinated_answer(sample_retrieved_docs):
    """Verify that an answer with fabricated facts is flagged."""
    detector = HallucinationDetector()
    answer = "Photosynthesis produces titanium alloy structures inside Martian volcanic craters."
    result = detector.verify_grounding(answer, sample_retrieved_docs)

    assert result.is_grounded is False
    assert len(result.unsupported_claims) > 0


# ---------------------------------------------------------
# FallbackHandler Tests
# ---------------------------------------------------------

def test_fallback_handler_approval(sample_retrieved_docs):
    """Verify that compliant outputs are approved."""
    verifier = CitationVerifier()
    detector = HallucinationDetector()
    handler = FallbackHandler()

    answer = "Photosynthesis converts light into chemical energy [1]."
    c_res = verifier.verify_citations(answer, sample_retrieved_docs)
    g_res = detector.verify_grounding(answer, sample_retrieved_docs)

    decision = handler.evaluate_and_enforce(answer, c_res, g_res)
    assert decision.approved is True
    assert decision.final_answer == answer
    assert decision.action_taken == "approved"


def test_fallback_handler_trigger_on_hallucination(sample_retrieved_docs):
    """Verify that detected hallucinations trigger safe fallback response."""
    verifier = CitationVerifier()
    detector = HallucinationDetector()
    handler = FallbackHandler(strict_mode=True)

    answer = "Photosynthesis constructs titanium spaceships on Jupiter [1]."
    c_res = verifier.verify_citations(answer, sample_retrieved_docs)
    g_res = detector.verify_grounding(answer, sample_retrieved_docs)

    decision = handler.evaluate_and_enforce(answer, c_res, g_res)
    assert decision.approved is False
    assert decision.final_answer == DEFAULT_FALLBACK_MESSAGE
    assert decision.action_taken == "fallback_triggered"
    assert len(decision.reasons) > 0


# ---------------------------------------------------------
# Integration Test via FastAPI Endpoint
# ---------------------------------------------------------

def test_api_query_guardrail_telemetry(monkeypatch):
    """Test that /query endpoint includes guardrail execution metrics and trace spans."""
    app = create_app()
    client = TestClient(app)

    # Mock retriever to return deterministic chunk
    mock_retrieved = [
        {
            "chunk_id": "test_chunk_1",
            "chunk_text": "The Eiffel Tower was completed in 1889 in Paris.",
            "metadata": {"filename": "eiffel.txt"},
            "score": 0.95,
        }
    ]

    with patch("src.retrieval.retriever.Retriever.retrieve", return_value=mock_retrieved), \
         patch("src.llm.llm_client.LLMClient.generate", return_value="The Eiffel Tower was built in 1889 [1]."):
        resp = client.post("/query", json={"query": "When was Eiffel Tower built?"})

    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "The Eiffel Tower was built in 1889 [1]." in data["answer"]
    assert data["guardrail_status"] == "approved"
    assert data["citation_score"] == 1.0
    assert data["grounding_score"] >= 0.8
