"""
GramAI - Voice Service Tests
Tests for STT and TTS services.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestSTTService:
    """Test Speech-to-Text service."""

    def test_stt_import(self):
        """STT service should import without errors."""
        from services.stt_service import stt_service
        assert stt_service is not None

    def test_stt_availability_check(self):
        """STT should report availability status."""
        from services.stt_service import stt_service
        # Should not crash even without model
        result = stt_service.is_available()
        assert isinstance(result, bool)

    def test_stt_transcribe_empty(self):
        """STT should handle empty audio gracefully."""
        from services.stt_service import stt_service
        result = stt_service.transcribe(b"")
        assert "success" in result
        assert "text" in result


class TestTTSService:
    """Test Text-to-Speech service."""

    def test_tts_import(self):
        """TTS service should import without errors."""
        from services.tts_service import tts_service
        assert tts_service is not None

    def test_tts_availability_check(self):
        """TTS should report availability status."""
        from services.tts_service import tts_service
        result = tts_service.is_available()
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
