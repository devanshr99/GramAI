# GramAI - ग्रामAI

## 🌾 Offline AI Assistant for Rural India | ग्रामीण भारत के लिए ऑफ़लाइन AI सहायक

GramAI is an intelligent, voice-enabled assistant designed for rural India. It operates fully offline, providing voice and text interaction in Hindi and other regional languages. It delivers accurate guidance on agriculture, health, education, and government schemes.

If internet is available, GramAI optionally enhances its analysis with online real-time data and supports multimodal photo uploads (e.g. upload a leaf picture to analyze a crop disease). If offline, it runs entirely on-device using a local GGUF Large Language Model and a local semantic search engine.

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
│  │ Frontend  │  │ FastAPI  │  │ Local GGUF LLM   │  │
│  │ HTML/JS   │──│ Backend  │──│ (Phi-3 Mini)     │  │
│  └──────────┘  └────┬─────┘  └──────────────────┘  │
│                     │                                │
│  ┌──────────┐  ┌────▼─────┐  ┌──────────────────┐  │
│  │ Vosk STT │  │ RAG      │  │ FAISS Index      │  │
│  │ (Hindi)  │  │ Pipeline │──│ Vector Store     │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                                      │
│  ┌──────────┐  Knowledge Base:                      │
│  │ pyttsx3  │  🌾 Agriculture  📚 Education         │
│  │ TTS      │  🏥 Health       🏛️ Govt. Schemes     │
│  └──────────┘                                       │
└─────────────────────────────────────────────────────┘
```

## ✨ Upgraded Features

- 🎤 **Voice Input** — Speak in Hindi, get transcribed answers instantly.
- 🔊 **Voice Output** — Tap to read any response aloud.
- 📷 **Photo Analysis (Online Mode)** — Upload crop, soil, or object photos to ask questions and get visual analyses (like ChatGPT).
- 🧠 **Intelligent Offline RAG** — Powered by:
  - **Local LLM**: runs `Phi-3 Mini` (GGUF 4-bit) on CPU using `transformers` (no native C++ compilation required).
  - **Vector Database**: Semantic search with `FAISS` and `Sentence-Transformers (all-MiniLM-L6-v2)`.
  - **Query Expansion**: Enriches searches with translation equivalents and synonyms.
  - **Intent Detection**: Classifies requests into greetings, weather queries, or knowledge database lookups.
  - **Conversation Memory**: Feeds previous message history context into prompt generators.
- ⛅ **Real-Time Enhancements** — Blends live weather feeds (Open-Meteo cache) with agricultural knowledge when internet is active.
- 🔌 **Fully Offline** — Requires zero external connections after the initial model cache setup.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10 to 3.14**
- **8GB+ RAM** recommended (for comfortable CPU generation)

### 1. Clone & Setup

```bash
# Clone the repository
git clone <your-repo-url> GramAI
cd GramAI

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Download Vosk Hindi Model

For local voice input (STT) support:

```bash
cd backend/models
# Download small Hindi model
wget https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip
unzip vosk-model-small-hi-0.22.zip
mv vosk-model-small-hi-0.22 vosk-model-hi
```

### 3. Start GramAI

```bash
cd backend
python main.py
```

*On the first run, GramAI will automatically generate vector embeddings for the knowledge base files and download the `Phi-3 Mini GGUF` weights from the Hugging Face Hub, caching them in `backend/models`.*

Open your browser: **http://localhost:8000** 🎉

---

## 📱 Raspberry Pi Deployment

### Automated Setup

```bash
cd deployment
sudo chmod +x setup.sh hotspot-setup.sh
sudo ./setup.sh          # Install all system requirements
sudo ./hotspot-setup.sh  # Configure Pi as local WiFi access point
```

After setup, villagers can:
1. Connect to the **"GramAI-WiFi"** network (password: `gramai1234`).
2. Open browser and type → **http://192.168.4.1:8000**
3. Tap the microphone and start asking questions! 🎤

---

## 📁 Project Structure

```
GRAMAI/
├── backend/
│   ├── main.py              # FastAPI application & startup pipeline
│   ├── config.py            # Local GGUF & embedding configurations
│   ├── routers/             # API endpoints (chat, voice, health, weather)
│   ├── services/            # Core business services
│   │   ├── llm_service.py   # Local Phi-3 GGUF & Online API routing
│   │   ├── rag_service.py   # Upgraded memory, expansion & intent RAG
│   │   ├── stt_service.py   # Speech-to-Text (Vosk)
│   │   ├── tts_service.py   # Text-to-Speech (pyttsx3)
│   │   └── vector_store.py  # FAISS Vector database + semantic embedder
│   └── data/                # Knowledge base documents and FAISS indices
├── frontend/
│   ├── index.html           # SPA entry point
│   ├── src/                 # React & Vite sources
│   │   ├── components/      # ChatArea, InputArea, Weather cards
│   │   ├── i18n/            # Multi-language translation packs
│   │   └── index.css        # Premium glassmorphism styles
│   └── public/              # Assets & offline service worker
├── deployment/              # Pi deployment & Docker configurations
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat/query` | Submit query (base64 image optional, handles local GGUF / RAG / online APIs) |
| `POST` | `/api/chat/search` | Raw FAISS semantic search |
| `GET` | `/api/chat/categories` | Get active document categories |
| `POST` | `/api/voice/transcribe` | Upload voice recording for transcription |
| `POST` | `/api/voice/speak` | Synthesize TTS speech audio |
| `GET` | `/api/chat/online-status` | Report if online AI key is configured |
| `GET` | `/api/health` | Service checks |

---

## ⚙️ Configuration

Create a `.env` file in the `backend/` directory to customize configurations:

```bash
# Online AI key (Optional: triggers Gemini/Claude enhancements and photo uploads)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Local GGUF Settings
LOCAL_LLM_REPO=microsoft/Phi-3-mini-4k-instruct-gguf
LOCAL_LLM_FILE=Phi-3-mini-4k-instruct-q4.gguf

# Server
HOST=0.0.0.0
PORT=8000
```

---

## 📋 Knowledge Base

| Category | Topics Covered |
|----------|----------------|
| 🌾 कृषि (Agriculture) | Crops (wheat/paddy/rice), organic manures, urea, drip irrigation, pest treatments. |
| 📚 शिक्षा (Education) | Schools, scholarships (PM-Scholarship), skill development, vocational courses. |
| 🏥 स्वास्थ्य (Health) | First aid, fever treatment, malaria, dengue, pregnancy guidance, nutrition. |
| 🏛️ सरकारी योजना (Schemes) | PM-KISAN, Ayushman Bharat health card, PMAY, MGNREGA, pension programs. |

---

## 🤝 Contributing

To add new documents:
1. Append JSON objects to the data files in `backend/data/`.
2. Delete the `backend/data/faiss_index` folder.
3. Restart the server. The FAISS database will automatically rebuild the index with the new entries!

---

> **🌾 Built with ❤️ for the farmers, students, and families of rural India.**
> **ग्रामीण भारत के किसानों, छात्रों और परिवारों के लिए ❤️ से बनाया गया।**
