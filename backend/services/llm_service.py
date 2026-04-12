"""
GramAI - LLM Service
Handles Claude API integration for language model inference.
"""

import logging
from typing import Optional

import httpx

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class LLMService:
    """Manages Claude API for text generation."""

    def __init__(self):
        self.api_key = ANTHROPIC_API_KEY
        self.model = CLAUDE_MODEL
        self.client = httpx.AsyncClient(timeout=60.0)
        self._available = None

    async def check_availability(self) -> bool:
        """Check if Claude API is configured."""
        self._available = bool(self.api_key)
        if not self._available:
             logger.warning("ANTHROPIC_API_KEY not set. Claude API is unavailable.")
        return self._available

    async def generate(
        self,
        prompt: str,
        context: str = "",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate a response using the Claude API."""
        if self._available is None:
            await self.check_availability()

        if not self._available:
            return self._fallback_response()

        full_system = system_prompt or SYSTEM_PROMPT
        if context:
            full_system += f"\n\nसंदर्भ जानकारी (Context):\n{context}"

        try:
            response = await self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "system": full_system,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": temperature,
                }
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [])
                if content:
                    return content[0].get("text", "कोई जवाब नहीं मिला।")
                return "कोई जवाब नहीं मिला।"
            elif response.status_code == 401:
                return "⚠️ Invalid API key. Check ANTHROPIC_API_KEY in .env"
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                return "⚠️ API Error"

        except httpx.TimeoutException:
            logger.error("LLM request timed out")
            return "माफ करें, जवाब देने में समय लग रहा है। कृपया दोबारा पूछें।"
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return self._fallback_response()

    async def chat(
        self,
        messages: list,
        context: str = "",
        temperature: float = 0.7
    ) -> str:
        """Chat-style interaction with the LLM."""
        if self._available is None:
            await self.check_availability()

        if not self._available:
            return self._fallback_response()

        system_msg = SYSTEM_PROMPT
        if context:
            system_msg += f"\n\nसंदर्भ जानकारी (Context):\n{context}"

        # Ensure messages map properly to Claude API Format
        formatted_messages = []
        for msg in messages:
            if msg.get("role") != "system":
                role = "assistant" if msg.get("role") == "assistant" else "user"
                formatted_messages.append({
                    "role": role,
                    "content": msg.get("content", "")
                })

        try:
            response = await self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "system": system_msg,
                    "messages": formatted_messages,
                    "max_tokens": 1024,
                    "temperature": temperature,
                }
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [])
                if content:
                    return content[0].get("text", "कोई जवाब नहीं मिला।")
                return "कोई जवाब नहीं मिला।"
            else:
                logger.error(f"Claude chat error: {response.status_code} - {response.text}")
                return "⚠️ API Error"

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return self._fallback_response()

    def _fallback_response(self) -> str:
        """Provide a fallback response when API is unavailable."""
        return (
            "⚠️ AI मॉडल अभी उपलब्ध नहीं है।\n\n"
            "कृपया सुनिश्चित करें कि ANTHROPIC_API_KEY .env फ़ाइल में सेट है।"
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
llm_service = LLMService()
