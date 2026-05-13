
from turbo.config import InferenceConfig


class VLLMBackend:
    def __init__(self, config: InferenceConfig, device_name: str = ""):
        self.config = config
        self.device_name = device_name
        self.llm = None
        self.sampling_params = None

    async def load(self):
        try:
            from vllm import LLM, SamplingParams
        except ImportError:
            raise ImportError(
                "vLLM not installed. Run: pip install turboprivate-ai[inference]"
            )

        model_path = (
            str(self.config.model_path)
            if self.config.model_path
            else self.config.model_name
        )
        dtype = (
            self.config.dtype if self.config.dtype != "auto" else "auto"
        )

        self.llm = LLM(
            model=model_path,
            dtype=dtype,
            max_model_len=self.config.kv_cache_size,
            gpu_memory_utilization=0.90,
            trust_remote_code=True,
        )
        self.sampling_params = SamplingParams

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stream: bool = False,
    ) -> dict:
        params = self.sampling_params(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        outputs = self.llm.generate([prompt], params)
        result = outputs[0]
        return {
            "text": result.outputs[0].text,
            "tokens": len(result.outputs[0].token_ids),
            "finish_reason": result.outputs[0].finish_reason,
        }

    async def chat(
        self,
        messages: list[dict],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> dict:
        # Build prompt from messages using a standard chat template
        parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                parts.append(f"<<SYS>>\n{content}\n<</SYS>>\n\n")
            elif role == "user":
                parts.append(f"[INST] {content} [/INST]")
            elif role == "assistant":
                parts.append(f"{content}")
        prompt = "\n".join(parts)
        return await self.generate(
            prompt, max_tokens, temperature, stream=stream
        )

    async def embed(self, text: str) -> list[float]:
        return []

    async def unload(self):
        if self.llm:
            del self.llm
            self.llm = None
