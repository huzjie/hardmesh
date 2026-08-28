"""智谱 GLM Provider。"""
from hardmesh.providers.base import OpenAICompatibleProvider


class GLMProvider(OpenAICompatibleProvider):
    name = "glm"
    default_model = "glm-5.3-flash"
