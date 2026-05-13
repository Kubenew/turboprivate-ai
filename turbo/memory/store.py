import uuid
from pathlib import Path

import numpy as np


class EmbeddingStore:
    def __init__(
        self,
        storage_path: Path = Path("./data/memory"),
        dim: int = 384,
    ):
        self.storage_path = storage_path
        self.dim = dim
        storage_path.mkdir(parents=True, exist_ok=True)
        self.collections: dict[str, dict] = {}

    async def create_collection(self, name: str):
        collection_dir = self.storage_path / name
        collection_dir.mkdir(parents=True, exist_ok=True)
        self.collections[name] = {
            "dir": collection_dir,
            "documents": [],
        }

    async def add(
        self,
        collection: str,
        text: str,
        metadata: dict | None = None,
        embedding: list[float] | None = None,
    ) -> str:
        if collection not in self.collections:
            await self.create_collection(collection)
        doc_id = str(uuid.uuid4())
        entry = {
            "id": doc_id,
            "text": text,
            "metadata": metadata or {},
            "embedding": embedding or [],
        }
        self.collections[collection]["documents"].append(entry)
        return doc_id

    async def add_batch(
        self,
        collection: str,
        texts: list[str],
        embeddings: list[list[float]] | None = None,
        metadata: list[dict] | None = None,
    ) -> list[str]:
        ids = []
        for i, text in enumerate(texts):
            emb = embeddings[i] if embeddings else None
            meta = metadata[i] if metadata else None
            doc_id = await self.add(collection, text, meta, emb)
            ids.append(doc_id)
        return ids

    async def search(
        self,
        collection: str,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict]:
        docs = self.collections.get(collection, {}).get(
            "documents", []
        )
        if not docs:
            return []
        query_vec = np.array(query_embedding, dtype=np.float32)
        scores = []
        for doc in docs:
            if doc["embedding"]:
                doc_vec = np.array(
                    doc["embedding"], dtype=np.float32
                )
                norm_q = np.linalg.norm(query_vec)
                norm_d = np.linalg.norm(doc_vec)
                denom = norm_q * norm_d + 1e-10
                sim = float(np.dot(query_vec, doc_vec) / denom)
                scores.append((sim, doc))
            else:
                scores.append((0.0, doc))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "id": doc["id"],
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": round(float(score), 4),
            }
            for score, doc in scores[:top_k]
        ]

    async def get(
        self, collection: str, doc_id: str
    ) -> dict | None:
        for doc in self.collections.get(collection, {}).get(
            "documents", []
        ):
            if doc["id"] == doc_id:
                return doc
        return None

    async def delete(self, collection: str, doc_id: str) -> bool:
        docs = self.collections.get(collection, {}).get(
            "documents", []
        )
        for i, doc in enumerate(docs):
            if doc["id"] == doc_id:
                docs.pop(i)
                return True
        return False

    async def stats(self) -> dict:
        return {
            name: len(data["documents"])
            for name, data in self.collections.items()
        }

    async def list_collections(self) -> list[str]:
        return list(self.collections.keys())
