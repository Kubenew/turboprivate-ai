import json
import uuid
from datetime import UTC, datetime
from pathlib import Path


class AuditTrail:
    def __init__(self, storage_path: Path = Path("./data/audit")):
        self.storage_path = storage_path
        storage_path.mkdir(parents=True, exist_ok=True)

    async def log(
        self,
        action: str,
        result: dict,
        prompt: str = "",
        response: str = "",
        tenant: str = "default",
        user_id: str | None = None,
        model: str = "",
    ):
        now = datetime.now(UTC)
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": now.isoformat(),
            "action": action,
            "tenant": tenant,
            "user_id": user_id,
            "model": model,
            "prompt_preview": prompt[:200] if prompt else "",
            "response_preview": response[:200] if response else "",
            "allowed": result.get(
                "allowed", result.get("passed", True)
            ),
            "reason": result.get("reason"),
            "result": result,
        }
        date = now.strftime("%Y-%m-%d")
        log_file = self.storage_path / f"{date}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return entry["id"]

    async def query(
        self,
        start: str = "",
        end: str = "",
        limit: int = 100,
        action: str | None = None,
        blocked_only: bool = False,
    ) -> list[dict]:
        results = []
        for f in sorted(self.storage_path.glob("*.jsonl")):
            if len(results) >= limit:
                break
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    ts = entry["timestamp"][:10]
                    if start and ts < start:
                        continue
                    if end and ts > end:
                        continue
                    if action and entry.get("action") != action:
                        continue
                    if blocked_only and entry.get("allowed", True):
                        continue
                    results.append(entry)
                    if len(results) >= limit:
                        break
        return results

    async def stats(self) -> dict:
        total = 0
        blocked = 0
        for f in self.storage_path.glob("*.jsonl"):
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    total += 1
                    entry = json.loads(line)
                    if not entry.get("allowed", True):
                        blocked += 1
        return {
            "total_entries": total,
            "blocked_entries": blocked,
            "block_rate": round(blocked / total, 4) if total else 0.0,
        }
