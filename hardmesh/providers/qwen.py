"""阿里通义千问 Provider。"""
from hardmesh.providers.base import OpenAICompatibleProvider


class QwenProvider(OpenAICompatibleProvider):
    name = "qwen"
    default_model = "qwen-plus"
