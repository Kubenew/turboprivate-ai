import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from turbo.api.deps import get_inference_engine, get_inference_gateway
from turbo.inference.engine import InferenceEngine
from turbo.inference.gateway import InferenceGateway

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    stream: bool = False
    max_tokens: int = 1024
    temperature: float = 0.7


class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int = 1024
    temperature: float = 0.7


class EmbeddingRequest(BaseModel):
    model: str
    input: str


@router.post("/chat/completions")
async def chat_completions(
    req: ChatRequest,
    engine: InferenceEngine = Depends(get_inference_engine),
    gateway: InferenceGateway = Depends(get_inference_gateway),
):
    messages = [m.model_dump() for m in req.messages]
    backend = gateway.choose_backend(req.model)
    if backend:
        result = await gateway.forward(backend, req.model, {"messages": messages, "max_tokens": req.max_tokens, "temperature": req.temperature})
        return result
    result = await engine.chat(messages=messages, max_tokens=req.max_tokens, temperature=req.temperature, stream=req.stream)
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "model": req.model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": result.get("text", "")}, "finish_reason": "stop"}],
    }


@router.post("/completions")
async def completions(
    req: CompletionRequest,
    engine: InferenceEngine = Depends(get_inference_engine),
    gateway: InferenceGateway = Depends(get_inference_gateway),
):
    backend = gateway.choose_backend(req.model)
    if backend:
        result = await gateway.forward(backend, req.model, {"prompt": req.prompt, "max_tokens": req.max_tokens, "temperature": req.temperature})
        return result
    result = await engine.generate(prompt=req.prompt, max_tokens=req.max_tokens, temperature=req.temperature)
    return {
        "id": f"cmpl-{uuid.uuid4().hex[:12]}",
        "object": "text_completion",
        "model": req.model,
        "choices": [{"index": 0, "text": result.get("text", ""), "finish_reason": "stop"}],
    }


@router.post("/embeddings")
async def embeddings(
    req: EmbeddingRequest,
    engine: InferenceEngine = Depends(get_inference_engine),
):
    vec = await engine.embed(req.input)
    return {
        "object": "list",
        "data": [{"object": "embedding", "index": 0, "embedding": vec}],
        "model": req.model,
    }
