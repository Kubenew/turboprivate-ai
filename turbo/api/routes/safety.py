from fastapi import APIRouter, Depends

from turbo.api.deps import get_audit_trail, get_safety_gate
from turbo.safety.audit import AuditTrail
from turbo.safety.gate import SafetyGate

router = APIRouter()


@router.get("/safety/status")
async def safety_status(gate: SafetyGate = Depends(get_safety_gate)):
    return {
        "pre_flight": [v.name for v in gate.pre_flight_verifiers],
        "post_flight": [v.name for v in gate.post_flight_verifiers],
        "pre_flight_count": len(gate.pre_flight_verifiers),
        "post_flight_count": len(gate.post_flight_verifiers),
    }


@router.get("/safety/policies")
async def list_policies():
    return {"policies": []}


@router.get("/safety/audit")
async def audit_log(
    start: str = "",
    end: str = "",
    limit: int = 100,
    action: str | None = None,
    blocked_only: bool = False,
    audit: AuditTrail = Depends(get_audit_trail),
):
    entries = await audit.query(start=start, end=end, limit=limit, action=action, blocked_only=blocked_only)
    stats = await audit.stats()
    return {"entries": entries, "stats": stats}


@router.get("/safety/check")
async def safety_check(
    prompt: str = "",
    response: str = "",
    gate: SafetyGate = Depends(get_safety_gate),
    audit: AuditTrail = Depends(get_audit_trail),
):
    pre = await gate.check_pre_flight(prompt) if prompt else {"allowed": True}
    post = await gate.check_post_flight(prompt, response) if response else {"allowed": True}
    await audit.log("safety_check", {"pre_flight": pre, "post_flight": post}, prompt=prompt, response=response)
    return {"pre_flight": pre, "post_flight": post}
