"""
GramAI - Chat Router
Supports Online mode (Gemini API) and Offline mode (Knowledge Base + Ollama).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

from services.rag_service import rag_service
from services.online_ai import online_ai
from config import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class QueryRequest(BaseModel):
    query: str = Field(..., description="User's question")
    category: Optional[str] = Field(None, description="Filter by category")
    use_llm: bool = Field(True, description="Whether to use LLM")
    language: str = Field(DEFAULT_LANGUAGE, description="Response language")
    mode: str = Field("offline", description="'online' for Gemini AI, 'offline' for knowledge base")
    history: Optional[List[dict]] = Field(None, description="Chat history for online mode context")


class QueryResponse(BaseModel):
    response: str
    sources: List[dict] = []
    query: str
    category: Optional[str] = None
    documents_found: int = 0
    language: str = DEFAULT_LANGUAGE
    mode: str = "offline"


class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    n_results: int = Field(5, ge=1, le=10)


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query in either online or offline mode.
    - Online: Uses Google Gemini API for any question
    - Offline: Uses local knowledge base + optional Ollama LLM
    """
    lang = request.language if request.language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

    try:
        if request.mode == "online":
            # Online mode: Use Gemini API
            response_text = await online_ai.chat(
                query=request.query,
                language=lang,
                history=request.history
            )
            return QueryResponse(
                response=response_text,
                sources=[],
                query=request.query,
                category=request.category,
                documents_found=0,
                language=lang,
                mode="online"
            )
        else:
            # Offline mode: Use RAG pipeline with knowledge base
            result = await rag_service.query(
                user_query=request.query,
                category=request.category,
                use_llm=request.use_llm,
                language=lang
            )
            result["language"] = lang
            result["mode"] = "offline"
            return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")


@router.post("/search")
async def search_knowledge(request: SearchRequest):
    """Search the knowledge base directly."""
    try:
        results = await rag_service.search_knowledge(
            query=request.query,
            category=request.category,
            n_results=request.n_results
        )
        return {"results": results, "query": request.query, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/categories")
async def get_categories():
    return {
        "categories": rag_service.get_categories(),
        "labels": {
            "कृषि": "Agriculture", "शिक्षा": "Education",
            "स्वास्थ्य": "Health", "सरकारी योजना": "Government Schemes"
        }
    }


@router.get("/languages")
async def get_languages():
    return {"languages": SUPPORTED_LANGUAGES, "default": DEFAULT_LANGUAGE}


@router.get("/online-status")
async def get_online_status():
    """Check if online AI (OpenRouter/DeepSeek) is available."""
    configured = online_ai.is_configured()
    available = False
    if configured:
        available = await online_ai.check_availability()
    return {
        "configured": configured,
        "available": available,
        "provider": "DeepSeek v3.2" if configured else "Not configured",
        "hint": "Set OPENROUTER_API_KEY in .env file" if not configured else "Ready"
    }


