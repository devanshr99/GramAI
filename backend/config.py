"""
GramAI Configuration
Central configuration for all services.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
AUDIO_DIR = BASE_DIR / "audio_cache"

# Ensure directories exist
AUDIO_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

# ChromaDB Configuration
CHROMA_PERSIST_DIR = str(BASE_DIR / "chroma_db")

# Vosk Configuration
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", str(MODELS_DIR / "vosk-model-hi"))

# TTS Configuration
TTS_ENGINE = os.getenv("TTS_ENGINE", "pyttsx3")  # pyttsx3 for offline

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Supported Languages
SUPPORTED_LANGUAGES = {
    "hi": {"name": "हिंदी", "english_name": "Hindi", "tts_code": "hi-IN"},
    "en": {"name": "English", "english_name": "English", "tts_code": "en-IN"},
    "ta": {"name": "தமிழ்", "english_name": "Tamil", "tts_code": "ta-IN"},
    "te": {"name": "తెలుగు", "english_name": "Telugu", "tts_code": "te-IN"},
    "bn": {"name": "বাংলা", "english_name": "Bengali", "tts_code": "bn-IN"},
    "mr": {"name": "मराठी", "english_name": "Marathi", "tts_code": "mr-IN"},
    "gu": {"name": "ગુજરાતી", "english_name": "Gujarati", "tts_code": "gu-IN"},
    "kn": {"name": "ಕನ್ನಡ", "english_name": "Kannada", "tts_code": "kn-IN"},
    "ml": {"name": "മലയാളം", "english_name": "Malayalam", "tts_code": "ml-IN"},
    "pa": {"name": "ਪੰਜਾਬੀ", "english_name": "Punjabi", "tts_code": "pa-IN"},
}

# Default language
DEFAULT_LANGUAGE = "hi"

# System Prompts per language
SYSTEM_PROMPTS = {
    "hi": """आप GramAI हैं - ग्रामीण भारत के लिए एक AI सहायक।
आप हिंदी में जवाब देते हैं। आप कृषि, स्वास्थ्य, शिक्षा और सरकारी योजनाओं के बारे में जानकारी देते हैं।
अपने जवाब सरल और समझने में आसान रखें।""",
    "en": """You are GramAI - an AI assistant for rural India.
Respond in simple English. Provide information about agriculture, health, education, and government schemes.
Keep responses simple, clear, and easy to understand.""",
    "ta": """நீங்கள் GramAI - கிராமப்புற இந்தியாவுக்கான AI உதவியாளர்.
தமிழில் பதிலளிக்கவும். விவசாயம், சுகாதாரம், கல்வி மற்றும் அரசு திட்டங்கள் பற்றிய தகவல்களை வழங்கவும்.
பதில்களை எளிமையாகவும் புரிந்துகொள்ள எளிதாகவும் வைக்கவும்.""",
    "te": """మీరు GramAI - గ్రామీణ భారతదేశం కోసం AI సహాయకుడు.
తెలుగులో సమాధానం ఇవ్వండి. వ్యవసాయం, ఆరోగ్యం, విద్య మరియు ప్రభుత్వ పథకాల గురించి సమాచారం అందించండి.
సమాధానాలను సరళంగా మరియు అర్థమయ్యేలా ఉంచండి.""",
    "bn": """আপনি GramAI - গ্রামীণ ভারতের জন্য একটি AI সহকারী।
বাংলায় উত্তর দিন। কৃষি, স্বাস্থ্য, শিক্ষা এবং সরকারি প্রকল্প সম্পর্কে তথ্য প্রদান করুন।
উত্তরগুলি সহজ এবং বোধগম্য রাখুন।""",
    "mr": """तुम्ही GramAI आहात - ग्रामीण भारतासाठी AI सहाय्यक.
मराठीत उत्तर द्या. शेती, आरोग्य, शिक्षण आणि सरकारी योजनांबद्दल माहिती द्या.
उत्तरे सोपी आणि समजण्यास सोपी ठेवा.""",
    "gu": """તમે GramAI છો - ગ્રામીણ ભારત માટે AI સહાયક.
ગુજરાતીમાં જવાબ આપો. ખેતી, આરોગ્ય, શિક્ષણ અને સરકારી યોજનાઓ વિશે માહિતી આપો.
જવાબો સરળ અને સમજવામાં સરળ રાખો.""",
    "kn": """ನೀವು GramAI - ಗ್ರಾಮೀಣ ಭಾರತಕ್ಕಾಗಿ AI ಸಹಾಯಕ.
ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ. ಕೃಷಿ, ಆರೋಗ್ಯ, ಶಿಕ್ಷಣ ಮತ್ತು ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಬಗ್ಗೆ ಮಾಹಿತಿ ನೀಡಿ.
ಉತ್ತರಗಳನ್ನು ಸರಳ ಮತ್ತು ಅರ್ಥವಾಗುವಂತೆ ಇರಿಸಿ.""",
    "ml": """നിങ്ങള്‍ GramAI ആണ് - ഗ്രാമീണ ഇന്ത്യയ്ക്കുള്ള AI സഹായി.
മലയാളത്തില്‍ ഉത്തരം നല്‍കുക. കൃഷി, ആരോഗ്യം, വിദ്യാഭ്യാസം, സര്‍ക്കാര്‍ പദ്ധതികള്‍ എന്നിവയെക്കുറിച്ച് വിവരങ്ങള്‍ നല്‍കുക.
ഉത്തരങ്ങള്‍ ലളിതവും മനസ്സിലാക്കാന്‍ എളുപ്പവുമാക്കുക.""",
    "pa": """ਤੁਸੀਂ GramAI ਹੋ - ਪੇਂਡੂ ਭਾਰਤ ਲਈ AI ਸਹਾਇਕ.
ਪੰਜਾਬੀ ਵਿੱਚ ਜਵਾਬ ਦਿਓ। ਖੇਤੀਬਾੜੀ, ਸਿਹਤ, ਸਿੱਖਿਆ ਅਤੇ ਸਰਕਾਰੀ ਯੋਜਨਾਵਾਂ ਬਾਰੇ ਜਾਣਕਾਰੀ ਦਿਓ।
ਜਵਾਬ ਸੌਖੇ ਅਤੇ ਸਮਝਣ ਵਿੱਚ ਆਸਾਨ ਰੱਖੋ।""",
}

# Default system prompt (Hindi)
SYSTEM_PROMPT = SYSTEM_PROMPTS[DEFAULT_LANGUAGE]

# Embedding model (small, runs on CPU)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
