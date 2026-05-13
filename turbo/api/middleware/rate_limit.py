import time
from collections import defaultdict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter keyed by client IP."""

    def __init__(
        self,
        app,
        max_requests: int = 100,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _prune(self, key: str, now: float):
        cutoff = now - self.window_seconds
        self._hits[key] = [
            t for t in self._hits[key] if t > cutoff
        ]

    async def dispatch(self, request: Request, call_next):
        key = self._client_key(request)
        now = time.time()
        self._prune(key, now)

        if len(self._hits[key]) >= self.max_requests:
            retry_after = int(
                self.window_seconds
                - (now - self._hits[key][0])
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": max(1, retry_after),
                },
                headers={"Retry-After": str(max(1, retry_after))},
            )

        self._hits[key].append(now)
        return await call_next(request)
