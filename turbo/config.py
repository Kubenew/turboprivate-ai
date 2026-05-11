from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class InferenceConfig(BaseSettings):
    model_name: str = "llama3-8b-int4"
    model_path: Path | None = None
    backend: Literal["vllm", "llamacpp", "auto"] = "auto"
    gpu_type: Literal["auto", "consumer", "cloud", "cpu"] = "auto"
    max_batch_size: int = 32
    max_wait_ms: int = 50
    kv_cache_size: int = 8192
    dtype: str = "auto"


class SafetyConfig(BaseSettings):
    enabled: bool = True
    pre_flight: bool = True
    post_flight: bool = True
    sandbox: Literal["gvisor", "none"] = "gvisor"
    audit_trail: bool = True
    blocking_threshold: float = 0.7


class MemoryConfig(BaseSettings):
    enabled: bool = False
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    storage_path: Path = Field(default=Path("./data/memory"))
    chunk_size: int = 512
    chunk_overlap: int = 64


class AuthConfig(BaseSettings):
    enabled: bool = True
    provider: Literal["jwt", "oauth2", "none"] = "jwt"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60


class ObservabilityConfig(BaseSettings):
    tracing: bool = True
    metrics: bool = True
    logging_level: str = "INFO"
    otlp_endpoint: str | None = None


class ClusterConfig(BaseSettings):
    name: str = "turbo-cluster"
    provider: Literal["bare-metal", "proxmox", "morpheus", "hetzner"] = "bare-metal"
    k3s_version: str = "v1.30.0+k3s1"
    gpu_operator: bool = True
    monitoring: bool = True
    backup_enabled: bool = True


class TurboConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TURBO_", env_nested_delimiter="__")

    inference: InferenceConfig = Field(default_factory=InferenceConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    cluster: ClusterConfig = Field(default_factory=ClusterConfig)

    data_dir: Path = Field(default=Path("./data"))
    log_dir: Path = Field(default=Path("./logs"))


config = TurboConfig()
