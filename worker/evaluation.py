from celery import Celery

app = Celery("turboprivate", broker="redis://localhost:6379/0")


@app.task
def run_safety_evaluation(prompt: str, response: str):
    return {"score": 0.0, "verdict": "pass"}
