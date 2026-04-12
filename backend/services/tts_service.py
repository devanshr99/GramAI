"""
GramAI - Text-to-Speech Service
Offline TTS for Hindi language output.
"""

import io
import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import TTS engines
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not installed. Install with: pip install pyttsx3")


class TTSService:
    """Offline Text-to-Speech service."""

    def __init__(self):
        self.engine = None
        self._initialized = False
        self._cache_dir = Path(__file__).parent.parent / "audio_cache"
        self._cache_dir.mkdir(exist_ok=True)

    def initialize(self):
        """Initialize TTS engine."""
        if self._initialized:
            return True

        if not PYTTSX3_AVAILABLE:
            logger.error("No TTS engine available.")
            return False

        try:
            self.engine = pyttsx3.init()
            # Configure for Hindi-friendly settings
            self.engine.setProperty('rate', 150)  # Speed
            self.engine.setProperty('volume', 0.9)  # Volume

            # Try to set Hindi voice if available
            voices = self.engine.getProperty('voices')
            hindi_voice = None
            for voice in voices:
                if 'hindi' in voice.name.lower() or 'hi-in' in voice.id.lower() or 'hindi' in str(voice.languages).lower():
                    hindi_voice = voice
                    break

            if hindi_voice:
                self.engine.setProperty('voice', hindi_voice.id)
                logger.info(f"Using Hindi voice: {hindi_voice.name}")
            else:
                logger.warning("Hindi voice not found. Using default voice.")
                # Use the first available voice
                if voices:
                    self.engine.setProperty('voice', voices[0].id)

            self._initialized = True
            logger.info("TTS engine initialized.")
            return True

        except Exception as e:
            logger.error(f"TTS initialization error: {e}")
            return False

    def synthesize_to_file(self, text: str) -> Optional[str]:
        """
        Convert text to speech and save as WAV file.

        Returns:
            Path to the generated audio file, or None on failure.
        """
        if not self._initialized:
            if not self.initialize():
                return None

        try:
            # Generate cache key from text
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
            output_path = self._cache_dir / f"tts_{text_hash}.wav"

            # Check cache
            if output_path.exists():
                return str(output_path)

            # Generate audio
            self.engine.save_to_file(text, str(output_path))
            self.engine.runAndWait()

            if output_path.exists():
                return str(output_path)
            else:
                logger.error("TTS file was not created.")
                return None

        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            return None

    def speak(self, text: str):
        """Speak text directly (for server-side testing)."""
        if not self._initialized:
            if not self.initialize():
                return

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS speak error: {e}")

    def get_available_voices(self) -> list:
        """List available voices."""
        if not self._initialized:
            self.initialize()

        if not self.engine:
            return []

        voices = self.engine.getProperty('voices')
        return [
            {
                "id": v.id,
                "name": v.name,
                "languages": str(v.languages)
            }
            for v in voices
        ]

    def is_available(self) -> bool:
        """Check if TTS is available."""
        return PYTTSX3_AVAILABLE and self._initialized

    def clear_cache(self):
        """Clear the audio cache."""
        for f in self._cache_dir.glob("tts_*.wav"):
            f.unlink()


# Singleton instance
tts_service = TTSService()
