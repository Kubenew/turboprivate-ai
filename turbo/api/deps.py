import logging

from fastapi import Request

from turbo.config import config
from turbo.inference.engine import InferenceEngine
from turbo.inference.gateway import InferenceGateway
from turbo.memory.rag import RAGPipeline
from turbo.memory.store import EmbeddingStore
from turbo.safety.audit import AuditTrail
from turbo.safety.gate import SafetyGate
from turbo.safety.governance import ApprovalWorkflow, PolicyEngine


def get_inference_engine(request: Request) -> InferenceEngine:
    return request.app.state.inference_engine


def get_inference_gateway(request: Request) -> InferenceGateway:
    return request.app.state.inference_gateway


def get_safety_gate(request: Request) -> SafetyGate:
    return request.app.state.safety_gate


def get_audit_trail(request: Request) -> AuditTrail:
    return request.app.state.audit_trail


def get_policy_engine(request: Request) -> PolicyEngine:
    return request.app.state.policy_engine


def get_approval_workflow(request: Request) -> ApprovalWorkflow:
    return request.app.state.approval_workflow


def get_rag_pipeline(request: Request) -> RAGPipeline:
    return request.app.state.rag_pipeline


def get_memory_store(request: Request) -> EmbeddingStore:
    return request.app.state.memory_store


async def init_app_state(app):
    app.state.inference_engine = InferenceEngine(config.inference)
    app.state.inference_gateway = InferenceGateway()
    app.state.safety_gate = SafetyGate()
    app.state.audit_trail = AuditTrail()
    app.state.policy_engine = PolicyEngine()
    app.state.approval_workflow = ApprovalWorkflow()
    app.state.memory_store = EmbeddingStore()
    app.state.rag_pipeline = RAGPipeline(store=app.state.memory_store)


async def shutdown_app_state(app):
    await app.state.inference_engine.unload()
    await app.state.inference_gateway.close()
    if hasattr(app.state, "audit_trail") and hasattr(app.state.audit_trail, "storage_path"):
        logger = logging.getLogger("turboprivate.shutdown")
        logger.info("Audit trail flushed")
