#!/usr/bin/env bash
set -euo pipefail

echo "=== TurboPrivate AI Smoke Test ==="

echo "1. Health check..."
curl -sf http://localhost:8000/health | grep -q '"status":"ok"' || { echo "FAIL"; exit 1; }

echo "2. Readiness check..."
curl -sf http://localhost:8000/ready | grep -q '"status":"ready"' || { echo "FAIL"; exit 1; }

echo "3. List models..."
curl -sf http://localhost:8000/api/v1/models | grep -q '"models":' || { echo "FAIL"; exit 1; }

echo "4. Safety status..."
curl -sf http://localhost:8000/api/v1/safety/status | grep -q '"pre_flight":' || { echo "FAIL"; exit 1; }

echo "5. Dashboard metrics..."
curl -sf http://localhost:8000/api/v1/admin/dashboard | grep -q '"requests":' || { echo "FAIL"; exit 1; }

echo "=== All smoke tests passed ==="
