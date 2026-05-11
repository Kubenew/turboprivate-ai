from turbo.config import TurboConfig


def test_default_config():
    cfg = TurboConfig()
    assert cfg.inference.backend == "auto"
    assert cfg.safety.enabled is True
    assert cfg.auth.provider == "jwt"


def test_inference_config():
    cfg = TurboConfig()
    assert cfg.inference.max_batch_size == 32
    assert cfg.inference.kv_cache_size == 8192


def test_safety_config():
    cfg = TurboConfig()
    assert cfg.safety.pre_flight is True
    assert cfg.safety.post_flight is True
    assert cfg.safety.blocking_threshold == 0.7
