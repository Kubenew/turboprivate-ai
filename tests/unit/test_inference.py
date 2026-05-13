import numpy as np

from turbo.inference.cache import KVCache, PromptCache
from turbo.inference.engine import detect_hardware
from turbo.inference.gateway import InferenceGateway
from turbo.inference.quantize import (
    QuantConfig,
    pack_int4,
    turboquant_v3_compress,
    turboquant_v3_decompress,
    unpack_int4,
)


def test_hardware_detection():
    hw_type, hw_name = detect_hardware()
    assert hw_type in ("cpu", "consumer", "cloud")
    assert isinstance(hw_name, str)


def test_pack_unpack_roundtrip():
    original = np.array([1, -2, 3, -4, 5, -6, 7, -8], dtype=np.int8)
    packed = pack_int4(original)
    unpacked = unpack_int4(packed, len(original))
    assert np.array_equal(original, unpacked)


def test_quantize_dequantize_symmetric():
    W = np.random.uniform(-1.0, 1.0, (16, 64)).astype(np.float32)
    config = QuantConfig(
        group_size=32, activation_aware=False, outlier_keep_ratio=0.0,
        rank=0, zero_point=False
    )
    comp = turboquant_v3_compress(W, config)
    W_rec = turboquant_v3_decompress(comp)
    mse = np.mean((W - W_rec) ** 2)
    assert mse < 0.02

def test_quantize_dequantize_asymmetric():
    W = np.random.uniform(-0.5, 2.0, (16, 64)).astype(np.float32)
    config = QuantConfig(
        group_size=32, activation_aware=False, outlier_keep_ratio=0.0,
        rank=0, zero_point=True
    )
    comp = turboquant_v3_compress(W, config)
    W_rec = turboquant_v3_decompress(comp)
    mse = np.mean((W - W_rec) ** 2)
    assert mse < 0.02


def test_kv_cache():
    cache = KVCache(capacity=10)
    cache.put("test_key", ("data",))
    assert cache.get("test_key") is not None
    assert cache.get("nonexistent") is None


def test_prompt_cache():
    cache = PromptCache(capacity=10)
    cache.store("hello", "world")
    assert cache.lookup("hello") == "world"
    assert cache.lookup("missing") is None


def test_gateway_register_and_route():
    gw = InferenceGateway()
    gw.register_model("llama3", ["http://localhost:8001", "http://localhost:8002"])
    backend = gw.choose_backend("llama3")
    assert backend is not None
    assert backend.url.startswith("http://")


def test_gateway_no_backend():
    gw = InferenceGateway()
    assert gw.choose_backend("nonexistent") is None
