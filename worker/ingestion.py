from celery import Celery

app = Celery("turboprivate", broker="redis://localhost:6379/0")


@app.task
def ingest_document(file_path: str, collection: str = "default"):
    return {"status": "completed", "file": file_path}
