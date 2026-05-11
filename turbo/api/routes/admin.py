from fastapi import APIRouter, Depends

from turbo.api.deps import get_approval_workflow, get_inference_gateway
from turbo.safety.governance import ApprovalWorkflow

router = APIRouter()


@router.get("/admin/dashboard")
async def dashboard(gateway=Depends(get_inference_gateway)):
    models = list(gateway.pools.keys())
    return {
        "requests": 0,
        "tokens": 0,
        "latency_p50": 0,
        "latency_p95": 0,
        "latency_p99": 0,
        "models": [{"name": m, "requests": 0, "latency": 0} for m in models],
        "active_models": len(models),
    }


@router.get("/admin/governance/approvals")
async def approval_queue(workflow: ApprovalWorkflow = Depends(get_approval_workflow)):
    return {"pending": workflow.pending, "total": len(workflow.pending)}


@router.post("/admin/governance/approve/{request_id}")
async def approve_request(request_id: int, workflow: ApprovalWorkflow = Depends(get_approval_workflow)):
    await workflow.approve(request_id)
    return {"status": "approved", "id": request_id}
