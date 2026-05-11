from pathlib import Path

from turbo.memory.store import EmbeddingStore


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size")

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


class RAGPipeline:
    def __init__(
        self,
        store: EmbeddingStore,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        embedding_model: str = "BAAI/bge-small-en-v1.5",
    ):
        self.store = store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model
        self._embedder = None

    def _get_embedder(self):
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer(self.embedding_model)
            except ImportError:
                pass
        return self._embedder

    async def ingest_text(
        self,
        text: str,
        collection: str = "default",
        source: str = "text",
        metadata: dict | None = None,
    ) -> list[str]:
        chunks = chunk_text(text, self.chunk_size, self.chunk_overlap)
        embedder = self._get_embedder()
        embeddings = None
        if embedder:
            embeddings = embedder.encode(chunks).tolist()
        meta_list = []
        for i, chunk in enumerate(chunks):
            m = {"source": source, "chunk_index": i, "total_chunks": len(chunks), **(metadata or {})}
            meta_list.append(m)
        return await self.store.add_batch(collection, chunks, embeddings, meta_list)

    async def ingest_file(
        self,
        file_path: Path,
        collection: str = "default",
        metadata: dict | None = None,
    ) -> list[str]:
        from turbo.memory.parser import DocumentParser
        parser = DocumentParser()
        text = await parser.parse(file_path)
        file_meta = {"filename": file_path.name, "path": str(file_path), **(metadata or {})}
        return await self.ingest_text(text, collection, source=str(file_path), metadata=file_meta)

    async def query(
        self,
        question: str,
        collection: str = "default",
        top_k: int = 5,
    ) -> list[dict]:
        embedder = self._get_embedder()
        if embedder:
            query_vec = embedder.encode([question])[0].tolist()
        else:
            query_vec = [0.0] * 384
        return await self.store.search(collection, query_vec, top_k)

    async def augment(
        self,
        question: str,
        collection: str = "default",
        top_k: int = 3,
        system_prompt: str | None = None,
    ) -> str:
        docs = await self.query(question, collection, top_k)
        context = "\n\n".join(f"---\n{d['text']}" for d in docs)
        if system_prompt:
            return f"{system_prompt}\n\nContext:\n{context}\n\nQuestion: {question}"
        return f"Context:\n{context}\n\nQuestion: {question}"
