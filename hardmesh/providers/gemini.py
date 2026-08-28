"""Google Gemini Provider（generateContent 端点）。"""
import json
import urllib.request
from typing import Dict, List

from hardmesh.providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    name = "gemini"
    default_model = "gemini-3.6-flash"

    def __init__(self, config=None):
        super().__init__(config)
        self.base_url = self.config.get("base_url", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
        self.model = self.config.get("model", self.default_model)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        url = f"{self.base_url}/models/{self.model}:generateContent"
        contents = []
        for m in messages:
            contents.append({"role": "user" if m["role"] == "user" else "model",
                             "parts": [{"text": m["content"]}]})
        payload = {"contents": contents}
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        if self.api_key:
            req.add_header("x-goog-api-key", self.api_key)
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read().decode())
        try:
            return resp["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return ""

    def complete(self, prompt: str, **kwargs) -> str:
        return self.chat([{"role": "user", "content": prompt}], **kwargs)
