"""
GramAI - Main FastAPI Application
Offline AI Assistant for Rural India

Entry point for the backend server.
"""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Configure logging with UTF-8 support for Windows
import io
handler = logging.StreamHandler(
    io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("gramai")

# Import services
from services.vector_store import vector_store
from services.llm_service import llm_service
from services.stt_service import stt_service
from services.tts_service import tts_service

# Import routers
from routers import chat, voice, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # === STARTUP ===
    logger.info("=" * 60)
    logger.info("[GramAI] Offline AI Assistant for Rural India")
    logger.info("=" * 60)

    # Initialize vector store
    logger.info("Initializing knowledge base...")
    try:
        vector_store.initialize()
        logger.info("[OK] Knowledge base loaded successfully.")
    except Exception as e:
        logger.error(f"[FAIL] Knowledge base error: {e}")

    # Check LLM availability
    logger.info("Checking LLM availability...")
    llm_ok = await llm_service.check_availability()
    if llm_ok:
        logger.info(f"[OK] LLM ({llm_service.model}) is available.")
    else:
        logger.warning(
            f"[WARN] LLM ({llm_service.model}) not available. "
            "Set ANTHROPIC_API_KEY in .env. System will use knowledge base only."
        )

    # Initialize STT
    logger.info("Initializing Speech-to-Text...")
    stt_ok = stt_service.initialize()
    if stt_ok:
        logger.info("[OK] STT (Vosk) is available.")
    else:
        logger.warning("[WARN] STT not available. Voice input disabled.")

    # Initialize TTS
    logger.info("Initializing Text-to-Speech...")
    tts_ok = tts_service.initialize()
    if tts_ok:
        logger.info("[OK] TTS is available.")
    else:
        logger.warning("[WARN] TTS not available. Voice output disabled.")

    logger.info("=" * 60)
    logger.info("[READY] GramAI server is ready!")
    logger.info("Open http://localhost:8000 in your browser")
    logger.info("=" * 60)

    yield

    # === SHUTDOWN ===
    logger.info("Shutting down GramAI...")
    await llm_service.close()
    logger.info("GramAI shut down successfully.")


# Create FastAPI application
app = FastAPI(
    title="GramAI - GramAI",
    description="Offline AI Assistant for Rural India | ग्रामीण भारत के लिए ऑफ़लाइन AI सहायक",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware (allow all origins for local network access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(health.router)

# Serve frontend: supports Vite build (dist/) or dev public assets
frontend_dir = Path(__file__).parent.parent / "frontend"
dist_dir = frontend_dir / "dist"
public_dir = frontend_dir / "public"

# Determine which directory to serve from
serve_dir = dist_dir if dist_dir.exists() else None
assets_dir = (dist_dir / "assets" if dist_dir.exists()
              else public_dir / "assets" if (public_dir / "assets").exists()
              else None)

if assets_dir and assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

if dist_dir.exists():
    # Production: serve built static files
    static_dir = dist_dir / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/sw.js")
    async def serve_sw():
        sw = dist_dir / "sw.js"
        if sw.exists():
            return FileResponse(str(sw), media_type="application/javascript",
                                headers={"Cache-Control": "no-cache", "Service-Worker-Allowed": "/"})
        return FileResponse(str(dist_dir / "index.html"))

    @app.get("/favicon.ico")
    async def serve_favicon():
        icon = assets_dir / "icon-96.png" if assets_dir else None
        if icon and icon.exists():
            return FileResponse(str(icon), media_type="image/png")
        return FileResponse(str(dist_dir / "index.html"))

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        """Serve the React SPA - all routes go to index.html."""
        file_path = dist_dir / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(dist_dir / "index.html"))
else:
    # Dev mode or no build: serve API only (frontend on Vite dev server port 3000)
    if assets_dir and assets_dir.exists():
        @app.get("/sw.js")
        async def serve_sw_dev():
            sw = public_dir / "sw.js"
            if sw.exists():
                return FileResponse(str(sw), media_type="application/javascript",
                                    headers={"Cache-Control": "no-cache", "Service-Worker-Allowed": "/"})
            return {"error": "No service worker"}

        @app.get("/favicon.ico")
        async def serve_favicon_dev():
            icon = assets_dir / "icon-96.png"
            if icon.exists():
                return FileResponse(str(icon), media_type="image/png")
            return {"error": "No favicon"}

    @app.get("/")
    async def root():
        return {
            "message": "GramAI API is running!",
            "docs": "/docs",
            "frontend": "Run 'npm run dev' in frontend/ directory to start the React UI on port 3000"
        }



if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )
