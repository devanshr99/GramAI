#!/bin/bash
# ================================================
# GramAI - Linux / Raspberry Pi Setup Script
# Offline AI Assistant for Rural India
# ================================================
# Usage: chmod +x setup.sh && sudo ./setup.sh
# ================================================

set -e

echo "=============================================="
echo "🌾 GramAI - Setup Script"
echo "🌾 ग्रामAI - सेटअप स्क्रिप्ट"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Please run as root (sudo ./setup.sh)${NC}"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "\n${GREEN}📁 Project directory: $PROJECT_DIR${NC}"

# ---- Step 1: System Updates ----
echo -e "\n${GREEN}[1/7] Updating system...${NC}"
apt-get update -y
apt-get install -y python3 python3-pip python3-venv \
    espeak libespeak-dev ffmpeg curl wget git

# ---- Step 2: Install Ollama ----
echo -e "\n${GREEN}[2/7] Installing Ollama...${NC}"
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
    echo -e "${GREEN}✅ Ollama installed${NC}"
else
    echo -e "${YELLOW}Ollama already installed${NC}"
fi

# ---- Step 3: Pull LLM Model ----
echo -e "\n${GREEN}[3/7] Pulling Mistral model (this may take a while)...${NC}"
ollama pull mistral

# ---- Step 4: Setup Python Environment ----
echo -e "\n${GREEN}[4/7] Setting up Python environment...${NC}"
cd "$PROJECT_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# ---- Step 5: Download Vosk Hindi Model ----
echo -e "\n${GREEN}[5/7] Downloading Vosk Hindi model...${NC}"
VOSK_DIR="$PROJECT_DIR/backend/models"
mkdir -p "$VOSK_DIR"

if [ ! -d "$VOSK_DIR/vosk-model-hi" ]; then
    cd "$VOSK_DIR"
    wget -q --show-progress https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip -O vosk-hi.zip
    unzip -q vosk-hi.zip
    mv vosk-model-small-hi-0.22 vosk-model-hi
    rm vosk-hi.zip
    echo -e "${GREEN}✅ Vosk Hindi model downloaded${NC}"
else
    echo -e "${YELLOW}Vosk Hindi model already exists${NC}"
fi

# ---- Step 6: Create Service File ----
echo -e "\n${GREEN}[6/7] Creating systemd service...${NC}"
cat > /etc/systemd/system/gramai.service << EOF
[Unit]
Description=GramAI - Offline AI Assistant
After=network.target ollama.service

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$PROJECT_DIR/backend
Environment=PATH=$PROJECT_DIR/venv/bin:/usr/bin
ExecStart=$PROJECT_DIR/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gramai.service

# ---- Step 7: Start Services ----
echo -e "\n${GREEN}[7/7] Starting services...${NC}"
systemctl start ollama 2>/dev/null || true
sleep 3
systemctl start gramai

echo -e "\n${GREEN}=============================================="
echo "✅ GramAI सेटअप पूरा हुआ!"
echo "✅ GramAI Setup Complete!"
echo ""
echo "🌐 Open in browser: http://localhost:8000"
echo "📱 Mobile: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "📋 Commands:"
echo "  Start:   sudo systemctl start gramai"
echo "  Stop:    sudo systemctl stop gramai"
echo "  Status:  sudo systemctl status gramai"
echo "  Logs:    sudo journalctl -u gramai -f"
echo "==============================================${NC}"
