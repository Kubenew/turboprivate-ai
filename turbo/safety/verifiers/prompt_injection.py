import re

from turbo.safety.verifiers import BaseVerifier

INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore.*(previous|above|all).*instructions"),
    re.compile(r"(?i)forget|disregard|ignore.*(prompt|context|rules)"),
    re.compile(r"(?i)you are (now|no longer|not ).*(assistant|AI|chatbot|helpful)"),
    re.compile(r"(?i)act as|pretend to be|role.?play as"),
    re.compile(r"(?i)system.*(prompt|message|instruction).*(override|bypass|change)"),
    re.compile(r"(?i)output.*(raw|unfiltered|unbounded|unrestricted)"),
    re.compile(r"(?i)dangerous.*(capability|action|command)"),
    re.compile(r"(?i)(jailbreak|prompt.?inject|leak|exfiltrat)"),
    re.compile(r"(?i)(DAN|do anything now|no filter|no limits|unrestricted mode)"),
    re.compile(r"(?i)repeat.*(above|previous).*(word|text|sentence|message)"),
    re.compile(r"(?i)output.*(password|secret|key|token|credential)"),
    re.compile(r"(?i)how to (hack|crack|exploit|bypass)"),
    re.compile(r"(?i)(sudo|su |chmod 777|chown|passwd).*(command|run|execute)"),
    re.compile(r"(?i)ignore.*(safety|guardrail|restriction|policy|ethical)"),
    re.compile(r"(?i)what.*(secret|hidden|internal|confidential).*(prompt|instruction)"),
]


class PromptInjectionDetector(BaseVerifier):
    def __init__(self, threshold: float = 0.3):
        super().__init__("prompt_injection")
        self.threshold = threshold

    async def verify(self, prompt: str = "", response: str = "", **kwargs) -> dict:
        target = prompt
        hits = []
        for pattern in INJECTION_PATTERNS:
            if pattern.search(target):
                hits.append(pattern.pattern)
        injection_score = min(1.0, len(hits) * 0.2)
        return {
            "reward": round(1.0 - injection_score, 4),
            "score": round(injection_score, 4),
            "blocked": injection_score > self.threshold,
            "reason": "prompt_injection_detected" if injection_score > self.threshold else None,
            "verifier": self.name,
            "details": {
                "injection_score": round(injection_score, 4),
                "pattern_matches": len(hits),
                "threshold": self.threshold,
            },
        }
