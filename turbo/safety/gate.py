from turbo.safety.verifiers import BaseVerifier
from turbo.safety.verifiers.anti_hacking import CyberAntiHackingVerifier
from turbo.safety.verifiers.hallucination import HallucinationScorer
from turbo.safety.verifiers.overengineering import OverEngineeringDetector
from turbo.safety.verifiers.patch import PatchVerifier
from turbo.safety.verifiers.pii_detector import PIIDetector
from turbo.safety.verifiers.prompt_injection import PromptInjectionDetector
from turbo.safety.verifiers.vulnerability import VulnerabilityScannerVerifier


class SafetyGate:
    def __init__(self):
        self.pre_flight_verifiers: list[BaseVerifier] = [
            PromptInjectionDetector(),
            PIIDetector(redact=True),
            CyberAntiHackingVerifier(),
        ]
        self.post_flight_verifiers: list[BaseVerifier] = [
            CyberAntiHackingVerifier(),
            OverEngineeringDetector(),
            VulnerabilityScannerVerifier(),
            PatchVerifier(),
            HallucinationScorer(),
            PIIDetector(redact=True),
        ]

    def add_pre_flight(self, verifier: BaseVerifier):
        self.pre_flight_verifiers.append(verifier)

    def add_post_flight(self, verifier: BaseVerifier):
        self.post_flight_verifiers.append(verifier)

    async def check_pre_flight(self, prompt: str, tenant: str = "default") -> dict:
        results = []
        blocked = False
        block_reason = None
        for v in self.pre_flight_verifiers:
            result = await v.verify(prompt=prompt)
            results.append(result)
            if result.get("blocked"):
                blocked = True
                block_reason = result.get("reason", f"blocked_by_{v.name}")
        return {
            "allowed": not blocked,
            "blocked": blocked,
            "reason": block_reason,
            "verifier_results": results,
        }

    async def check_post_flight(self, prompt: str, response: str, tenant: str = "default") -> dict:
        results = []
        blocked = False
        block_reason = None
        for v in self.post_flight_verifiers:
            result = await v.verify(prompt=prompt, response=response)
            results.append(result)
            if result.get("blocked"):
                blocked = True
                block_reason = result.get("reason", f"blocked_by_{v.name}")
        return {
            "allowed": not blocked,
            "blocked": blocked,
            "reason": block_reason,
            "verifier_results": results,
        }
