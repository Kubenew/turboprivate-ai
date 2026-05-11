from fastapi import APIRouter, Depends
from pydantic import BaseModel

from turbo.api.deps import get_memory_store, get_rag_pipeline
from turbo.memory.rag import RAGPipeline
from turbo.memory.store import EmbeddingStore

router = APIRouter()


class IngestRequest(BaseModel):
    text: str
    collection: str = "default"
    source: str = "api"


class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict


@router.post("/memory/ingest")
async def ingest_documents(
    req: IngestRequest,
    rag: RAGPipeline = Depends(get_rag_pipeline),
):
    ids = await rag.ingest_text(text=req.text, collection=req.collection, source=req.source)
    stats = await rag.store.stats()
    return {"status": "completed", "ids": ids, "documents_ingested": len(ids), "stats": stats}


@router.get("/memory/search")
async def search_memory(
    q: str,
    collection: str = "default",
    top_k: int = 5,
    rag: RAGPipeline = Depends(get_rag_pipeline),
):
    results = await rag.query(question=q, collection=collection, top_k=top_k)
    return {"results": results, "query": q, "collection": collection, "total": len(results)}


@router.get("/memory/stats")
async def memory_stats(store: EmbeddingStore = Depends(get_memory_store)):
    stats = await store.stats()
    collections = await store.list_collections()
    return {"collections": collections, "document_counts": stats, "total_documents": sum(stats.values())}
