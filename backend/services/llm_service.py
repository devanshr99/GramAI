"""
GramAI - LLM Service
Handles Ollama integration for offline language model inference.
"""

import logging
from typing import Optional, Dict, AsyncGenerator

import httpx

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class LLMService:
    """Manages Ollama LLM for text generation."""

    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self.client = httpx.AsyncClient(timeout=120.0)
        self._available = None

    async def check_availability(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]
                self._available = self.model in model_names or any(
                    self.model in name for name in model_names
                )
                if not self._available:
                    logger.warning(
                        f"Model '{self.model}' not found. Available: {model_names}. "
                        f"Pull it with: ollama pull {self.model}"
                    )
                return self._available
            return False
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            self._available = False
            return False

    async def generate(
        self,
        prompt: str,
        context: str = "",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate a response using the LLM."""
        if self._available is None:
            await self.check_availability()

        if not self._available:
            return self._fallback_response(prompt)

        # Build the full prompt with context
        full_system = system_prompt or SYSTEM_PROMPT
        if context:
            full_system += f"\n\nसंदर्भ जानकारी (Context):\n{context}"

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": full_system,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": 512,
                        "top_p": 0.9,
                    }
                }
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "कोई जवाब नहीं मिला।")
            else:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return self._fallback_response(prompt)

        except httpx.TimeoutException:
            logger.error("LLM request timed out")
            return "माफ करें, जवाब देने में समय लग रहा है। कृपया दोबारा पूछें।"
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return self._fallback_response(prompt)

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
            return self._fallback_response(messages[-1].get("content", "") if messages else "")

        system_msg = SYSTEM_PROMPT
        if context:
            system_msg += f"\n\nसंदर्भ जानकारी (Context):\n{context}"

        # Build messages list with system prompt
        full_messages = [{"role": "system", "content": system_msg}]
        full_messages.extend(messages)

        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": full_messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": 512,
                        "top_p": 0.9,
                    }
                }
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "कोई जवाब नहीं मिला।")
            else:
                logger.error(f"Ollama chat error: {response.status_code}")
                return self._fallback_response("")

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return self._fallback_response("")

    def _fallback_response(self, query: str) -> str:
        """Provide a fallback response when LLM is unavailable."""
        return (
            "⚠️ AI मॉडल अभी उपलब्ध नहीं है।\n\n"
            "कृपया सुनिश्चित करें कि Ollama चल रहा है:\n"
            f"1. Terminal में चलाएं: `ollama serve`\n"
            f"2. मॉडल डाउनलोड करें: `ollama pull {self.model}`\n\n"
            "तब तक, आप ज्ञान आधार (Knowledge Base) से जानकारी खोज सकते हैं।"
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
llm_service = LLMService()
