from worker.celery_app import app


@app.task
def run_safety_evaluation(prompt: str, response: str):
    return {"score": 0.0, "verdict": "pass"}
