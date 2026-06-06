"""LLMClient - OpenAI-compatible client for Grok/xAI and other providers.

Provides a clean interface for LLM calls across the AI Agent Swarm Framework.
Designed to be easily swappable and support both cloud (xAI, OpenAI) and local models.
"""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional

from openai import OpenAI


class LLMClient:
    """
    Unified LLM client supporting OpenAI-compatible APIs (including xAI Grok).

    Example usage for xAI:
        client = LLMClient(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1",
            model="grok-3-latest" or "grok-beta"
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "grok-beta",
        temperature: float = 0.7,
        max_tokens: int = 800,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("XAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not self.api_key:
            raise ValueError(
                "No API key found. Set OPENAI_API_KEY or XAI_API_KEY environment variable, "
                "or pass api_key directly."
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ) -> str:
        """Send a chat completion request and return the text response."""
        response = self.client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )
        return response.choices[0].message.content.strip()

    def simple_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Convenience method for single-prompt completion."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return self.chat_completion(messages)

    def __repr__(self):
        return f"<LLMClient model={self.model} base_url={self.base_url}>"