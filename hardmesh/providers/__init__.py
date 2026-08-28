"""LLM Provider 适配层：9 家提供商 + mock。"""
from hardmesh.providers.base import LLMProvider, OpenAICompatibleProvider  # noqa: F401
from hardmesh.providers.mock import MockProvider  # noqa: F401

__all__ = ["LLMProvider", "OpenAICompatibleProvider", "MockProvider"]


def get_provider(name: str, config: dict = None):
    """按名称构造 provider，未配置时回退 mock。"""
    config = config or {}
    mapping = {
        "openai": ("OpenAIProvider", "https://api.openai.com/v1"),
        "anthropic": ("AnthropicProvider", "https://api.anthropic.com/v1"),
        "deepseek": ("DeepSeekProvider", "https://api.deepseek.com/v1"),
        "qwen": ("QwenProvider", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        "kimi": ("KimiProvider", "https://api.moonshot.cn/v1"),
        "glm": ("GLMProvider", "https://open.bigmodel.cn/api/paas/v4"),
        "gemini": ("GeminiProvider", "https://generativelanguage.googleapis.com/v1beta"),
        "ollama": ("OllamaProvider", "http://localhost:11434/v1"),
    }
    if name == "mock" or name not in mapping:
        return MockProvider(config)
    cls_name, base_url = mapping[name]
    mod = __import__("hardmesh.providers." + name, fromlist=[cls_name])
    cls = getattr(mod, cls_name)
    cfg = dict(config)
    cfg.setdefault("base_url", base_url)
    return cls(cfg)
