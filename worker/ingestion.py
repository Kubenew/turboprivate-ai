from worker.celery_app import app


@app.task
def ingest_document(file_path: str, collection: str = "default"):
    return {"status": "completed", "file": file_path}
