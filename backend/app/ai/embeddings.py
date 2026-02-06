from app.config import get_settings

settings = get_settings()


class EmbeddingService:
    def __init__(self):
        self._collection = None

    def _get_collection(self):
        if self._collection is None:
            import chromadb

            client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
            self._collection = client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    async def index_document(self, document_id: str, text: str, metadata: dict | None = None):
        collection = self._get_collection()
        chunks = self._chunk_text(text, chunk_size=1000, overlap=200)

        ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"document_id": document_id, "chunk_index": i, **(metadata or {})} for i in range(len(chunks))]

        collection.upsert(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
        )

    async def search(self, query: str, n_results: int = 5, where: dict | None = None) -> list[dict]:
        collection = self._get_collection()
        kwargs = {"query_texts": [query], "n_results": n_results}
        if where:
            kwargs["where"] = where

        results = collection.query(**kwargs)

        output = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                output.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                })
        return output

    async def delete_document(self, document_id: str):
        collection = self._get_collection()
        collection.delete(where={"document_id": document_id})

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start += chunk_size - overlap
        return chunks


embedding_service = EmbeddingService()
