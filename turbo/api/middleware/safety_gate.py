import json
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("turboprivate.middleware.safety")

GUARDED_PATHS = ("/v1/chat/completions", "/v1/completions")


class SafetyGateMiddleware(BaseHTTPMiddleware):
    """Intercept inference requests and run pre-flight safety checks."""

    async def dispatch(self, request: Request, call_next):
        if request.method != "POST":
            return await call_next(request)

        if not any(request.url.path.startswith(p) for p in GUARDED_PATHS):
            return await call_next(request)

        # Read and parse request body
        body_bytes = await request.body()
        try:
            payload = json.loads(body_bytes)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return await call_next(request)

        # Extract prompt text for safety check
        prompt = ""
        if "messages" in payload:
            msgs = payload["messages"]
            if msgs:
                prompt = msgs[-1].get("content", "")
        elif "prompt" in payload:
            prompt = payload.get("prompt", "")

        if not prompt:
            return await call_next(request)

        # Run pre-flight safety gate
        gate = getattr(request.app.state, "safety_gate", None)
        if gate is None:
            return await call_next(request)

        result = await gate.check_pre_flight(prompt)

        if result.get("blocked"):
            logger.warning(
                "Pre-flight safety block: %s", result.get("reason")
            )
            # Log to audit trail if available
            audit = getattr(request.app.state, "audit_trail", None)
            if audit:
                await audit.log(
                    "pre_flight_block",
                    result,
                    prompt=prompt,
                )
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Request blocked by safety gate",
                    "reason": result.get("reason"),
                    "verifier_results": result.get(
                        "verifier_results"
                    ),
                },
            )

        return await call_next(request)
