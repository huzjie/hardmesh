"""Ollama 本地 Provider。"""
from hardmesh.providers.base import OpenAICompatibleProvider


class OllamaProvider(OpenAICompatibleProvider):
    name = "ollama"
    default_model = "qwen3.8"
