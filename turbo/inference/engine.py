
from turbo.config import InferenceConfig


def _import_torch():
    try:
        import torch
        return torch
    except ImportError:
        return None


def detect_hardware():
    torch = _import_torch()
    if torch is None:
        return "cpu", "cpu"
    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        major = props.major
        name = props.name.lower()
        if major >= 9:
            return "cloud", "h100"
        if major >= 8:
            if "a100" in name:
                return "cloud", "a100"
            return "consumer", name.replace(" ", "").lower()
        if major >= 7:
            return "consumer", name.replace(" ", "").lower()
        return "cloud", "unknown_gpu"
    if torch.backends.mps.is_available():
        return "consumer", "mps"
    return "cpu", "cpu"


class InferenceEngine:
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.backend = None
        self._loaded = False

    async def load(self):
        hw_type, hw_name = detect_hardware()
        backend_type = self.config.backend
        if backend_type == "auto":
            if hw_type == "cpu":
                backend_type = "llamacpp"
            else:
                backend_type = "vllm"

        if backend_type == "vllm":
            from turbo.inference.backends.vllm_backend import VLLMBackend
            self.backend = VLLMBackend(self.config, hw_name)
        elif backend_type == "llamacpp":
            from turbo.inference.backends.llamacpp_backend import LlamaCppBackend
            self.backend = LlamaCppBackend(self.config)

        await self.backend.load()
        self._loaded = True

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stream: bool = False,
    ) -> dict:
        if not self._loaded:
            await self.load()
        return await self.backend.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=stream,
        )

    async def chat(
        self,
        messages: list[dict],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> dict:
        if not self._loaded:
            await self.load()
        return await self.backend.chat(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
        )

    async def embed(self, text: str) -> list[float]:
        if not self._loaded:
            await self.load()
        return await self.backend.embed(text)

    async def unload(self):
        if self.backend:
            await self.backend.unload()
        self._loaded = False
        self.model = None
        self.tokenizer = None
        torch = _import_torch()
        if torch and torch.cuda.is_available():
            torch.cuda.empty_cache()
