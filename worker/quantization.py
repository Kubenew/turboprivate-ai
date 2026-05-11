from celery import Celery

app = Celery("turboprivate", broker="redis://localhost:6379/0")


@app.task
def quantize_model(model_name: str, bits: int = 4, method: str = "awq"):
    return {"status": "completed", "model": model_name}
