"""Vector database operations wrapper for document indexing and querying."""

from pathlib import Path
from typing import Any
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Manages vector database storage, indexing, and nearest-neighbor search."""

    def __init__(
        self,
        provider: str = "chroma",
        collection_name: str = "rag_documents",
        persist_directory: str = "./chroma_db",
    ) -> None:
        """Initialize VectorStore client and collection.

        Args:
            provider: Vector DB engine ('chroma', 'faiss', 'pinecone').
            collection_name: Name of target collection/index.
            persist_directory: Local storage path for persistence.
        """
        self.provider = provider
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._client = None
        self._collection = None
        self._documents: list[dict[str, Any]] = []

    def _init_db(self) -> None:
        """Initialize connection to the vector database."""
        if self._client is not None:
            return

        if self.provider == "chroma":
            try:
                import chromadb

                Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
                self._client = chromadb.PersistentClient(path=self.persist_directory)
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name
                )
                logger.info(f"Connected to ChromaDB collection: {self.collection_name}")
            except ImportError:
                logger.warning("chromadb not installed. Operating in in-memory list mode.")
                self._client = "in_memory"
        else:
            self._client = "in_memory"

    def add_documents(
        self,
        chunks: list[dict[str, Any]],
        embeddings: list[list[float]],
    ) -> None:
        """Add text chunks and corresponding embedding vectors to vector store.

        Args:
            chunks: List of chunk dictionaries containing text and metadata.
            embeddings: List of embedding vectors for each chunk.
        """
        if not chunks:
            return

        self._init_db()

        if self._collection is not None:
            ids = [chunk["chunk_id"] for chunk in chunks]
            documents = [chunk["chunk_text"] for chunk in chunks]
            metadatas = [chunk.get("metadata", {}) for chunk in chunks]

            if hasattr(self._collection, "upsert"):
                self._collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas,
                )
            else:
                self._collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas,
                )
            logger.info(f"Indexed {len(chunks)} chunks into ChromaDB collection.")
        else:
            for chunk, emb in zip(chunks, embeddings):
                self._documents.append({"chunk": chunk, "embedding": emb})
            logger.info(f"Appended {len(chunks)} chunks to in-memory store.")

    def clear(self) -> int:
        """Clear all stored documents and vectors.

        Returns:
            Number of documents that were deleted.
        """
        self._init_db()
        count = 0
        if self._collection is not None and self._client != "in_memory":
            count = self._collection.count()
            self._client.delete_collection(name=self.collection_name)
            self._collection = self._client.get_or_create_collection(name=self.collection_name)
            logger.info("Cleared %d chunks from ChromaDB collection '%s'.", count, self.collection_name)
        elif isinstance(self._documents, list):
            count = len(self._documents)
            self._documents.clear()
            logger.info("Cleared %d chunks from in-memory store.", count)
        return count


    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Query vector store for the most similar document chunks.

        Args:
            query_embedding: Vector representation of the search query.
            top_k: Number of most similar items to return.

        Returns:
            List of matching document chunks with similarity scores.
        """
        self._init_db()

        if self._collection is not None:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self._collection.count() or 1),
            )
            hits = []
            if results and results.get("documents"):
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
                ids = results["ids"][0] if results.get("ids") else [""] * len(docs)
                distances = (
                    results["distances"][0] if results.get("distances") else [0.0] * len(docs)
                )

                for doc_id, text, meta, dist in zip(ids, docs, metas, distances):
                    hits.append(
                        {
                            "chunk_id": doc_id,
                            "chunk_text": text,
                            "metadata": meta,
                            "distance": dist,
                            "score": 1.0 - dist if isinstance(dist, (int, float)) else 1.0,
                        }
                    )
            return hits

        # In-memory fallback (returns indexed documents up to top_k)
        return [
            {
                "chunk_id": item["chunk"]["chunk_id"],
                "chunk_text": item["chunk"]["chunk_text"],
                "metadata": item["chunk"].get("metadata", {}),
                "score": 1.0,
            }
            for item in self._documents[:top_k]
        ]
