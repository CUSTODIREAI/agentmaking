#!/bin/bash
# SuperBender Installer - One-liner install for any Linux system
# Usage: curl -sL https://raw.githubusercontent.com/CUSTODIREAI/agentmaking/main/install.sh | bash

set -e

echo "=============================================="
echo "  SUPERBENDER INSTALLER"
echo "  AI Memory Agent + Changelog Tracker"
echo "=============================================="
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required"
    echo "Install with: sudo apt install python3 python3-pip"
    exit 1
fi

# Install directory
INSTALL_DIR="$HOME/agent"

echo "[1/5] Creating install directory..."
mkdir -p "$INSTALL_DIR"

echo "[2/5] Downloading Bender..."
cd "$INSTALL_DIR"

# Download core files
curl -sL https://raw.githubusercontent.com/CUSTODIREAI/agentmaking/main/memory_agent.py -o memory_agent.py
curl -sL https://raw.githubusercontent.com/CUSTODIREAI/agentmaking/main/bender.py -o bender.py
chmod +x bender.py

# Download hooks
mkdir -p hooks
curl -sL https://raw.githubusercontent.com/CUSTODIREAI/agentmaking/main/hooks/pre-commit-strict -o hooks/pre-commit-strict
curl -sL https://raw.githubusercontent.com/CUSTODIREAI/agentmaking/main/hooks/install-strict.sh -o hooks/install-strict.sh
chmod +x hooks/*

echo "[3/5] Installing Python dependencies..."
pip3 install --user sentence-transformers numpy 2>/dev/null || {
    echo "WARNING: Could not install sentence-transformers"
    echo "Semantic search will be disabled. Install manually:"
    echo "  pip3 install sentence-transformers numpy"
}

echo "[4/5] Setting up CLI..."
# Create symlink or copy to /usr/local/bin
if [ -w /usr/local/bin ]; then
    ln -sf "$INSTALL_DIR/bender.py" /usr/local/bin/bender
else
    echo "Need sudo to install CLI globally..."
    sudo ln -sf "$INSTALL_DIR/bender.py" /usr/local/bin/bender
fi

echo "[5/5] Initializing memory database..."
mkdir -p "$INSTALL_DIR/memories"
python3 -c "
import sys
sys.path.insert(0, '$INSTALL_DIR')
from memory_agent import MemoryAgent
agent = MemoryAgent('$INSTALL_DIR/memories')
agent.remember('Bender installed on $(hostname) at $(date)', 'system')
print('Memory initialized!')
"

echo ""
echo "=============================================="
echo "  BENDER INSTALLED SUCCESSFULLY!"
echo "=============================================="
echo ""
echo "Location: $INSTALL_DIR"
echo ""
echo "USAGE:"
echo "  bender \"question\"           - Search knowledge"
echo "  bender learn \"fact\" [cat]   - Store knowledge"
echo "  bender log \"change\"         - Log changelog entry"
echo "  bender changelog            - View recent changes"
echo "  bender stats                - Show statistics"
echo "  bender help                 - Full help"
echo ""
echo "PROTECT A REPO:"
echo "  ~/agent/hooks/install-strict.sh /path/to/repo"
echo ""
echo "=============================================="
