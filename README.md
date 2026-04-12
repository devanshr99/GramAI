# GramAI - ग्रामAI

## 🌾 Offline AI Assistant for Rural India | ग्रामीण भारत के लिए ऑफ़लाइन AI सहायक

GramAI is a fully offline AI-powered assistant designed for rural India. It provides voice-based interaction in Hindi, offering knowledge about agriculture, health, education, and government schemes — all without requiring internet connectivity.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User's Mobile Phone                │
│                  (WiFi Connection)                    │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │    Local WiFi Network  │
         │   (Raspberry Pi AP)    │
         └───────────┬───────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                GramAI Server                         │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Frontend  │  │ FastAPI  │  │ Ollama LLM       │  │
│  │ HTML/JS   │──│ Backend  │──│ (Mistral/Llama3) │  │
│  └──────────┘  └────┬─────┘  └──────────────────┘  │
│                     │                                │
│  ┌──────────┐  ┌────▼─────┐  ┌──────────────────┐  │
│  │ Vosk STT │  │ RAG      │  │ ChromaDB         │  │
│  │ (Hindi)  │  │ Pipeline │──│ Vector Store     │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                                      │
│  ┌──────────┐  Knowledge Base:                      │
│  │ pyttsx3  │  🌾 Agriculture  📚 Education         │
│  │ TTS      │  🏥 Health       🏛️ Govt. Schemes     │
│  └──────────┘                                       │
└─────────────────────────────────────────────────────┘
```

## ✨ Features

- 🎤 **Voice Input** — Speak in Hindi, get answers
- 🔊 **Voice Output** — Listen to responses
- 🌾 **Agriculture** — Crop advice, fertilizers, irrigation
- 🏥 **Health** — First aid, vaccination, nutrition
- 📚 **Education** — Scholarships, skills, digital literacy
- 🏛️ **Government Schemes** — PM-KISAN, Ayushman Bharat, MGNREGA
- 📱 **Mobile-Friendly** — Works on any phone's browser
- 🔌 **Fully Offline** — No internet needed after setup
- 🤖 **AI-Powered** — Uses local LLM via Ollama
- 📡 **WiFi Hotspot** — Creates local network for village access

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Ollama** — [Download here](https://ollama.ai)
- **8GB+ RAM** recommended

### 1. Clone & Setup

```bash
# Clone the repository
git clone <your-repo-url> GramAI
cd GramAI

# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate
# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Setup Ollama

```bash
# Install Ollama (Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull mistral
# OR for smaller devices:
ollama pull phi

# Start Ollama server
ollama serve
```

### 3. (Optional) Download Vosk Hindi Model

For voice input support:

```bash
cd backend/models
wget https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip
unzip vosk-model-small-hi-0.22.zip
mv vosk-model-small-hi-0.22 vosk-model-hi
```

### 4. Start GramAI

```bash
cd backend
python main.py
```

Open in browser: **http://localhost:8000** 🎉

---

## 📱 Raspberry Pi Deployment

### Automated Setup

```bash
cd deployment
sudo chmod +x setup.sh hotspot-setup.sh
sudo ./setup.sh          # Install everything
sudo ./hotspot-setup.sh  # Create WiFi hotspot
```

After setup, villagers can:
1. Connect to **"GramAI-WiFi"** network (password: `gramai1234`)
2. Open browser → **http://192.168.4.1:8000**
3. Start asking questions! 🎤

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Device | Raspberry Pi 4 (4GB) | RPi 4 (8GB) / Mini PC |
| Storage | 16GB SD Card | 64GB SD Card |
| Power | 5V 3A | 5V 3A USB-C |

---

## 🐳 Docker Deployment

```bash
cd deployment
docker-compose up -d
```

> **Note:** Ollama must be running on the host machine. The Docker container connects to it via `host.docker.internal`.

---

## 📁 Project Structure

```
GRAMAI/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py             # Configuration
│   ├── routers/              # API endpoints
│   │   ├── chat.py           # Chat & RAG queries
│   │   ├── voice.py          # STT/TTS endpoints
│   │   └── health.py         # Health checks
│   ├── services/             # Core services
│   │   ├── llm_service.py    # Ollama integration
│   │   ├── rag_service.py    # RAG pipeline
│   │   ├── stt_service.py    # Speech-to-Text
│   │   ├── tts_service.py    # Text-to-Speech
│   │   └── vector_store.py   # ChromaDB
│   └── data/                 # Knowledge base (Hindi)
│       ├── agriculture.json
│       ├── education.json
│       ├── health.json
│       └── schemes.json
├── frontend/
│   ├── index.html            # Mobile-first UI
│   ├── css/style.css         # Premium dark theme
│   └── js/app.js             # Chat & voice logic
├── deployment/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── setup.sh              # Linux/RPi setup
│   ├── setup.bat             # Windows setup
│   └── hotspot-setup.sh      # WiFi AP config
├── tests/
│   ├── test_chat.py
│   ├── test_voice.py
│   └── test_rag.py
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat/query` | Send a query (RAG + LLM) |
| `POST` | `/api/chat/search` | Search knowledge base |
| `GET` | `/api/chat/categories` | List categories |
| `POST` | `/api/voice/transcribe` | Upload audio for STT |
| `POST` | `/api/voice/speak` | Generate TTS audio |
| `GET` | `/api/voice/status` | Voice service status |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/status` | Detailed system status |

### Example Query

```bash
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "गेहूं की खेती कैसे करें?", "category": "कृषि"}'
```

---

## 🧪 Testing

```bash
pip install pytest
cd tests
pytest -v
```

---

## 🌐 Demo Usage

1. **Text Query**: Type "PM-KISAN योजना क्या है?" → Get detailed answer
2. **Voice Query**: Click 🎤 → Speak in Hindi → Auto-transcribed & answered
3. **Category Filter**: Tap a category card to filter by topic
4. **Quick Actions**: Tap preset questions for instant answers
5. **Listen**: Click 🔊 on any response to hear it read aloud

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and customize:

```bash
# LLM Model (choose based on hardware)
OLLAMA_MODEL=mistral       # 7B, good quality, needs 8GB RAM
# OLLAMA_MODEL=phi          # 2.7B, lighter, needs 4GB RAM
# OLLAMA_MODEL=llama3       # 8B, best quality, needs 8GB RAM

# Server
HOST=0.0.0.0
PORT=8000
```

---

## 📋 Knowledge Base

| Category | Items | Topics |
|----------|-------|--------|
| 🌾 कृषि (Agriculture) | 10 | Crops, fertilizers, irrigation, pests, organic farming |
| 📚 शिक्षा (Education) | 7 | Schools, scholarships, skills, digital literacy |
| 🏥 स्वास्थ्य (Health) | 8 | First aid, vaccination, nutrition, schemes |
| 🏛️ सरकारी योजना (Schemes) | 10 | PM-KISAN, Ayushman, PMAY, MGNREGA, Jan Dhan |

**Total: 35+ knowledge articles** covering essential rural needs.

---

## 🤝 Contributing

To add new knowledge:
1. Add entries to the appropriate JSON file in `backend/data/`
2. Follow the existing format (id, category, title, content, keywords)
3. Restart the server — data auto-loads into vector store

---

## 📄 License

MIT License — Free to use for rural development and social impact projects.

---

## 🙏 Acknowledgments

- **Ollama** — Local LLM inference
- **ChromaDB** — Vector storage
- **Vosk** — Offline speech recognition
- **FastAPI** — High-performance Python API

---

> **🌾 Built with ❤️ for the farmers, students, and families of rural India.**
> **ग्रामीण भारत के किसानों, छात्रों और परिवारों के लिए ❤️ से बनाया गया।**
