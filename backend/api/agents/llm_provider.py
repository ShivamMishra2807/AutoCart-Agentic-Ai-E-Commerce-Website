"""
AutoCart Unified LLM Provider Integration.
Supports both Groq Cloud (Llama 3.3 / Mixtral) and Google Gemini SDK (`google-genai`),
with automatic failover, bounded timeouts, token caps, and grounded local fallback.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import requests

logger = logging.getLogger(__name__)

def _load_local_env() -> Dict[str, str]:
    env_path = Path(__file__).resolve().parents[3] / '.env'
    if not env_path.exists():
        return {}
    values = {}
    try:
        for raw in env_path.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, val = line.split('=', 1)
            values[key.strip()] = val.strip().strip('"').strip("'")
    except Exception as e:
        logger.warning("Failed to read local .env: %s", e)
    return values

_LOCAL_ENV = _load_local_env()


class LLMConfig:
    @staticmethod
    def get_groq_api_key() -> str:
        return (
            os.getenv('GROQ_API_KEY')
            or _LOCAL_ENV.get('GROQ_API_KEY', '')
        ).strip()

    @staticmethod
    def get_groq_model() -> str:
        return (
            os.getenv('GROQ_MODEL')
            or _LOCAL_ENV.get('GROQ_MODEL', '')
            or 'llama-3.3-70b-versatile'
        ).strip()

    @staticmethod
    def get_gemini_api_key() -> str:
        return (
            os.getenv('GEMINI_API_KEY')
            or os.getenv('GOOGLE_API_KEY')
            or _LOCAL_ENV.get('GEMINI_API_KEY', '')
            or _LOCAL_ENV.get('GOOGLE_API_KEY', '')
        ).strip()

    @staticmethod
    def get_gemini_model() -> str:
        return (
            os.getenv('GEMINI_MODEL')
            or _LOCAL_ENV.get('GEMINI_MODEL', '')
            or 'gemini-3.8-flash'
        ).strip()

    @staticmethod
    def get_timeout() -> int:
        try:
            return int(os.getenv('LLM_TIMEOUT', os.getenv('GEMINI_TIMEOUT', '4')))
        except ValueError:
            return 4


class GroqProvider:
    """
    Direct HTTPS REST Client for Groq Cloud API.
    Does not require external proprietary packages; uses requests for zero-dependency reliability.
    """
    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
    _circuit_open_until = 0.0

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or LLMConfig.get_groq_api_key()
        self.model = model or LLMConfig.get_groq_model()
        self.timeout = LLMConfig.get_timeout()

    @property
    def is_configured(self) -> bool:
        if not self.api_key or str(self.api_key).strip().lower().startswith('your_') or 'placeholder' in str(self.api_key).lower() or len(str(self.api_key).strip()) < 10:
            return False
        return True

    def generate(
        self,
        system_instruction: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1000
    ) -> Optional[str]:
        if not self.is_configured:
            return None
        if time.time() < GroqProvider._circuit_open_until:
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        for attempt in range(2):
            try:
                res = requests.post(self.BASE_URL, headers=headers, json=payload, timeout=self.timeout)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices") or []
                    if choices and "message" in choices[0] and choices[0]["message"].get("content"):
                        return choices[0]["message"]["content"].strip()
                    return None
                elif res.status_code in (429, 503):
                    GroqProvider._circuit_open_until = time.time() + 180.0
                    logger.warning("Groq rate limit hit. Pausing Groq calls for 3m.")
                    return None
                else:
                    logger.warning("Groq API error (%s): %s", res.status_code, res.text[:200])
                    return None
            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt == 0:
                    time.sleep(0.3)
                    continue
                logger.warning("Groq request timed out or network failed: %s", e)
                return None
            except Exception as e:
                logger.warning("Groq request failed: %s", e)
                return None
        return None


class GeminiProvider:
    """
    Encapsulates interaction with Google Gemini API via official google-genai SDK.
    """
    _circuit_open_until = 0.0

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or LLMConfig.get_gemini_api_key()
        self.model = model or LLMConfig.get_gemini_model()
        self.timeout = LLMConfig.get_timeout()
        self._client = None
        if self.api_key:
            try:
                import google.genai as genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.debug("Google GenAI SDK initialization skipped: %s", e)
                self._client = None

    @property
    def is_configured(self) -> bool:
        if not self.api_key or str(self.api_key).strip().lower().startswith('your_') or 'placeholder' in str(self.api_key).lower() or len(str(self.api_key).strip()) < 10:
            return False
        return bool(self._client)

    def generate(
        self,
        system_instruction: str,
        contents: Any,
        temperature: float = 0.2,
        max_output_tokens: int = 1000
    ) -> Optional[str]:
        if not self.is_configured:
            return None
        if time.time() < GeminiProvider._circuit_open_until:
            return None

        from google.genai import types
        # Newer Gemini models spend part of the output limit "thinking" first, which cut replies off mid-sentence.
        # Give the answer room, and turn thinking off where the SDK supports it.
        kwargs = dict(system_instruction=system_instruction, temperature=temperature,
                      max_output_tokens=max(int(max_output_tokens), 2048))
        try:
            config = types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0), **kwargs)
        except Exception:
            config = types.GenerateContentConfig(**kwargs)

        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
        except Exception as e:
            err_str = str(e)
            if '429' in err_str or 'RESOURCE_EXHAUSTED' in err_str or '503' in err_str or 'quota' in err_str.lower():
                GeminiProvider._circuit_open_until = time.time() + 300.0
                logger.info("Gemini quota exhausted or high demand. Circuit open for 5m; fast-failing to deterministic engine.")
            elif 'API_KEY_INVALID' in err_str or 'INVALID_ARGUMENT' in err_str or '400' in err_str:
                GeminiProvider._circuit_open_until = time.time() + 600.0
                logger.warning("Gemini API key is invalid or placeholder. Circuit open for 10m; fast-failing to deterministic engine: %s", e)
            else:
                logger.warning("Gemini API call failed: %s", e)
            return None
        return None


class UnifiedLLMProvider:
    """
    Unified LLM router that prioritizes Groq (if key available), falls back to Gemini,
    and returns None cleanly to let the grounded deterministic engine take over.
    """
    def __init__(self):
        self.groq = GroqProvider()
        self.gemini = GeminiProvider()

    @property
    def active_provider_name(self) -> str:
        if self.groq.is_configured:
            return f"groq ({self.groq.model})"
        if self.gemini.is_configured:
            return f"google-gemini ({self.gemini.model})"
        return "grounded-engine"

    @property
    def is_configured(self) -> bool:
        if os.getenv('AUTOCART_DISABLE_LLM') == '1':  # tests: never call a real API or spend free quota
            return False
        return self.groq.is_configured or self.gemini.is_configured

    @property
    def is_available(self) -> bool:
        return self.is_configured

    def generate(
        self,
        system_instruction: str,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Attempts Groq first, then Gemini, returns {'text': ..., 'provider': ...}
        """
        if os.getenv('AUTOCART_DISABLE_LLM') == '1':
            return {'text': None, 'provider': 'grounded-engine', 'model': 'local-deterministic'}

        # 1. Try Groq
        if self.groq.is_configured:
            text = self.groq.generate(system_instruction, prompt, temperature, max_tokens)
            if text:
                return {'text': text, 'provider': 'groq', 'model': self.groq.model}

        # 2. Try Gemini
        if self.gemini.is_configured:
            text = self.gemini.generate(system_instruction, prompt, temperature, max_tokens)
            if text:
                return {'text': text, 'provider': 'google-gemini', 'model': self.gemini.model}

        return {'text': None, 'provider': 'grounded-engine', 'model': 'local-deterministic'}
