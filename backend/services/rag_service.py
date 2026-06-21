"""
GramAI - RAG (Retrieval-Augmented Generation) Service
Combines FAISS vector store, Local LLM inference, conversation memory,
intent detection, query expansion, and online data enhancements.
"""

import logging
import re
from typing import Optional, List, Dict

from services.vector_store import vector_store
from services.llm_service import llm_service
from config import SYSTEM_PROMPTS, DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

# No-LLM response headers per language
_KB_HEADERS = {
    "hi": "📖 ज्ञान आधार से जानकारी:",
    "en": "📖 Information from Knowledge Base:",
    "ta": "📖 அறிவுத் தளத்திலிருந்து தகவல்:",
    "te": "📖 నాలెడ్జ్ బేస్ నుండి సమాచారం:",
    "bn": "📖 জ্ঞান ভাণ্ডার থেকে তথ্য:",
    "mr": "📖 ज्ञान आधारातून माहिती:",
    "gu": "📖 જ્ઞાન આધાર માંથી માહિતી:",
    "kn": "📖 ಜ್ಞಾನ ಆಧಾರದಿಂದ ಮಾಹಿತಿ:",
    "ml": "📖 വിജ്ഞาน ശേഖരത്തിൽ നിന്നുള്ള വിവരങ്ങൾ:",
    "pa": "📖 ਗਿਆਨ ਅਧਾਰ ਤੋਂ ਜਾਣਕਾਰੀ:",
}

_NO_INFO = {
    "hi": "इस विषय पर जानकारी उपलब्ध नहीं है।",
    "en": "No information available on this topic.",
    "ta": "இந்த தலைப்பில் தகவல் கிடைக்கவில்லை.",
    "te": "ఈ అంశంపై సమాచారం అందుబాటులో లేదు.",
    "bn": "এই বিষয়ে তথ্য পাওয়া যায়নি।",
    "mr": "या विषयावर माहिती उपलब्ध नाही.",
    "gu": "આ વિષય પર माहिती उपलब्ध નથી.",
    "kn": "ಈ ವಿಷಯದ ಬಗ್ಗೆ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ.",
    "ml": "ഈ വിഷയത്തിൽ വിവരങ്ങൾ ലഭ്യമല്ല.",
    "pa": "ਇਸ ਵਿਸ਼ੇ 'ਤੇ ਜਾਣਕਾਰੀ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।",
}


class RAGService:
    """Intelligent RAG pipeline supporting query expansion, intent detection, and conversation memory."""

    def __init__(self):
        self.max_context_docs = 3

    def _expand_query(self, query: str) -> str:
        """Expand user query with synonyms and translation terms to improve retrieval recall."""
        from services.vector_store import EN_HI_MAP
        tokens = re.findall(r'[\w\u0900-\u097F]+', query.lower())
        expanded = list(tokens)

        # Append translated equivalents
        for token in tokens:
            hi = EN_HI_MAP.get(token)
            if hi:
                expanded.extend(re.findall(r'[\w\u0900-\u097F]+', hi.lower()))

        # Simple synonym expansion
        synonyms = {
            "बुखार": ["ताप", "ज्वर", "fever", "illness", "बीमारी", "स्वास्थ्य"],
            "गेहूं": ["कनक", "गेंहू", "wheat", "crop", "फसल", "कृषि"],
            "इलाज": ["उपचार", "दवा", "चिकित्सा", "treatment", "डॉक्टर"],
            "खेती": ["कृषि", "फसल", "farming", "crop", "किसान"],
            "धान": ["चावल", "धान", "rice", "paddy"],
            "योजना": ["सरकारी योजना", "स्कीम", "scheme", "सर्करी"],
            "बुवाई": ["रोपण", "बोना", "sowing", "बीज"],
            "रोग": ["बीमारी", "कीट", "pest", "disease", "स्वास्थ्य"],
        }
        for token in tokens:
            if token in synonyms:
                expanded.extend(synonyms[token])

        return " ".join(set(expanded))

    def _detect_intent(self, query: str) -> dict:
        """Detect intent types: greeting, weather/real-time info, or general RAG inquiry."""
        q = query.lower()
        
        # 1. Check if greeting
        greetings = ["hi", "hello", "namaste", "pranam", "hey", "नमस्ते", "प्रणाम", "हेलो", "राम राम"]
        if any(g in q for g in greetings) and len(q.split()) <= 2:
            return {"type": "greeting"}

        # 2. Check if weather/realtime request
        weather_keywords = ["weather", "mausam", "rain", "precipitation", "temperature", "तापमान", "मौसम", "बारिश", "हवा"]
        if any(wkw in q for wkw in weather_keywords):
            return {"type": "weather"}

        return {"type": "info"}

    def _get_cached_weather(self) -> str:
        """Retrieve latest weather cache block to enhance prompts with current local context."""
        import json
        from pathlib import Path
        cache_file = Path("data/weather_cache.json")
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                last = data.get("last_result", {})
                if last:
                    return (
                        f"Current weather context (Delhi NCR/User location):\n"
                        f"Temperature: {last.get('temperature', 28.0)}°C\n"
                        f"Condition: {last.get('condition', 'Clear')}\n"
                        f"Forecast: {last.get('prediction', 'Normal temperature trends.')}\n"
                    )
            except Exception:
                pass
        return "Weather context: 28°C, Clear sky (Delhi NCR)."

    async def query(
        self,
        user_query: str,
        category: Optional[str] = None,
        use_llm: bool = True,
        n_results: int = 3,
        language: str = DEFAULT_LANGUAGE,
        history: Optional[List[dict]] = None
    ) -> Dict:
        """
        Process a query through the upgraded RAG pipeline.
        
        1. Detect intent (greeting, weather, general info).
        2. Expand query tokens for search query accuracy.
        3. Retrieve relevant documents using FAISS semantic search.
        4. Apply sliding window conversation memory.
        5. Optionally inject real-time weather metadata into context.
        6. Generate text using either local GGUF or online APIs.
        """
        intent = self._detect_intent(user_query)

        # Handle greetings immediately for immediate responsiveness
        if intent["type"] == "greeting":
            welcome_map = {
                "hi": "नमस्ते! मैं GramAI हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?",
                "en": "Hello! I am GramAI. How can I help you today?",
                "hg": "Namaste! Main GramAI hoon. Aaj main aapki kaise help kar sakta hoon?"
            }
            return {
                "response": welcome_map.get(language, welcome_map["hi"]),
                "sources": [],
                "query": user_query,
                "category": category,
                "documents_found": 0
            }

        # Step 1: Query Expansion & Retrieval
        expanded_query = self._expand_query(user_query)
        documents = vector_store.search(
            query=expanded_query,
            n_results=n_results,
            category=category
        )

        # Build context
        context_parts = []
        sources = []
        for doc in documents:
            context_parts.append(doc["content"])
            sources.append({
                "title": doc["metadata"].get("title", ""),
                "category": doc["metadata"].get("category", ""),
                "subcategory": doc["metadata"].get("subcategory", ""),
                "relevance": round(doc.get("relevance_score", 0), 3)
            })

        context = "\n\n---\n\n".join(context_parts)

        # Step 2: Inject real-time context if weather-related
        if intent["type"] == "weather":
            weather_data = self._get_cached_weather()
            context = f"{weather_data}\n\n---\n\n{context}"

        # Step 3: Parse Conversation Memory
        memory_str = ""
        if history:
            memory_turns = []
            for turn in history[-4:]:
                role = "User" if turn.get("role") == "user" else "Assistant"
                text = turn.get("text", "")
                if text and not text.startswith("⚠️"):
                    memory_turns.append(f"{role}: {text}")
            if memory_turns:
                memory_str = "\n".join(memory_turns)

        # Step 4: Construct custom system prompt with memory
        system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS[DEFAULT_LANGUAGE])
        if memory_str:
            system_prompt += f"\n\nConversation Memory (Previous turns):\n{memory_str}"

        # Step 5: Response Generation
        if use_llm:
            response_text = await llm_service.generate(
                prompt=user_query,
                context=context,
                system_prompt=system_prompt
            )
        else:
            # Return raw knowledge base results without LLM
            header = _KB_HEADERS.get(language, _KB_HEADERS[DEFAULT_LANGUAGE])
            if context_parts:
                response_text = f"{header}\n\n"
                for i, part in enumerate(context_parts, 1):
                    title = sources[i-1]["title"] if i-1 < len(sources) else ""
                    response_text += f"**{i}. {title}**\n{part}\n\n"
            else:
                response_text = _NO_INFO.get(language, _NO_INFO[DEFAULT_LANGUAGE])

        return {
            "response": response_text,
            "sources": sources,
            "query": user_query,
            "category": category,
            "documents_found": len(documents)
        }

    async def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """Search knowledge base without LLM generation."""
        expanded = self._expand_query(query)
        documents = vector_store.search(
            query=expanded,
            n_results=n_results,
            category=category
        )
        return documents

    def get_categories(self) -> List[str]:
        """Get available knowledge categories."""
        return vector_store.get_categories()


# Singleton instance
rag_service = RAGService()
