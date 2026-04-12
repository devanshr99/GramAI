"""
GramAI - Online AI Service
Uses OpenRouter API with DeepSeek v3.2 for online chat mode.
"""

import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-v3.2-exp"


class OnlineAIService:
    """Online AI chat via OpenRouter + DeepSeek v3.2."""

    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.client = httpx.AsyncClient(timeout=60.0)
        self._available = False

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def check_availability(self) -> bool:
        if not self.api_key:
            self._available = False
            return False
        self._available = True
        return True

    async def chat(
        self,
        query: str,
        language: str = "en",
        system_prompt: Optional[str] = None,
        history: Optional[list] = None
    ) -> str:
        if not self.api_key:
            return (
                "⚠️ Online AI not configured.\n\n"
                "Add your OpenRouter API key to .env:\n"
                "OPENROUTER_API_KEY=sk-or-v1-xxxxx"
            )

        lang_map = {
            "hi": "Respond in Hindi (Devanagari script). Be helpful and accurate.",
            "en": "Respond in clear, simple English. Be helpful and accurate.",
            "hg": "Respond in Hinglish (Hindi written in Roman/Latin script, casual conversational style mixing Hindi and English words). Be helpful.",
            "ta": "Respond in Tamil.", "te": "Respond in Telugu.",
            "bn": "Respond in Bengali.", "mr": "Respond in Marathi.",
            "gu": "Respond in Gujarati.", "kn": "Respond in Kannada.",
            "ml": "Respond in Malayalam.", "pa": "Respond in Punjabi.",
            "ur": "Respond in Urdu (Nastaliq script).",
            "or": "Respond in Odia.",
            "as": "Respond in Assamese.",
            "ne": "Respond in Nepali.",
            "kok": "Respond in Konkani (Devanagari script).",
            "doi": "Respond in Dogri (Devanagari script).",
            "mai": "Respond in Maithili (Devanagari script).",
            "sa": "Respond in Sanskrit (Devanagari script).",
            "mni": "Respond in Manipuri/Meitei.",
            "sd": "Respond in Sindhi.",
            "ks": "Respond in Kashmiri.",
            "bodo": "Respond in Bodo (Devanagari script).",
            "sat": "Respond in Santali.",
        }


        system = system_prompt or (
            f"You are GramAI, a helpful AI assistant for rural India. "
            f"You help with agriculture, health, education, government schemes, and any general questions. "
            f"{lang_map.get(language, 'Respond in English.')} "
            f"Keep responses clear and concise (2-3 paragraphs max)."
        )

        messages = [{"role": "system", "content": system}]

        # Add conversation history
        if history:
            for msg in history[-6:]:
                text = msg.get("text", "")
                if text and not text.startswith("⚠️"):
                    role = "user" if msg.get("role") == "user" else "assistant"
                    messages.append({"role": role, "content": text})

        messages.append({"role": "user", "content": query})

        try:
            resp = await self.client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://gramai.app",
                    "X-Title": "GramAI",
                },
                json={
                    "model": MODEL,
                    "messages": messages,
                    "max_tokens": 800,
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            )

            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    if content:
                        return content
                return "No response generated."

            elif resp.status_code == 401:
                return "⚠️ Invalid API key. Check OPENROUTER_API_KEY in .env"

            elif resp.status_code == 402:
                return "⚠️ Insufficient credits. Top up at https://openrouter.ai/credits"

            elif resp.status_code == 429:
                return "⚠️ Rate limited. Wait a moment and try again."

            else:
                logger.error(f"OpenRouter error {resp.status_code}: {resp.text[:200]}")
                return f"⚠️ AI error ({resp.status_code}). Try again."

        except httpx.TimeoutException:
            return "⚠️ Request timed out. Check your internet connection."
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            return "⚠️ Could not connect to AI service."

    async def close(self):
        await self.client.aclose()


online_ai = OnlineAIService()
