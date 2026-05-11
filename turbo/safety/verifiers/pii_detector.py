import re

from turbo.safety.verifiers import BaseVerifier

PII_PATTERNS = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "phone": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "api_key": re.compile(r"(?i)\b(sk-[a-zA-Z0-9]{20,}|api[_-]?key['\"]?\s*[:=]\s*['\"][a-zA-Z0-9_\-]{16,})"),
}


class PIIDetector(BaseVerifier):
    def __init__(self, redact: bool = True, auto_block: bool = True):
        super().__init__("pii_detector")
        self.redact = redact
        self.auto_block = auto_block

    async def verify(self, prompt: str = "", response: str = "", **kwargs) -> dict:
        target = response or prompt
        findings = {}
        for name, pattern in PII_PATTERNS.items():
            matches = pattern.findall(target)
            if matches:
                findings[name] = len(matches)
        total_pii = sum(findings.values())
        return {
            "reward": round(max(0.0, 1.0 - total_pii * 0.2), 4),
            "score": round(min(1.0, total_pii * 0.2), 4),
            "blocked": self.auto_block and total_pii > 0,
            "reason": f"pii_detected: {findings}" if total_pii > 0 else None,
            "verifier": self.name,
            "details": {
                "pii_found": findings,
                "total_pii_entities": total_pii,
                "redacted": self.redact,
            },
        }
