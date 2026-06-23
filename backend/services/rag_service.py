"""
GramAI - RAG (Retrieval-Augmented Generation) Service [UPGRADED]
Combines FAISS vector store, BM25 keyword search, Local LLM inference,
conversation summary memory, confidence routing, adaptive context,
intent detection, dynamic query expansion, and online data enhancements.

Upgrade Agents Integrated:
  Agent 1: Advanced Query Expansion (via query_expansion module)
  Agent 2: Hybrid Search (FAISS Semantic + BM25 Keyword, 0.7/0.3 blend)
  Agent 3: Confidence Routing (HIGH ≥ 0.80, MEDIUM ≥ 0.60, LOW < 0.60)
  Agent 4: Adaptive Context Window (3/5/8 docs based on complexity)
  Agent 5: Conversation Summary Memory (topic/crop/disease/scheme/location)
  Agent 7: Offline Weather Intelligence (seasonal + cached)
  Agent 8: Structured Prompt Optimization
"""

import json
import logging
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Set

from services.vector_store import vector_store
from services.llm_service import llm_service
from services.query_expansion import query_expander
from config import SYSTEM_PROMPTS, DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, DATA_DIR

logger = logging.getLogger(__name__)

# ─── Confidence Routing Thresholds (Agent 3) ────────────────────────────────
HIGH_CONFIDENCE = 0.80
MEDIUM_CONFIDENCE = 0.60

# ─── Adaptive Context Doc Counts (Agent 4) ──────────────────────────────────
CONTEXT_DOCS = {"simple": 3, "medium": 5, "complex": 8}

# ─── No-LLM response headers per language ───────────────────────────────────
_KB_HEADERS = {
    "hi": "📖 ज्ञान आधार से जानकारी:",
    "en": "📖 Information from Knowledge Base:",
    "ta": "📖 அறிவுத் தளத்திலிருந்து தகவல்:",
    "te": "📖 నాలెడ్జ్ బేస్ నుండి సమాచారం:",
    "bn": "📖 জ্ঞান ভাণ্ডার থেকে তথ্য:",
    "mr": "📖 ज्ञान आधारातून माहिती:",
    "gu": "📖 જ્ઞાન આધાર માંથી માહિતી:",
    "kn": "📖 ಜ್ಞಾನ ಆಧಾರದಿಂದ ಮಾಹಿತಿ:",
    "ml": "📖 വിജ്ഞാന ശേഖരത്തിൽ നിന്നുള്ള വിവരങ്ങൾ:",
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


# ─── Conversation Summary Memory (Agent 5) ──────────────────────────────────

class ConversationMemory:
    """Extracts and stores structured context from conversation history.
    
    Tracks: topics, crops, diseases, government schemes, locations.
    Uses keyword matching against agriculture dictionaries (no ML overhead).
    """

    # Known topic keywords
    _TOPIC_KEYWORDS = {
        "कृषि": ["खेती", "फसल", "कृषि", "farming", "agriculture", "crop", "किसान", "farmer",
                  "बुवाई", "sowing", "सिंचाई", "irrigation", "उर्वरक", "fertilizer", "खाद"],
        "स्वास्थ्य": ["स्वास्थ्य", "health", "बीमारी", "disease", "इलाज", "treatment",
                       "डॉक्टर", "doctor", "दवा", "medicine", "अस्पताल", "hospital"],
        "शिक्षा": ["शिक्षा", "education", "स्कूल", "school", "पढ़ाई", "study",
                    "छात्रवृत्ति", "scholarship", "परीक्षा", "exam"],
        "सरकारी योजना": ["योजना", "scheme", "सरकारी", "government", "pm-kisan", "आयुष्मान",
                          "pmfby", "मनरेगा", "mgnrega", "सब्सिडी", "subsidy", "पेंशन", "pension"],
        "मौसम": ["मौसम", "weather", "बारिश", "rain", "तापमान", "temperature"],
    }

    # Known crop names (loaded from dictionary at first use)
    _CROP_NAMES: Set[str] = set()
    _DISEASE_NAMES: Set[str] = set()
    _SCHEME_NAMES: Set[str] = set()
    _LOCATION_NAMES: Set[str] = {
        "बिहार", "उत्तर प्रदेश", "मध्य प्रदेश", "राजस्थान", "महाराष्ट्र", "पंजाब",
        "हरियाणा", "गुजरात", "तमिलनाडु", "कर्नाटक", "आंध्र प्रदेश", "तेलंगाना",
        "पश्चिम बंगाल", "ओडिशा", "छत्तीसगढ़", "झारखंड", "असम", "केरल",
        "delhi", "bihar", "uttar pradesh", "madhya pradesh", "rajasthan",
        "maharashtra", "punjab", "haryana", "gujarat", "tamil nadu",
        "karnataka", "andhra pradesh", "telangana", "west bengal",
        "odisha", "chhattisgarh", "jharkhand", "assam", "kerala",
    }
    _dicts_loaded = False

    def __init__(self):
        self.topics: List[str] = []
        self.crops: List[str] = []
        self.diseases: List[str] = []
        self.schemes: List[str] = []
        self.locations: List[str] = []
        self.recent_turns: List[dict] = []

    @classmethod
    def _load_entity_names(cls):
        """Load entity names from agriculture dictionaries (once)."""
        if cls._dicts_loaded:
            return
        try:
            crop_file = DATA_DIR / "crop_dictionary.json"
            if crop_file.exists():
                with open(crop_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for key, entry in data.items():
                    cls._CROP_NAMES.add(key.lower())
                    for en in entry.get("en", []):
                        cls._CROP_NAMES.add(en.lower())
                    for hi in entry.get("hi", []):
                        cls._CROP_NAMES.add(hi.lower())
                    for alias in entry.get("aliases", []):
                        cls._CROP_NAMES.add(alias.lower())

            disease_file = DATA_DIR / "disease_dictionary.json"
            if disease_file.exists():
                with open(disease_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for key, entry in data.items():
                    cls._DISEASE_NAMES.add(key.lower())
                    for en in entry.get("en", []):
                        cls._DISEASE_NAMES.add(en.lower())
                    for hi in entry.get("hi", []):
                        cls._DISEASE_NAMES.add(hi.lower())

            # Scheme names from hardcoded list
            cls._SCHEME_NAMES = {
                "pm-kisan", "pmkisan", "किसान सम्मान निधि", "आयुष्मान", "ayushman",
                "pm-jay", "pmfby", "फसल बीमा", "मनरेगा", "mgnrega", "nrega",
                "pmay", "आवास योजना", "उज्ज्वला", "ujjwala", "जन धन", "jan dhan",
                "pm-sym", "pmksy", "सुकन्या", "sukanya", "किसान क्रेडिट कार्ड", "kcc",
                "सॉयल हेल्थ कार्ड", "soil health card",
            }
        except Exception as e:
            logger.warning(f"Failed to load entity names for memory: {e}")

        cls._dicts_loaded = True

    def update(self, history: Optional[List[dict]]):
        """Extract entities from conversation history."""
        if not history:
            return

        self.__class__._load_entity_names()

        # Store recent turns (last 4)
        self.recent_turns = []
        for turn in history[-4:]:
            text = turn.get("text", "")
            if text and not text.startswith("⚠️"):
                role = "User" if turn.get("role") == "user" else "Assistant"
                self.recent_turns.append({"role": role, "text": text})

        # Extract entities from all history text
        all_text = " ".join(t.get("text", "") for t in history).lower()
        tokens = set(re.findall(r'[\w\u0900-\u097F]+', all_text))

        # Detect topics
        for topic, keywords in self._TOPIC_KEYWORDS.items():
            if any(kw in tokens for kw in keywords):
                if topic not in self.topics:
                    self.topics.append(topic)

        # Detect crops
        for token in tokens:
            if token in self._CROP_NAMES and token not in self.crops:
                self.crops.append(token)

        # Detect diseases
        for token in tokens:
            if token in self._DISEASE_NAMES and token not in self.diseases:
                self.diseases.append(token)

        # Detect schemes (check multi-word too)
        for scheme in self._SCHEME_NAMES:
            if scheme in all_text and scheme not in self.schemes:
                self.schemes.append(scheme)

        # Detect locations
        for loc in self._LOCATION_NAMES:
            if loc.lower() in all_text and loc not in self.locations:
                self.locations.append(loc)

    def get_context_summary(self) -> str:
        """Return structured memory string for prompt injection."""
        parts = []

        if self.topics:
            parts.append(f"Topics discussed: {', '.join(self.topics[:5])}")
        if self.crops:
            parts.append(f"Crops mentioned: {', '.join(self.crops[:5])}")
        if self.diseases:
            parts.append(f"Diseases mentioned: {', '.join(self.diseases[:5])}")
        if self.schemes:
            parts.append(f"Schemes mentioned: {', '.join(self.schemes[:5])}")
        if self.locations:
            parts.append(f"Locations mentioned: {', '.join(self.locations[:5])}")

        # Add recent conversation turns
        if self.recent_turns:
            turn_strs = [f"{t['role']}: {t['text'][:150]}" for t in self.recent_turns[-3:]]
            parts.append("Recent conversation:\n" + "\n".join(turn_strs))

        return "\n".join(parts) if parts else ""


# ─── BM25 Keyword Search (Agent 2) ──────────────────────────────────────────

class BM25Index:
    """Lightweight BM25 index over the vector store documents.
    
    Built lazily on first search call; corpus is tokenized once and cached.
    """

    def __init__(self):
        self._bm25 = None
        self._doc_indices: List[int] = []
        self._built = False

    def _build(self):
        """Build BM25 index from vector store documents."""
        if self._built:
            return

        if not vector_store._initialized:
            vector_store.initialize()

        if not vector_store.documents:
            self._built = True
            return

        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            logger.warning("rank_bm25 not installed. BM25 search disabled. Install with: pip install rank-bm25")
            self._built = True
            return

        # Tokenize all documents
        corpus = []
        self._doc_indices = []
        for i, doc in enumerate(vector_store.documents):
            text = doc.get("full_text", f"{doc.get('title', '')} {doc.get('content', '')}")
            tokens = re.findall(r'[\w\u0900-\u097F]+', text.lower())
            corpus.append(tokens)
            self._doc_indices.append(i)

        if corpus:
            self._bm25 = BM25Okapi(corpus)
            logger.info(f"BM25 index built over {len(corpus)} documents.")

        self._built = True

    def search(self, query: str, n_results: int = 5, category: Optional[str] = None) -> List[Dict]:
        """Search using BM25 keyword scoring."""
        self._build()

        if self._bm25 is None or not self._doc_indices:
            return []

        query_tokens = re.findall(r'[\w\u0900-\u097F]+', query.lower())
        if not query_tokens:
            return []

        scores = self._bm25.get_scores(query_tokens)

        # Pair scores with document indices and sort descending
        scored = sorted(
            zip(scores, self._doc_indices),
            key=lambda x: x[0],
            reverse=True
        )

        results = []
        for score, idx in scored:
            if score <= 0:
                continue
            if idx >= len(vector_store.documents):
                continue

            doc = vector_store.documents[idx]

            # Category filter
            if category and doc.get("category") != category:
                continue

            results.append({
                "content": f"{doc['title']}. {doc['content']}",
                "metadata": {
                    "category": doc.get("category", ""),
                    "subcategory": doc.get("subcategory", ""),
                    "title": doc.get("title", ""),
                },
                "relevance_score": round(float(score), 3),
                "doc_id": doc.get("id", f"doc_{idx}"),
            })

            if len(results) >= n_results:
                break

        return results


# ─── Main RAG Service ────────────────────────────────────────────────────────

class RAGService:
    """Intelligent RAG pipeline with hybrid search, confidence routing,
    adaptive context, conversation memory, and structured prompts."""

    def __init__(self):
        self.bm25_index = BM25Index()

    # ── Agent 4: Complexity Assessment ───────────────────────────────────

    def _assess_complexity(self, query: str) -> str:
        """Classify query complexity: 'simple', 'medium', 'complex'.
        
        Heuristics:
          - Token count
          - Question word count
          - Multi-topic indicators (aur/and/ya/or)
          - Comparison words
          - Technical terms
        """
        tokens = re.findall(r'[\w\u0900-\u097F]+', query.lower())
        n_tokens = len(tokens)

        # Question indicators
        question_words = {"क्या", "कैसे", "कब", "क्यों", "कहाँ", "कितना", "कौन",
                          "what", "how", "when", "why", "where", "which", "who"}
        q_count = sum(1 for t in tokens if t in question_words)

        # Multi-topic / comparison indicators
        multi_indicators = {"और", "तथा", "एवं", "या", "अथवा", "बनाम",
                            "and", "or", "versus", "vs", "compare", "difference",
                            "तुलना", "अंतर", "फर्क"}
        multi_count = sum(1 for t in tokens if t in multi_indicators)

        # Technical / complex indicators
        tech_terms = {"विश्लेषण", "analysis", "प्रक्रिया", "process", "तकनीक",
                      "technique", "रणनीति", "strategy", "विस्तार", "detail",
                      "समझाइए", "explain", "बताइए", "describe"}
        tech_count = sum(1 for t in tokens if t in tech_terms)

        # Score-based classification
        complexity_score = 0
        if n_tokens > 15:
            complexity_score += 2
        elif n_tokens > 8:
            complexity_score += 1

        complexity_score += q_count
        complexity_score += multi_count * 2
        complexity_score += tech_count

        if complexity_score >= 4:
            return "complex"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "simple"

    # ── Intent Detection ─────────────────────────────────────────────────

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

    # ── Agent 2: Hybrid Search ───────────────────────────────────────────

    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """Min-max normalize scores to [0, 1]."""
        if not scores:
            return []
        min_s = min(scores)
        max_s = max(scores)
        if max_s == min_s:
            return [1.0] * len(scores)
        return [(s - min_s) / (max_s - min_s) for s in scores]

    def _hybrid_search(
        self, query: str, expanded_query: str, n_results: int,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Combine FAISS semantic search + BM25 keyword search.
        
        Final score = 0.7 * semantic_score + 0.3 * keyword_score
        Returns deduplicated, re-ranked results.
        """
        # Fetch more candidates than needed for better merging
        fetch_k = n_results * 3

        # FAISS semantic search (using expanded query)
        semantic_results = vector_store.search(
            query=expanded_query,
            n_results=fetch_k,
            category=category
        )

        # BM25 keyword search (using expanded query)
        keyword_results = self.bm25_index.search(
            query=expanded_query,
            n_results=fetch_k,
            category=category
        )

        # Build unified document map keyed by title (as stable ID)
        doc_map: Dict[str, Dict] = {}

        # Index semantic results
        sem_scores = [r.get("relevance_score", 0) for r in semantic_results]
        norm_sem = self._normalize_scores(sem_scores)

        for i, doc in enumerate(semantic_results):
            key = doc["metadata"].get("title", f"sem_{i}")
            doc_map[key] = {
                "content": doc["content"],
                "metadata": doc["metadata"],
                "semantic_score": norm_sem[i] if i < len(norm_sem) else 0,
                "keyword_score": 0.0,
            }

        # Index keyword results
        kw_scores = [r.get("relevance_score", 0) for r in keyword_results]
        norm_kw = self._normalize_scores(kw_scores)

        for i, doc in enumerate(keyword_results):
            key = doc["metadata"].get("title", f"kw_{i}")
            if key in doc_map:
                doc_map[key]["keyword_score"] = norm_kw[i] if i < len(norm_kw) else 0
            else:
                doc_map[key] = {
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "semantic_score": 0.0,
                    "keyword_score": norm_kw[i] if i < len(norm_kw) else 0,
                }

        # Compute final blended score
        ranked = []
        for key, doc in doc_map.items():
            final_score = 0.7 * doc["semantic_score"] + 0.3 * doc["keyword_score"]
            ranked.append({
                "content": doc["content"],
                "metadata": doc["metadata"],
                "relevance_score": round(final_score, 3),
            })

        # Sort by final score descending
        ranked.sort(key=lambda x: x["relevance_score"], reverse=True)

        return ranked[:n_results]

    # ── Agent 7: Offline Weather Intelligence ────────────────────────────

    def _get_weather_intelligence(self) -> str:
        """Retrieve weather context combining cache + seasonal prediction.
        
        Priority:
          1. Actual cached weather data (from weather router)
          2. Seasonal prediction based on current month
        """
        weather_parts = []

        # Try cached weather first
        cache_file = DATA_DIR / "weather_cache.json"
        cached_data = None
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                last = data.get("last_result", {})
                if last:
                    cached_data = last
                    weather_parts.append(
                        f"Temperature: {last.get('temperature', 'N/A')}°C\n"
                        f"Condition: {last.get('condition', 'N/A')}\n"
                        f"City: {last.get('city', 'N/A')}"
                    )
                    # Add daily forecast summary if available
                    daily = last.get("daily_forecast", [])
                    if daily and len(daily) >= 3:
                        forecast_str = "; ".join(
                            f"{d.get('date', 'N/A')}: {d.get('min_temp', '')}–{d.get('max_temp', '')}°C {d.get('condition', '')}"
                            for d in daily[:3]
                        )
                        weather_parts.append(f"3-day forecast: {forecast_str}")
            except Exception:
                pass

        # Seasonal prediction (always available, even offline with no cache)
        now = datetime.now()
        month = now.month
        if 6 <= month <= 9:
            season = "Monsoon (खरीफ / Kharif season)"
            advisory = "मानसून सीजन - धान, मक्का, सोयाबीन की बुवाई का समय। बाढ़ और जल जमाव से सावधान रहें।"
            temp_range = "28-35°C"
        elif month in (10, 11):
            season = "Post-monsoon (रबी बुवाई / Rabi sowing)"
            advisory = "रबी सीजन शुरू - गेहूं, चना, सरसों की बुवाई का अच्छा समय।"
            temp_range = "18-30°C"
        elif month in (12, 1, 2):
            season = "Winter (रबी / Rabi season)"
            advisory = "सर्दी का मौसम - गेहूं और सब्जियों की देखभाल करें। पाला से फसल बचाएं।"
            temp_range = "5-22°C"
        elif month in (3, 4, 5):
            season = "Summer (गर्मी / Zaid season)"
            advisory = "गर्मी का मौसम - सिंचाई का विशेष ध्यान रखें। जायद फसलें (खीरा, तरबूज, मूंग) उगा सकते हैं।"
            temp_range = "30-45°C"
        else:
            season = "Transition"
            advisory = "मौसम परिवर्तन की अवधि।"
            temp_range = "25-35°C"

        weather_parts.append(f"Season: {season}")
        if not cached_data:
            weather_parts.append(f"Expected temperature range: {temp_range}")
        weather_parts.append(f"Agricultural advisory: {advisory}")

        return "\n".join(weather_parts)

    # ── Agent 8: Structured Context Builder ──────────────────────────────

    def _build_structured_context(
        self, documents: List[Dict], weather_context: Optional[str],
        memory: ConversationMemory, confidence_level: str
    ) -> str:
        """Build structured context string for LLM prompt.
        
        Replaces raw document concatenation with categorized, labeled context
        that helps the LLM generate more accurate answers.
        """
        parts = []

        # Reference documents
        if documents:
            parts.append("📋 Reference Documents:")
            for i, doc in enumerate(documents, 1):
                meta = doc.get("metadata", {})
                score = doc.get("relevance_score", 0)

                # Confidence label
                if score >= HIGH_CONFIDENCE:
                    conf_label = "HIGH ✅"
                elif score >= MEDIUM_CONFIDENCE:
                    conf_label = "MEDIUM ⚠️"
                else:
                    conf_label = "LOW ❌"

                parts.append(
                    f"\n[Document {i}]\n"
                    f"Category: {meta.get('category', 'N/A')}\n"
                    f"Title: {meta.get('title', 'N/A')}\n"
                    f"Confidence: {score:.2f} ({conf_label})\n"
                    f"Content: {doc['content']}"
                )

        # Weather context
        if weather_context:
            parts.append(f"\n🌤️ Weather Context:\n{weather_context}")

        # Conversation memory
        memory_summary = memory.get_context_summary()
        if memory_summary:
            parts.append(f"\n💬 Conversation Memory:\n{memory_summary}")

        # Confidence routing hint for LLM
        if confidence_level == "high":
            parts.append(
                "\n📌 Instruction: High-confidence match found. "
                "Answer directly using the reference documents above. Be concise and precise."
            )
        elif confidence_level == "low":
            parts.append(
                "\n📌 Instruction: Low-confidence match. The reference documents may not fully address the query. "
                "Use your general knowledge along with any relevant context above. "
                "If unsure, clearly indicate uncertainty."
            )

        return "\n".join(parts)

    # ── Main Query Pipeline ──────────────────────────────────────────────

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
        2. Assess query complexity → adaptive doc count (Agent 4).
        3. Expand query dynamically (Agent 1).
        4. Hybrid search: FAISS semantic + BM25 keyword (Agent 2).
        5. Compute confidence → routing decision (Agent 3).
        6. Build conversation summary memory (Agent 5).
        7. Inject weather intelligence if relevant (Agent 7).
        8. Build structured prompt context (Agent 8).
        9. Generate response via confidence-routed LLM path (Agent 3).
        """
        intent = self._detect_intent(user_query)

        # Handle greetings immediately for instant responsiveness
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

        # Step 1: Assess complexity → adaptive doc count (Agent 4)
        complexity = self._assess_complexity(user_query)
        adaptive_n = CONTEXT_DOCS.get(complexity, 3)
        # Use the larger of requested n_results and adaptive count
        effective_n = max(n_results, adaptive_n)
        logger.info(f"Query complexity: {complexity} → fetching {effective_n} docs")

        # Step 2: Dynamic Query Expansion (Agent 1)
        expanded_query = query_expander.expand(user_query)
        logger.info(f"Expanded query: '{user_query}' → {len(expanded_query.split())} tokens")

        # Step 3: Hybrid Search (Agent 2)
        documents = self._hybrid_search(
            query=user_query,
            expanded_query=expanded_query,
            n_results=effective_n,
            category=category
        )

        # Step 4: Compute Confidence Level (Agent 3)
        if documents:
            avg_confidence = sum(d.get("relevance_score", 0) for d in documents) / len(documents)
            top_confidence = documents[0].get("relevance_score", 0) if documents else 0
        else:
            avg_confidence = 0
            top_confidence = 0

        if top_confidence >= HIGH_CONFIDENCE:
            confidence_level = "high"
        elif top_confidence >= MEDIUM_CONFIDENCE:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        logger.info(f"Confidence: top={top_confidence:.3f}, avg={avg_confidence:.3f} → {confidence_level}")

        # Step 5: Conversation Summary Memory (Agent 5)
        memory = ConversationMemory()
        memory.update(history)

        # Step 6: Weather Intelligence (Agent 7) — inject if weather-related
        weather_context = None
        if intent["type"] == "weather":
            weather_context = self._get_weather_intelligence()

        # Step 7: Build Structured Context (Agent 8)
        context = self._build_structured_context(
            documents=documents,
            weather_context=weather_context,
            memory=memory,
            confidence_level=confidence_level
        )

        # Build sources list
        sources = []
        for doc in documents:
            sources.append({
                "title": doc["metadata"].get("title", ""),
                "category": doc["metadata"].get("category", ""),
                "subcategory": doc["metadata"].get("subcategory", ""),
                "relevance": round(doc.get("relevance_score", 0), 3)
            })

        # Step 8: Construct system prompt with memory
        system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS[DEFAULT_LANGUAGE])
        memory_summary = memory.get_context_summary()
        if memory_summary:
            system_prompt += f"\n\nConversation Memory (Previous context):\n{memory_summary}"

        # Step 9: Response Generation with Confidence Routing (Agent 3)
        if use_llm:
            if confidence_level == "high":
                # HIGH: Use local LLM for fast, direct answer
                logger.info("Confidence routing: HIGH → local LLM (fast path)")
                response_text = await llm_service.generate_local(
                    prompt=user_query,
                    context=context,
                    system_prompt=system_prompt,
                    temperature=0.3
                )
            elif confidence_level == "medium":
                # MEDIUM: Use standard LLM pipeline (online or local)
                logger.info("Confidence routing: MEDIUM → standard LLM pipeline")
                response_text = await llm_service.generate(
                    prompt=user_query,
                    context=context,
                    system_prompt=system_prompt
                )
            else:
                # LOW: Enhanced prompt + standard pipeline (tries online first)
                logger.info("Confidence routing: LOW → enhanced prompt + standard LLM pipeline")
                enhanced_prompt = (
                    f"The following question may not have a direct match in the knowledge base. "
                    f"Please use your general knowledge along with any available context to provide "
                    f"the best possible answer.\n\n"
                    f"Question: {user_query}"
                )
                response_text = await llm_service.generate(
                    prompt=enhanced_prompt,
                    context=context,
                    system_prompt=system_prompt
                )
        else:
            # Return raw knowledge base results without LLM
            header = _KB_HEADERS.get(language, _KB_HEADERS[DEFAULT_LANGUAGE])
            if documents:
                response_text = f"{header}\n\n"
                for i, doc in enumerate(documents, 1):
                    title = sources[i-1]["title"] if i-1 < len(sources) else ""
                    content = doc["content"]
                    response_text += f"**{i}. {title}**\n{content}\n\n"
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
        expanded = query_expander.expand(query)
        documents = self._hybrid_search(
            query=query,
            expanded_query=expanded,
            n_results=n_results,
            category=category
        )
        return documents

    def get_categories(self) -> List[str]:
        """Get available knowledge categories."""
        return vector_store.get_categories()


# Singleton instance
rag_service = RAGService()
