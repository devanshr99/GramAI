#!/bin/bash
# ============================================================
# GramAI - Complete Mobile Deployment Script
# Deploys as PWA + optional Android APK via Capacitor
# ============================================================

set -e

echo "=========================================="
echo "  GramAI Mobile Deployment"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# ---- Step 1: Setup Python Environment ----
echo -e "\n${GREEN}[1/5] Setting up Python environment...${NC}"
cd "$PROJECT_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r backend/requirements.txt --quiet

# ---- Step 2: Download AI Models (if needed) ----
echo -e "\n${GREEN}[2/5] Checking AI models...${NC}"

# Check Ollama
if command -v ollama &> /dev/null; then
    echo "Ollama found. Pulling model..."
    ollama pull mistral 2>/dev/null || echo -e "${YELLOW}Could not pull model. Will use knowledge base only.${NC}"
else
    echo -e "${YELLOW}Ollama not installed. Install from https://ollama.ai for AI generation.${NC}"
fi

# ---- Step 3: Configure for Mobile (WiFi Hotspot) ----
echo -e "\n${GREEN}[3/5] Configuring network access...${NC}"

# Get local IP
LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "0.0.0.0")
echo "Server will be accessible at: http://${LOCAL_IP}:8000"

# Create .env if not exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cat > "$PROJECT_DIR/.env" << EOF
HOST=0.0.0.0
PORT=8000
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
EOF
    echo "Created .env configuration file"
fi

# ---- Step 4: Create systemd service (for auto-start) ----
echo -e "\n${GREEN}[4/5] Setting up auto-start service...${NC}"

if [ -d "/etc/systemd/system" ]; then
    sudo tee /etc/systemd/system/gramai.service > /dev/null << EOF
[Unit]
Description=GramAI Offline AI Assistant
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python backend/main.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable gramai.service
    sudo systemctl start gramai.service
    echo -e "${GREEN}GramAI service installed and started!${NC}"
else
    echo -e "${YELLOW}systemd not available. Start manually with: python backend/main.py${NC}"
fi

# ---- Step 5: Summary ----
echo -e "\n${GREEN}[5/5] Deployment Complete!${NC}"
echo "=========================================="
echo -e "  PWA URL:  ${GREEN}http://${LOCAL_IP}:8000${NC}"
echo "  "
echo "  On any phone connected to the same WiFi:"
echo "  1. Open Chrome/Safari"
echo "  2. Go to http://${LOCAL_IP}:8000"
echo "  3. Tap 'Install' or 'Add to Home Screen'"
echo "  4. The app will work offline!"
echo "=========================================="
