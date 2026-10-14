# Empirical Chunking Benchmark Report
**Comparison: Naive Sliding-Window Chunking vs. Block-Type Chunking**

| Evaluation Metric | Naive Sliding Window (500 chars) | Block-Type Chunker (Docling AST) | Relative Gain |
| :--- | :---: | :---: | :---: |
| **Overall Recall@5** | **92.0%** (23/25) | **96.0%** (24/25) | **+4.0%** |
| **Mean NDCG@5** | **0.821** | **0.916** | **+11.5%** |

### Breakdown by Question Category

| Category | Queries | Naive Recall@5 | Block-Type Recall@5 | Naive NDCG@5 | Block-Type NDCG@5 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Cell/Row Lookup** | 8 | 100.0% | **100.0%** | 0.875 | **0.954** |
| **Table + Intro Context** | 7 | 71.4% | **85.7%** | 0.609 | **0.804** |
| **Narrative Synthesis** | 6 | 100.0% | **100.0%** | 0.877 | **0.938** |
| **Negative Control** | 4 | 100.0% | **100.0%** | 1.000 | **1.000** |

### Key Findings:
1. **Cell / Row Lookups**: Block-type chunking achieves superior retrieval because Key-Value linear serialization prepends column headers to every row.
2. **Table + Intro Context**: Naive splitters sever tables mid-row and detach them from introductory prose. Block chunking preserves section lineage and links preceding prose.
3. **Negative Controls**: Zero false-positive intrusions observed.