# TurboPrivate AI

<p align="center">
  <a href="https://pypi.org/project/turboprivate-ai/"><img src="https://img.shields.io/pypi/v/turboprivate-ai?color=blue&logo=pypi" alt="PyPI version"></a>
  <a href="https://pypi.org/project/turboprivate-ai/"><img src="https://img.shields.io/pypi/pyversions/turboprivate-ai?logo=python" alt="Python versions"></a>
  <a href="https://github.com/Kubenew/turboprivate-ai/actions"><img src="https://img.shields.io/github/actions/workflow/status/Kubenew/turboprivate-ai/ci.yml?branch=main&logo=github" alt="CI status"></a>
  <a href="https://pypi.org/project/turboprivate-ai/"><img src="https://img.shields.io/pypi/dm/turboprivate-ai?logo=pypi" alt="Downloads"></a>
  <a href="https://github.com/Kubenew/turboprivate-ai/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Kubenew/turboprivate-ai?logo=open-source-initiative" alt="License"></a>
  <a href="https://github.com/Kubenew/turboprivate-ai"><img src="https://img.shields.io/github/stars/Kubenew/turboprivate-ai?logo=github" alt="Stars"></a>
</p>

Unified platform for self-hosted LLM inference + enterprise safety governance.

## Features

- **Inference Engine** — vLLM/llama.cpp backends with auto hardware detection, TurboQuant-v3 INT4 quantization, QoS routing, dynamic batching, KV/prompt caching
- **Safety Gate** — Pre-flight and post-flight verification with 7 verifiers: anti-hacking, PII detection, prompt injection, overengineering, patch analysis, vulnerability scanning, hallucination scoring
- **Memory & RAG** — Vector store with cosine similarity search, multi-format document parser (PDF, DOCX, HTML, CSV, JSON, XML, YAML, Markdown)
- **Infrastructure** — K3s provisioning via SSH/Terraform, age-encrypted backups, Helm chart deployment
- **Frontend** — React SPA dashboard with model management, safety governance, memory search, and settings
- **Auth** — JWT-based authentication with RBAC
- **Observability** — Prometheus metrics, OpenTelemetry tracing, structured logging
- **CLI** — 20+ commands for model management, safety policies, infrastructure, and backups

## Quick Start

```bash
pip install turboprivate-ai
turbo serve --reload
```

## Changelog

### 0.1.1 (2026-05-11)

- Migrated to hatchling build system
- Fixed missing `InferenceEngine` import in `turbo.inference`
- Fixed `TracerProvider` bug in OpenTelemetry instrumentation
- Added structured logging to all exception handlers
- Consolidated Celery workers into shared `worker.celery_app`
- Added CI workflow with ruff linting + pytest
- Improved graceful shutdown (audit trail flush)
- Updated dependencies (replaced `unstructured` with actual used libs)

## Documentation

- `turbo/cli.py` — CLI entry point and command reference
- `turbo/api/main.py` — FastAPI application
- `turbo/safety/gate.py` — Safety gate configuration
- `frontend/` — React SPA
- `helm/turboprivate/` — Kubernetes deployment
