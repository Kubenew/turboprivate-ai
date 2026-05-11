class CompositeRewardScorer:
    def __init__(self):
        self.weights: dict[str, float] = {
            "anti_hacking": 0.25,
            "vulnerability_scanner": 0.20,
            "patch": 0.15,
            "overengineering": 0.10,
            "hallucination_scorer": 0.10,
            "pii_detector": 0.10,
            "prompt_injection": 0.10,
        }
        self.safety_gate_threshold = 0.40

    def set_weight(self, name: str, weight: float):
        self.weights[name] = weight

    def score(self, verifier_results: list[dict]) -> dict:
        total = 0.0
        weight_sum = 0.0
        safety_violation = False
        details = {}

        for result in verifier_results:
            name = result.get("verifier", "unknown")
            w = self.weights.get(name, 1.0)
            reward = result.get("reward", 0.5)
            total += reward * w
            weight_sum += w
            details[name] = {
                "reward": reward,
                "weight": w,
                "blocked": result.get("blocked", False),
            }
            if result.get("blocked"):
                safety_violation = True

        composite = total / weight_sum if weight_sum else 0.0
        if safety_violation:
            composite = min(composite, self.safety_gate_threshold)

        return {
            "composite_reward": round(composite, 4),
            "passed": composite >= self.safety_gate_threshold,
            "safety_violation": safety_violation,
            "details": details,
        }
