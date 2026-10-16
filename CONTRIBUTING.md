# Contributing to Rag_Full_Version

Thank you for your interest in contributing to **Rag_Full_Version**! We welcome contributions from developers, researchers, and practitioners who want to advance production-grade document intelligence, hierarchical chunking, and deterministic verification.

This document outlines our development workflow, coding standards, architecture principles, and pull request guidelines.

---

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Local Setup](#local-setup)
3. [Architecture & Design Principles](#architecture--design-principles)
4. [Coding & Documentation Standards](#coding--documentation-standards)
   - [Naming Conventions](#naming-conventions)
   - [Docstrings (Concise Google Style)](#docstrings-concise-google-style)
   - [Type Annotations](#type-annotations)
5. [Development & Testing Workflow](#development--testing-workflow)
   - [Running the Test Suite](#running-the-test-suite)
   - [Testing Document Parsing & Diagnostics](#testing-document-parsing--diagnostics)
6. [Submitting a Pull Request](#submitting-a-pull-request)
   - [Branch Naming](#branch-naming)
   - [Commit Conventions](#commit-conventions)
   - [PR Checklist](#pr-checklist)
7. [Reporting Issues & Feature Requests](#reporting-issues--feature-requests)

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for everyone. Please be respectful, constructive, and collaborative in all discussions, issues, and pull requests.

---

## Getting Started

### Prerequisites
- **Python**: 3.11+ (Python 3.12 or 3.13 recommended)
- **Git**
- Optional: Docker & Docker Compose (for containerized deployment)

### Local Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/Rag_Full_Version.git
   cd Rag_Full_Version
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to supply necessary API keys (e.g., `MISTRAL_API_KEY`, `LANGSMITH_API_KEY`) if you intend to run end-to-end VLM repair or LangSmith tracing.

---

## Architecture & Design Principles

Contributions should adhere to the core design principles defined in our architecture:

1. **Modularity**: Every module in `src/` has a single, well-defined responsibility:
   - `src/ingestion/`: Document loading, layout parsing (AST), table health checking, and VLM repair.
   - `src/chunking/`: Structural block chunking, sliding-window row grouping, and relational breadcrumbs.
   - `src/retrieval/`: Dense vector retrieval, sparse BM25, Reciprocal Rank Fusion (RRF), and hit collapsing.
   - `src/guardrails/`: Citation verification, hallucination checks, and response approval.
   - `src/observability/`: Tracing, latency metrics, and LangSmith integration.
   - `src/evaluation/`: Hit Rate, MRR, Precision@K, Recall@K, and scorecard generation.
2. **Config-Driven**: Avoid hardcoding parameters. Use `config.yaml` and environment variables.
3. **Deterministic First, VLM on Demand**: Never run expensive LLMs/VLMs when fast deterministic checks (sub-2ms lexical grounding, arithmetic checks, regex) can solve or guardrail the task.
4. **Document Hierarchy (AST)**: Always preserve document tree relationships (`section_path`, parent-child hierarchy, prose links) when handling text chunks.

---

## Coding & Documentation Standards

All contributions must follow the repository rules outlined in [`AGENTS.md`](file:///C:/GithubProjects/Rag_Full_Version/AGENTS.md).

### Naming Conventions
- **Modules & Packages**: `snake_case` (e.g., `vector_store.py`, `quality_scorer.py`)
- **Classes**: `PascalCase` (e.g., `LayoutParser`, `TableSanityChecker`, `HitCollapser`)
- **Functions & Methods**: `snake_case` (e.g., `parse_file()`, `check_pure_total_math()`)
- **Variables & Attributes**: `snake_case` (e.g., `chunk_size`, `grounding_ratio`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_CHUNK_SIZE`, `SUPPORTED_EXTENSIONS`)

### Docstrings (Concise Google Style)
All public modules, classes, and functions must have concise Google-style docstrings:
- Keep the summary to 1–2 clear lines.
- Only include `Args`, `Returns`, `Yields`, and `Raises` when necessary.
- Avoid redundant prose or overly verbose explanations.

```python
def check_pure_total_math(
    headers: list[str],
    rows: list[list[str]],
    tolerance: float = 2.0,
) -> tuple[bool | None, str | None]:
    """Reconcile numerical column sums against an unambiguous bottom Total row.

    Args:
        headers: List of column header names.
        rows: Matrix of table row cells.
        tolerance: Allowed absolute discrepancy for rounding errors.

    Returns:
        Tuple of (reconciled_status, failure_reason_if_any).
    """
```

### Type Annotations
- Use modern Python type hints (`str`, `list[dict]`, `int | float`, `Optional[T]`) on all function signatures.

---

## Development & Testing Workflow

### Running the Test Suite
Before submitting any changes, verify that the complete test suite passes without errors:

```bash
# Run all tests
pytest -v

# Run a specific test module
pytest tests/test_table_health.py -v
pytest tests/test_block_chunking.py -v
```

> **Note**: Test discovery is configured via `pytest.ini` to discover tests exclusively in `tests/`.

### Testing Document Parsing & Diagnostics
To test document chunking and inspect table health reports on sample documents:

```bash
python scripts/test_pdf_chunking.py data/sample.pdf --query "What are the financial metrics?"
```

Inspection reports will be generated under `reports/inspection_<filename>.md`.

---

## Submitting a Pull Request

### Branch Naming
Create a feature or bugfix branch with a descriptive name:
- `feat/add-qdrant-vector-store`
- `fix/table-accounting-bracket-parser`
- `docs/update-ingestion-architecture`
- `test/add-multipage-table-fixtures`

### Commit Conventions
We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat(...)`: A new feature or capability.
- `fix(...)`: A bug fix.
- `docs(...)`: Documentation changes only.
- `refactor(...)`: Code change that neither fixes a bug nor adds a feature.
- `test(...)`: Adding or updating tests.
- `chore(...)`: Maintenance, dependency updates, or build configuration.

*Example:* `feat(ingestion): add pure total arithmetic reconciliation to table sanity checker`

### PR Checklist
Before opening a pull request, ensure:
- [ ] Your code passes the full test suite (`pytest -v`).
- [ ] New functionality includes corresponding unit or integration tests under `tests/`.
- [ ] All public functions, classes, and modules include concise Google-style docstrings.
- [ ] Type annotations are present across all new code signatures.
- [ ] Any new configuration option is documented in `config.yaml` or `.env.example`.
- [ ] Commit history is clean and descriptive.

---

## Reporting Issues & Feature Requests

If you encounter a bug or have an idea for improvement:
1. Check existing [GitHub Issues](https://github.com/Souheil007/Rag_Full_Version/issues) to avoid duplicates.
2. Open an issue with:
   - A clear, descriptive title.
   - Steps to reproduce (for bugs), including sample document snippets if possible.
   - Expected vs. actual behavior.
   - Your environment (OS, Python version).

---

Thank you for helping make **Rag_Full_Version** reliable and production-ready!
