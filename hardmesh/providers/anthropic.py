"""Anthropic Claude Provider（messages 端点）。"""
import json
import urllib.request
from typing import Dict, List

from hardmesh.providers.base import LLMProvider


class AnthropicProvider(LLMProvider):
    name = "anthropic"
    default_model = "claude-sonnet-5"

    def __init__(self, config=None):
        super().__init__(config)
        self.base_url = self.config.get("base_url", "https://api.anthropic.com/v1").rstrip("/")
        self.model = self.config.get("model", self.default_model)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        url = self.base_url + "/messages"
        payload = {"model": self.model, "max_tokens": 2048,
                   "messages": [m for m in messages if m["role"] in ("user", "assistant")]}
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("x-api-key", self.api_key)
        req.add_header("anthropic-version", "2023-06-01")
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read().decode())
        try:
            return "".join(b.get("text", "") for b in resp["content"] if b.get("type") == "text")
        except (KeyError, IndexError):
            return ""

    def complete(self, prompt: str, **kwargs) -> str:
        return self.chat([{"role": "user", "content": prompt}], **kwargs)
