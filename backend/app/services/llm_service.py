"""LLM service — all LLM calls go through this module.

Never call OpenAI directly from agents or tools.
Always use LLMService.complete() or LLMService.complete_json().
"""

import json
import logging

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.exceptions import LLMError

logger = logging.getLogger(__name__)


class LLMService:
    """Wrapper for all LLM API calls.

    Uses OpenAI SDK for text generation.
    NVIDIA API is reserved for embeddings only (handled in embedding_tool.py).
    """

    def __init__(self, api_key: str) -> None:
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://integrate.api.nvidia.com/v1"
        )

    async def complete(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        """Send a prompt to the LLM and return the text response.

        Args:
            prompt: The user prompt to send.
            model: Model name override. Defaults to settings.default_llm_model.
            temperature: Sampling temperature (0 = deterministic).

        Returns:
            The LLM's text response.

        Raises:
            LLMError: If the API call fails or returns empty content.
        """
        model = model or settings.nvidia_model
        logger.debug("LLM call starting — model: %s, prompt length: %d", model, len(prompt))

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )
            content = response.choices[0].message.content or ""
            logger.debug("LLM call complete — response length: %d", len(content))
            return content

        except Exception as e:
            logger.error("LLM call failed: %s", e, exc_info=True)
            raise LLMError(f"LLM call failed: {e}") from e

    async def complete_json(
        self,
        prompt: str,
        model: str | None = None,
    ) -> dict:
        """Send a prompt and parse the response as JSON.

        Appends a JSON instruction to the prompt and uses temperature=0
        for deterministic output.

        Args:
            prompt: The user prompt (should request JSON output).
            model: Model name override.

        Returns:
            Parsed JSON dict from the LLM response.

        Raises:
            LLMError: If the API call fails or response is not valid JSON.
        """
        model = model or settings.nvidia_model
        raw = await self.complete(
            prompt + "\nRespond with ONLY valid JSON.",
            model=model,
            temperature=0,
        )

        # Clean common LLM artifacts around JSON
        cleaned = raw.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.removeprefix("```json")
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```")
        if cleaned.endswith("```"):
            cleaned = cleaned.removesuffix("```")
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error("JSON parse failed. Raw LLM output: %s", raw[:500])
            raise LLMError(f"LLM returned invalid JSON: {e}") from e
