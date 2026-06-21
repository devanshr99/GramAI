"""
GramAI - LLM Service (Local GGUF + Claude/OpenRouter Fallbacks)
Manages local GGUF models for offline mode and API endpoints when online.
"""

import logging
import os
import httpx
from typing import Optional, List, Dict
from pathlib import Path

from config import (
    ANTHROPIC_API_KEY, CLAUDE_MODEL, SYSTEM_PROMPT, MODELS_DIR,
    LOCAL_LLM_REPO, LOCAL_LLM_FILE
)

logger = logging.getLogger(__name__)


class LLMService:
    """Manages local GGUF model execution and API-based language model generation."""

    def __init__(self):
        self.api_key = ANTHROPIC_API_KEY
        self.model = CLAUDE_MODEL
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # Local GGUF settings
        self.local_model_repo = LOCAL_LLM_REPO
        self.local_model_file = LOCAL_LLM_FILE
        self.local_model = None
        self.local_tokenizer = None
        self._local_model_loaded = False
        self._available = True  # Always true since we have a local LLM fallback

    async def check_availability(self) -> bool:
        """Check if LLM is ready (local model fallback is always available)."""
        return True

    def _load_local_model(self):
        """Lazily load the local GGUF model on CPU."""
        if self._local_model_loaded:
            return
        
        model_path = MODELS_DIR / self.local_model_file
        logger.info(f"Checking for local GGUF model at {model_path}...")
        
        try:
            if not model_path.exists():
                logger.info(f"Local GGUF model not found. Downloading {self.local_model_file} from Hugging Face ({self.local_model_repo})...")
                from huggingface_hub import hf_hub_download
                hf_hub_download(
                    repo_id=self.local_model_repo,
                    filename=self.local_model_file,
                    local_dir=MODELS_DIR,
                    local_dir_use_symlinks=False
                )
            
            # Import transformers and load GGUF model
            logger.info("Loading GGUF model into memory (CPU)...")
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.local_model = AutoModelForCausalLM.from_pretrained(
                self.local_model_repo,
                gguf_file=self.local_model_file,
                low_cpu_mem_usage=True
            )
            self.local_tokenizer = AutoTokenizer.from_pretrained(
                self.local_model_repo,
                gguf_file=self.local_model_file
            )
            self._local_model_loaded = True
            logger.info("Local GGUF model loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading local GGUF model: {e}")
            self._local_model_loaded = False

    async def generate_local(
        self,
        prompt: str,
        context: str = "",
        system_prompt: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """Generate response locally using the GGUF model."""
        self._load_local_model()
        if not self._local_model_loaded or not self.local_model:
            return "⚠️ स्थानीय एआई मॉडल लोड करने में विफल रहा। (Failed to load local AI model.)"

        sys_msg = system_prompt or SYSTEM_PROMPT
        
        # Build prompt using standard instruction format (Phi-3 / Chat template compatible)
        # Structure context and query cleanly
        full_context = f"संदर्भ जानकारी:\n{context}\n\n" if context else ""
        formatted_prompt = (
            f"<|system|>\n{sys_msg}\n{full_context}<|end|>\n"
            f"<|user|>\n{prompt}<|end|>\n"
            f"<|assistant|>\n"
        )

        try:
            import torch
            inputs = self.local_tokenizer(formatted_prompt, return_tensors="pt")
            
            # Generate tokens
            with torch.no_grad():
                outputs = self.local_model.generate(
                    **inputs,
                    max_new_tokens=250,
                    temperature=temperature,
                    do_sample=(temperature > 0.1),
                    pad_token_id=self.local_tokenizer.eos_token_id
                )
            
            # Decode response skipping the input prompt
            input_len = inputs.input_ids.shape[1]
            response = self.local_tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True)
            return response.strip()
        except Exception as e:
            logger.error(f"Local generation error: {e}")
            return "⚠️ स्थानीय एआई पीढ़ी के दौरान त्रुटि हुई। (Error during local AI generation.)"

    async def check_internet_connection(self) -> bool:
        """Check if internet is available by doing a fast ping test."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get("https://huggingface.co", follow_redirects=False)
                return resp.status_code < 400 or resp.status_code >= 500
        except Exception:
            return False

    async def generate(
        self,
        prompt: str,
        context: str = "",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate a response, falling back to local LLM if offline or API is missing."""
        internet_online = await self.check_internet_connection()

        # If internet is not available or ANTHROPIC_API_KEY is not configured, run local GGUF LLM
        if not internet_online or not self.api_key:
            logger.info("Using local GGUF LLM for generation...")
            return await self.generate_local(prompt, context, system_prompt, temperature=0.3)

        # Online mode: Run Anthropic Claude API or OpenRouter Fallback
        logger.info("Internet is active. Routing query to online AI APIs...")
        
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
            else:
                logger.warning(f"Claude API failed ({response.status_code}). Trying OpenRouter fallback...")
                
        except Exception as e:
            logger.error(f"Claude API exception: {e}. Trying OpenRouter fallback...")

        # Fallback to OpenRouter if configured
        from services.online_ai import OPENROUTER_API_KEY, MODEL, OPENROUTER_URL
        if OPENROUTER_API_KEY:
            try:
                response = await self.client.post(
                    OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://gramai.app",
                        "X-Title": "GramAI",
                    },
                    json={
                        "model": MODEL,
                        "messages": [
                            {"role": "system", "content": full_system},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 800,
                        "temperature": temperature,
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "कोई जवाब नहीं मिला।")
            except Exception as e:
                logger.error(f"OpenRouter API error: {e}")

        # Final offline GGUF fallback if online calls failed
        logger.warning("Online APIs failed or not configured. Falling back to local GGUF LLM...")
        return await self.generate_local(prompt, context, system_prompt, temperature=0.3)

    async def chat(
        self,
        messages: list,
        context: str = "",
        temperature: float = 0.7
    ) -> str:
        """Chat-style interaction, falls back to local GGUF if offline."""
        internet_online = await self.check_internet_connection()

        if not internet_online or not self.api_key:
            # Fallback to local GGUF LLM
            latest_query = messages[-1].get("content", "") if messages else ""
            return await self.generate_local(latest_query, context, SYSTEM_PROMPT, temperature=0.3)

        # Online Chat implementation
        from services.online_ai import OPENROUTER_API_KEY, MODEL, OPENROUTER_URL
        if OPENROUTER_API_KEY:
            try:
                response = await self.client.post(
                    OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://gramai.app",
                        "X-Title": "GramAI",
                    },
                    json={
                        "model": MODEL,
                        "messages": messages,
                        "max_tokens": 1024,
                        "temperature": temperature,
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
            except Exception as e:
                logger.error(f"Chat OpenRouter error: {e}")

        # Fallback to local LLM
        latest_query = messages[-1].get("content", "") if messages else ""
        return await self.generate_local(latest_query, context, SYSTEM_PROMPT, temperature=0.3)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
llm_service = LLMService()
