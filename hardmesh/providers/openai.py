"""OpenAI Provider。"""
from hardmesh.providers.base import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    name = "openai"
    default_model = "gpt-5.6"
