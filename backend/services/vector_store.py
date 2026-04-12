"""
GramAI - Vector Store Service (Improved)
JSON-based search with bilingual English-Hindi support.
"""

import json
import math
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional
from collections import Counter

from config import DATA_DIR

logger = logging.getLogger(__name__)

# English-Hindi category and keyword mapping for cross-language search
EN_HI_MAP = {
    # Category mappings
    'agriculture': 'कृषि', 'farming': 'कृषि', 'crop': 'कृषि', 'crops': 'कृषि',
    'health': 'स्वास्थ्य', 'medical': 'स्वास्थ्य', 'medicine': 'स्वास्थ्य',
    'doctor': 'स्वास्थ्य', 'disease': 'स्वास्थ्य', 'fever': 'बुखार',
    'education': 'शिक्षा', 'school': 'शिक्षा', 'college': 'शिक्षा',
    'scholarship': 'छात्रवृत्ति', 'study': 'शिक्षा',
    'scheme': 'सरकारी योजना', 'schemes': 'सरकारी योजना', 'government': 'सरकारी',
    'pension': 'पेंशन', 'insurance': 'बीमा',
    # Agriculture terms
    'wheat': 'गेहूं', 'rice': 'धान', 'paddy': 'धान', 'potato': 'आलू',
    'fertilizer': 'उर्वरक', 'irrigation': 'सिंचाई', 'water': 'पानी',
    'pest': 'कीट', 'organic': 'जैविक', 'soil': 'मिट्टी',
    'seed': 'बीज', 'sowing': 'बुवाई', 'harvest': 'कटाई',
    'cultivate': 'खेती', 'cultivation': 'खेती', 'farm': 'खेती',
    'grow': 'उगाना', 'growing': 'खेती', 'plant': 'पौधा', 'planting': 'बुवाई',
    'vegetable': 'सब्जी', 'fruit': 'फल', 'dairy': 'दूध', 'cow': 'गाय',
    'buffalo': 'भैंस', 'animal': 'पशुपालन', 'cattle': 'पशुपालन',
    'drip': 'ड्रिप', 'sprinkler': 'स्प्रिंकलर', 'urea': 'यूरिया',
    'compost': 'खाद', 'manure': 'खाद', 'neem': 'नीम',
    # Health terms
    'malaria': 'मलेरिया', 'dengue': 'डेंगू', 'diarrhea': 'दस्त',
    'cold': 'सर्दी', 'cough': 'खांसी', 'pregnancy': 'गर्भावस्था',
    'vaccine': 'टीकाकरण', 'vaccination': 'टीकाकरण', 'hospital': 'अस्पताल',
    'treatment': 'इलाज', 'cure': 'इलाज', 'remedy': 'उपचार',
    # Education terms
    'exam': 'परीक्षा', 'admission': 'प्रवेश', 'degree': 'डिग्री',
    'engineering': 'इंजीनियरिंग',
    # How/what/why helpers
    'how': '', 'what': '', 'is': '', 'the': '', 'to': '', 'do': '',
    'can': '', 'about': '', 'tell': '', 'explain': '', 'me': '',
    'please': '', 'give': '', 'information': '', 'info': '',
}

# English query to category hint
EN_CATEGORY_HINTS = {
    'crop': 'कृषि', 'crops': 'कृषि', 'farming': 'कृषि', 'agriculture': 'कृषि',
    'grow': 'कृषि', 'growing': 'कृषि', 'plant': 'कृषि', 'seed': 'कृषि',
    'wheat': 'कृषि', 'rice': 'कृषि', 'potato': 'कृषि', 'vegetable': 'कृषि',
    'soil': 'कृषि', 'irrigation': 'कृषि', 'fertilizer': 'कृषि', 'organic': 'कृषि',
    'pest': 'कृषि', 'cow': 'कृषि', 'dairy': 'कृषि', 'cattle': 'कृषि',
    'health': 'स्वास्थ्य', 'fever': 'स्वास्थ्य', 'disease': 'स्वास्थ्य',
    'medicine': 'स्वास्थ्य', 'doctor': 'स्वास्थ्य', 'hospital': 'स्वास्थ्य',
    'treatment': 'स्वास्थ्य', 'malaria': 'स्वास्थ्य', 'dengue': 'स्वास्थ्य',
    'vaccine': 'स्वास्थ्य', 'pregnancy': 'स्वास्थ्य',
    'education': 'शिक्षा', 'school': 'शिक्षा', 'college': 'शिक्षा',
    'scholarship': 'शिक्षा', 'exam': 'शिक्षा', 'admission': 'शिक्षा',
    'scheme': 'सरकारी योजना', 'government': 'सरकारी योजना', 'pension': 'सरकारी योजना',
    'insurance': 'सरकारी योजना', 'pm': 'सरकारी योजना', 'kisan': 'सरकारी योजना',
    'ayushman': 'सरकारी योजना',
}


class VectorStoreService:
    """Bilingual keyword search using TF-IDF similarity."""

    def __init__(self):
        self.documents: List[Dict] = []
        self.doc_tokens: List[List[str]] = []
        self.idf: Dict[str, float] = {}
        self._initialized = False

    def initialize(self):
        if self._initialized:
            return
        logger.info("Initializing lightweight vector store...")
        self._load_all_data()
        self._build_index()
        self._initialized = True
        logger.info(f"Vector store ready with {len(self.documents)} documents.")

    def _load_all_data(self):
        data_files = {
            "agriculture.json": "कृषि",
            "education.json": "शिक्षा",
            "health.json": "स्वास्थ्य",
            "schemes.json": "सरकारी योजना"
        }
        for filename, category in data_files.items():
            filepath = DATA_DIR / filename
            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for item in data:
                        self.documents.append({
                            "id": item["id"],
                            "category": item.get("category", category),
                            "subcategory": item.get("subcategory", ""),
                            "title": item.get("title", ""),
                            "content": item.get("content", ""),
                            "keywords": item.get("keywords", []),
                            "full_text": f"{item.get('title', '')} {item.get('content', '')} {' '.join(item.get('keywords', []))}"
                        })
                    logger.info(f"Loaded {len(data)} documents from {filename}")
                except Exception as e:
                    logger.error(f"Error loading {filepath}: {e}")

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        tokens = re.findall(r'[\w\u0900-\u097F]+', text)
        return [t for t in tokens if len(t) > 1]

    def _translate_query(self, tokens: List[str]) -> List[str]:
        """Expand English tokens to include Hindi equivalents."""
        expanded = list(tokens)
        for token in tokens:
            hindi = EN_HI_MAP.get(token)
            if hindi:
                expanded.extend(self._tokenize(hindi))
        return expanded

    def _detect_category_hint(self, tokens: List[str]) -> Optional[str]:
        """Detect likely category from English tokens."""
        cat_votes = Counter()
        for token in tokens:
            cat = EN_CATEGORY_HINTS.get(token)
            if cat:
                cat_votes[cat] += 1
        if cat_votes:
            return cat_votes.most_common(1)[0][0]
        return None

    def _build_index(self):
        self.doc_tokens = [self._tokenize(doc["full_text"]) for doc in self.documents]
        n_docs = len(self.documents)
        doc_freq = Counter()
        for tokens in self.doc_tokens:
            for token in set(tokens):
                doc_freq[token] += 1
        self.idf = {
            token: math.log((n_docs + 1) / (freq + 1)) + 1
            for token, freq in doc_freq.items()
        }

    def _score(self, query_tokens: List[str], doc_idx: int) -> float:
        if not query_tokens or doc_idx >= len(self.doc_tokens):
            return 0.0
        doc_tokens = self.doc_tokens[doc_idx]
        doc = self.documents[doc_idx]
        doc_counter = Counter(doc_tokens)
        score = 0.0

        for token in query_tokens:
            tf = doc_counter.get(token, 0) / max(len(doc_tokens), 1)
            idf = self.idf.get(token, 1.0)
            score += tf * idf

            # Bonus for keyword match
            lower_keywords = [k.lower() for k in doc["keywords"]]
            if token in lower_keywords:
                score += 3.0

            # Bonus for title match
            if token in self._tokenize(doc["title"]):
                score += 2.0

        return score

    def search(self, query: str, n_results: int = 3, category: Optional[str] = None) -> List[Dict]:
        if not self._initialized:
            self.initialize()

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # Expand English tokens to Hindi equivalents
        expanded_tokens = self._translate_query(query_tokens)
        # Remove empty strings
        expanded_tokens = [t for t in expanded_tokens if t]

        # Auto-detect category from English query if not specified
        effective_category = category
        if not effective_category:
            hint = self._detect_category_hint(query_tokens)
            if hint:
                effective_category = hint

        # Score all documents
        scored = []
        for i, doc in enumerate(self.documents):
            if effective_category and doc["category"] != effective_category:
                continue

            score = self._score(expanded_tokens, i)
            if score > 0:
                scored.append((i, score))

        # If category filtering returned nothing, try without category filter
        if not scored and effective_category:
            for i, doc in enumerate(self.documents):
                score = self._score(expanded_tokens, i)
                if score > 0:
                    scored.append((i, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        max_score = scored[0][1] if scored else 1.0
        for idx, score in scored[:n_results]:
            doc = self.documents[idx]
            results.append({
                "content": f"{doc['title']}. {doc['content']}",
                "metadata": {
                    "category": doc["category"],
                    "subcategory": doc["subcategory"],
                    "title": doc["title"],
                },
                "relevance_score": round(min(score / max_score, 1.0), 3)
            })
        return results

    def count(self) -> int:
        return len(self.documents)

    def get_categories(self) -> List[str]:
        return ["कृषि", "शिक्षा", "स्वास्थ्य", "सरकारी योजना"]


vector_store = VectorStoreService()
