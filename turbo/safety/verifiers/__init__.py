from abc import ABC, abstractmethod


class BaseVerifier(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def verify(self, prompt: str = "", response: str = "", **kwargs) -> dict:
        pass

    async def __call__(self, prompt: str = "", response: str = "", **kwargs) -> dict:
        return await self.verify(prompt, response, **kwargs)
