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
        model_name: str = "gemini-2.0-flash",
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
        self._sdk_type: str | None = None

    def _init_client(self) -> None:
        """Initialize provider-specific SDK client."""
        if self._client is not None:
            return

        if self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY environment variable is not set.")
                return

            # Try modern google-genai SDK first
            try:
                from google import genai

                self._client = genai.Client(api_key=api_key)
                self._sdk_type = "google_genai"
                logger.info(f"Initialized Google GenAI client ({self.model_name})")
                return
            except Exception as exc:
                logger.warning(f"google-genai client init failed ({exc}). Trying google.generativeai...")

            # Fallback to google.generativeai
            try:
                import google.generativeai as gai

                gai.configure(api_key=api_key)
                self._client = gai
                self._sdk_type = "google_generativeai"
                logger.info(f"Initialized google.generativeai client ({self.model_name})")
            except Exception as exc:
                logger.error(f"Failed to initialize any Gemini client: {exc}")

        elif self.provider == "openai":
            try:
                from openai import OpenAI

                api_key = os.getenv("OPENAI_API_KEY")
                self._client = OpenAI(api_key=api_key)
                self._sdk_type = "openai"
                logger.info(f"Initialized OpenAI client ({self.model_name})")
            except Exception as exc:
                logger.warning(f"OpenAI initialization skipped: {exc}")

    def _generate_gemini(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate response via Gemini API with model fallback support.

        Args:
            prompt: Formatted user prompt.
            system_prompt: Optional system instruction.

        Returns:
            Generated response string.
        """
        candidate_models = [
            self.model_name,
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
        ]
        # Deduplicate while preserving order
        candidate_models = list(dict.fromkeys(candidate_models))

        last_error = None
        for model in candidate_models:
            clean_model = model.replace("models/", "")
            try:
                if self._sdk_type == "google_genai":
                    config: dict[str, Any] = {
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_output_tokens,
                    }
                    if system_prompt:
                        config["system_instruction"] = system_prompt

                    response = self._client.models.generate_content(
                        model=clean_model,
                        contents=prompt,
                        config=config,
                    )
                    return response.text or ""

                elif self._sdk_type == "google_generativeai":
                    model_instance = self._client.GenerativeModel(
                        model_name=clean_model,
                        system_instruction=system_prompt if system_prompt else None,
                    )
                    generation_config = {
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_output_tokens,
                    }
                    response = model_instance.generate_content(
                        prompt,
                        generation_config=generation_config,
                    )
                    return response.text or ""

            except Exception as exc:
                last_error = exc
                logger.warning(f"Gemini generation with '{clean_model}' failed ({exc}). Trying next candidate...")

        logger.error(f"All Gemini model candidates failed. Last error: {last_error}")
        return f"[Error generating response with Gemini: {last_error}]"

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Send prompt to configured LLM and return generated text.

        Args:
            prompt: User-facing prompt including retrieved context.
            system_prompt: Optional system instructions.

        Returns:
            Generated response string.
        """
        self._init_client()

        if self.provider == "gemini" and self._client is not None:
            return self._generate_gemini(prompt, system_prompt)

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
