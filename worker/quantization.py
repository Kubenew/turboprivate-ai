from worker.celery_app import app


@app.task
def quantize_model(model_name: str, bits: int = 4, method: str = "awq"):
    return {"status": "completed", "model": model_name}
