from turbo.safety.verifiers import BaseVerifier


class PatchVerifier(BaseVerifier):
    def __init__(self, complexity_threshold: int = 4000):
        super().__init__("patch")
        self.complexity_threshold = complexity_threshold

    async def verify(self, prompt: str = "", response: str = "", **kwargs) -> dict:
        target = response or prompt
        has_patch = "```diff" in target or "patch" in target.lower()
        overly_complex = len(target) > self.complexity_threshold
        reward = 0.8 if has_patch else 0.3
        if overly_complex:
            reward -= 0.3
        reward = max(0.0, min(1.0, reward))
        return {
            "reward": round(reward, 4),
            "score": round(1.0 - reward, 4),
            "blocked": overly_complex and not has_patch,
            "reason": "overly_complex_patch" if overly_complex else None,
            "verifier": self.name,
            "details": {
                "has_patch": has_patch,
                "overly_complex": overly_complex,
                "length": len(target),
            },
        }
