#!/usr/bin/env bash
set -euo pipefail

# TurboPrivate AI — 30-Second Installer
# Detects hardware and spins up the optimal Docker Compose profile.

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  TurboPrivate AI — 30-Second Installer   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is required. Install Docker and try again.${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose V2 is required.${NC}"
    exit 1
fi

echo -e "${YELLOW}✓ Docker detected${NC}"

# Detect Hardware
OS_TYPE=$(uname -s)
ARCH_TYPE=$(uname -m)
COMPOSE_FILE="docker-compose.cpu.yml"

echo -e "${YELLOW}🔍 Detecting hardware...${NC}"

if [ "$OS_TYPE" = "Darwin" ]; then
    if [ "$ARCH_TYPE" = "arm64" ]; then
        echo -e "${GREEN}🍎 Apple Silicon detected — optimizing for CPU/Metal${NC}"
        COMPOSE_FILE="docker-compose.mac.yml"
    else
        echo -e "${YELLOW}⚠️ Intel Mac detected — using CPU mode${NC}"
        COMPOSE_FILE="docker-compose.cpu.yml"
    fi
elif command -v nvidia-smi &> /dev/null; then
    GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    echo -e "${GREEN}🟢 NVIDIA GPU detected: $GPU${NC}"
    COMPOSE_FILE="docker-compose.gpu.yml"
else
    echo -e "${YELLOW}⚠️ No GPU detected — using CPU mode${NC}"
    COMPOSE_FILE="docker-compose.cpu.yml"
fi

# Download compose file if not present
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${YELLOW}📦 Downloading $COMPOSE_FILE...${NC}"
    curl -sSL "https://raw.githubusercontent.com/Kubenew/turboprivate-ai/main/$COMPOSE_FILE" -o "$COMPOSE_FILE"
fi

# Create .env if not present
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env template...${NC}"
    cat > .env << 'EOF'
TURBOPRIVATE_ENV=production
TURBOPRIVATE_LOG_LEVEL=info
DB_PASSWORD=change_me_in_production
GRAFANA_PASSWORD=admin
EOF
fi

# Start stack
echo -e "${GREEN} Starting TurboPrivate AI...${NC}"
docker compose -f "$COMPOSE_FILE" up -d

echo
echo -e "${GREEN}✓ Installation complete!${NC}"
echo
echo -e "${YELLOW} API Endpoint: http://localhost:8000/v1${NC}"
echo -e "${YELLOW}📊 Dashboard: http://localhost:5173${NC}"
echo -e "${YELLOW}📈 Grafana: http://localhost:5174 (admin/admin)${NC}"
echo
echo -e "${GREEN}Test it:${NC}"
echo '  curl http://localhost:8000/v1/chat/completions \\'
echo '    -H "Content-Type: application/json" \\'
echo '    -d '\''{"model": "llama-3.1-8b", "messages": [{"role": "user", "content": "Hello!"}]}'\'''
echo
echo -e "${GREEN}Docs: https://github.com/Kubenew/turboprivate-ai${NC}"
