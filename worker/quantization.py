import logging
from pathlib import Path

from worker.celery_app import app

logger = logging.getLogger("turboprivate.worker.quantization")


@app.task(bind=True, max_retries=2)
def quantize_model(
    self,
    model_name: str,
    bits: int = 4,
    method: str = "awq",
    output_dir: str | None = None,
):
    """Quantize a model using TurboQuant engine."""
    try:
        import asyncio

        from turbo.inference.quantize import Quantizer

        quantizer = Quantizer(method=method, bits=bits)
        out = Path(output_dir or f"./models/{model_name}-int{bits}")

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(
                quantizer.quantize(model_name, out)
            )
        finally:
            loop.close()

        return {
            "status": "completed",
            "model": model_name,
            "bits": bits,
            "method": method,
            "output_path": str(out),
        }
    except Exception as exc:
        logger.error("Quantization failed: %s", exc)
        raise self.retry(exc=exc, countdown=10)
