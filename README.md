# TurboPrivate AI

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

## Documentation

- `turbo/cli.py` — CLI entry point and command reference
- `turbo/api/main.py` — FastAPI application
- `turbo/safety/gate.py` — Safety gate configuration
- `frontend/` — React SPA
- `helm/turboprivate/` — Kubernetes deployment
