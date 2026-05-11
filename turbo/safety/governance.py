from pathlib import Path

import yaml


class PolicyEngine:
    def __init__(self, policies_path: Path = Path("./policies")):
        self.policies_path = policies_path
        self.policies: dict[str, dict] = {}

    def load_policies(self):
        for f in self.policies_path.glob("*.yaml"):
            with open(f) as fh:
                data = yaml.safe_load(fh)
                self.policies.update(data or {})

    async def evaluate(self, action: str, context: dict) -> dict:
        rule = self.policies.get(action, {})
        allowed = rule.get("allow", True)
        requires_approval = rule.get("requires_approval", False)
        return {
            "allowed": allowed,
            "requires_approval": requires_approval,
            "reason": rule.get("reason", ""),
        }


class ApprovalWorkflow:
    def __init__(self):
        self.pending: list[dict] = []

    async def submit(self, request: dict):
        self.pending.append(request)
        return {"status": "pending", "id": len(self.pending)}

    async def approve(self, request_id: int):
        if 0 < request_id <= len(self.pending):
            self.pending[request_id - 1]["status"] = "approved"
