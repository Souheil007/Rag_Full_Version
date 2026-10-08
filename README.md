# RAG Full Version

A production-ready, modular Retrieval-Augmented Generation (RAG) system built with clean Python architecture.

---

## 📁 Project Structure

```
Rag_Full_Version/
├── README.md              # Project description, setup guide, and architecture
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys)
├── .env.example           # Example environment template
├── .gitignore             # Git ignore definitions
├── config.yaml            # Central configuration file
├── AGENTS.md              # Coding standards & agent instructions
├── .agents/
│   └── skills/
│       └── rag-conventions/
│           └── SKILL.md   # Skill for naming conventions and docstring guidelines
├── src/
│   ├── ingestion/         # Document ingestion (PDF, CSV, TXT, DOCX, MD)
│   │   ├── __init__.py
│   │   └── loader.py
│   ├── chunking/          # Text splitting strategies
│   │   ├── __init__.py
│   │   └── chunker.py
│   ├── embeddings/        # Text embeddings (SentenceTransformers, OpenAI, Gemini)
│   │   ├── __init__.py
│   │   └── embedder.py
│   ├── vectordb/          # Vector storage (ChromaDB, FAISS, in-memory)
│   │   ├── __init__.py
│   │   └── vector_store.py
│   ├── retrieval/         # Similarity search & context filtering
│   │   ├── __init__.py
│   │   └── retriever.py
│   ├── prompts/           # Prompt templates & formatting
│   │   ├── __init__.py
│   │   └── prompt_templates.py
│   ├── llm/               # LLM provider clients (Gemini, OpenAI, Anthropic)
│   │   ├── __init__.py
│   │   └── llm_client.py
│   ├── api/               # FastAPI endpoints & request models
│   │   ├── __init__.py
│   │   └── routes.py
│   └── utils/             # Helpers, logger, and config loader
│       ├── __init__.py
│       └── helpers.py
├── tests/                 # Unit & integration tests
│   ├── __init__.py
│   └── test_app.py
├── logs/                  # Application log files
│   └── app.log
└── main.py                # Service entry point
```

---

## 🚀 Getting Started

### 1. Installation

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

### 3. Run the Application

Start the FastAPI server:

```bash
python main.py
```

API will be available at: `http://localhost:8000`  
Interactive Swagger docs: `http://localhost:8000/docs`

---

## 🧪 Running Tests

Run unit tests with pytest:

```bash
pytest tests/ -v
```

---

## 📐 Conventions & Standards

- **Naming**: `snake_case` for modules/functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- **Docstrings**: Concise Google-style Python docstrings for all functions, classes, and modules.
- **Rules & Skills**: Defined in `AGENTS.md` and `.agents/skills/rag-conventions/SKILL.md`.
