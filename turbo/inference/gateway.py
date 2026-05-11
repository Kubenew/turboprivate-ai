import asyncio
import logging
import time
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger("turboprivate.gateway")


@dataclass
class Backend:
    url: str
    healthy: bool = True
    last_latency_ms: float = 9999.0
    active_requests: int = 0
    last_seen: float = field(default_factory=time.time)

    def score(self) -> float:
        return self.last_latency_ms + self.active_requests * 5.0


class InferenceGateway:
    def __init__(self):
        self.pools: dict[str, list[Backend]] = {}
        self._client: httpx.AsyncClient | None = None
        self._health_task: asyncio.Task | None = None

    def register_model(self, model: str, backend_urls: list[str]):
        self.pools[model] = [Backend(url=u) for u in backend_urls]

    def choose_backend(self, model: str) -> Backend | None:
        pool = self.pools.get(model)
        if not pool:
            return None
        healthy = [b for b in pool if b.healthy]
        if not healthy:
            return None
        return min(healthy, key=lambda b: b.score())

    async def forward(self, backend: Backend, model: str, payload: dict) -> dict:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        backend.active_requests += 1
        t0 = time.time()
        try:
            resp = await self._client.post(f"{backend.url}/infer/{model}", json=payload)
            resp.raise_for_status()
            backend.last_latency_ms = (time.time() - t0) * 1000
            return resp.json()
        except Exception as e:
            logger.warning("Forward request to %s failed: %s", backend.url, e)
            backend.last_latency_ms = (time.time() - t0) * 1000
            backend.healthy = False
            raise
        finally:
            backend.active_requests -= 1
            backend.last_seen = time.time()

    async def health_check(self, interval: int = 5, timeout: int = 2, path: str = "/health"):
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=timeout)
        while True:
            try:
                all_backends = [b for pool in self.pools.values() for b in pool]
                results = await asyncio.gather(
                    *[self._ping(b, path, timeout) for b in all_backends],
                    return_exceptions=True,
                )
                for b, ok in zip(all_backends, results):
                    b.healthy = bool(ok) and ok is not True
                healthy = sum(1 for b in all_backends if b.healthy)
                logger.info(f"Health check: {healthy}/{len(all_backends)} backends healthy")
            except Exception as e:
                logger.error("Health check error: %s", e)
            await asyncio.sleep(interval)

    async def _ping(self, backend: Backend, path: str, timeout: int) -> bool:
        try:
            resp = await self._client.get(f"{backend.url}{path}")
            return resp.is_success
        except Exception as e:
            logger.debug("Backend %s ping failed: %s", backend.url, e)
            return False

    def start_health_checks(self, interval: int = 5, timeout: int = 2, path: str = "/health"):
        self._health_task = asyncio.create_task(self.health_check(interval, timeout, path))

    async def stop_health_checks(self):
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass

    async def close(self):
        await self.stop_health_checks()
        if self._client:
            await self._client.aclose()
            self._client = None
