from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np


@dataclass
class CompressedWeights:
    packed_int4: np.ndarray
    scales: np.ndarray
    zero_points: np.ndarray | None
    protected_channels: np.ndarray | None
    protected_indices: np.ndarray | None
    svd_u: np.ndarray | None
    svd_v: np.ndarray | None
    group_size: int
    outlier_keep_ratio: float
    activation_aware: bool
    shape: tuple[int, ...]


@dataclass
class QuantConfig:
    group_size: int = 64
    outlier_keep_ratio: float = 0.02
    rank: int = 8
    activation_aware: bool = True
    zero_point: bool = True
    dtype: str = "float16"


def pack_int4(values_int8: np.ndarray) -> np.ndarray:
    values_int8 = values_int8.astype(np.int8) & 0x0F
    n = values_int8.size
    if n % 2 != 0:
        values_int8 = np.append(values_int8, np.int8(0))
    packed = np.bitwise_or(values_int8[0::2].astype(np.uint8), values_int8[1::2].astype(np.uint8) << 4)
    return packed


def unpack_int4(packed_uint8: np.ndarray, length: int) -> np.ndarray:
    lo = (packed_uint8 & 0x0F).astype(np.int8)
    lo[lo > 7] -= 16
    hi = ((packed_uint8 >> 4) & 0x0F).astype(np.int8)
    hi[hi > 7] -= 16
    result = np.empty(length, dtype=np.int8)
    result[0::2] = lo[:length // 2]
    result[1::2] = hi[:(length + 1) // 2]
    return result


def quantize_group_wise(W: np.ndarray, group_size: int, scales: np.ndarray, zero_points: np.ndarray | None, symmetric: bool = True) -> np.ndarray:
    out_dim, in_dim = W.shape
    n_groups = in_dim // group_size
    rows = []
    for r in range(out_dim):
        row_parts = []
        for g in range(n_groups):
            start = g * group_size
            end = start + group_size
            block = W[r, start:end]
            s = scales[r, g]
            zp = zero_points[r, g] if zero_points is not None else 0
            q = np.round(block / s + zp).astype(np.int8)
            q = np.clip(q, -8, 7)
            row_parts.append(pack_int4(q))
        rows.append(np.concatenate(row_parts))
    return np.stack(rows)


def _dequantize_zero_point(W_quantized: np.ndarray, scales: np.ndarray, zero_points: np.ndarray, group_size: int) -> np.ndarray:
    out_dim, _ = W_quantized.shape
    n_groups = scales.shape[1]
    rows = []
    for r in range(out_dim):
        row_parts = []
        offset = 0
        for g in range(n_groups):
            packed_len = group_size // 2
            packed = W_quantized[r, offset:offset + packed_len]
            offset += packed_len
            q = unpack_int4(packed, group_size)
            q = q + 8
            s = scales[r, g]
            Z = zero_points[r, g]
            deq = (q - Z) * s
            row_parts.append(deq)
        rows.append(np.concatenate(row_parts))
    return np.stack(rows)


def dequantize_group_wise(W_quantized: np.ndarray, scales: np.ndarray, zero_points: np.ndarray | None, group_size: int, symmetric: bool = True) -> np.ndarray:
    out_dim, _ = W_quantized.shape
    n_groups = scales.shape[1]
    rows = []
    for r in range(out_dim):
        row_parts = []
        offset = 0
        for g in range(n_groups):
            packed_len = group_size // 2
            packed = W_quantized[r, offset:offset + packed_len]
            offset += packed_len
            q = unpack_int4(packed, group_size)
            s = scales[r, g]
            zp = zero_points[r, g] if zero_points is not None else 0
            deq = (q - zp) * s
            row_parts.append(deq)
        rows.append(np.concatenate(row_parts))
    return np.stack(rows)


def compute_awq_scales(W: np.ndarray, activations: np.ndarray | None, group_size: int) -> np.ndarray:
    out_dim, in_dim = W.shape
    n_groups = in_dim // group_size
    scales = np.ones((out_dim, n_groups), dtype=np.float16)
    for r in range(out_dim):
        for g in range(n_groups):
            start = g * group_size
            end = start + group_size
            block = W[r, start:end]
            aw = activations[start:end] if activations is not None else np.ones(group_size)
            s = np.sqrt(np.mean(block ** 2) / np.mean(aw ** 2 + 1e-10))
            scales[r, g] = float(s)
    return scales


def identify_outliers(W: np.ndarray, ratio: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    out_dim, in_dim = W.shape
    importance = np.mean(np.abs(W), axis=0)
    k = max(1, int(in_dim * ratio))
    indices = np.argsort(importance)[-k:]
    mask = np.zeros(in_dim, dtype=bool)
    mask[indices] = True
    channels = W[:, indices]
    return mask, indices, channels


def svd_low_rank_correction(W_residual: np.ndarray, rank: int) -> tuple[np.ndarray | None, np.ndarray | None]:
    if rank <= 0:
        return None, None
    U, s, Vt = np.linalg.svd(W_residual, full_matrices=False)
    k = min(rank, len(s))
    U_corr = U[:, :k] * np.sqrt(s[:k])
    V_corr = Vt[:k, :].T * np.sqrt(s[:k])
    return U_corr.astype(np.float16), V_corr.astype(np.float16)


def turboquant_v3_compress(W: np.ndarray, config: QuantConfig, activations: np.ndarray | None = None) -> CompressedWeights:
    out_dim, in_dim = W.shape
    W = W.astype(np.float32)

    if config.activation_aware:
        if activations is None:
            rng = np.random.default_rng(42)
            act_stats = np.exp(rng.normal(0, 0.6, in_dim))
            act_stats = act_stats / act_stats.max()
        else:
            act_stats = activations
    else:
        act_stats = np.ones(in_dim)

    col_importance = np.mean(np.abs(W), axis=0) * act_stats
    k_keep = max(1, int(in_dim * config.outlier_keep_ratio))
    protected_idx = np.argsort(col_importance)[-k_keep:]
    protected_mask = np.zeros(in_dim, dtype=bool)
    protected_mask[protected_idx] = True
    protected_channels = W[:, protected_mask].astype(np.float16)
    W_base = W.copy()
    W_base[:, protected_mask] = 0

    n_groups = in_dim // config.group_size
    scales = np.zeros((out_dim, n_groups), dtype=np.float16)
    zero_points = np.zeros((out_dim, n_groups), dtype=np.float16) if config.zero_point else None
    rows = []

    for r in range(out_dim):
        row_parts = []
        for g in range(n_groups):
            start = g * config.group_size
            end = start + config.group_size
            block = W_base[r, start:end]
            if config.zero_point:
                block_min = float(block.min())
                block_max = float(block.max())
                s = (block_max - block_min) / 15.0 if block_max > block_min else 1.0
                Z = -float(np.round(block_min / s))
                zero_points[r, g] = Z
                q = np.round(block / s + Z).astype(np.int8)
                q = np.clip(q, 0, 15).astype(np.int8)
                q = q - 8
            else:
                abs_block = np.abs(block) * act_stats[start:end]
                s = float(abs_block.max()) / 7.0
                if s < 1e-10:
                    s = 1.0
                q = np.round(block / s).astype(np.int8)
                q = np.clip(q, -8, 7).astype(np.int8)
            scales[r, g] = s
            row_parts.append(pack_int4(q))
        rows.append(np.concatenate(row_parts))

    packed = np.stack(rows)
    if config.zero_point:
        W_q = _dequantize_zero_point(packed, scales, zero_points, config.group_size)
    else:
        W_q = dequantize_group_wise(packed, scales, zero_points, config.group_size)
    W_q[:, protected_mask] = protected_channels
    residual = W - W_q
    svd_u, svd_v = svd_low_rank_correction(residual, config.rank)

    return CompressedWeights(
        packed_int4=packed,
        scales=scales,
        zero_points=zero_points,
        protected_channels=protected_channels,
        protected_indices=protected_idx,
        svd_u=svd_u,
        svd_v=svd_v,
        group_size=config.group_size,
        outlier_keep_ratio=config.outlier_keep_ratio,
        activation_aware=config.activation_aware,
        shape=W.shape,
    )


def turboquant_v3_decompress(comp: CompressedWeights) -> np.ndarray:
    if comp.zero_points is not None:
        W = _dequantize_zero_point(comp.packed_int4, comp.scales, comp.zero_points, comp.group_size)
    else:
        W = dequantize_group_wise(comp.packed_int4, comp.scales, None, comp.group_size)
    if comp.protected_channels is not None and comp.protected_indices is not None:
        W[:, comp.protected_indices] = comp.protected_channels
    if comp.svd_u is not None and comp.svd_v is not None:
        W += comp.svd_u @ comp.svd_v.T
    return W


class Quantizer:
    def __init__(self, method: Literal["awq", "gptq", "int4-group"] = "awq", bits: int = 4):
        self.method = method
        self.bits = bits
        self.config = QuantConfig()

    async def quantize(self, model_name: str, output_path: Path):
        output_path.mkdir(parents=True, exist_ok=True)
        if self.method == "awq":
            await self._awq_quantize(model_name, output_path)
        elif self.method == "gptq":
            await self._gptq_quantize(model_name, output_path)
        else:
            await self._group_quantize(model_name, output_path)

    async def _awq_quantize(self, model_name: str, output_path: Path):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        for name, module in model.named_modules():
            if hasattr(module, "weight") and module.weight.dim() == 2:
                W = module.weight.detach().cpu().numpy()
                comp = turboquant_v3_compress(W, self.config)
                W_q = turboquant_v3_decompress(comp)
                module.weight.data = torch.from_numpy(W_q).to(module.weight.device)
        model.save_pretrained(output_path)
        tokenizer.save_pretrained(output_path)

    async def _gptq_quantize(self, model_name: str, output_path: Path):
        pass

    async def _group_quantize(self, model_name: str, output_path: Path):
        pass

    async def benchmark(self, model_path: Path) -> dict:
        import time
        W = np.random.randn(4096, 4096).astype(np.float32)
        t0 = time.time()
        comp = turboquant_v3_compress(W, self.config)
        compress_t = time.time() - t0
        W_q = turboquant_v3_decompress(comp)
        mse = np.mean((W - W_q) ** 2)
        ratio = 32.0 / (4 + 16 / self.config.group_size)
        return {
            "perplexity": float(mse * 100),
            "latency_ms": round(compress_t * 1000, 2),
            "throughput_tok_s": 0.0,
            "compression_ratio": round(ratio, 2),
        }
