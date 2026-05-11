# Deployment Guide

## Prerequisites

- Python 3.11+
- GPU with CUDA support (optional, CPU-only works)
- Docker & Docker Compose (for containerized deployment)
- Kubernetes cluster (optional, for production)
- 16GB+ RAM (32GB+ recommended for 7B+ models)

## Quick Deploy (Docker Compose)

```bash
# Clone the repo
git clone https://github.com/Kubenew/turboprivate-ai.git
cd turboprivate-ai

# Start full stack
docker compose -f docker-compose.full.yml up -d

# Check status
docker compose ps
```

## Production Deploy (Kubernetes)

### 1. Install CLI

```bash
pip install turboprivate-ai
```

### 2. Generate Configuration

```bash
turbo infra init --provider bare-metal --name prod-cluster
```

Edit `turboprivate.yaml` with your node details:

```yaml
cluster_name: prod-cluster
provider: bare-metal
k3s_version: v1.30.0+k3s1
nodes:
  - host: 192.168.1.10
    user: root
    role: master
  - host: 192.168.1.11
    user: root
    role: worker
    gpu: true
  - host: 192.168.1.12
    user: root
    role: worker
    gpu: true
```

### 3. Deploy

```bash
turbo infra deploy --config turboprivate.yaml
```

### 4. Verify

```bash
turbo infra status --name prod-cluster
```

## Hardware Recommendations

| Model Size | Min RAM | Recommended GPU | Storage |
|---|---|---|---|
| 7-8B (INT4) | 16GB | RTX 3090/4090 (24GB) | 50GB |
| 13-14B (INT4) | 32GB | RTX 4090 (24GB) | 100GB |
| 32B (INT4) | 64GB | 2x RTX 4090 / A100 | 200GB |
| 70B (INT4) | 128GB | A100 80GB / H100 | 500GB |

## Provider Support

| Provider | Type | Status |
|---|---|---|
| Bare-metal (SSH) | On-prem | ✅ Stable |
| Proxmox VE | Virtualization | ✅ Stable |
| HPE Morpheus | Hyperconverged | ✅ Stable |
| Hetzner Cloud | Cloud | ✅ Stable |
| AWS EC2 | Cloud | 🚧 In development |
