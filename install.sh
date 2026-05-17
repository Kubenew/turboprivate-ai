#!/usr/bin/env bash
set -euo pipefail

# TurboPrivate AI — One-Click Installer
# Usage: curl -fsSL https://get.turboprivate.ai | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  TurboPrivate AI — One-Click Installer   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3.11+ is required${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$PYTHON_VERSION 3.11" | awk '{print ($1 >= $2)}') -ne 1 ]]; then
    echo -e "${RED}Error: Python 3.11+ required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${YELLOW}✓ Python $PYTHON_VERSION detected${NC}"

# Check GPU (optional)
if command -v nvidia-smi &> /dev/null; then
    GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    echo -e "${YELLOW}✓ GPU detected: $GPU${NC}"
else
    echo -e "${YELLOW}⚠ No GPU detected — CPU mode will be used${NC}"
fi

# Install
echo
echo -e "${GREEN}Installing TurboPrivate AI...${NC}"
pip install turboprivate-ai[full] --quiet

echo
echo -e "${GREEN}✓ Installation complete!${NC}"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. turbo doctor          # Check system readiness"
echo "  2. turbo deploy --provider bare-metal --gpu auto"
echo "  3. turbo model serve meta-llama/Llama-3.1-8B --quant int4"
echo "  4. turbo chat"
echo
echo -e "${GREEN}Docs: https://github.com/Kubenew/turboprivate-ai${NC}"
