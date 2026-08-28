"""LLM Provider 基类与 OpenAI 兼容客户端。"""
import json
import urllib.request
from typing import Any, Dict, List, Optional


class LLMProvider:
    name = "base"

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.api_key = self.config.get("api_key", "")

    def complete(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        raise NotImplementedError


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI 兼容 chat/completions 客户端，零第三方依赖。"""

    name = "openai_compat"
    default_model = ""

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.base_url = self.config.get("base_url", "").rstrip("/")
        self.model = self.config.get("model", self.default_model)
        self.timeout = float(self.config.get("timeout", 60))

    def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self.base_url + "/chat/completions"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        if self.api_key:
            req.add_header("Authorization", "Bearer " + self.api_key)
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read().decode("utf-8"))

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        payload = {"model": self.model, "messages": messages, "temperature": kwargs.get("temperature", 0.2)}
        resp = self._post(payload)
        try:
            return resp["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return ""

    def complete(self, prompt: str, **kwargs) -> str:
        return self.chat([{"role": "user", "content": prompt}], **kwargs)
