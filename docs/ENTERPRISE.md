# Enterprise Deployment Guide

This guide covers production deployment scenarios for TurboPrivate AI in enterprise environments.

## 1. Air-Gapped Installation

For environments with no internet access:

### Prerequisites
- Jump host with internet access
- USB drive or internal transfer mechanism
- Target air-gapped servers

### Steps

1. **Download on jump host**:
   ```bash
   pip download turboprivate-ai[full] -d /tmp/turboprivate-packages
   docker save -o turboprivate-images.tar \
     turboprivate-ai/api:latest \
     turboprivate-ai/inference:latest \
     postgres:16-alpine \
     redis:7-alpine \
     prom/prometheus:latest \
     grafana/grafana:latest
   ```

2. **Transfer to air-gapped environment**:
   ```bash
   # Copy via USB or secure transfer
   scp /tmp/turboprivate-packages/* user@airgapped-host:/opt/packages/
   scp turboprivate-images.tar user@airgapped-host:/opt/images/
   ```

3. **Install on target**:
   ```bash
   pip install --no-index --find-links=/opt/packages turboprivate-ai[full]
   docker load -i /opt/images/turboprivate-images.tar
   ```

4. **Deploy**:
   ```bash
   turbo deploy --provider bare-metal --gpu auto --offline
   ```

## 2. High Availability Setup

### Multi-Node K3s Cluster

```bash
# Master node
turbo deploy --provider k3s --role master --nodes 3

# Worker nodes (auto-join)
turbo deploy --provider k3s --role worker --master-ip 10.0.0.1
```

### HPA Configuration

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: inference
  minReplicas: 1
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: gpu_utilization
        target:
          type: AverageValue
          averageValue: "80"
```

### Redis Sentinel (HA Broker)

```yaml
# docker-compose.ha.yml
services:
  redis-sentinel:
    image: redis:7-alpine
    command: redis-sentinel /etc/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/sentinel.conf
```

## 3. Secrets Management

### HashiCorp Vault

```bash
# Enable KV secrets engine
vault secrets enable -path=turboprivate kv-v2

# Store secrets
vault kv put turboprivate/api api_key="sk-..."
vault kv put turboprivate/db password="..."

# Configure TurboPrivate to use Vault
export TURBOPRIVATE_VAULT_ADDR=https://vault.internal:8200
export TURBOPRIVATE_VAULT_TOKEN=hvs....
```

### Kubernetes Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: turboprivate-secrets
type: Opaque
data:
  api-key: <base64-encoded>
  db-password: <base64-encoded>
```

## 4. Corporate Proxy & CA

### Proxy Configuration

```bash
export HTTP_PROXY=http://proxy.corp:8080
export HTTPS_PROXY=http://proxy.corp:8080
export NO_PROXY=localhost,127.0.0.1,.internal
```

### Custom CA Certificate

```bash
# Add CA to trust store
cp corp-ca.crt /usr/local/share/ca-certificates/
update-ca-certificates

# Configure Python
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

## 5. Hardware Sizing Calculator

| Model | Min GPU | Recommended | Concurrent Users | VRAM |
|-------|---------|-------------|------------------|------|
| Llama 3.1 8B | RTX 3090 | RTX 4090 | 10-50 | 8 GB |
| Llama 3.1 70B | A100 40GB | A100 80GB | 5-20 | 48 GB |
| Qwen2.5 32B | RTX 4090 | A100 80GB | 10-30 | 22 GB |
| Mixtral 8x7B | 2x A100 | 4x A100 | 20-100 | 64 GB |

### Memory Formula
```
VRAM = Model_Size * Quant_Factor + Context_Overhead
INT4: Factor = 0.5 GB per 1B params
INT8: Factor = 1.0 GB per 1B params
FP16: Factor = 2.0 GB per 1B params
```

## 6. Migration Guides

### From OpenAI API

```python
# Before
from openai import OpenAI
client = OpenAI(api_key="sk-...")

# After
from openai import OpenAI
client = OpenAI(
    base_url="http://turboprivate:8000/v1",
    api_key="anything"
)
# Rest of your code unchanged!
```

### From Ollama

```bash
# Ollama
ollama run llama3.1:8b

# TurboPrivate
turbo model pull meta-llama/Llama-3.1-8B
turbo model serve meta-llama/Llama-3.1-8B --quant int4
```

### From vLLM Direct

```bash
# vLLM
python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-3.1-8B

# TurboPrivate (adds safety, monitoring, RAG)
turbo model serve meta-llama/Llama-3.1-8B --quant int4
```

## 7. Production Checklist

- [ ] TLS 1.3 enabled on all endpoints
- [ ] mTLS for internal service communication
- [ ] RBAC configured with OIDC/SAML
- [ ] Rate limiting enabled (100 req/min default)
- [ ] Audit logging to SIEM
- [ ] Backup encryption enabled
- [ ] Resource limits set (CPU/memory/GPU)
- [ ] Health checks configured
- [ ] Monitoring dashboards active
- [ ] Incident response playbook documented
- [ ] Penetration test completed
- [ ] Compliance review signed off

## 8. Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| GPU not detected | Run `turbo doctor`, check NVIDIA drivers |
| OOM errors | Reduce `--max-model-len` or batch size |
| Slow inference | Enable prefix caching, check GPU utilization |
| Safety gate blocking | Review Mythos Safe logs, adjust thresholds |
| RAG not returning docs | Check embedding model consistency, HNSW index |

### Debug Mode

```bash
export TURBOPRIVATE_LOG_LEVEL=debug
turbo serve --debug
```

---

*For support, contact enterprise@turboprivate.ai*
