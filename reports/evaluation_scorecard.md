# 📊 RAG Evaluation Scorecard

**Overall System Score:** `1.0 / 1.0`
**Total Evaluated Cases:** `4`

## 🔍 1. Retrieval Performance Metrics
| Metric | Score | Description |
| :--- | :---: | :--- |
| **Precision@K** | `0.35` | Ratio of retrieved chunks that are relevant |
| **Recall@K** | `0.875` | Ratio of total ground-truth facts retrieved |
| **Hit Rate@K** | `1.0` | Binary presence of relevant item in top-K |
| **MRR** | `0.875` | Mean Reciprocal Rank of first relevant item |

## 🤖 2. Generation Quality Metrics (LLM-as-a-Judge)
| Metric | Score | Description |
| :--- | :---: | :--- |
| **Faithfulness / Groundedness** | `1.0` | Extracted claim grounding in context |
| **Answer Relevance** | `1.0` | Direct alignment with user query |
| **Lexical Match (Similarity)** | `0.3336` | Word-level overlap with ground truth |
