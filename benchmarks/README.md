# Benchmarks

## RTX 4090 — Llama 3.1 8B (INT4 via TurboQuant)

| Metric | Value |
|---|---|
| Hardware | NVIDIA RTX 4090 (24GB VRAM) |
| Model | Llama 3.1 8B |
| Quantization | INT4 (group-wise, group_size=32) |
| Backend | vLLM |
| Batch Size | 1 |

### Throughput

| Setting | Tokens/sec |
|---|---|
| Prompt: 128 tokens, Gen: 256 tokens | 118 tok/s |
| Prompt: 512 tokens, Gen: 128 tokens | 85 tok/s |
| Prompt: 2048 tokens, Gen: 256 tokens | 62 tok/s |

### Memory

| Quantization | VRAM Usage |
|---|---|
| FP16 (baseline) | ~16.2 GB |
| INT4 (TurboQuant) | ~5.8 GB |
| Savings | **64% reduction** |

### Cost Comparison

| Provider | Cost per 1M tokens | Cost Ratio |
|---|---|---|
| TurboPrivate AI (self-hosted, RTX 4090) | ~$0.02 | 1x |
| OpenAI GPT-4o-mini | $0.15 | ~7.5x |
| Anthropic Claude Haiku | $0.25 | ~12.5x |
| AWS Bedrock Llama 3 8B | $0.40 | ~20x |

*Self-hosted costs based on amortized hardware over 3 years + electricity at €0.12/kWh.*
