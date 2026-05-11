from collections import OrderedDict


class KVCache:
    def __init__(self, capacity: int = 8192, prefix_len: int = 64):
        self.capacity = capacity
        self.prefix_len = prefix_len
        self._cache: OrderedDict[str, tuple] = OrderedDict()

    def get(self, key: str) -> tuple | None:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, kv_state: tuple):
        self._cache[key] = kv_state
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)

    def match_prefix(self, prompt: str) -> str | None:
        prefix = prompt[:self.prefix_len]
        for key in reversed(self._cache):
            if key.startswith(prefix):
                return key
        return None

    def clear(self):
        self._cache.clear()


class PromptCache:
    def __init__(self, capacity: int = 4096):
        self.capacity = capacity
        self._cache: OrderedDict[str, str] = OrderedDict()

    def lookup(self, prompt: str) -> str | None:
        if prompt in self._cache:
            self._cache.move_to_end(prompt)
            return self._cache[prompt]
        return None

    def store(self, prompt: str, completion: str):
        self._cache[prompt] = completion
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)

    def stats(self) -> dict:
        return {
            "size": len(self._cache),
            "capacity": self.capacity,
        }
