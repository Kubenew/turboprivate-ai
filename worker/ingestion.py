import logging
from pathlib import Path

from worker.celery_app import app

logger = logging.getLogger("turboprivate.worker.ingestion")


@app.task(bind=True, max_retries=3)
def ingest_document(
    self,
    file_path: str,
    collection: str = "default",
    chunk_size: int = 512,
    chunk_overlap: int = 64,
):
    """Ingest a document into the RAG memory store."""
    try:
        import asyncio

        from turbo.memory.rag import RAGPipeline
        from turbo.memory.store import EmbeddingStore

        store = EmbeddingStore()
        pipeline = RAGPipeline(
            store=store,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        path = Path(file_path)
        if not path.exists():
            return {
                "status": "error",
                "file": file_path,
                "error": f"File not found: {file_path}",
            }

        loop = asyncio.new_event_loop()
        try:
            ids = loop.run_until_complete(
                pipeline.ingest_file(path, collection=collection)
            )
        finally:
            loop.close()

        return {
            "status": "completed",
            "file": file_path,
            "collection": collection,
            "chunks_ingested": len(ids),
            "document_ids": ids,
        }
    except Exception as exc:
        logger.error("Document ingestion failed: %s", exc)
        raise self.retry(exc=exc, countdown=5)
