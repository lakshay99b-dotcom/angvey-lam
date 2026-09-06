"""Minimal LLM client — Groq (OpenAI-compatible) first."""

from __future__ import annotations

import json
import os
from typing import Any, Optional

import httpx


class LLMClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.groq.com/openai/v1",
        model: str = "llama-3.3-70b-versatile",
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key. Set GROQ_API_KEY (or OPENAI_API_KEY) or pass api_key=..."
            )
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: Optional[dict] = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]

    def chat_json(self, messages: list[dict[str, str]], **kwargs: Any) -> dict:
        text = self.chat(
            messages,
            response_format={"type": "json_object"},
            **kwargs,
        )
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            if text.endswith("```"):
                text = text[:-3]
        return json.loads(text)
