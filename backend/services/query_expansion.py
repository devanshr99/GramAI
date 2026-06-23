"""
GramAI - Advanced Query Expansion Engine
Dynamically expands user queries using:
  - Hindi ↔ English translation mapping
  - Agricultural terminology from crop/disease/fertilizer dictionaries
  - Government scheme aliases
  - WordNet synonyms (optional, graceful fallback)
"""

import json
import logging
import re
from pathlib import Path
from typing import Set

from config import DATA_DIR

logger = logging.getLogger(__name__)


class QueryExpander:
    """Dynamic query expansion with agricultural intelligence."""

    def __init__(self):
        self._loaded = False
        # Flat lookup: token → set of expansions
        self._expansion_map: dict[str, Set[str]] = {}
        # Hindi ↔ English bidirectional map
        self._hi_en_map: dict[str, list[str]] = {}
        # WordNet availability
        self._wordnet_available = False

    def _load(self):
        """Lazily load all dictionaries and build expansion map."""
        if self._loaded:
            return
        logger.info("Loading query expansion dictionaries...")

        # --- Load agriculture dictionaries ---
        dict_files = {
            "crop_dictionary.json": "crop",
            "disease_dictionary.json": "disease",
            "fertilizer_dictionary.json": "fertilizer",
        }
        for filename, dict_type in dict_files.items():
            filepath = DATA_DIR / filename
            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._index_dictionary(data, dict_type)
                    logger.info(f"Loaded {len(data)} entries from {filename}")
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")

        # --- Build Hindi ↔ English translation map ---
        self._build_translation_map()

        # --- Build government scheme aliases ---
        self._build_scheme_aliases()

        # --- Check WordNet availability ---
        try:
            from nltk.corpus import wordnet
            # Quick check that data is available
            wordnet.synsets("rice")
            self._wordnet_available = True
            logger.info("WordNet available for English synonym expansion.")
        except Exception:
            self._wordnet_available = False
            logger.info("WordNet not available; using built-in synonyms only.")

        self._loaded = True
        logger.info(f"Query expansion ready: {len(self._expansion_map)} tokens indexed.")

    def _index_dictionary(self, data: dict, dict_type: str):
        """Index a dictionary into the flat expansion map."""
        for key, entry in data.items():
            all_terms: Set[str] = set()

            # Primary key (Hindi term)
            all_terms.add(key.lower())

            # English names
            for en in entry.get("en", []):
                all_terms.add(en.lower())

            # Hindi names
            for hi in entry.get("hi", []):
                all_terms.add(hi.lower())

            # Aliases
            for alias in entry.get("aliases", []):
                all_terms.add(alias.lower())

            # Affected crops (for diseases)
            for crop in entry.get("affects", []):
                all_terms.add(crop.lower())

            # Register every term as pointing to all other terms
            for term in list(all_terms):
                # Tokenize multi-word terms
                tokens = re.findall(r'[\w\u0900-\u097F]+', term)
                for token in tokens:
                    if token not in self._expansion_map:
                        self._expansion_map[token] = set()
                    self._expansion_map[token].update(all_terms)

    def _build_translation_map(self):
        """Comprehensive Hindi ↔ English bidirectional translation map."""
        translations = {
            # Agriculture
            "खेती": ["farming", "agriculture", "cultivation"],
            "कृषि": ["agriculture", "farming"],
            "फसल": ["crop", "harvest"],
            "किसान": ["farmer", "kisan"],
            "बीज": ["seed", "seeds"],
            "बुवाई": ["sowing", "planting", "seeding"],
            "रोपण": ["transplanting", "planting"],
            "सिंचाई": ["irrigation", "watering"],
            "उर्वरक": ["fertilizer"],
            "खाद": ["manure", "fertilizer", "compost"],
            "कीट": ["pest", "insect"],
            "कीटनाशक": ["pesticide", "insecticide"],
            "फफूंदी": ["fungus", "fungal"],
            "खरपतवार": ["weed", "weeds"],
            "मिट्टी": ["soil", "earth"],
            "जमीन": ["land", "ground"],
            "पानी": ["water"],
            "बारिश": ["rain", "rainfall"],
            "सूखा": ["drought"],
            "बाढ़": ["flood"],
            "उपज": ["yield", "produce", "production"],
            "भंडारण": ["storage"],
            "मंडी": ["market", "mandi"],
            "दाम": ["price", "rate"],
            # Seasons
            "खरीफ": ["kharif", "monsoon season"],
            "रबी": ["rabi", "winter season"],
            "जायद": ["zaid", "summer season"],
            "मानसून": ["monsoon"],
            "गर्मी": ["summer", "heat"],
            "सर्दी": ["winter", "cold"],
            # Health
            "इलाज": ["treatment", "cure", "remedy"],
            "उपचार": ["treatment", "therapy"],
            "दवा": ["medicine", "drug"],
            "चिकित्सा": ["medical", "treatment"],
            "डॉक्टर": ["doctor", "physician"],
            "अस्पताल": ["hospital"],
            "स्वास्थ्य": ["health"],
            "बीमारी": ["disease", "illness", "sickness"],
            "रोग": ["disease"],
            "लक्षण": ["symptoms"],
            "टीकाकरण": ["vaccination", "immunization"],
            "गर्भवती": ["pregnant", "pregnancy"],
            "पोषण": ["nutrition"],
            # Government
            "योजना": ["scheme", "plan", "program"],
            "सरकारी": ["government", "govt"],
            "सरकार": ["government"],
            "सब्सिडी": ["subsidy"],
            "अनुदान": ["grant", "subsidy"],
            "लाभार्थी": ["beneficiary"],
            "पात्रता": ["eligibility"],
            "आवेदन": ["application", "apply"],
            "पेंशन": ["pension"],
            "बीमा": ["insurance"],
            # Education
            "शिक्षा": ["education"],
            "विद्यालय": ["school"],
            "छात्रवृत्ति": ["scholarship"],
            "परीक्षा": ["exam", "examination"],
            # Animal husbandry
            "पशुपालन": ["animal husbandry", "livestock"],
            "गाय": ["cow"],
            "भैंस": ["buffalo"],
            "बकरी": ["goat"],
            "मुर्गी": ["poultry", "chicken"],
            "दूध": ["milk"],
            "चारा": ["fodder", "feed"],
        }

        # Build bidirectional map and index into expansion map
        for hi_term, en_terms in translations.items():
            all_terms = {hi_term.lower()} | {e.lower() for e in en_terms}

            # Index each token
            for term in list(all_terms):
                tokens = re.findall(r'[\w\u0900-\u097F]+', term)
                for token in tokens:
                    if token not in self._expansion_map:
                        self._expansion_map[token] = set()
                    self._expansion_map[token].update(all_terms)

            # Also store in hi_en_map for direct lookup
            self._hi_en_map[hi_term] = en_terms

    def _build_scheme_aliases(self):
        """Government scheme alias mapping."""
        schemes = {
            "pm-kisan": ["किसान सम्मान निधि", "kisan samman nidhi", "pm kisan", "पीएम किसान"],
            "pmkisan": ["pm-kisan", "किसान सम्मान निधि", "kisan samman nidhi"],
            "आयुष्मान": ["ayushman", "pm-jay", "pmjay", "आयुष्मान भारत", "ayushman bharat"],
            "pmfby": ["फसल बीमा", "crop insurance", "fasal bima", "प्रधानमंत्री फसल बीमा"],
            "मनरेगा": ["mgnrega", "nrega", "mnrega", "रोजगार गारंटी", "employment guarantee"],
            "pmay": ["आवास योजना", "housing scheme", "प्रधानमंत्री आवास", "aawas yojana"],
            "उज्ज्वला": ["ujjwala", "gas connection", "lpg", "गैस कनेक्शन"],
            "जन धन": ["jan dhan", "bank account", "बैंक खाता", "जनधन"],
            "pm-sym": ["श्रम योगी मानधन", "pension", "पेंशन", "मजदूर पेंशन"],
            "pmksy": ["कृषि सिंचाई योजना", "irrigation scheme", "सिंचाई योजना"],
            "सॉयल हेल्थ कार्ड": ["soil health card", "मिट्टी जांच", "soil testing"],
            "सुकन्या": ["sukanya", "बेटी बचाओ", "girl scheme", "sukanya samriddhi"],
            "किसान क्रेडिट कार्ड": ["kisan credit card", "kcc", "केसीसी"],
        }

        for key, aliases in schemes.items():
            all_terms = {key.lower()} | {a.lower() for a in aliases}
            for term in list(all_terms):
                tokens = re.findall(r'[\w\u0900-\u097F]+', term)
                for token in tokens:
                    if token not in self._expansion_map:
                        self._expansion_map[token] = set()
                    self._expansion_map[token].update(all_terms)

    def _get_wordnet_synonyms(self, word: str) -> Set[str]:
        """Get English synonyms from WordNet (if available)."""
        if not self._wordnet_available:
            return set()
        try:
            from nltk.corpus import wordnet
            synonyms = set()
            for syn in wordnet.synsets(word)[:3]:  # Limit to top 3 synsets
                for lemma in syn.lemmas()[:5]:  # Limit lemmas
                    name = lemma.name().replace("_", " ").lower()
                    if name != word.lower():
                        synonyms.add(name)
            return synonyms
        except Exception:
            return set()

    def expand(self, query: str) -> str:
        """
        Expand a query with all available synonym/alias sources.
        
        Pipeline:
        1. Tokenize query
        2. For each token: dictionary expansion (crops, diseases, fertilizers, schemes, translations)
        3. For English tokens: optional WordNet synonyms
        4. Deduplicate and return
        """
        self._load()

        tokens = re.findall(r'[\w\u0900-\u097F]+', query.lower())
        expanded: Set[str] = set(tokens)

        for token in tokens:
            # Dictionary-based expansion (covers all agri/scheme/translation maps)
            dict_expansions = self._expansion_map.get(token, set())
            if dict_expansions:
                # Add individual tokens from multi-word expansions
                for exp in dict_expansions:
                    exp_tokens = re.findall(r'[\w\u0900-\u097F]+', exp)
                    expanded.update(exp_tokens)

            # WordNet expansion for English tokens (ASCII check)
            if token.isascii() and len(token) > 2:
                wn_syns = self._get_wordnet_synonyms(token)
                for syn in wn_syns:
                    syn_tokens = re.findall(r'[\w]+', syn)
                    expanded.update(syn_tokens)

        return " ".join(expanded)


# Singleton instance
query_expander = QueryExpander()
