"""DeepSeek Provider。"""
from hardmesh.providers.base import OpenAICompatibleProvider


class DeepSeekProvider(OpenAICompatibleProvider):
    name = "deepseek"
    default_model = "deepseek-chat"
