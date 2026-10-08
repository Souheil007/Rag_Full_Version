# Plan 5: System Design, Scaling (100x), and Interview Playbook (ADRs)

## 🎯 Objective
Document architectural tradeoffs, scalability bottlenecks at 100x volume, and decision-making frameworks (answering: *"Why RAG over fine-tuning?"* and *"What breaks first at 100x scale?"*).

---

## 🏗️ 100x Scale Architecture Blueprint

```mermaid
flowchart TD
    subgraph Client_Layer["Client & Ingress"]
        LB["Load Balancer / Ingress (FastAPI Replicas)"]
    end

    subgraph Caching_and_Routing["Caching & Routing"]
        Redis["Distributed Redis Semantic Cache"]
        Router["Model Router (Flash vs Pro)"]
    end

    subgraph Distributed_Storage["Storage & Retrieval"]
        Qdrant["Distributed Vector DB (HNSW / IVF-PQ Sharded Index)"]
        ES["Elasticsearch / OpenSearch (Distributed BM25)"]
    end

    subgraph Async_Workers["Asynchronous Ingestion Pipeline"]
        Queue["Kafka / Celery Ingestion Queue"]
        Workers["Ingestion & Chunking Workers (Batch GPU Embeddings)"]
    end

    LB --> Redis
    Redis --> Router
    Router --> Qdrant
    Router --> ES
    Queue --> Workers
    Workers --> Qdrant
    Workers --> ES
```

---

## 📁 Files & Documentation to Create

1. **`docs/ADR/001_rag_vs_fine_tuning.md`**
   - Detailed comparison matrix: Dynamic updates vs domain styling, data privacy, hallucinations, and maintenance cost.
2. **`docs/ADR/002_scaling_at_100x.md`**
   - Failure analysis at 100x:
     - Vector Index RAM exhaustion $\rightarrow$ HNSW index quantization (Product Quantization / Scalar Quantization).
     - Ingestion bottleneck $\rightarrow$ Async event-driven queue (Kafka/Celery) with batch embedding workers.
     - Rate limits & LLM concurrency $\rightarrow$ Tiered token pooling and backoff retries.
3. **`docs/ADR/003_chunking_and_retrieval_tradeoffs.md`**
   - Ablation analysis of chunk sizes (256 vs 512 vs 1024), overlaps, and Hybrid RRF vs Single Vector Search.
4. **`docs/INTERVIEW_CHEAT_SHEET.md`**
   - Comprehensive answers and talking points for the top 10 senior AI engineer interview scenarios.

---

## 📋 Task Checklist

- [ ] Create `docs/ADR/` directory.
- [ ] Write `docs/ADR/001_rag_vs_fine_tuning.md`.
- [ ] Write `docs/ADR/002_scaling_at_100x.md`.
- [ ] Write `docs/ADR/003_chunking_and_retrieval_tradeoffs.md`.
- [ ] Write `docs/INTERVIEW_CHEAT_SHEET.md`.
