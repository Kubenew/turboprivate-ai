import logging

from worker.celery_app import app

logger = logging.getLogger("turboprivate.worker.evaluation")


@app.task(bind=True, max_retries=3)
def run_safety_evaluation(self, prompt: str, response: str):
    """Run post-flight safety evaluation on a prompt/response pair."""
    try:
        import asyncio

        from turbo.safety.gate import SafetyGate
        from turbo.safety.reward import CompositeRewardScorer

        gate = SafetyGate()
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                gate.check_post_flight(prompt, response)
            )
        finally:
            loop.close()

        scorer = CompositeRewardScorer()
        verifier_results = result.get("verifier_results", [])
        reward = scorer.score(verifier_results)

        return {
            "status": "completed",
            "allowed": result.get("allowed", True),
            "blocked": result.get("blocked", False),
            "reason": result.get("reason"),
            "composite_reward": reward.get("composite_reward", 0),
            "safety_violation": reward.get("safety_violation", False),
            "verifier_count": len(verifier_results),
        }
    except Exception as exc:
        logger.error("Safety evaluation failed: %s", exc)
        raise self.retry(exc=exc, countdown=5)
