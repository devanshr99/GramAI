"""
GramAI - Voice Router
Handles voice input (STT) and output (TTS) endpoints.
"""

import io
import wave
import struct
import base64
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional

from services.stt_service import stt_service
from services.tts_service import tts_service

router = APIRouter(prefix="/api/voice", tags=["Voice"])


class TranscribeResponse(BaseModel):
    """Response model for speech transcription."""
    text: str
    confidence: float
    success: bool
    error: Optional[str] = None


class TTSRequest(BaseModel):
    """Request model for text-to-speech."""
    text: str = Field(..., description="Text to convert to speech")


class AudioUploadRequest(BaseModel):
    """Request for audio data as base64."""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    sample_rate: int = Field(16000, description="Audio sample rate")
    format: str = Field("wav", description="Audio format: wav, webm, raw")


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe uploaded audio file to Hindi text.
    Accepts WAV format, 16kHz mono recommended.
    """
    try:
        audio_data = await file.read()

        if not audio_data:
            raise HTTPException(status_code=400, detail="Empty audio file")

        result = stt_service.transcribe(audio_data)
        return TranscribeResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")


@router.post("/transcribe-base64", response_model=TranscribeResponse)
async def transcribe_base64(request: AudioUploadRequest):
    """
    Transcribe base64-encoded audio to Hindi text.
    Used by the web frontend for direct microphone capture.
    """
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_data)

        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio data")

        # If raw PCM, wrap in WAV header
        if request.format == "raw":
            audio_bytes = _wrap_pcm_as_wav(audio_bytes, request.sample_rate)

        result = stt_service.transcribe(audio_bytes, request.sample_rate)
        return TranscribeResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")


@router.post("/speak")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech and return audio file path.
    Returns the path to the generated audio file.
    """
    try:
        audio_path = tts_service.synthesize_to_file(request.text)

        if audio_path and Path(audio_path).exists():
            return FileResponse(
                audio_path,
                media_type="audio/wav",
                filename="response.wav"
            )
        else:
            raise HTTPException(
                status_code=503,
                detail="TTS service unavailable or synthesis failed."
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


@router.get("/status")
async def voice_status():
    """Check the status of voice services."""
    return {
        "stt": {
            "available": stt_service.is_available(),
            "engine": "Vosk" if stt_service.is_available() else "Not available",
            "info": "Download Vosk Hindi model from https://alphacephei.com/vosk/models"
        },
        "tts": {
            "available": tts_service.is_available(),
            "engine": "pyttsx3" if tts_service.is_available() else "Not available",
            "voices": tts_service.get_available_voices() if tts_service.is_available() else []
        }
    }


def _wrap_pcm_as_wav(pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> bytes:
    """Wrap raw PCM data in a WAV header."""
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    return wav_io.getvalue()
