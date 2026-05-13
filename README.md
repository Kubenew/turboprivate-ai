# TurboPrivate AI — Private & Safe Enterprise AI Platform

<p align="center">
  <a href="https://pypi.org/project/turboprivate-ai/"><img src="https://img.shields.io/pypi/v/turboprivate-ai?color=blue&logo=pypi" alt="PyPI version"></a>
  <a href="https://pypi.org/project/turboprivate-ai/"><img src="https://img.shields.io/pypi/pyversions/turboprivate-ai?logo=python" alt="Python versions"></a>
  <a href="https://github.com/Kubenew/turboprivate-ai/actions"><img src="https://img.shields.io/github/actions/workflow/status/Kubenew/turboprivate-ai/ci.yml?branch=main&logo=github" alt="CI status"></a>
  <a href="https://pypi.org/project/turboprivate-ai/"><img src="https://img.shields.io/pypi/dm/turboprivate-ai?logo=pypi" alt="Downloads"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue" alt="License"></a>
  <a href="https://github.com/Kubenew/turboprivate-ai"><img src="https://img.shields.io/github/stars/Kubenew/turboprivate-ai?logo=github" alt="Stars"></a>
</p>

<p align="center">
  <strong>Run powerful LLMs on your own hardware — 40–60% cheaper than public clouds, with built-in enterprise safety & governance.</strong>
</p>

---

## Why TurboPrivate AI?

- **Full data sovereignty** — nothing leaves your infrastructure
- **Dramatic cost reduction** — INT4/AWQ quantization + smart routing
- **Enterprise Safety** — powered by Mythos Safe (defensive evaluation, jailbreak protection, audit)
- **OpenAI compatible** — drop-in replacement for your existing applications
- **One-command deploy** — from bare metal to production in minutes

## Key Features

- **TurboQuant Engine** — State-of-the-art INT4/AWQ quantization with minimal quality loss
- **Mythos Safe** — Multi-layer defensive safety (pre & post-flight gates)
- **Private RAG** — Secure document ingestion and retrieval
- **Full-stack observability** — Prometheus, Grafana, OpenTelemetry
- **Enterprise ready** — RBAC, audit trail, multi-tenancy, compliance support
- **Hardware flexibility** — RTX 4090, A100/H100, or even CPU-only

## Performance (RTX 4090)

| Model | Quant | Tokens/sec | VRAM Usage | Cost vs Groq/AWS |
|---|---|---|---|---|
| Llama 3.1 8B | INT4 | 110+ | ~5.8 GB | **~8x cheaper** |
| Qwen2.5 32B | INT4 | 45+ | ~22 GB | **~6x cheaper** |
| Llama 3.1 70B | INT4 | 18+ | ~48 GB | **~5x cheaper** |

## Quick Start

```bash
# 1. Deploy full stack (K8s)
turbo deploy --provider bare-metal --gpu auto

# 2. Serve model
turbo model serve meta-llama/Llama-3.1-8B --quant int4

# 3. Chat
turbo chat
```

Or use Docker Compose for quick testing:

```bash
docker compose -f docker-compose.full.yml up -d
```

## Pricing

| Tier | Price | Best For | Includes |
|---|---|---|---|
| **PoC / Pilot** | €15,000 – €35,000 | 4–8 weeks trial | Deployment, 2 models, training, support |
| **Enterprise License** | €65,000 / year | Single cluster, up to 10 users | Full features, unlimited models, SLA 99.5% |
| **Enterprise Plus** | €120,000 – €180,000 / year | Multiple clusters, 50+ users | Priority support, custom verifiers, SOC2 |
| **Managed Service** | €8,000 – €25,000 / month | No ops team | Fully managed by us |

**Volume discounts** available for 3+ clusters.  
All prices exclude hardware.

Interested in a private demo?  
📅 [Book a 30-min PoC Call](mailto:felix@turboprivate.ai) | ✉️ [Contact Sales](mailto:felix@turboprivate.ai)

## Architecture

```
CLI / SDK / Dashboard
        ↓
   API Gateway (FastAPI · Auth · Rate Limiting)
        ↓
┌─────────────────┐  ┌───────────────────┐
│  Mythos Safe    │  │  TurboQuant INT4  │
│  Verifiers ·    │  │  vLLM/llama.cpp   │
│  Audit Trail    │  │  Inference Engine │
└─────────────────┘  └───────────────────┘
        ↓
   Memory & RAG (TurboMemory · pdf2struct)
        ↓
┌──────────┐ ┌──────────┐ ┌──────────┐
│  K3s     │ │Monitoring│ │ Storage  │
│  Cluster │ │Prom/Graf │ │ PG/Redis │
└──────────┘ └──────────┘ └──────────┘
```

## Demo

<p align="center">
  <img src="https://raw.githubusercontent.com/Kubenew/turboprivate-ai/main/demo/turboprivate-demo.gif" alt="TurboPrivate AI deployment demo" width="100%">
</p>

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — Full system design
- [Deployment](docs/DEPLOYMENT.md) — Production deployment guide
- [CLI Reference](turbo/cli.py) — All CLI commands
- [API Reference](turbo/api/main.py) — FastAPI routes
- [Safety Gate](turbo/safety/gate.py) — Verifier configuration
- [Demo Assets](demo/) — GIF recording tape + deploy script

## Changelog

### 0.1.3 (2026-05-13)
- Extended demo GIF to 61s with 5-scene animation (intro, deploy, serve+chat, safety block, dashboard)
- Switched README GIF to absolute GitHub raw URL for PyPI rendering

### 0.1.2 (2026-05-11)
- Enterprise-ready README with pricing table and benchmarks
- Added docs/ARCHITECTURE.md with system design diagrams
- Added docs/DEPLOYMENT.md with production deployment guide
- Added examples/ with HTTP, safety, RAG, and quantization samples
- Added .env.example with all configuration options
- Added benchmarks/ with RTX 4090 performance results
- Switched license from MIT to Apache 2.0
- Added `turbo doctor` CLI command for system health checks
- Added GitHub Actions Docker build workflow
- Updated pyproject.toml with `full` install extra

### 0.1.1 (2026-05-11)
- Migrated to hatchling build system
- Fixed missing `InferenceEngine` import in `turbo.inference`
- Fixed `TracerProvider` bug in OpenTelemetry instrumentation
- Added structured logging to all exception handlers
- Consolidated Celery workers into shared `worker.celery_app`
- Added CI workflow with ruff linting + pytest
- Improved graceful shutdown (audit trail flush)
- Updated dependencies (replaced `unstructured` with actual used libs)

## License

Apache 2.0 — see [LICENSE](LICENSE).

---

<p align="center">
  Built by <a href="https://github.com/Kubenew">Kubenew</a> — ex-HPE engineer, 12+ years enterprise infrastructure
</p>
