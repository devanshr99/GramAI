"""
GramAI - RAG (Retrieval-Augmented Generation) Service
Combines vector search with LLM generation for accurate responses.
Supports multi-language response generation.
"""

import logging
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
    "gu": "આ વિષય પર માહિતી ઉપલબ્ધ નથી.",
    "kn": "ಈ ವಿಷಯದ ಬಗ್ಗೆ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ.",
    "ml": "ഈ വിഷയത്തിൽ വിവരങ്ങൾ ലഭ്യമല്ല.",
    "pa": "ਇਸ ਵਿਸ਼ੇ 'ਤੇ ਜਾਣਕਾਰੀ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।",
}


class RAGService:
    """Retrieval-Augmented Generation pipeline with multi-language support."""

    def __init__(self):
        self.max_context_docs = 3

    async def query(
        self,
        user_query: str,
        category: Optional[str] = None,
        use_llm: bool = True,
        n_results: int = 3,
        language: str = DEFAULT_LANGUAGE
    ) -> Dict:
        """
        Process a query through the RAG pipeline.

        1. Search vector store for relevant documents
        2. Build context from retrieved documents
        3. Generate response using LLM with context (in requested language)
        """
        # Step 1: Retrieve relevant documents
        documents = vector_store.search(
            query=user_query,
            n_results=n_results,
            category=category
        )

        # Build context from retrieved documents
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

        # Get language-specific system prompt
        system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS[DEFAULT_LANGUAGE])

        # Step 2: Generate response
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
        documents = vector_store.search(
            query=query,
            n_results=n_results,
            category=category
        )
        return documents

    def get_categories(self) -> List[str]:
        """Get available knowledge categories."""
        return vector_store.get_categories()


# Singleton instance
rag_service = RAGService()
