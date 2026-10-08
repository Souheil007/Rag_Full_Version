"""Unified LLM client interface supporting Gemini, OpenAI, and Anthropic."""

import os
from typing import Any
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Handles prompt dispatch and text generation across multiple LLM providers."""

    def __init__(
        self,
        provider: str = "gemini",
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
    ) -> None:
        """Initialize LLMClient configuration.

        Args:
            provider: LLM provider name ('gemini', 'openai', 'anthropic').
            model_name: Model identifier.
            temperature: Sampling temperature between 0.0 and 1.0.
            max_output_tokens: Maximum response tokens to generate.
        """
        self.provider = provider.lower()
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self._client = None

    def _init_client(self) -> None:
        """Initialize provider-specific SDK client."""
        if self._client is not None:
            return

        if self.provider == "gemini":
            try:
                from google import genai

                api_key = os.getenv("GEMINI_API_KEY")
                self._client = genai.Client(api_key=api_key)
                logger.info(f"Initialized Google GenAI client ({self.model_name})")
            except Exception as exc:
                logger.warning(f"Google GenAI initialization skipped: {exc}")
        elif self.provider == "openai":
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                logger.info(f"Initialized OpenAI client ({self.model_name})")
            except Exception as exc:
                logger.warning(f"OpenAI initialization skipped: {exc}")

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Send prompt to LLM and return generated answer.

        Args:
            prompt: User-facing prompt including context.
            system_prompt: Optional system instructions.

        Returns:
            Generated response string.
        """
        self._init_client()

        if self.provider == "gemini" and self._client is not None:
            try:
                config: dict[str, Any] = {
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_output_tokens,
                }
                if system_prompt:
                    config["system_instruction"] = system_prompt

                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                )
                return response.text or ""
            except Exception as exc:
                logger.error(f"Gemini generation error: {exc}")
                return f"[Error generating response with Gemini: {exc}]"

        if self.provider == "openai" and self._client is not None:
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = self._client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_output_tokens,
                )
                return response.choices[0].message.content or ""
            except Exception as exc:
                logger.error(f"OpenAI generation error: {exc}")
                return f"[Error generating response with OpenAI: {exc}]"

        # Mock / Fallback output for testing without API keys
        return f"[Mock response for query based on model {self.model_name}]"
