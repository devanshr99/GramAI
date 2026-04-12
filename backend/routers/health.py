"""
GramAI - Health Check Router
System health and status endpoints.
"""

import platform
from fastapi import APIRouter

from services.llm_service import llm_service
from services.stt_service import stt_service
from services.tts_service import tts_service
from services.vector_store import vector_store

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "GramAI",
        "version": "1.0.0"
    }


@router.get("/status")
async def system_status():
    """Comprehensive system status check."""
    # Check LLM
    llm_available = await llm_service.check_availability()

    # Check vector store
    try:
        doc_count = vector_store.count()
        vs_status = doc_count > 0
    except Exception:
        doc_count = 0
        vs_status = False

    # System info
    system_info = {
        "platform": platform.system(),
        "architecture": platform.machine(),
        "python": platform.python_version(),
    }

    # Try to get memory info
    try:
        import psutil
        mem = psutil.virtual_memory()
        system_info["memory_total_gb"] = round(mem.total / (1024**3), 1)
        system_info["memory_available_gb"] = round(mem.available / (1024**3), 1)
        system_info["memory_percent"] = mem.percent
        system_info["cpu_count"] = psutil.cpu_count()
    except ImportError:
        system_info["memory_info"] = "psutil not installed"

    return {
        "status": "running",
        "services": {
            "llm": {
                "available": llm_available,
                "model": llm_service.model,
                "url": llm_service.base_url
            },
            "vector_store": {
                "available": vs_status,
                "documents": doc_count,
                "categories": vector_store.get_categories()
            },
            "stt": {
                "available": stt_service.is_available(),
                "engine": "Vosk"
            },
            "tts": {
                "available": tts_service.is_available(),
                "engine": "pyttsx3"
            }
        },
        "system": system_info
    }
