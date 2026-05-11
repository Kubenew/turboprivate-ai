
from turbo.config import InferenceConfig


class LlamaCppBackend:
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.llm = None

    async def load(self):
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError(
                "llama-cpp-python not installed. Run: pip install llama-cpp-python"
            )

        model_path = str(self.config.model_path) if self.config.model_path else self.config.model_name
        n_gpu_layers = -1 if self.config.gpu_type != "cpu" else 0

        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=self.config.kv_cache_size,
            verbose=False,
        )

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stream: bool = False,
    ) -> dict:
        output = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=stream,
        )
        if stream:
            return {"text": "", "tokens": 0, "finish_reason": "stop"}
        return {
            "text": output["choices"][0]["text"],
            "tokens": output["usage"]["completion_tokens"],
            "finish_reason": "stop",
        }

    async def chat(
        self,
        messages: list[dict],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> dict:
        output = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
        )
        if stream:
            return {"text": "", "tokens": 0, "finish_reason": "stop"}
        return {
            "text": output["choices"][0]["message"]["content"],
            "tokens": output["usage"]["completion_tokens"],
            "finish_reason": "stop",
        }

    async def embed(self, text: str) -> list[float]:
        return self.llm.create_embedding(text)["data"][0]["embedding"]

    async def unload(self):
        if self.llm:
            del self.llm
            self.llm = None
