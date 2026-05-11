import re

from turbo.safety.verifiers import BaseVerifier

BUZZWORDS = [
    "highly sophisticated",
    "enterprise-grade",
    "multi-layered",
    "cutting-edge",
    "next-generation",
    "state-of-the-art",
    "industry-leading",
    "best-in-class",
    "mission-critical",
]


class OverEngineeringDetector(BaseVerifier):
    def __init__(self, word_limit: int = 650):
        super().__init__("overengineering")
        self.word_limit = word_limit

    def score(self, response: str) -> float:
        s = 1.0
        word_count = len(response.split())
        if word_count > self.word_limit:
            s -= 0.2
        for bw in BUZZWORDS:
            if re.search(rf"(?i){re.escape(bw)}", response):
                s -= 0.25
                break
        return max(0.0, min(1.0, s))

    async def verify(self, prompt: str = "", response: str = "", **kwargs) -> dict:
        target = response or prompt
        calib_score = self.score(target)
        return {
            "reward": round(calib_score, 4),
            "score": round(1.0 - calib_score, 4),
            "blocked": calib_score < 0.3,
            "reason": "overly_complex_response" if calib_score < 0.3 else None,
            "verifier": self.name,
            "details": {
                "calibration_score": round(calib_score, 4),
                "word_count": len(target.split()),
            },
        }
