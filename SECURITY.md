# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

We take the security of TurboPrivate AI seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do NOT report security vulnerabilities through public GitHub issues.**

### How to Report

1. **Email**: Send a detailed report to `security@turboprivate.ai`
2. **Subject**: `[SECURITY] Brief description of the issue`
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce (PoC if possible)
   - Potential impact
   - Suggested fix (optional)

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 5 business days
- **Fix Timeline**: Depends on severity (Critical: 7 days, High: 14 days, Medium: 30 days)
- **Disclosure**: Coordinated disclosure after fix is available

## Threat Model

### Assets Protected
- Model weights and inference data
- Customer prompts and responses
- RAG document corpus and embeddings
- API keys and authentication tokens
- Audit logs and compliance records

### Attack Vectors
- **Prompt Injection**: Mitigated by Mythos Safe pre-flight gate
- **Data Exfiltration**: Mitigated by network isolation + output filtering
- **Model Poisoning**: Mitigated by weight verification + signed artifacts
- **Supply Chain**: Mitigated by pinned dependencies + SBOM generation
- **Privilege Escalation**: Mitigated by RBAC + least-privilege defaults

## Hardening Recommendations

### Network
- Run behind reverse proxy with TLS 1.3
- Use mTLS for internal service communication
- Restrict API access to trusted IPs/networks
- Enable rate limiting (default: 100 req/min per API key)

### Container/K8s
- Run as non-root user (`USER 1000`)
- Read-only root filesystem where possible
- Drop all capabilities except `NET_BIND_SERVICE`
- Set resource limits (CPU/memory)
- Scan images with Trivy/Grype before deployment

### Secrets
- Never commit secrets to git
- Use Kubernetes Secrets or HashiCorp Vault
- Rotate API keys regularly
- Enable audit logging for secret access

### Data
- Encrypt data at rest (AES-256)
- Use TLS 1.3 for all transit
- Enable PII detection and masking
- Regular backup encryption (age encryption)

## Known Limitations

- **Multi-modal**: Vision/audio support is experimental
- **Scale-to-zero**: GPU warm-up takes 30-60s
- **Model Training**: Not supported (inference only)
- **Air-gapped**: Requires manual model weight transfer

## Security Features

| Feature | Status | Description |
|---------|--------|-------------|
| Mythos Safe Gate | ✅ Active | 7 verifiers (injection, PII, toxicity, etc.) |
| RBAC | ✅ Active | Role-based access control |
| Audit Trail | ✅ Active | JSONL immutable logs |
| Rate Limiting | ✅ Active | Token bucket algorithm |
| mTLS | ✅ Active | Mutual TLS for service mesh |
| SBOM | ✅ Active | Generated in CI |
| Image Scanning | ✅ Active | Trivy in CI pipeline |
| OIDC/SAML | 🚧 Planned | Enterprise SSO integration |
| OPA/Policy |  Planned | Kubernetes policy engine |

## Compliance

TurboPrivate AI is designed to help organizations meet:
- **GDPR**: Data residency, right to erasure, audit trails
- **HIPAA**: BAA-ready, encryption, access controls
- **SOC 2**: Audit logging, access management, change management
- **PCI-DSS**: Network segmentation, encryption, logging
- **ISO 27001**: Information security management

See [docs/COMPLIANCE.md](docs/COMPLIANCE.md) for detailed readiness checklists.

## SBOM

Software Bill of Materials is generated automatically in CI and available:
- **Runtime**: `dist/sbom-runtime.json`
- **Dev**: `dist/sbom-dev.json`

Generated using `cyclonedx-bom` and `pip-compile`.

## Contact

- **Security Email**: security@turboprivate.ai
- **PGP Key**: Available on request
- **Bug Bounty**: Contact for details

---

*Last updated: 2026-05-16*
