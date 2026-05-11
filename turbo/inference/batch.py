import asyncio
import time
from dataclasses import dataclass, field


@dataclass
class BatchRequest:
    payload: dict
    future: asyncio.Future = field(default_factory=asyncio.Future)
    created_at: float = field(default_factory=time.time)


class DynamicBatcher:
    def __init__(self, max_batch_size: int = 8, max_wait_ms: int = 20):
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        self._queue: asyncio.Queue[BatchRequest] = asyncio.Queue()

    async def add(self, payload: dict) -> any:
        req = BatchRequest(payload=payload)
        await self._queue.put(req)
        return await req.future

    async def next_batch(self) -> list[BatchRequest]:
        deadline = time.time() + self.max_wait_ms / 1000
        batch = [await self._queue.get()]
        while time.time() < deadline and len(batch) < self.max_batch_size:
            try:
                req = await asyncio.wait_for(self._queue.get(), timeout=deadline - time.time())
                batch.append(req)
            except TimeoutError:
                break
        return batch

    def resolve_batch(self, batch: list[BatchRequest], results: list):
        for req, result in zip(batch, results):
            if not req.future.done():
                req.future.set_result(result)

    def reject_batch(self, batch: list[BatchRequest], error: Exception):
        for req in batch:
            if not req.future.done():
                req.future.set_exception(error)
