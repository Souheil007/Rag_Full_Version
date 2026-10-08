# Vector Database Module (`src/vectordb/`)

This module manages vector database connections, document embedding indexing, metadata persistence, and nearest-neighbor semantic search.

---

## 🏗️ Architecture & Active Provider

By default, this project uses **ChromaDB** as the primary vector store (with an in-memory fallback for zero-dependency unit tests).

```mermaid
flowchart LR
    Chunks["Text Chunks + Metadata"] --> Embedder["Embedder (all-MiniLM-L6-v2)"]
    Embedder --> VS["VectorStore (ChromaDB)"]
    VS --> HNSW["HNSW Graph Index (Cosine Distance)"]
    HNSW --> Disk["./chroma_db/ Persistence"]
```

---

## 💡 Why ChromaDB?

1. **Embedded & Serverless**: Runs directly inside the Python runtime—no external Docker containers, server management, or cloud accounts required.
2. **Local Persistence**: Automatically persists vectors, chunk text, and metadata to `./chroma_db/` across application restarts.
3. **HNSW Graph Indexing**: Implements Hierarchical Navigable Small World (HNSW) graphs for sub-millisecond Approximate Nearest Neighbor (ANN) search.
4. **Metadata Filtering**: Supports granular filtering (e.g., filtering by file type, source document, or timestamp).

---

## 📊 Vector Database Tradeoff Matrix (Engineering Decisions)

| Vector DB | Architecture | When to Use (Pros) | When to Avoid (Cons) |
| :--- | :--- | :--- | :--- |
| **ChromaDB** *(Default)* | Embedded (Local SQLite + HNSW) | Rapid development, modular prototypes, standalone CLI/APIs, datasets under 1M vectors. | Not designed for multi-node distributed clustering. |
| **FAISS (Meta)** | Low-level C++ Search Library | Unbeatable raw search speed and GPU-accelerated billion-scale static indexing. | No built-in metadata management, dynamic CRUD, or server interface. |
| **Qdrant / Milvus** | Distributed Rust / Go Engine | Enterprise production with 10M–1B+ vectors, complex payload filtering, and high QPS. | Requires dedicated Kubernetes / Docker infrastructure maintenance. |
| **Pinecone** | Fully Managed Cloud SaaS | Zero infrastructure maintenance, automatic scaling, and SLA-backed cloud hosting. | High operational cost, vendor lock-in, data leaves internal VPC. |

---

## 🔌 How to Switch Providers

Because the module implements the unified `VectorStore` interface, you can swap providers directly in `config.yaml` without changing application code:

```yaml
vectordb:
  provider: "chroma" # Options: chroma, faiss, pinecone, qdrant
  collection_name: "rag_documents"
  persist_directory: "./chroma_db"
```
