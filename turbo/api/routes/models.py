from fastapi import APIRouter, Depends
from pydantic import BaseModel

from turbo.api.deps import get_inference_gateway
from turbo.inference.gateway import InferenceGateway
from turbo.inference.quantize import Quantizer

router = APIRouter()


class PullRequest(BaseModel):
    name: str


class QuantizeRequest(BaseModel):
    name: str
    bits: int = 4
    method: str = "awq"


@router.get("/models")
async def list_models(
    gateway: InferenceGateway = Depends(get_inference_gateway),
):
    models = list(gateway.pools.keys())
    return {"models": models, "total": len(models)}


@router.post("/models/pull")
async def pull_model(req: PullRequest):
    return {
        "status": "started",
        "model": req.name,
        "message": f"Pulling model {req.name} in background",
    }


@router.post("/models/quantize")
async def quantize_model(req: QuantizeRequest):
    quantizer = Quantizer(method=req.method, bits=req.bits)
    output_path = f"./models/{req.name}-int{req.bits}"
    await quantizer.quantize(req.name, output_path)
    return {
        "status": "completed",
        "model": req.name,
        "bits": req.bits,
        "method": req.method,
        "output_path": output_path,
    }
