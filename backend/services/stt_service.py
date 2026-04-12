"""
GramAI - Speech-to-Text Service
Offline Hindi speech recognition using Vosk.
"""

import io
import json
import wave
import logging
import struct
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import Vosk (optional dependency)
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.warning("Vosk not installed. STT will be unavailable. Install with: pip install vosk")


class STTService:
    """Offline Speech-to-Text using Vosk."""

    def __init__(self):
        self.model = None
        self._initialized = False
        self._model_path = None

    def initialize(self, model_path: str = None):
        """Initialize Vosk model for Hindi."""
        if self._initialized:
            return True

        if not VOSK_AVAILABLE:
            logger.error("Vosk is not installed.")
            return False

        from config import VOSK_MODEL_PATH
        path = model_path or VOSK_MODEL_PATH

        model_dir = Path(path)
        if not model_dir.exists():
            logger.warning(
                f"Vosk Hindi model not found at {path}. "
                "Download from: https://alphacephei.com/vosk/models "
                "Get 'vosk-model-small-hi-0.22' and extract to backend/models/vosk-model-hi"
            )
            return False

        try:
            self.model = Model(str(model_dir))
            self._initialized = True
            self._model_path = path
            logger.info(f"Vosk STT initialized with model: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to init Vosk: {e}")
            return False

    def transcribe(self, audio_data: bytes, sample_rate: int = 16000) -> dict:
        """
        Transcribe audio data to text.

        Args:
            audio_data: Raw PCM audio bytes or WAV file bytes
            sample_rate: Audio sample rate (default 16000)

        Returns:
            dict with 'text', 'confidence', 'success' keys
        """
        if not self._initialized:
            if not self.initialize():
                return {
                    "text": "",
                    "confidence": 0,
                    "success": False,
                    "error": "STT model not initialized. Download Vosk Hindi model."
                }

        try:
            recognizer = KaldiRecognizer(self.model, sample_rate)
            recognizer.SetWords(True)

            # Check if it's a WAV file
            if audio_data[:4] == b'RIFF':
                audio_data = self._extract_pcm_from_wav(audio_data)

            # Process audio in chunks
            chunk_size = 4000
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                recognizer.AcceptWaveform(chunk)

            # Get final result
            result = json.loads(recognizer.FinalResult())
            text = result.get("text", "").strip()

            return {
                "text": text,
                "confidence": 1.0 if text else 0.0,
                "success": bool(text),
                "error": None if text else "No speech detected"
            }

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                "text": "",
                "confidence": 0,
                "success": False,
                "error": str(e)
            }

    def _extract_pcm_from_wav(self, wav_data: bytes) -> bytes:
        """Extract raw PCM data from WAV file bytes."""
        try:
            wav_io = io.BytesIO(wav_data)
            with wave.open(wav_io, 'rb') as wav_file:
                pcm_data = wav_file.readframes(wav_file.getnframes())
            return pcm_data
        except Exception:
            # If WAV parsing fails, return original data
            return wav_data

    def is_available(self) -> bool:
        """Check if STT is available."""
        return VOSK_AVAILABLE and self._initialized


# Singleton instance
stt_service = STTService()
