# TurboPrivate AI — Self-Hosted Enterprise AI Platform

> **Switch from OpenAI in 30 seconds.** Drop-in compatible API with built-in safety, governance, and 40–60% cost reduction.

<p align="center">
  <a href="https://pypi.org/project/turboprivate-ai/"><img src="https://img.shields.io/pypi/v/turboprivate-ai?color=blue&logo=pypi" alt="PyPI"></a>
  <a href="https://pypi.org/project/turboprivate-ai/"><img src="https://img.shields.io/pypi/pyversions/turboprivate-ai?logo=python" alt="Python"></a>
  <a href="https://github.com/Kubenew/turboprivate-ai/actions"><img src="https://img.shields.io/github/actions/workflow/status/Kubenew/turboprivate-ai/ci.yml?branch=main&logo=github" alt="CI"></a>
  <a href="https://pypi.org/project/turboprivate-ai/"><img src="https://img.shields.io/pypi/dm/turboprivate-ai?logo=pypi" alt="Downloads"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue" alt="License"></a>
  <a href="SECURITY.md"><img src="https://img.shields.io/badge/Security-Policy-red" alt="Security"></a>
</p>

<p align="center">
  <strong>Run powerful LLMs on your own hardware — with enterprise safety, governance, and full data sovereignty.</strong>
</p>

---

##  Quick Start

### One-Click Install
```bash
curl -fsSL https://get.turboprivate.ai | bash
```

### Or via pip
```bash
pip install turboprivate-ai
turbo deploy --provider bare-metal --gpu auto
turbo model serve meta-llama/Llama-3.1-8B --quant int4
turbo chat
```

### Docker Compose (Hardware-Aware)
```bash
git clone https://github.com/Kubenew/turboprivate-ai.git
cd turboprivate-ai

# Auto-detects GPU / Apple Silicon / CPU
curl -fsSL https://get.turboprivate.ai | bash

# Or manually:
docker compose -f docker-compose.gpu.yml up -d    # NVIDIA GPU
docker compose -f docker-compose.mac.yml up -d     # Apple Silicon
docker compose -f docker-compose.cpu.yml up -d     # CPU fallback
```

---

## Why TurboPrivate AI?

| Feature | TurboPrivate AI | Ollama | vLLM | OpenAI API |
|---------|----------------|--------|------|------------|
| **Data Sovereignty** | ✅ Full | ✅ Full | ✅ Full | ❌ Cloud |
| **Enterprise Safety** | ✅ Mythos Safe (7 verifiers) | ❌ None | ❌ None | ⚠️ Basic |
| **OpenAI Compatible** | ✅ 100% | ✅ Partial | ✅ Partial | ✅ Native |
| **INT4/AWQ Quantization** | ✅ TurboQuant v3 | ✅ GGUF | ✅ AWQ | N/A |
| **RAG Pipeline** | ✅ Built-in | ❌ External |  External | ❌ External |
| **Audit Trail** | ✅ Immutable JSONL | ❌ None | ❌ None | ⚠️ Limited |
| **RBAC / Multi-tenant** | ✅ Enterprise | ❌ None | ❌ None | ✅ Enterprise |
| **Kubernetes Native** | ✅ Helm + K3s | ❌ Manual | ⚠️ Manual | N/A |
| **Cost (RTX 4090)** | **~8x cheaper** | Free | Free | $5-10/M tokens |

---

## 🏢 For Enterprises

TurboPrivate AI is the **Enterprise On-Premise AI Gateway** — a secure, compliant orchestration layer between your corporate data and open-source models.

### What We Are
- ✅ **Secure Wrapper**: Mythos Safe gate with 7 verifiers (injection, PII, toxicity, etc.)
- ✅ **OpenAI Parity**: 100% compatible API — swap `base_url` and you're done
- ✅ **SAP HANA Native**: Direct, secure RAG connector with SQL injection guard + RLS
- ✅ **Audit & Compliance**: Immutable JSONL logs, GDPR/HIPAA/SOC 2 ready
- ✅ **Hardware Agnostic**: GPU, Apple Silicon, or CPU — auto-optimized

### What We Are Not
- ❌ **Model Training**: We don't train models from scratch
- ❌ **Custom UI**: We integrate Open WebUI / LibreChat instead of building our own
- ❌ **Vector DB**: We connect to Qdrant, Milvus, pgvector — we don't replace them

See [docs/ENTERPRISE.md](docs/ENTERPRISE.md) for architecture details.

### Security & Compliance
- **Full data sovereignty**: Nothing leaves your infrastructure
- **Mythos Safe**: 7-layer defense (injection, PII, toxicity, hallucination, etc.)
- **Audit trail**: Immutable JSONL logs with SIEM integration
- **RBAC**: Fine-grained access control with OIDC/SAML support
- **Compliance ready**: GDPR, HIPAA, SOC 2, PCI-DSS, ISO 27001

See [SECURITY.md](SECURITY.md) and [docs/COMPLIANCE.md](docs/COMPLIANCE.md) for details.

### Enterprise Integrations
- **SAP HANA**: Vector store + RAG pipeline ([Guide](docs/SAP_HANA_INTEGRATION.md))
- **SAP AI Core**: BYOM deployment support
- **Kubernetes**: Helm charts, HPA, multi-cluster
- **Observability**: Prometheus, Grafana, OpenTelemetry
- **Secrets**: HashiCorp Vault, AWS Secrets Manager, K8s Secrets

### Support & SLAs
| Tier | Response | Includes |
|------|----------|----------|
| **Community** | GitHub Issues | OSS core, docs, community support |
| **PoC / Pilot** | 48h | 4-8 week trial, 2 models, training |
| **Enterprise** | 4h | SLA 99.5%, unlimited models, TAM |
| **Enterprise Plus** | 1h | Multi-cluster, custom verifiers, SOC2 |

📅 [Book a 30-min PoC Call](mailto:felix@turboprivate.ai) | ✉️ [Contact Sales](mailto:felix@turboprivate.ai)

---

## 📊 Performance (RTX 4090)

| Model | Quant | Tokens/sec | VRAM | Cost vs Cloud |
|-------|-------|------------|------|---------------|
| Llama 3.1 8B | INT4 | 110+ | ~5.8 GB | **~8x cheaper** |
| Qwen2.5 32B | INT4 | 45+ | ~22 GB | **~6x cheaper** |
| Llama 3.1 70B | INT4 | 18+ | ~48 GB | **~5x cheaper** |

Independent benchmarks: [benchmarks/](benchmarks/)

---

## 🛡️ Architecture

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
──────────┐ ┌──────────┐ ┌──────────┐
│  K3s     │ │Monitoring│ │ Storage  │
│  Cluster │ │Prom/Graf │ │ PG/Redis │
└────────── └──────────┘ └──────────┘
```

---

## 🎬 Demo

<p align="center">
  <img src="https://raw.githubusercontent.com/Kubenew/turboprivate-ai/main/demo/turboprivate-demo.gif" alt="TurboPrivate AI deployment demo" width="100%">
</p>

---

##  Documentation

- [Architecture](docs/ARCHITECTURE.md) — System design
- [Deployment](docs/DEPLOYMENT.md) — Production guide
- [Enterprise Guide](docs/ENTERPRISE.md) — Air-gapped, HA, sizing, migration
- [Compliance](docs/COMPLIANCE.md) — GDPR, HIPAA, SOC 2, PCI-DSS readiness
- [SAP HANA Integration](docs/SAP_HANA_INTEGRATION.md) — Cost calculator, security checklist
- [CLI Reference](turbo/cli.py) — All commands
- [API Reference](turbo/api/main.py) — FastAPI routes
- [Security Policy](SECURITY.md) — Vulnerability reporting
- [Contributing](CONTRIBUTING.md) — How to contribute

---

## 🔄 Changelog

### 0.1.9 (2026-05-17)
- Optimized SAP HANA Secure Connector: pre-compiled regex for high-throughput PII masking
- Air-gapped installer support: `--offline` flag + local compose file detection
- CI/CD security pipeline: automated SQL injection blocking tests
- Performance tuning: vectorized masking hints, reduced regex overhead

### 0.1.8 (2026-05-17)
- SAP HANA Secure RAG Connector: SQL injection guard, RLS mapping, PII masking
- Hardware-aware installer: auto-detects NVIDIA / Apple Silicon / CPU
- Docker Compose profiles: gpu.yml, mac.yml, cpu.yml for optimal deployment
- README overhaul: "What We Are / Are Not" transparency, Enterprise Gateway positioning
- Modular architecture: decoupled inference backends, plug-and-play vector DBs

### 0.1.7 (2026-05-17)
- SECURITY.md with threat model, hardening guide, SBOM, responsible disclosure
- CONTRIBUTING.md with dev setup, testing, PR guidelines
- Enterprise Deployment Guide: air-gapped, HA, secrets, proxy, hardware sizing
- Compliance readiness: GDPR, HIPAA, SOC 2, PCI-DSS, ISO 27001, EU AI Act
- One-click installer (install.sh) + docker-compose.full.yml with GPU passthrough
- GitHub issue templates: bug report, feature request, security report
- README overhaul: feature comparison table, "For Enterprises" section, badges

### 0.1.6 (2026-05-16)
- SAP HANA integration guide: cost calculator, security checklist, BYOM, compliance
- Enterprise hardening best practices
- SECURITY.md and CONTRIBUTING.md added

### 0.1.5 (2026-05-16)
- SAP HANA vector store integration (LangChain + HanaDB)
- FastAPI RAG endpoint with similarity search
- Document ingestion with PDF/text + HNSW index

### 0.1.4 (2026-05-13)
- Production Helm charts (configmap, ingress, services)
- TurboQuant v3: AWQ + INT4 mixed-precision
- K3s provisioner with multi-node discovery
- vLLM backend: speculative decoding + prefix caching

[Full changelog →](https://github.com/Kubenew/turboprivate-ai/releases)

---

## 📄 License

Apache 2.0 — see [LICENSE](LICENSE).

---

<p align="center">
  Built by <a href="https://github.com/Kubenew">Kubenew</a> — ex-HPE engineer, 12+ years enterprise infrastructure
</p>
