# TurboPrivate AI — Deployment Guide

## Quick Start Options

### Option 1: Docker Compose (Recommended for testing / small setups)

```bash
git clone https://github.com/Kubenew/turboprivate-ai.git
cd turboprivate-ai

# Start full stack
docker compose -f docker-compose.full.yml up -d
```

### Option 2: One-command Kubernetes Deployment (Production)

```bash
# Install CLI
pip install turboprivate-ai

# Deploy full platform
turbo deploy --provider bare-metal \
             --gpu auto \
             --models llama3.1-8b,qwen2.5-32b \
             --storage longhorn
```

**Supported providers:**
- bare-metal
- proxmox
- hetzner
- morpheus
- hpe-greenlake (coming soon)

## Hardware Requirements

| Setup | GPU | RAM | Storage | Expected Performance |
|---|---|---|---|---|
| Small | 1× RTX 4090 | 64 GB | 500 GB NVMe | Llama 8B @ 100+ tok/s |
| Medium | 2–4× RTX 4090 / A100 | 128 GB | 2 TB | Llama 70B + RAG |
| Large | 8× H100 | 512 GB | 10 TB+ | Multiple heavy models |

## Post-Deployment Steps

```bash
# Check status
turbo status

# Pull and quantize model
turbo model pull meta-llama/Llama-3.1-8B
turbo model quantize Llama-3.1-8B --bits 4

# Start serving
turbo model serve Llama-3.1-8B-int4

# Open dashboard
turbo dashboard
```

## Production Best Practices

- Use gVisor sandbox for untrusted models (`--safety full`)
- Enable automatic backups (`--backup daily`)
- Set up monitoring alerts in Grafana
- Use separate namespaces for multi-tenancy
- Enable audit logging to PostgreSQL + export to SIEM

## Troubleshooting

- `turbo doctor` — run diagnostics
- Check logs: `turbo logs --service inference`
- Common issues:
  - CUDA not found → install NVIDIA Container Toolkit
  - Out of memory → use lower quantization (`--bits 4`)
  - Slow inference → enable dynamic batching

---

Need help with deployment?  
📅 [Book a free 30-minute PoC assistance call](mailto:felix@turboprivate.ai)
