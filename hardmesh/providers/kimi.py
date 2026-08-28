"""月之暗面 Kimi Provider。"""
from hardmesh.providers.base import OpenAICompatibleProvider


class KimiProvider(OpenAICompatibleProvider):
    name = "kimi"
    default_model = "kimi-k3"
